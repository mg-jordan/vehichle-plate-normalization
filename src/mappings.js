export const LETTER_TABLE = {
  ALIF: { ar: 'ا', en: 'A' },
  BA: { ar: 'ب', en: 'B' },
  HA: { ar: 'ح', en: 'J' },
  DAL: { ar: 'د', en: 'D' },
  RA: { ar: 'ر', en: 'R' },
  SIN: { ar: 'س', en: 'S' },
  SAD: { ar: 'ص', en: 'X' },
  TA: { ar: 'ط', en: 'T' },
  AIN: { ar: 'ع', en: 'E' },
  QAF: { ar: 'ق', en: 'G' },
  KAF: { ar: 'ك', en: 'K' },
  LAM: { ar: 'ل', en: 'L' },
  MIM: { ar: 'م', en: 'Z' },
  NUN: { ar: 'ن', en: 'N' },
  HAH: { ar: 'ه', en: 'H' },
  WAW: { ar: 'و', en: 'U' },
  YA: { ar: 'ي', en: 'V' },
};

export const ARABIC_TO_CODE = Object.freeze(
  Object.fromEntries(Object.entries(LETTER_TABLE).map(([code, row]) => [row.ar, code]))
);

export const LATIN_TO_CODE = Object.freeze(
  Object.fromEntries(Object.entries(LETTER_TABLE).map(([code, row]) => [row.en, code]))
);

export const CODE_TO_ARABIC = Object.freeze(
  Object.fromEntries(Object.entries(LETTER_TABLE).map(([code, row]) => [code, row.ar]))
);

export const CODE_TO_LATIN = Object.freeze(
  Object.fromEntries(Object.entries(LETTER_TABLE).map(([code, row]) => [code, row.en]))
);

export const VALID_ARABIC_LETTERS = new Set(Object.keys(ARABIC_TO_CODE));
export const VALID_LATIN_LETTERS = new Set(Object.keys(LATIN_TO_CODE));

export const ARABIC_INDIC_DIGITS = '٠١٢٣٤٥٦٧٨٩';
export const ASCII_DIGITS = '0123456789';

export const BIDI_CONTROL_CHARS = new Set([
  '‎',
  '‏',
  '‪',
  '‫',
  '‬',
  '‭',
  '‮',
  '⁦',
  '⁧',
  '⁨',
  '⁩',
]);
