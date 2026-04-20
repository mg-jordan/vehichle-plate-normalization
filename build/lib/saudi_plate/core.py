from __future__ import annotations

import re
import unicodedata
from dataclasses import replace
from typing import List, Sequence, Tuple

from .mappings import (
    ARABIC_INDIC_TO_ASCII,
    ARABIC_TO_CODE,
    ASCII_TO_ARABIC_INDIC,
    BIDI_CONTROL_CHARS,
    CODE_TO_ARABIC,
    CODE_TO_LATIN,
    LATIN_TO_CODE,
    VALID_ARABIC_LETTERS,
    VALID_LATIN_LETTERS,
)
from .models import (
    Correction,
    DigitSet,
    FormatStyle,
    NormalizeOptions,
    NormalizeResult,
    ParseOptions,
    ParseResult,
    Plate,
    Script,
    Strictness,
    ValidationIssue,
    ValidationResult,
)

SEPARATOR_PATTERN = re.compile(r"[\s\-_/\\.|]+")
ASCII_DIGIT_RE = re.compile(r"^[0-9]+$")

ARABIC_INPUT_FOLD_MAP = str.maketrans({
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ٱ": "ا",
    "ى": "ي",
    "ؤ": "و",
    "ئ": "ي",
    "ة": "ه",
})

ARABIC_INPUT_FOLD_MAP_LENIENT = str.maketrans({
})

def fold_arabic_input_variants(text: str, *, lenient: bool = False) -> str:
    folded = text.translate(ARABIC_INPUT_FOLD_MAP)
    if lenient:
        folded = folded.translate(ARABIC_INPUT_FOLD_MAP_LENIENT)
    return folded

class Policy:
    def __init__(
        self,
        *,
        allow_mixed_scripts: bool,
        allow_reordered_input: bool,
        allow_short_digits: bool,
    ) -> None:
        self.allow_mixed_scripts = allow_mixed_scripts
        self.allow_reordered_input = allow_reordered_input
        self.allow_short_digits = allow_short_digits


def resolve_policy(strictness: Strictness, options: ParseOptions | NormalizeOptions | None) -> Policy:
    if strictness == Strictness.STRICT:
        defaults = Policy(
            allow_mixed_scripts=False,
            allow_reordered_input=False,
            allow_short_digits=False,
        )
    elif strictness == Strictness.LENIENT:
        defaults = Policy(
            allow_mixed_scripts=True,
            allow_reordered_input=True,
            allow_short_digits=True,
        )
    else:
        defaults = Policy(
            allow_mixed_scripts=True,
            allow_reordered_input=True,
            allow_short_digits=True,
        )

    if options is None:
        return defaults

    return Policy(
        allow_mixed_scripts=defaults.allow_mixed_scripts if options.allow_mixed_scripts is None else options.allow_mixed_scripts,
        allow_reordered_input=defaults.allow_reordered_input if options.allow_reordered_input is None else options.allow_reordered_input,
        allow_short_digits=defaults.allow_short_digits if options.allow_short_digits is None else options.allow_short_digits,
    )


def clean_input(raw: str) -> Tuple[str, List[Correction]]:
    corrections: List[Correction] = []
    cleaned = unicodedata.normalize("NFKC", raw)
    if cleaned != raw:
        corrections.append(Correction("unicode_normalization", raw, cleaned))

    no_bidi = "".join(ch for ch in cleaned if ch not in BIDI_CONTROL_CHARS)
    if no_bidi != cleaned:
        corrections.append(Correction("bidi_control_removal", cleaned, no_bidi))
        cleaned = no_bidi

    folded = fold_arabic_input_variants(cleaned)
    if folded != cleaned:
        corrections.append(Correction("arabic_variant_folding", cleaned, folded))
        cleaned = folded
    
    digit_normalized = cleaned.translate(ARABIC_INDIC_TO_ASCII)
    if digit_normalized != cleaned:
        corrections.append(Correction("digit_conversion", cleaned, digit_normalized))
        cleaned = digit_normalized

    stripped = cleaned.strip()
    if stripped != cleaned:
        corrections.append(Correction("trim", cleaned, stripped))
        cleaned = stripped

    compacted = SEPARATOR_PATTERN.sub(" ", cleaned)
    compacted = re.sub(r"\s+", " ", compacted)
    if compacted != cleaned:
        corrections.append(Correction("separator_normalization", cleaned, compacted))
        cleaned = compacted

    return cleaned, corrections


def char_script(ch: str) -> Script:
    if ch in VALID_ARABIC_LETTERS:
        return Script.ARABIC
    if ch.upper() in VALID_LATIN_LETTERS:
        return Script.LATIN
    return Script.UNKNOWN


def detect_script(text: str) -> Script:
    scripts = {char_script(ch) for ch in text if char_script(ch) != Script.UNKNOWN}
    if not scripts:
        return Script.UNKNOWN
    if len(scripts) == 1:
        return next(iter(scripts))
    return Script.MIXED


def is_supported_letter(ch: str) -> bool:
    return ch in VALID_ARABIC_LETTERS or ch.upper() in VALID_LATIN_LETTERS


def to_letter_code(ch: str) -> str | None:
    if ch in ARABIC_TO_CODE:
        return ARABIC_TO_CODE[ch]
    return LATIN_TO_CODE.get(ch.upper())


def transliterate_letters(text: str, target_script: Script) -> str:
    if target_script not in {Script.ARABIC, Script.LATIN}:
        raise ValueError("target_script must be Script.ARABIC or Script.LATIN")

    converted: List[str] = []
    for ch in text:
        code = to_letter_code(ch)
        if code is None:
            converted.append(ch)
        elif target_script == Script.ARABIC:
            converted.append(CODE_TO_ARABIC[code])
        else:
            converted.append(CODE_TO_LATIN[code])
    return "".join(converted)


def convert_digits(text: str, target_digits: DigitSet) -> str:
    ascii_text = text.translate(ARABIC_INDIC_TO_ASCII)
    if target_digits == DigitSet.ASCII:
        return ascii_text
    if target_digits == DigitSet.ARABIC_INDIC:
        return ascii_text.translate(ASCII_TO_ARABIC_INDIC)
    raise ValueError("unsupported target digit set")


def tokenize(cleaned: str) -> Tuple[List[str], List[str], List[str]]:
    letters: List[str] = []
    digits: List[str] = []
    unknown: List[str] = []

    for ch in cleaned.replace(" ", ""):
        if ch.isdigit():
            digits.append(ch)
        elif is_supported_letter(ch):
            letters.append(ch)
        else:
            unknown.append(ch)
    return letters, digits, unknown


def parse_plate(raw_input: str, options: ParseOptions | None = None) -> ParseResult:
    options = options or ParseOptions()
    policy = resolve_policy(options.strictness, options)
    cleaned, corrections = clean_input(raw_input)
    letters_raw, digits_raw, unknown = tokenize(cleaned)
    warnings: List[ValidationIssue] = []
    errors: List[ValidationIssue] = []

    source_script = detect_script("".join(letters_raw))
    if source_script == Script.MIXED and not policy.allow_mixed_scripts:
        errors.append(
            ValidationIssue(
                code="MIXED_SCRIPTS_NOT_ALLOWED",
                message="Mixed Arabic and Latin plate letters are not allowed in strict mode.",
                field="letters",
            )
        )

    if unknown:
        errors.append(
            ValidationIssue(
                code="UNSUPPORTED_CHARACTERS",
                message=f"Unsupported characters found: {''.join(unknown)}",
                field="input",
                metadata={"characters": unknown},
            )
        )

    unsupported_characters_present = bool(unknown)

    if len(letters_raw) != 3:
        should_report_letter_count = True
        if unsupported_characters_present and len(letters_raw) < 3:
            # Avoid stacking a secondary count error when the primary problem is
            # that one or more characters are unsupported and therefore could
            # not participate in plate-letter parsing. Example: ``ABC1234``
            # should report the unsupported ``C`` rather than both
            # ``UNSUPPORTED_CHARACTERS`` and ``INVALID_LETTER_COUNT``.
            should_report_letter_count = False

        if should_report_letter_count:
            errors.append(
                ValidationIssue(
                    code="INVALID_LETTER_COUNT",
                    message=f"Expected exactly 3 letters, found {len(letters_raw)}.",
                    field="letters",
                )
            )

    if not digits_raw:
        errors.append(
            ValidationIssue(
                code="MISSING_DIGITS",
                message="Expected 1 to 4 digits, found none.",
                field="digits",
            )
        )
    elif len(digits_raw) > 4:
        errors.append(
            ValidationIssue(
                code="INVALID_DIGIT_COUNT",
                message=f"Expected at most 4 digits, found {len(digits_raw)}.",
                field="digits",
            )
        )
    elif len(digits_raw) < 4 and not policy.allow_short_digits:
        errors.append(
            ValidationIssue(
                code="SHORT_DIGITS_NOT_ALLOWED",
                message=f"Expected exactly 4 digits in strict mode, found {len(digits_raw)}.",
                field="digits",
            )
        )

    compact = cleaned.replace(" ", "")
    letters_then_digits = bool(re.fullmatch(r"[A-Za-z\u0621-\u064A]{3}[0-9]{1,4}", compact))
    digits_then_letters = bool(re.fullmatch(r"[0-9]{1,4}[A-Za-z\u0621-\u064A]{3}", compact))
    if digits_then_letters:
        if policy.allow_reordered_input:
            warnings.append(
                ValidationIssue(
                    code="REORDERED_INPUT",
                    message="Digits were entered before letters and were normalized.",
                    severity="warning",
                    field="order",
                )
            )
        else:
            errors.append(
                ValidationIssue(
                    code="REORDERED_INPUT_NOT_ALLOWED",
                    message="Digits before letters are not allowed in strict mode.",
                    field="order",
                )
            )
    elif not letters_then_digits and compact and not errors:
        warnings.append(
            ValidationIssue(
                code="NON_STANDARD_LAYOUT",
                message="Input was accepted after normalization from a non-standard layout.",
                severity="warning",
                field="order",
            )
        )

    if errors:
        return ParseResult(
            success=False,
            raw_input=raw_input,
            normalized_input=cleaned,
            plate=None,
            errors=errors,
            warnings=warnings,
        )

    letter_codes = tuple(to_letter_code(ch) for ch in letters_raw)
    if any(code is None for code in letter_codes):
        errors.append(
            ValidationIssue(
                code="UNKNOWN_LETTER",
                message="One or more letters could not be mapped to Saudi plate codes.",
                field="letters",
            )
        )
        return ParseResult(
            success=False,
            raw_input=raw_input,
            normalized_input=cleaned,
            plate=None,
            errors=errors,
            warnings=warnings,
        )

    plate = Plate(country="SA", letters=letter_codes, digits="".join(digits_raw), source_script=source_script)
    return ParseResult(
        success=True,
        raw_input=raw_input,
        normalized_input=cleaned,
        plate=plate,
        errors=(),
        warnings=warnings,
    )


def normalize_plate(raw_input: str | Plate, options: NormalizeOptions | None = None) -> NormalizeResult:
    if isinstance(raw_input, Plate):
        return NormalizeResult(success=True, canonical=raw_input.canonical, plate=raw_input)

    options = options or NormalizeOptions()
    cleaned, corrections = clean_input(raw_input)
    parse_result = parse_plate(
        cleaned,
        ParseOptions(
            strictness=options.strictness,
            allow_mixed_scripts=options.allow_mixed_scripts,
            allow_reordered_input=options.allow_reordered_input,
            allow_short_digits=options.allow_short_digits,
        ),
    )
    if not parse_result.success or parse_result.plate is None:
        return NormalizeResult(
            success=False,
            canonical=None,
            plate=None,
            corrections=corrections,
            errors=parse_result.errors,
            warnings=parse_result.warnings,
        )

    return NormalizeResult(
        success=True,
        canonical=parse_result.plate.canonical,
        plate=parse_result.plate,
        corrections=corrections,
        errors=(),
        warnings=parse_result.warnings,
    )


def validate_plate(raw_input: str | Plate, options: NormalizeOptions | None = None) -> ValidationResult:
    if isinstance(raw_input, Plate):
        issues: List[ValidationIssue] = []
        if len(raw_input.letters) != 3:
            issues.append(ValidationIssue("INVALID_LETTER_COUNT", "Expected exactly 3 letters.", field="letters"))
        if not ASCII_DIGIT_RE.fullmatch(raw_input.digits):
            issues.append(ValidationIssue("INVALID_DIGITS", "Digits must be ASCII digits.", field="digits"))
        if len(raw_input.digits) < 1 or len(raw_input.digits) > 4:
            issues.append(ValidationIssue("INVALID_DIGIT_COUNT", "Expected 1 to 4 digits.", field="digits"))
        return ValidationResult(is_valid=not issues, plate=raw_input, issues=issues)

    result = normalize_plate(raw_input, options)
    issues = list(result.errors) + list(result.warnings)
    return ValidationResult(is_valid=result.success, plate=result.plate, issues=issues)


def format_plate(plate_or_input: str | Plate, style: FormatStyle = FormatStyle.CANONICAL, options: NormalizeOptions | None = None) -> str:
    plate: Plate
    if isinstance(plate_or_input, Plate):
        plate = plate_or_input
    else:
        normalized = normalize_plate(plate_or_input, options)
        if not normalized.success or normalized.plate is None:
            messages = "; ".join(issue.message for issue in normalized.errors)
            raise ValueError(f"Cannot format invalid plate: {messages}")
        plate = normalized.plate

    latin = "".join(CODE_TO_LATIN[code] for code in plate.letters)
    arabic = " ".join(CODE_TO_ARABIC[code] for code in plate.letters)
    arabic_digits = convert_digits(plate.digits, DigitSet.ARABIC_INDIC)

    if style in {FormatStyle.CANONICAL, FormatStyle.STORAGE}:
        return f"{latin}-{plate.digits}"
    if style == FormatStyle.DISPLAY_EN:
        return f"{latin} {plate.digits}"
    if style == FormatStyle.COMPACT_EN:
        return f"{latin}{plate.digits}"
    if style == FormatStyle.DISPLAY_AR:
        return f"{arabic_digits} {arabic}"
    if style == FormatStyle.COMPACT_AR:
        return f"{arabic_digits}{''.join(CODE_TO_ARABIC[code] for code in plate.letters)}"
    raise ValueError(f"Unsupported format style: {style}")


def equals(a: str | Plate, b: str | Plate, options: NormalizeOptions | None = None) -> bool:
    a_result = normalize_plate(a, options) if isinstance(a, str) else NormalizeResult(True, a.canonical, a)
    b_result = normalize_plate(b, options) if isinstance(b, str) else NormalizeResult(True, b.canonical, b)
    return bool(a_result.success and b_result.success and a_result.canonical == b_result.canonical)
