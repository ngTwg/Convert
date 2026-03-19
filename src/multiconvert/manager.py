from __future__ import annotations

import heapq
import shutil
import tempfile
from collections.abc import Callable, Iterable
from pathlib import Path

from multiconvert.converters.base import BaseConverter
from multiconvert.errors import ConversionError
from multiconvert.formats import (
    DEFAULT_INTERMEDIATES,
    detect_format,
    ensure_extension,
    normalize_format,
)
from multiconvert.models import ConversionRequest, ConversionResult, RouteStep

LogFn = Callable[[str], None]


class ConverterManager:
    def __init__(self, converters: Iterable[BaseConverter]) -> None:
        self._converters = list(converters)

    @property
    def converters(self) -> tuple[BaseConverter, ...]:
        return tuple(self._converters)

    def active_converters(self) -> list[BaseConverter]:
        return [converter for converter in self._converters if converter.available()]

    def all_formats(self) -> set[str]:
        formats: set[str] = set()
        for converter in self.active_converters():
            for src, dst in converter.supported_pairs():
                formats.add(src)
                formats.add(dst)
        return formats

    def output_formats_for(self, source_format: str) -> set[str]:
        source_format = normalize_format(source_format) or source_format
        adjacency: dict[str, set[str]] = {}
        for converter in self.active_converters():
            for src, dst in converter.supported_pairs():
                adjacency.setdefault(src, set()).add(dst)

        outputs: set[str] = set()
        seen = {source_format}
        stack = [source_format]
        while stack:
            cur = stack.pop()
            for nxt in adjacency.get(cur, set()):
                if nxt in seen:
                    continue
                seen.add(nxt)
                outputs.add(nxt)
                stack.append(nxt)
        return outputs

    def find_route(
        self,
        source_format: str,
        target_format: str,
        *,
        prefer_intermediates: bool = True,
    ) -> list[tuple[str, str, BaseConverter]]:
        source_format = normalize_format(source_format) or source_format
        target_format = normalize_format(target_format) or target_format

        if source_format == target_format:
            return []

        adjacency: dict[str, list[tuple[str, BaseConverter]]] = {}
        for converter in self.active_converters():
            for src, dst in converter.supported_pairs():
                adjacency.setdefault(src, []).append((dst, converter))

        if source_format not in adjacency:
            raise ConversionError(
                f"No converter can read source format '{source_format}'."
            )

        queue: list[tuple[int, str]] = [(0, source_format)]
        distance: dict[str, int] = {source_format: 0}
        previous: dict[str, tuple[str, BaseConverter]] = {}

        while queue:
            cost, current = heapq.heappop(queue)
            if current == target_format:
                break
            if cost > distance.get(current, 10**9):
                continue

            for nxt, converter in adjacency.get(current, []):
                step_cost = max(converter.priority, 1)
                if prefer_intermediates and nxt in DEFAULT_INTERMEDIATES:
                    step_cost = max(step_cost - 1, 1)
                new_cost = cost + step_cost

                if new_cost < distance.get(nxt, 10**9):
                    distance[nxt] = new_cost
                    previous[nxt] = (current, converter)
                    heapq.heappush(queue, (new_cost, nxt))

        if target_format not in distance:
            raise ConversionError(
                f"No conversion route found: {source_format} -> {target_format}."
            )

        route: list[tuple[str, str, BaseConverter]] = []
        cur = target_format
        while cur != source_format:
            prev_fmt, converter = previous[cur]
            route.append((prev_fmt, cur, converter))
            cur = prev_fmt
        route.reverse()
        return route

    def convert(self, request: ConversionRequest, logger: LogFn | None = None) -> ConversionResult:
        source_format = request.source_format or detect_format(request.source)
        target_format = request.target_format or detect_format(request.destination)

        if not source_format:
            raise ConversionError(
                f"Cannot detect source format from file extension: {request.source.name}"
            )
        if not target_format:
            raise ConversionError(
                f"Cannot detect destination format from file extension: {request.destination.name}"
            )

        source_path = request.source.resolve()
        destination = ensure_extension(request.destination, target_format).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)

        if normalize_format(source_format) == normalize_format(target_format):
            shutil.copy2(source_path, destination)
            if logger:
                logger(f"Copied without conversion: {source_path.name}")
            return ConversionResult(destination=destination, route=[])

        force_ocr = bool(request.options.get("force_ocr"))
        if force_ocr:
            forced = self._find_route_with_forced_ocr(source_format, target_format)
            route = forced if forced is not None else self.find_route(source_format, target_format)
        else:
            route = self.find_route(source_format, target_format)
        route_steps: list[RouteStep] = []

        with tempfile.TemporaryDirectory(prefix="multiconvert_") as tmp_text:
            tmp_dir = Path(tmp_text)
            current_path = source_path
            for index, (src_fmt, dst_fmt, converter) in enumerate(route):
                is_last = index == len(route) - 1
                out_path = destination if is_last else tmp_dir / f"step_{index + 1}.{dst_fmt}"
                if logger:
                    logger(
                        f"Step {index + 1}/{len(route)}: {converter.name} ({src_fmt} -> {dst_fmt})"
                    )
                converter.convert(
                    current_path,
                    out_path,
                    src_fmt,
                    dst_fmt,
                    options=request.options,
                )
                route_steps.append(
                    RouteStep(
                        converter=converter.name,
                        source_format=src_fmt,
                        target_format=dst_fmt,
                    )
                )
                current_path = out_path

        if not destination.exists():
            raise ConversionError("Conversion finished but destination file is missing.")

        if logger:
            logger(f"Output created: {destination}")
        return ConversionResult(destination=destination, route=route_steps)

    def _find_route_with_forced_ocr(
        self,
        source_format: str,
        target_format: str,
    ) -> list[tuple[str, str, BaseConverter]] | None:
        source_format = normalize_format(source_format) or source_format
        target_format = normalize_format(target_format) or target_format
        ocr = next(
            (converter for converter in self.active_converters() if converter.name == "ocr"),
            None,
        )
        if ocr is None:
            return None

        candidates: list[list[tuple[str, str, BaseConverter]]] = []
        for src, mid in ocr.supported_pairs():
            if src != source_format:
                continue
            if mid == target_format:
                candidates.append([(source_format, target_format, ocr)])
                continue
            try:
                tail = self.find_route(mid, target_format)
            except ConversionError:
                continue
            candidates.append([(source_format, mid, ocr), *tail])

        if not candidates:
            return None

        def _cost(route: list[tuple[str, str, BaseConverter]]) -> int:
            return sum(max(step_converter.priority, 1) for _, _, step_converter in route)

        return min(candidates, key=_cost)
