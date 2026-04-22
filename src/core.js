import {
  ARABIC_INDIC_DIGITS,
  ARABIC_TO_CODE,
  ASCII_DIGITS,
  BIDI_CONTROL_CHARS,
  CODE_TO_ARABIC,
  CODE_TO_LATIN,
  LATIN_TO_CODE,
  VALID_ARABIC_LETTERS,
  VALID_LATIN_LETTERS,
} from './mappings.js';
import {
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
} from './models.js';

const SEPARATOR_PATTERN = /[\s\-_/\.|]+/g;
const ASCII_DIGIT_RE = /^[0-9]+$/;
const LETTERS_THEN_DIGITS_RE = /^[A-Za-zء-ي]{3}[0-9]{1,4}$/;
const DIGITS_THEN_LETTERS_RE = /^[0-9]{1,4}[A-Za-zء-ي]{3}$/;

const ARABIC_INPUT_FOLD_MAP = Object.freeze({
  'أ': 'ا',
  'إ': 'ا',
  'آ': 'ا',
  'ٱ': 'ا',
  'ى': 'ي',
  'ؤ': 'و',
  'ئ': 'ي',
  'ة': 'ه',
});

function replaceChars(text, fromChars, toChars) {
  let out = '';
  for (const ch of text) {
    const index = fromChars.indexOf(ch);
    out += index >= 0 ? toChars[index] : ch;
  }
  return out;
}

export function foldArabicInputVariants(text) {
  let out = '';
  for (const ch of text) {
    out += ARABIC_INPUT_FOLD_MAP[ch] ?? ch;
  }
  return out;
}

class Policy {
  constructor({ allowMixedScripts, allowReorderedInput, allowShortDigits }) {
    this.allowMixedScripts = allowMixedScripts;
    this.allowReorderedInput = allowReorderedInput;
    this.allowShortDigits = allowShortDigits;
  }
}

export function resolvePolicy(strictness, options = null) {
  let defaults;
  if (strictness === Strictness.STRICT) {
    defaults = new Policy({
      allowMixedScripts: false,
      allowReorderedInput: false,
      allowShortDigits: false,
    });
  } else {
    defaults = new Policy({
      allowMixedScripts: true,
      allowReorderedInput: true,
      allowShortDigits: true,
    });
  }

  if (!options) {
    return defaults;
  }

  return new Policy({
    allowMixedScripts: options.allowMixedScripts ?? defaults.allowMixedScripts,
    allowReorderedInput: options.allowReorderedInput ?? defaults.allowReorderedInput,
    allowShortDigits: options.allowShortDigits ?? defaults.allowShortDigits,
  });
}

export function cleanInput(raw, options = new ParseOptions()) {
  const normalizedOptions = options instanceof ParseOptions || options instanceof NormalizeOptions
    ? options
    : new ParseOptions(options);

  const corrections = [];
  let cleaned = raw.normalize('NFKC');
  if (cleaned !== raw) {
    corrections.push(new Correction('unicode_normalization', raw, cleaned));
  }

  const noBidi = [...cleaned].filter((ch) => !BIDI_CONTROL_CHARS.has(ch)).join('');
  if (noBidi !== cleaned) {
    corrections.push(new Correction('bidi_control_removal', cleaned, noBidi));
    cleaned = noBidi;
  }

  const shouldFoldArabicVariants = normalizedOptions.strictness !== Strictness.STRICT;
  if (shouldFoldArabicVariants) {
    const folded = foldArabicInputVariants(cleaned);
    if (folded !== cleaned) {
      corrections.push(new Correction('arabic_variant_folding', cleaned, folded));
      cleaned = folded;
    }
  }

  const digitNormalized = replaceChars(cleaned, ARABIC_INDIC_DIGITS, ASCII_DIGITS);
  if (digitNormalized !== cleaned) {
    corrections.push(new Correction('digit_conversion', cleaned, digitNormalized));
    cleaned = digitNormalized;
  }

  const stripped = cleaned.trim();
  if (stripped !== cleaned) {
    corrections.push(new Correction('trim', cleaned, stripped));
    cleaned = stripped;
  }

  let compacted = cleaned.replace(SEPARATOR_PATTERN, ' ');
  compacted = compacted.replace(/\s+/g, ' ');
  if (compacted !== cleaned) {
    corrections.push(new Correction('separator_normalization', cleaned, compacted));
    cleaned = compacted;
  }

  return { cleaned, corrections };
}

export function charScript(ch) {
  if (VALID_ARABIC_LETTERS.has(ch)) {
    return Script.ARABIC;
  }
  if (VALID_LATIN_LETTERS.has(ch.toUpperCase())) {
    return Script.LATIN;
  }
  return Script.UNKNOWN;
}

export function detectScript(text) {
  const scripts = new Set();
  for (const ch of text) {
    const script = charScript(ch);
    if (script !== Script.UNKNOWN) {
      scripts.add(script);
    }
  }
  if (scripts.size === 0) {
    return Script.UNKNOWN;
  }
  if (scripts.size === 1) {
    return [...scripts][0];
  }
  return Script.MIXED;
}

export function isSupportedLetter(ch) {
  return VALID_ARABIC_LETTERS.has(ch) || VALID_LATIN_LETTERS.has(ch.toUpperCase());
}

export function toLetterCode(ch) {
  if (ARABIC_TO_CODE[ch]) {
    return ARABIC_TO_CODE[ch];
  }
  return LATIN_TO_CODE[ch.toUpperCase()] ?? null;
}

export function transliterateLetters(text, targetScript) {
  if (targetScript !== Script.ARABIC && targetScript !== Script.LATIN) {
    throw new TypeError('targetScript must be Script.ARABIC or Script.LATIN');
  }

  let converted = '';
  for (const ch of text) {
    const code = toLetterCode(ch);
    if (code === null) {
      converted += ch;
    } else if (targetScript === Script.ARABIC) {
      converted += CODE_TO_ARABIC[code];
    } else {
      converted += CODE_TO_LATIN[code];
    }
  }
  return converted;
}

export function convertDigits(text, targetDigits) {
  const asciiText = replaceChars(text, ARABIC_INDIC_DIGITS, ASCII_DIGITS);
  if (targetDigits === DigitSet.ASCII) {
    return asciiText;
  }
  if (targetDigits === DigitSet.ARABIC_INDIC) {
    return replaceChars(asciiText, ASCII_DIGITS, ARABIC_INDIC_DIGITS);
  }
  throw new TypeError('unsupported target digit set');
}

export function tokenize(cleaned) {
  const letters = [];
  const digits = [];
  const unknown = [];

  for (const ch of cleaned.replace(/ /g, '')) {
    if (/\d/u.test(ch)) {
      digits.push(ch);
    } else if (isSupportedLetter(ch)) {
      letters.push(ch);
    } else {
      unknown.push(ch);
    }
  }
  return { letters, digits, unknown };
}

export function parsePlate(rawInput, options = new ParseOptions()) {
  const normalizedOptions = options instanceof ParseOptions ? options : new ParseOptions(options);
  const policy = resolvePolicy(normalizedOptions.strictness, normalizedOptions);
  const { cleaned } = cleanInput(rawInput, normalizedOptions);
  const { letters: lettersRaw, digits: digitsRaw, unknown } = tokenize(cleaned);
  const warnings = [];
  const errors = [];

  const sourceScript = detectScript(lettersRaw.join(''));
  if (sourceScript === Script.MIXED && !policy.allowMixedScripts) {
    errors.push(new ValidationIssue({
      code: 'MIXED_SCRIPTS_NOT_ALLOWED',
      message: 'Mixed Arabic and Latin plate letters are not allowed in strict mode.',
      field: 'letters',
    }));
  }

  if (unknown.length > 0) {
    errors.push(new ValidationIssue({
      code: 'UNSUPPORTED_CHARACTERS',
      message: `Unsupported characters found: ${unknown.join('')}`,
      field: 'input',
      metadata: { characters: unknown },
    }));
  }

  const unsupportedCharactersPresent = unknown.length > 0;

  if (lettersRaw.length !== 3) {
    let shouldReportLetterCount = true;
    if (unsupportedCharactersPresent && lettersRaw.length < 3) {
      shouldReportLetterCount = false;
    }
    if (shouldReportLetterCount) {
      errors.push(new ValidationIssue({
        code: 'INVALID_LETTER_COUNT',
        message: `Expected exactly 3 letters, found ${lettersRaw.length}.`,
        field: 'letters',
      }));
    }
  }

  if (digitsRaw.length === 0) {
    errors.push(new ValidationIssue({
      code: 'MISSING_DIGITS',
      message: 'Expected 1 to 4 digits, found none.',
      field: 'digits',
    }));
  } else if (digitsRaw.length > 4) {
    errors.push(new ValidationIssue({
      code: 'INVALID_DIGIT_COUNT',
      message: `Expected at most 4 digits, found ${digitsRaw.length}.`,
      field: 'digits',
    }));
  } else if (digitsRaw.length < 4 && !policy.allowShortDigits) {
    errors.push(new ValidationIssue({
      code: 'SHORT_DIGITS_NOT_ALLOWED',
      message: `Expected exactly 4 digits in strict mode, found ${digitsRaw.length}.`,
      field: 'digits',
    }));
  }

  const compact = cleaned.replace(/ /g, '');
  const lettersThenDigits = LETTERS_THEN_DIGITS_RE.test(compact);
  const digitsThenLetters = DIGITS_THEN_LETTERS_RE.test(compact);
  if (digitsThenLetters) {
    if (policy.allowReorderedInput) {
      warnings.push(new ValidationIssue({
        code: 'REORDERED_INPUT',
        message: 'Digits were entered before letters and were normalized.',
        severity: 'warning',
        field: 'order',
      }));
    } else {
      errors.push(new ValidationIssue({
        code: 'REORDERED_INPUT_NOT_ALLOWED',
        message: 'Digits before letters are not allowed in strict mode.',
        field: 'order',
      }));
    }
  } else if (!lettersThenDigits && compact && errors.length === 0) {
    warnings.push(new ValidationIssue({
      code: 'NON_STANDARD_LAYOUT',
      message: 'Input was accepted after normalization from a non-standard layout.',
      severity: 'warning',
      field: 'order',
    }));
  }

  if (errors.length > 0) {
    return new ParseResult({
      success: false,
      rawInput,
      normalizedInput: cleaned,
      plate: null,
      errors,
      warnings,
    });
  }

  const letterCodes = lettersRaw.map((ch) => toLetterCode(ch));
  if (letterCodes.some((code) => code === null)) {
    errors.push(new ValidationIssue({
      code: 'UNKNOWN_LETTER',
      message: 'One or more letters could not be mapped to Saudi plate codes.',
      field: 'letters',
    }));
    return new ParseResult({
      success: false,
      rawInput,
      normalizedInput: cleaned,
      plate: null,
      errors,
      warnings,
    });
  }

  const plate = new Plate({
    country: 'SA',
    letters: letterCodes,
    digits: digitsRaw.join(''),
    sourceScript,
  });

  return new ParseResult({
    success: true,
    rawInput,
    normalizedInput: cleaned,
    plate,
    errors: [],
    warnings,
  });
}

export function normalizePlate(rawInput, options = new NormalizeOptions()) {
  if (rawInput instanceof Plate) {
    return new NormalizeResult({
      success: true,
      canonical: rawInput.canonical,
      plate: rawInput,
    });
  }

  const normalizedOptions = options instanceof NormalizeOptions ? options : new NormalizeOptions(options);
  const { corrections } = cleanInput(rawInput, normalizedOptions);
  const parseResult = parsePlate(
    rawInput,
    new ParseOptions({
      strictness: normalizedOptions.strictness,
      allowMixedScripts: normalizedOptions.allowMixedScripts,
      allowReorderedInput: normalizedOptions.allowReorderedInput,
      allowShortDigits: normalizedOptions.allowShortDigits,
    })
  );

  if (!parseResult.success || parseResult.plate === null) {
    return new NormalizeResult({
      success: false,
      canonical: null,
      plate: null,
      corrections,
      errors: parseResult.errors,
      warnings: parseResult.warnings,
    });
  }

  return new NormalizeResult({
    success: true,
    canonical: parseResult.plate.canonical,
    plate: parseResult.plate,
    corrections,
    errors: [],
    warnings: parseResult.warnings,
  });
}

export function validatePlate(rawInput, options = new NormalizeOptions()) {
  if (rawInput instanceof Plate) {
    const issues = [];
    if (rawInput.letters.length !== 3) {
      issues.push(new ValidationIssue({
        code: 'INVALID_LETTER_COUNT',
        message: 'Expected exactly 3 letters.',
        field: 'letters',
      }));
    }
    if (!ASCII_DIGIT_RE.test(rawInput.digits)) {
      issues.push(new ValidationIssue({
        code: 'INVALID_DIGITS',
        message: 'Digits must be ASCII digits.',
        field: 'digits',
      }));
    }
    if (rawInput.digits.length < 1 || rawInput.digits.length > 4) {
      issues.push(new ValidationIssue({
        code: 'INVALID_DIGIT_COUNT',
        message: 'Expected 1 to 4 digits.',
        field: 'digits',
      }));
    }
    return new ValidationResult({ isValid: issues.length === 0, plate: rawInput, issues });
  }

  const result = normalizePlate(rawInput, options);
  const issues = [...result.errors, ...result.warnings];
  return new ValidationResult({
    isValid: result.success,
    plate: result.plate,
    issues,
  });
}

export function formatPlate(plateOrInput, style = FormatStyle.CANONICAL, options = new NormalizeOptions()) {
  let plate;
  if (plateOrInput instanceof Plate) {
    plate = plateOrInput;
  } else {
    const normalized = normalizePlate(plateOrInput, options);
    if (!normalized.success || normalized.plate === null) {
      const messages = normalized.errors.map((issue) => issue.message).join('; ');
      throw new TypeError(`Cannot format invalid plate: ${messages}`);
    }
    plate = normalized.plate;
  }

  const latin = plate.letters.map((code) => CODE_TO_LATIN[code]).join('');
  const arabic = plate.letters.map((code) => CODE_TO_ARABIC[code]).join(' ');
  const arabicDigits = convertDigits(plate.digits, DigitSet.ARABIC_INDIC);

  if (style === FormatStyle.CANONICAL || style === FormatStyle.STORAGE) {
    return `${latin}-${plate.digits}`;
  }
  if (style === FormatStyle.DISPLAY_EN) {
    return `${latin} ${plate.digits}`;
  }
  if (style === FormatStyle.COMPACT_EN) {
    return `${latin}${plate.digits}`;
  }
  if (style === FormatStyle.DISPLAY_AR) {
    return `${arabicDigits} ${arabic}`;
  }
  if (style === FormatStyle.COMPACT_AR) {
    return `${arabicDigits}${plate.letters.map((code) => CODE_TO_ARABIC[code]).join('')}`;
  }
  throw new TypeError(`Unsupported format style: ${style}`);
}

export function equals(a, b, options = new NormalizeOptions()) {
  const aResult = typeof a === 'string'
    ? normalizePlate(a, options)
    : new NormalizeResult({ success: true, canonical: a.canonical, plate: a });
  const bResult = typeof b === 'string'
    ? normalizePlate(b, options)
    : new NormalizeResult({ success: true, canonical: b.canonical, plate: b });
  return Boolean(aResult.success && bResult.success && aResult.canonical === bResult.canonical);
}
