from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional

PlateKind = Literal[
    "current_canonical",
    "current_shorthand_letter_first",
    "current_shorthand_digit_first",
    "legacy_arabic",
]


class AcceptanceMode(str, Enum):
    STRICT = "strict"
    STANDARD = "standard"


class FormatStyle(str, Enum):
    CANONICAL = "canonical"
    DISPLAY = "display"
    COMPACT = "compact"


@dataclass(slots=True)
class PlateOptions:
    mode: AcceptanceMode = AcceptanceMode.STANDARD
    fold_eastern_arabic_digits: bool = True
    remove_separators: bool = True


@dataclass(slots=True)
class ParsedPlate:
    kind: PlateKind
    raw_input: str
    cleaned_input: str
    is_legacy: bool
    governorate_code: Optional[str] = None
    letter: Optional[str] = None
    serial: Optional[str] = None
    canonical: Optional[str] = None
    legacy_letter: Optional[str] = None
    legacy_digits: Optional[str] = None
    legacy_normalized: Optional[str] = None


@dataclass(slots=True)
class ParseResult:
    success: bool
    plate: Optional[ParsedPlate] = None
    corrections: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ValidationIssue:
    code: str
    level: Literal["error", "warning"]
    message: str


@dataclass(slots=True)
class ValidationResult:
    is_valid: bool
    plate: Optional[ParsedPlate] = None
    issues: list[ValidationIssue] = field(default_factory=list)


@dataclass(slots=True)
class NormalizeResult:
    success: bool
    canonical: Optional[str] = None
    plate: Optional[ParsedPlate] = None
    corrections: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class IraqiPlateService:
    """
    Iraqi plate parser, normalizer, validator, formatter, and equality comparer.

    Canonical current format:
        GGAN{1-5}

    Accepted in strict mode:
        - canonical current only, after allowed cleanup

    Accepted in standard mode:
        - canonical current
        - A + D{3,7}
        - D{3,7} + A
        - ArabicLetter + D{3,7} (legacy)

    Legacy inputs accepted in standard mode are normalized into canonical form as:
        GG + ArabicLetter + serial
    and reported with a legacy warning.
    """

    _SEPARATORS_RE = re.compile(r"[\s.\-_/\\]+", re.UNICODE)
    _CANONICAL_RE = re.compile(r"^(1[1-9]|2[0-9])([A-Z])([0-9]{1,5})$")
    _CANONICAL_LEGACY_RE = re.compile(r"^(1[1-9]|2[0-9])([\u0600-\u06FF])([0-9]{1,5})$")
    _LETTER_FIRST_RE = re.compile(r"^([A-Z])([0-9]{3,7})$")
    _DIGIT_FIRST_RE = re.compile(r"^([0-9]{3,7})([A-Z])$")
    _LEGACY_RE = re.compile(r"^([\u0600-\u06FF])([0-9]{3,7})$")

    _EASTERN_ARABIC_DIGIT_MAP = str.maketrans(
        {
            "٠": "0",
            "١": "1",
            "٢": "2",
            "٣": "3",
            "٤": "4",
            "٥": "5",
            "٦": "6",
            "٧": "7",
            "٨": "8",
            "٩": "9",
            "۰": "0",
            "۱": "1",
            "۲": "2",
            "۳": "3",
            "۴": "4",
            "۵": "5",
            "۶": "6",
            "۷": "7",
            "۸": "8",
            "۹": "9",
        }
    )

    def normalize_plate(self, input: str, options: Optional[PlateOptions] = None) -> NormalizeResult:
        parse_result = self.parse_plate(input, options=options)
        if not parse_result.success or not parse_result.plate:
            return NormalizeResult(
                success=False,
                canonical=None,
                plate=None,
                corrections=parse_result.corrections,
                errors=parse_result.errors,
                warnings=parse_result.warnings,
            )

        return NormalizeResult(
            success=True,
            canonical=parse_result.plate.canonical,
            plate=parse_result.plate,
            corrections=parse_result.corrections,
            errors=[],
            warnings=parse_result.warnings,
        )

    def parse_plate(self, input: str, options: Optional[PlateOptions] = None) -> ParseResult:
        options = options or PlateOptions()

        if not isinstance(input, str):
            return ParseResult(success=False, errors=["input_must_be_string"])

        cleaned, corrections = self._clean_input(input, options)

        if not cleaned:
            return ParseResult(success=False, corrections=corrections, errors=["empty_after_cleanup"])

        if self._contains_control_characters(cleaned):
            return ParseResult(success=False, corrections=corrections, errors=["contains_control_characters"])

        match = self._CANONICAL_RE.fullmatch(cleaned)
        if match:
            gg, letter, serial = match.groups()
            plate = ParsedPlate(
                kind="current_canonical",
                raw_input=input,
                cleaned_input=cleaned,
                is_legacy=False,
                governorate_code=gg,
                letter=letter,
                serial=serial,
                canonical=f"{gg}{letter}{serial}",
            )
            return ParseResult(success=True, plate=plate, corrections=corrections)

        if options.mode != AcceptanceMode.STRICT:
            match = self._CANONICAL_LEGACY_RE.fullmatch(cleaned)
            if match:
                gg, letter, serial = match.groups()
                plate = ParsedPlate(
                    kind="legacy_arabic",
                    raw_input=input,
                    cleaned_input=cleaned,
                    is_legacy=True,
                    governorate_code=gg,
                    letter=letter,
                    serial=serial,
                    canonical=f"{gg}{letter}{serial}",
                    legacy_letter=letter,
                    legacy_digits=f"{gg}{serial}",
                    legacy_normalized=f"{letter}{gg}{serial}",
                )
                return ParseResult(success=True, plate=plate, corrections=corrections, warnings=["legacy_number"])

        if options.mode == AcceptanceMode.STRICT:
            return ParseResult(
                success=False,
                corrections=corrections,
                errors=["strict_requires_canonical_current_format"],
            )

        match = self._LETTER_FIRST_RE.fullmatch(cleaned)
        if match:
            letter, digits = match.groups()
            current = self._build_current_from_shorthand(
                raw_input=input,
                cleaned=cleaned,
                kind="current_shorthand_letter_first",
                letter=letter,
                digits=digits,
            )
            if isinstance(current, str):
                return ParseResult(success=False, corrections=corrections, errors=[current])
            return ParseResult(
                success=True,
                plate=current,
                corrections=corrections + ["reordered_to_canonical"],
                warnings=["non_canonical_order_normalized"],
            )

        match = self._DIGIT_FIRST_RE.fullmatch(cleaned)
        if match:
            digits, letter = match.groups()
            current = self._build_current_from_shorthand(
                raw_input=input,
                cleaned=cleaned,
                kind="current_shorthand_digit_first",
                letter=letter,
                digits=digits,
            )
            if isinstance(current, str):
                return ParseResult(success=False, corrections=corrections, errors=[current])
            return ParseResult(
                success=True,
                plate=current,
                corrections=corrections + ["reordered_to_canonical"],
                warnings=["non_canonical_order_normalized"],
            )

        match = self._LEGACY_RE.fullmatch(cleaned)
        if match:
            legacy_letter, digits = match.groups()
            legacy = self._build_legacy_from_shorthand(
                raw_input=input,
                cleaned=cleaned,
                legacy_letter=legacy_letter,
                digits=digits,
            )
            if isinstance(legacy, str):
                return ParseResult(success=False, corrections=corrections, errors=[legacy])
            return ParseResult(
                success=True,
                plate=legacy,
                corrections=corrections,
                warnings=["legacy_number"],
            )

        return ParseResult(success=False, corrections=corrections, errors=["invalid_structure"])

    def validate_plate(self, input: str, options: Optional[PlateOptions] = None) -> ValidationResult:
        parse_result = self.parse_plate(input, options=options)
        issues: list[ValidationIssue] = []

        for code in parse_result.warnings:
            issues.append(
                ValidationIssue(
                    code=code,
                    level="warning",
                    message=self._message_for_issue(code),
                )
            )

        for code in parse_result.errors:
            issues.append(
                ValidationIssue(
                    code=code,
                    level="error",
                    message=self._message_for_issue(code),
                )
            )

        return ValidationResult(is_valid=parse_result.success, plate=parse_result.plate, issues=issues)

    def format_plate(
        self,
        input_or_plate: str | ParsedPlate,
        style: FormatStyle = FormatStyle.CANONICAL,
        options: Optional[PlateOptions] = None,
    ) -> Optional[str]:
        if isinstance(input_or_plate, ParsedPlate):
            plate = input_or_plate
        else:
            parse_result = self.parse_plate(input_or_plate, options=options)
            if not parse_result.success or not parse_result.plate:
                return None
            plate = parse_result.plate

        if not plate.canonical or not plate.governorate_code or not plate.letter or plate.serial is None:
            return None

        if style in {FormatStyle.CANONICAL, FormatStyle.COMPACT}:
            return plate.canonical
        if style == FormatStyle.DISPLAY:
            return f"{plate.governorate_code} {plate.letter} {plate.serial}"
        return plate.canonical

    def equals(self, a: str, b: str, options: Optional[PlateOptions] = None) -> bool:
        normalized_a = self.normalize_plate(a, options=options)
        normalized_b = self.normalize_plate(b, options=options)

        if not normalized_a.success or not normalized_b.success:
            return False
        if normalized_a.canonical is None or normalized_b.canonical is None:
            return False
        return normalized_a.canonical == normalized_b.canonical

    def _clean_input(self, value: str, options: PlateOptions) -> tuple[str, list[str]]:
        corrections: list[str] = []
        value = unicodedata.normalize("NFKC", value)

        if options.remove_separators:
            new_value = self._SEPARATORS_RE.sub("", value)
            if new_value != value:
                corrections.append("removed_separators")
            value = new_value

        if options.fold_eastern_arabic_digits:
            new_value = value.translate(self._EASTERN_ARABIC_DIGIT_MAP)
            if new_value != value:
                corrections.append("folded_eastern_arabic_digits")
            value = new_value

        new_value = value.upper()
        if new_value != value:
            corrections.append("uppercased_latin_letter")
        value = new_value
        return value, corrections

    def _build_current_from_shorthand(
        self,
        raw_input: str,
        cleaned: str,
        kind: Literal["current_shorthand_letter_first", "current_shorthand_digit_first"],
        letter: str,
        digits: str,
    ) -> ParsedPlate | str:
        if not (3 <= len(digits) <= 7):
            return "digit_count_must_be_3_to_7_for_shorthand"

        gg = digits[:2]
        serial = digits[2:]

        if not self._is_valid_governorate(gg):
            return "governorate_out_of_range"
        if not (1 <= len(serial) <= 5):
            return "serial_length_out_of_range"

        return ParsedPlate(
            kind=kind,
            raw_input=raw_input,
            cleaned_input=cleaned,
            is_legacy=False,
            governorate_code=gg,
            letter=letter,
            serial=serial,
            canonical=f"{gg}{letter}{serial}",
        )

    def _build_legacy_from_shorthand(
        self,
        raw_input: str,
        cleaned: str,
        legacy_letter: str,
        digits: str,
    ) -> ParsedPlate | str:
        if not (3 <= len(digits) <= 7):
            return "digit_count_must_be_3_to_7_for_legacy"

        gg = digits[:2]
        serial = digits[2:]

        if not self._is_valid_governorate(gg):
            return "governorate_out_of_range"
        if not (1 <= len(serial) <= 5):
            return "serial_length_out_of_range"

        return ParsedPlate(
            kind="legacy_arabic",
            raw_input=raw_input,
            cleaned_input=cleaned,
            is_legacy=True,
            governorate_code=gg,
            letter=legacy_letter,
            serial=serial,
            canonical=f"{gg}{legacy_letter}{serial}",
            legacy_letter=legacy_letter,
            legacy_digits=digits,
            legacy_normalized=f"{legacy_letter}{digits}",
        )

    @staticmethod
    def _contains_control_characters(value: str) -> bool:
        return any(unicodedata.category(ch).startswith("C") for ch in value)

    @staticmethod
    def _is_valid_governorate(gg: str) -> bool:
        return gg.isdigit() and len(gg) == 2 and 11 <= int(gg) <= 29

    @staticmethod
    def _message_for_issue(code: str) -> str:
        messages = {
            "legacy_number": "Accepted input is a legacy number format.",
            "non_canonical_order_normalized": "Input order was normalized to canonical format.",
            "input_must_be_string": "Input must be a string.",
            "empty_after_cleanup": "Input became empty after cleanup.",
            "contains_control_characters": "Input contains control characters.",
            "strict_requires_canonical_current_format": "Strict mode accepts only canonical current format.",
            "invalid_structure": "Input does not match any accepted plate structure.",
            "digit_count_must_be_3_to_7_for_shorthand": "Shorthand formats require 3 to 7 digits.",
            "digit_count_must_be_3_to_7_for_legacy": "Legacy format requires 3 to 7 digits.",
            "governorate_out_of_range": "Governorate code must be between 11 and 29.",
            "serial_length_out_of_range": "Serial length must be between 1 and 5 digits.",
        }
        return messages.get(code, code)
