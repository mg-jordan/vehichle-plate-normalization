import { CODE_TO_LATIN } from './mappings.js';

export const Strictness = Object.freeze({
  STRICT: 'strict',
  STANDARD: 'standard',
  LENIENT: 'lenient',
});

export const Script = Object.freeze({
  ARABIC: 'arabic',
  LATIN: 'latin',
  MIXED: 'mixed',
  UNKNOWN: 'unknown',
});

export const DigitSet = Object.freeze({
  ASCII: 'ascii',
  ARABIC_INDIC: 'arabic_indic',
});

export const FormatStyle = Object.freeze({
  CANONICAL: 'canonical',
  STORAGE: 'storage',
  DISPLAY_EN: 'display_en',
  DISPLAY_AR: 'display_ar',
  COMPACT_EN: 'compact_en',
  COMPACT_AR: 'compact_ar',
});

export class Plate {
  constructor({ country, letters, digits, sourceScript = Script.UNKNOWN }) {
    this.country = country;
    this.letters = Object.freeze([...letters]);
    this.digits = digits;
    this.sourceScript = sourceScript;
  }

  get canonical() {
    const latin = this.letters.map((code) => CODE_TO_LATIN[code]).join('');
    return `${latin}-${this.digits}`;
  }
}

export class ValidationIssue {
  constructor({ code, message, severity = 'error', field = null, metadata = null }) {
    this.code = code;
    this.message = message;
    this.severity = severity;
    this.field = field;
    this.metadata = metadata;
  }
}

export class Correction {
  constructor(type, before, after) {
    this.type = type;
    this.before = before;
    this.after = after;
  }
}

export class ParseOptions {
  constructor({
    strictness = Strictness.STANDARD,
    allowMixedScripts = null,
    allowReorderedInput = null,
    allowShortDigits = null,
  } = {}) {
    this.strictness = strictness;
    this.allowMixedScripts = allowMixedScripts;
    this.allowReorderedInput = allowReorderedInput;
    this.allowShortDigits = allowShortDigits;
  }
}

export class NormalizeOptions {
  constructor({
    strictness = Strictness.STANDARD,
    allowMixedScripts = null,
    allowReorderedInput = null,
    allowShortDigits = null,
  } = {}) {
    this.strictness = strictness;
    this.allowMixedScripts = allowMixedScripts;
    this.allowReorderedInput = allowReorderedInput;
    this.allowShortDigits = allowShortDigits;
  }
}

export class ParseResult {
  constructor({ success, rawInput, normalizedInput = null, plate = null, errors = [], warnings = [] }) {
    this.success = success;
    this.rawInput = rawInput;
    this.normalizedInput = normalizedInput;
    this.plate = plate;
    this.errors = errors;
    this.warnings = warnings;
  }
}

export class NormalizeResult {
  constructor({ success, canonical = null, plate = null, corrections = [], errors = [], warnings = [] }) {
    this.success = success;
    this.canonical = canonical;
    this.plate = plate;
    this.corrections = corrections;
    this.errors = errors;
    this.warnings = warnings;
  }
}

export class ValidationResult {
  constructor({ isValid, plate = null, issues = [] }) {
    this.isValid = isValid;
    this.plate = plate;
    this.issues = issues;
  }
}
