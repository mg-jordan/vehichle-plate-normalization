# saudi-plate

A production-ready JavaScript library for Saudi vehicle plate parsing, normalization, validation, formatting, and equality comparison.

## Features
- Parse raw user input from Arabic, Latin, or mixed script input
- Normalize Arabic-Indic digits to ASCII for storage
- Validate Saudi plate structure with strict, standard, and lenient modes
- Format plates for canonical storage, English display, and Arabic display
- Compare plate inputs by canonical identity
- Zero runtime dependencies

## Saudi letter mapping
This library uses the Saudi plate mapping, not general Arabic transliteration.

| Arabic | Latin | Code |
|---|---|---|
| ا | A | ALIF |
| ب | B | BA |
| ح | J | HA |
| د | D | DAL |
| ر | R | RA |
| س | S | SIN |
| ص | X | SAD |
| ط | T | TA |
| ع | E | AIN |
| ق | G | QAF |
| ك | K | KAF |
| ل | L | LAM |
| م | Z | MIM |
| ن | N | NUN |
| ه | H | HAH |
| و | U | WAW |
| ي | V | YA |

## Installation
```bash
npm install saudi-plate
```

## Quick start
```js
import { normalizePlate, formatPlate, validatePlate, FormatStyle } from 'saudi-plate';

const result = normalizePlate('١٢٣٤ ا ب ح');
console.log(result.success); // true
console.log(result.canonical); // ABJ-1234

console.log(formatPlate('ABJ1234', FormatStyle.DISPLAY_AR));
console.log(validatePlate('1234 ABJ').isValid);
```

## API
### `normalizePlate(input, options?)`
Returns an object with:
- `success`
- `canonical`
- `plate`
- `corrections`
- `errors`
- `warnings`

### `parsePlate(input, options?)`
Returns structural parsing results.

### `validatePlate(input, options?)`
Returns `isValid`, `plate`, and `issues`.

### `formatPlate(inputOrPlate, style = FormatStyle.CANONICAL, options?)`
Supported styles:
- `canonical`
- `storage`
- `display_en`
- `display_ar`
- `compact_en`
- `compact_ar`

### `equals(a, b, options?)`
Compares two inputs by canonical identity.

## Strictness modes
### Strict
- No mixed Arabic and Latin letters
- No digits-before-letters input
- Exactly 4 digits required

### Standard
- Mixed scripts allowed
- Reordered input allowed with warnings
- 1 to 4 digits allowed

### Lenient
- Same acceptance policy as standard, intended for search and support tools

## Notes
- The library is focused on text parsing and normalization, not OCR or registry lookup.
- Canonical storage format is `LATINLETTERS-DIGITS`, for example `ABJ-1234`.
