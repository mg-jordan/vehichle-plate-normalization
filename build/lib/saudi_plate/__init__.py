"""Saudi vehicle plate parsing, normalization, validation, and formatting."""

from .api import (
    convert_digits,
    detect_script,
    equals,
    format_plate,
    normalize_plate,
    parse_plate,
    transliterate_letters,
    validate_plate,
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

__all__ = [
    "Correction",
    "DigitSet",
    "FormatStyle",
    "NormalizeOptions",
    "NormalizeResult",
    "ParseOptions",
    "ParseResult",
    "Plate",
    "Script",
    "Strictness",
    "ValidationIssue",
    "ValidationResult",
    "convert_digits",
    "detect_script",
    "equals",
    "format_plate",
    "normalize_plate",
    "parse_plate",
    "transliterate_letters",
    "validate_plate",
]

__version__ = "0.1.0"
