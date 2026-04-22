# SaudiPlate

A production-ready .NET library for Saudi vehicle plate parsing, normalization, validation, formatting, and equality comparison.

---

# Features

* Parse raw user input from Arabic, Latin, or mixed script input
* Normalize Arabic-Indic digits to ASCII for storage
* Validate Saudi plate structure with strict and standard modes
* Format plates for canonical storage, English display, and Arabic display
* Compare plate inputs by canonical identity
* Zero external dependencies

---

# Saudi Letter Mapping

This library uses the official Saudi plate mapping (not general Arabic transliteration).

| Arabic | Latin | Code |
| ------ | ----- | ---- |
| ا      | A     | ALIF |
| ب      | B     | BA   |
| ح      | J     | HA   |
| د      | D     | DAL  |
| ر      | R     | RA   |
| س      | S     | SIN  |
| ص      | X     | SAD  |
| ط      | T     | TA   |
| ع      | E     | AIN  |
| ق      | G     | QAF  |
| ك      | K     | KAF  |
| ل      | L     | LAM  |
| م      | Z     | MIM  |
| ن      | N     | NUN  |
| ه      | H     | HAH  |
| و      | U     | WAW  |
| ي      | V     | YA   |

---

# Installation

```bash
dotnet add package SaudiPlate
```

---

# Quick Start

```csharp
using SaudiPlate;

var result = SaudiPlateApi.NormalizePlate("١٢٣٤ ا ب ح");

Console.WriteLine(result.Success);     // true
Console.WriteLine(result.Canonical);  // ABJ-1234

Console.WriteLine(
    SaudiPlateApi.FormatPlate("ABJ1234", FormatStyle.DisplayAr)
);

var validation = SaudiPlateApi.ValidatePlate("1234 ABJ");
Console.WriteLine(validation.IsValid);
```

---

# API

## NormalizePlate

```csharp
var result = SaudiPlateApi.NormalizePlate(input, options);
```

Returns:

* `Success`
* `Canonical`
* `Plate`
* `Warnings`
* `Errors`

---

## ValidatePlate

```csharp
var result = SaudiPlateApi.ValidatePlate(input, options);
```

Returns:

* `IsValid`
* `Plate`
* `Issues`

---

## FormatPlate

```csharp
SaudiPlateApi.FormatPlate(inputOrPlate, FormatStyle.DisplayAr);
```

Supported styles:

* `Canonical`
* `DisplayEn`
* `DisplayAr`

---

## EqualsPlate

```csharp
SaudiPlateApi.EqualsPlate(a, b, options);
```

Compares two inputs by canonical identity.

---

# Strictness Modes

## Strict

* No mixed Arabic and Latin letters
* No digits-before-letters input
* Exactly 4 digits required
* No folded Arabic characters (أ، إ، آ، ة، ى، ئ...)

## Standard

* Mixed scripts allowed
* Reordered input allowed with warnings
* 1 to 4 digits allowed
* Folded Arabic characters normalized

---

# Test Matrix

The following matrix summarizes the full test coverage (37/37 passing):

## Valid Inputs

| Input      | Mode     | Result | Canonical |
| ---------- | -------- | ------ | --------- |
| ABJ1234    | Standard | ✔️     | ABJ-1234  |
| ABJ1234    | Strict   | ✔️     | ABJ-1234  |
| ABJ-1234   | Standard | ✔️     | ABJ-1234  |
| ا ب ح ١٢٣٤ | Standard | ✔️     | ABJ-1234  |
| ا ب ح ١٢٣٤ | Strict   | ✔️     | ABJ-1234  |

---

## Normalization Cases

| Input     | Standard    | Strict | Notes                            |
| --------- | ----------- | ------ | -------------------------------- |
| 1234 ABJ  | ✔️ ABJ-1234 | ❌      | REORDERED_INPUT                  |
| ABJ__1234 | ✔️ ABJ-1234 | ✔️     | Cleans punctuation               |
| AبJ1234   | ✔️ ABJ-1234 | ❌      | Mixed scripts rejected in strict |

---

## Invalid Inputs

| Input     | Mode | Error                  |
| --------- | ---- | ---------------------- |
| ABC 1234  | Both | UNSUPPORTED_CHARACTERS |
| ABJ 12345 | Both | INVALID_DIGIT_COUNT    |

---

## Strict Mode Rejections

| Input      | Standard    | Strict | Reason                   |
| ---------- | ----------- | ------ | ------------------------ |
| ABJ 123    | ✔️ ABJ-123  | ❌      | SHORT_DIGITS_NOT_ALLOWED |
| أ ب ح ١٢٣٤ | ✔️ ABJ-1234 | ❌      | Folded Arabic            |
| إ ب ح ١٢٣٤ | ✔️ ABJ-1234 | ❌      | Folded Arabic            |
| آ ب ح ١٢٣٤ | ✔️ ABJ-1234 | ❌      | Folded Arabic            |
| ا ب ة ١٢٣٤ | ✔️ ABH-1234 | ❌      | Folded Arabic            |
| ا ب ى ١٢٣٤ | ✔️ ABV-1234 | ❌      | Folded Arabic            |
| ا ب ئ ١٢٣٤ | ✔️ ABV-1234 | ❌      | Folded Arabic            |

---

## Arabic Mapping Examples

| Input     | Canonical | Display (Arabic) |
| --------- | --------- | ---------------- |
| ح         | J         | ح                |
| ه / ة     | H         | ه                |
| ي / ى / ئ | V         | ي                |

---

## Equality Behavior

| A       | B          | Equal |
| ------- | ---------- | ----- |
| ABJ1234 | ا ب ح ١٢٣٤ | ✔️    |

---

# Notes

* Canonical format: `LETTERS-DIGITS` (e.g. `ABJ-1234`)
* Designed for validation, normalization, and formatting
* Not intended for OCR or vehicle registry lookup
* Fully deterministic and locale-independent

---

# License

MIT
