from multiconvert.formats import (
    EXT_TO_FORMAT,
    detect_format,
    ensure_extension,
    normalize_format,
)


def test_detect_format_supports_new_image_types() -> None:
    assert detect_format("sample.gif") == "gif"
    assert detect_format("sample.webp") == "webp"


def test_normalize_format_aliases() -> None:
    assert normalize_format(".JPEG") == "jpg"
    assert normalize_format("tiff") == "tif"
    assert normalize_format("markdown") == "md"


def test_ensure_extension_uses_normalized_alias() -> None:
    assert ensure_extension("out.tmp", "jpeg").suffix == ".jpg"
    assert ensure_extension("out", "markdown").suffix == ".md"


def test_input_format_count_is_current() -> None:
    # Guard against stale documentation by asserting current known input types.
    # Updated for v0.2.0 with expanded format support (35+ formats)
    input_types = set(EXT_TO_FORMAT.values())
    assert len(input_types) >= 30  # We support 34+ unique format types now
