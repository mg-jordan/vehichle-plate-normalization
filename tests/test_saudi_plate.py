import contextlib
import io

from saudi_plate import (
    DigitSet,
    FormatStyle,
    NormalizeOptions,
    Script,
    Strictness,
    convert_digits,
    detect_script,
    equals,
    format_plate,
    normalize_plate,
    parse_plate,
    transliterate_letters,
    validate_plate,
)


def test_normalize_arabic_input_to_canonical():
    result = normalize_plate("ا ب ح ١٢٣٤")
    assert result.success is True
    assert result.canonical == "ABJ-1234"
    assert result.plate is not None
    assert result.plate.letters == ("ALIF", "BA", "HA")


def test_normalize_arabic_variant_input_is_silent():
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        result = normalize_plate("أ ب ح ١٢٣٤")

    assert stdout.getvalue() == ""
    assert result.success is True
    assert result.canonical == "ABJ-1234"


def test_normalize_digits_then_letters_with_warning():
    result = normalize_plate("1234 ABJ")
    assert result.success is True
    assert result.canonical == "ABJ-1234"
    assert any(issue.code == "REORDERED_INPUT" for issue in result.warnings)


def test_strict_mode_rejects_reordered_input():
    result = normalize_plate(
        "1234 ABJ",
        NormalizeOptions(strictness=Strictness.STRICT),
    )
    assert result.success is False
    assert any(issue.code == "REORDERED_INPUT_NOT_ALLOWED" for issue in result.errors)


def test_strict_mode_requires_exactly_four_digits():
    result = normalize_plate(
        "ABJ 123",
        NormalizeOptions(strictness=Strictness.STRICT),
    )
    assert result.success is False
    assert any(issue.code == "SHORT_DIGITS_NOT_ALLOWED" for issue in result.errors)


def test_invalid_letter_is_rejected():
    result = normalize_plate("ABC 1234")
    assert result.success is False
    assert [issue.code for issue in result.errors] == ["UNSUPPORTED_CHARACTERS"]


def test_display_formats():
    assert format_plate("ABJ1234", FormatStyle.CANONICAL) == "ABJ-1234"
    assert format_plate("ABJ1234", FormatStyle.DISPLAY_EN) == "ABJ 1234"
    assert format_plate("ABJ1234", FormatStyle.DISPLAY_AR) == "١٢٣٤ ا ب ح"


def test_equals_cross_script():
    assert equals("ABJ1234", "ا ب ح ١٢٣٤") is True


def test_detect_script():
    assert detect_script("ABJ") == Script.LATIN
    assert detect_script("ابح") == Script.ARABIC
    assert detect_script("AبJ") == Script.MIXED


def test_transliterate_letters():
    assert transliterate_letters("ابح", Script.LATIN) == "ABJ"
    assert transliterate_letters("ABJ", Script.ARABIC) == "ابح"


def test_convert_digits():
    assert convert_digits("١٢٣٤", DigitSet.ASCII) == "1234"
    assert convert_digits("1234", DigitSet.ARABIC_INDIC) == "١٢٣٤"


def test_validate_plate_reports_issues():
    result = validate_plate("OOO 1234")
    assert result.is_valid is False
    assert len(result.issues) > 0


def test_parse_plate_success():
    result = parse_plate("ABJ-1234")
    assert result.success is True
    assert result.plate is not None
    assert result.plate.canonical == "ABJ-1234"
