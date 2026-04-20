from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Sequence, Tuple

from .mappings import CODE_TO_LATIN


class Strictness(str, Enum):
    STRICT = "strict"
    STANDARD = "standard"
    LENIENT = "lenient"


class Script(str, Enum):
    ARABIC = "arabic"
    LATIN = "latin"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class DigitSet(str, Enum):
    ASCII = "ascii"
    ARABIC_INDIC = "arabic_indic"


class FormatStyle(str, Enum):
    CANONICAL = "canonical"
    STORAGE = "storage"
    DISPLAY_EN = "display_en"
    DISPLAY_AR = "display_ar"
    COMPACT_EN = "compact_en"
    COMPACT_AR = "compact_ar"


@dataclass(frozen=True)
class Plate:
    country: str
    letters: Tuple[str, str, str]
    digits: str
    source_script: Script = Script.UNKNOWN

    @property
    def canonical(self) -> str:
        latin = "".join(CODE_TO_LATIN[code] for code in self.letters)
        return f"{latin}-{self.digits}"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"
    field: Optional[str] = None
    metadata: Optional[dict] = None


@dataclass(frozen=True)
class Correction:
    type: str
    before: str
    after: str


@dataclass(frozen=True)
class ParseOptions:
    strictness: Strictness = Strictness.STANDARD
    allow_mixed_scripts: Optional[bool] = None
    allow_reordered_input: Optional[bool] = None
    allow_short_digits: Optional[bool] = None


@dataclass(frozen=True)
class NormalizeOptions:
    strictness: Strictness = Strictness.STANDARD
    allow_mixed_scripts: Optional[bool] = None
    allow_reordered_input: Optional[bool] = None
    allow_short_digits: Optional[bool] = None


@dataclass(frozen=True)
class ParseResult:
    success: bool
    raw_input: str
    normalized_input: Optional[str] = None
    plate: Optional[Plate] = None
    errors: Sequence[ValidationIssue] = field(default_factory=list)
    warnings: Sequence[ValidationIssue] = field(default_factory=list)


@dataclass(frozen=True)
class NormalizeResult:
    success: bool
    canonical: Optional[str] = None
    plate: Optional[Plate] = None
    corrections: Sequence[Correction] = field(default_factory=list)
    errors: Sequence[ValidationIssue] = field(default_factory=list)
    warnings: Sequence[ValidationIssue] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    plate: Optional[Plate] = None
    issues: Sequence[ValidationIssue] = field(default_factory=list)
