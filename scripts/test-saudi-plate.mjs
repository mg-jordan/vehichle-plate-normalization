import assert from 'node:assert';
import {
  normalizePlate,
  equals as platesEqual,
  formatPlate,
  FormatStyle,
} from 'saudi-plate';

const scenarioDefs = [
    {
    id: 'T001',
    name: 'Canonical English compact',
    input: 'ABJ1234',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_en: 'ABJ 1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_en: 'ABJ 1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
    },
    },
    {
    id: 'T002',
    name: 'English with separators',
    input: 'ABJ-1234',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_en: 'ABJ 1234',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_en: 'ABJ 1234',
        expect_warning_codes: [],
        },
    },
    },
    {
    id: 'T003',
    name: 'Arabic letters and Arabic-Indic digits',
    input: 'ا ب ح ١٢٣٤',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_en: 'ABJ 1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_en: 'ABJ 1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
    },
    },
    {
    id: 'T004',
    name: 'Digits before letters',
    input: '1234 ABJ',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_warning_codes: ['REORDERED_INPUT'],
        },
        strict: {
        expect_success: false,
        expect_error_codes: ['REORDERED_INPUT_NOT_ALLOWED'],
        },
    },
    },
    {
    id: 'T005',
    name: 'Short digits',
    input: 'ABJ 123',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-123',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: false,
        expect_error_codes: ['SHORT_DIGITS_NOT_ALLOWED'],
        },
    },
    },
    {
    id: 'T006',
    name: 'Mixed Arabic and Latin letters',
    input: 'AبJ1234',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        },
        strict: {
        expect_success: false,
        expect_error_codes: ['MIXED_SCRIPTS_NOT_ALLOWED'],
        },
    },
    },
    {
    id: 'T007',
    name: 'Unsupported Latin letters',
    input: 'ABC 1234',
    expectations: {
        standard: {
        expect_success: false,
        expect_error_codes: ['UNSUPPORTED_CHARACTERS'],
        },
        strict: {
        expect_success: false,
        expect_error_codes: ['UNSUPPORTED_CHARACTERS'],
        },
    },
    },
    {
    id: 'T008',
    name: 'Too many digits',
    input: 'ABJ 12345',
    expectations: {
        standard: {
        expect_success: false,
        expect_error_codes: ['INVALID_DIGIT_COUNT'],
        },
        strict: {
        expect_success: false,
        expect_error_codes: ['INVALID_DIGIT_COUNT'],
        },
    },
    },
    {
    id: 'T009',
    name: 'Unsupported punctuation is cleaned',
    input: ' ABJ__1234 ',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        },
        strict: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        },
    },
    },
    {
    id: 'T010',
    name: 'Saudi H mapping uses H only for ه',
    input: 'ABH 1234',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABH-1234',
        expect_display_ar: '١٢٣٤ ا ب ه',
        },
        strict: {
        expect_success: true,
        expect_canonical: 'ABH-1234',
        expect_display_ar: '١٢٣٤ ا ب ه',
        },
    },
    },
    {
    id: 'T011',
    name: 'Saudi J mapping uses ح',
    input: 'ABJ 1234',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        },
        strict: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        },
    },
    },
    {
    id: 'T012',
    name: 'equals works across Arabic and English forms',
    input: 'ABJ1234',
    compare_to: 'ا ب ح ١٢٣٤',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_equals: true,
        },
        strict: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_equals: true,
        },
    }
    },
    {
    id: 'T013',
    name: 'Arabic alif with hamza above folds to bare alif',
    input: 'أ ب ح ١٢٣٤',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: false,
        expect_canonical: 'ABJ-1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
    },
    },
    {
    id: 'T014',
    name: 'Arabic alif with hamza below folds to bare alif',
    input: 'إ ب ح ١٢٣٤',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: false,
        expect_canonical: 'ABJ-1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
    },
    },
    {
    id: 'T015',
    name: 'Arabic alif madda folds to bare alif',
    input: 'آ ب ح ١٢٣٤',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABJ-1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: false,
        expect_canonical: 'ABJ-1234',
        expect_display_ar: '١٢٣٤ ا ب ح',
        expect_warning_codes: [],
        },
    },
    },
    {
    id: 'T016',
    name: 'Ta marbuta folds to ha',
    input: 'ا ب ة ١٢٣٤',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABH-1234',
        expect_display_ar: '١٢٣٤ ا ب ه',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: false,
        expect_canonical: 'ABH-1234',
        expect_display_ar: '١٢٣٤ ا ب ه',
        expect_warning_codes: [],
        },
    },
    },
    {
    id: 'T017',
    name: 'Alef maqsura folds to ya',
    input: 'ا ب ى ١٢٣٤',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABV-1234',
        expect_display_ar: '١٢٣٤ ا ب ي',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: false,
        expect_canonical: 'ABV-1234',
        expect_display_ar: '١٢٣٤ ا ب ي',
        expect_warning_codes: [],
        },
    },
    },
    {
    id: 'T018',
    name: 'Ya with hamza folds to ya',
    input: 'ا ب ئ ١٢٣٤',
    expectations: {
        standard: {
        expect_success: true,
        expect_canonical: 'ABV-1234',
        expect_display_ar: '١٢٣٤ ا ب ي',
        expect_warning_codes: [],
        },
        strict: {
        expect_success: false,
        expect_canonical: 'ABV-1234',
        expect_display_ar: '١٢٣٤ ا ب ي',
        expect_warning_codes: [],
        },
    },
    },
];

function extractCodes(items = []) {
  return items.map(item => item?.code).filter(Boolean).sort();
}

function arraysEqual(a = [], b = []) {
  return JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
}

function getDisplayEn(result, options) {
  return formatPlate(result.plate, FormatStyle.DISPLAY_EN, options);
}

function getDisplayAr(result, options) {
  return formatPlate(result.plate, FormatStyle.DISPLAY_AR, options);
}

const expandedCases = scenarioDefs.flatMap(def =>
  ['standard', 'strict']
    .filter(mode => def.expectations?.[mode])
    .map(mode => ({
      ...def,
      mode,
      options: { strictness: mode },
      ...def.expectations[mode],
    }))
);

let passed = 0;
let failed = 0;

for (const t of expandedCases) {
  let result;

  try {
    result = normalizePlate(t.input, t.options);
    const canonicalOut = result?.canonical ?? '—';

    if (t.expect_success) {
      assert.equal(result.success, true, 'Expected success');

      if (t.expect_canonical !== undefined) {
        assert.equal(result.canonical, t.expect_canonical, 'Canonical mismatch');
      }

      if (t.expect_display_en !== undefined) {
        assert.equal(
          getDisplayEn(result, t.options),
          t.expect_display_en,
          'English display mismatch'
        );
      }

      if (t.expect_display_ar !== undefined) {
        assert.equal(
          getDisplayAr(result, t.options),
          t.expect_display_ar,
          'Arabic display mismatch'
        );
      }

      if (t.expect_warning_codes !== undefined) {
        const warningCodes = extractCodes(result.warnings);
        assert.ok(
          arraysEqual(warningCodes, t.expect_warning_codes),
          `Warning codes mismatch. Expected ${JSON.stringify(t.expect_warning_codes)}, got ${JSON.stringify(warningCodes)}`
        );
      }

      if (t.expect_equals !== undefined) {
        const eq = platesEqual(t.input, t.compare_to, t.options);
        assert.equal(eq, t.expect_equals, 'equals(...) mismatch');
      }
    } else {
      assert.equal(result.success, false, 'Expected failure');

      if (t.expect_error_codes !== undefined) {
        const errorCodes = extractCodes(result.errors);
        assert.ok(
          arraysEqual(errorCodes, t.expect_error_codes),
          `Error codes mismatch. Expected ${JSON.stringify(t.expect_error_codes)}, got ${JSON.stringify(errorCodes)}`
        );
      }
    }

    console.log(
      `✅ ${t.id}/${t.mode} | input="${t.input}" | canonical="${canonicalOut}"`
    );
    passed++;
  } catch (err) {
    const canonicalOut = result?.canonical ?? '—';
    const errors = result?.errors?.map(e => e.code) ?? [];
    const warnings = result?.warnings?.map(w => w.code) ?? [];

    console.error(
      `❌ ${t.id}/${t.mode} | input="${t.input}" | canonical="${canonicalOut}" | errors=${JSON.stringify(errors)} | warnings=${JSON.stringify(warnings)} | ${err.message}`
    );
    failed++;
  }
}

console.log(`\nSummary: ${passed}/${expandedCases.length} passed, ${failed} failed`);

if (failed > 0) {
  process.exit(1);
}