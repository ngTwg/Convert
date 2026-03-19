from pathlib import Path

from multiconvert.converters.base import BaseConverter
from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest


class DummyConverter(BaseConverter):
    def __init__(self, name: str, pairs: set[tuple[str, str]], priority: int = 5) -> None:
        self.name = name
        self.priority = priority
        self._pairs = pairs

    def supported_pairs(self) -> set[tuple[str, str]]:
        return self._pairs

    def available(self) -> bool:
        return True

    def convert(
        self,
        source: Path,
        destination: Path,
        source_format: str,
        target_format: str,
        options: dict,
    ) -> None:
        destination.write_text(
            f"{source.name}:{source_format}->{target_format}", encoding="utf-8"
        )


def test_find_route_prefers_lower_cost() -> None:
    a = DummyConverter("a", {("md", "html"), ("html", "pdf")}, priority=3)
    b = DummyConverter("b", {("md", "pdf")}, priority=10)
    manager = ConverterManager([a, b])
    route = manager.find_route("md", "pdf")
    assert [step[2].name for step in route] == ["a", "a"]


def test_convert_runs_multi_step(tmp_path: Path) -> None:
    c1 = DummyConverter("step1", {("md", "html")})
    c2 = DummyConverter("step2", {("html", "pdf")})
    manager = ConverterManager([c1, c2])
    source = tmp_path / "input.md"
    source.write_text("# Hello", encoding="utf-8")
    destination = tmp_path / "out.pdf"

    request = ConversionRequest(source=source, destination=destination, target_format="pdf")
    result = manager.convert(request)

    assert result.destination.exists()
    assert result.route[-1].target_format == "pdf"


def test_force_ocr_prefers_ocr_route(tmp_path: Path) -> None:
    ocr = DummyConverter("ocr", {("pdf", "txt")}, priority=20)
    direct = DummyConverter("direct", {("pdf", "docx")}, priority=1)
    tail = DummyConverter("tail", {("txt", "docx")}, priority=1)
    manager = ConverterManager([ocr, direct, tail])
    source = tmp_path / "scan.pdf"
    source.write_text("stub", encoding="utf-8")
    destination = tmp_path / "out.docx"

    request = ConversionRequest(
        source=source,
        destination=destination,
        target_format="docx",
        options={"force_ocr": True},
    )
    result = manager.convert(request)
    assert [step.converter for step in result.route] == ["ocr", "tail"]
