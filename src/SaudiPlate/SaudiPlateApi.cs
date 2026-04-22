using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace SaudiPlate;

public static class SaudiPlateApi
{
    private static readonly Regex SeparatorPattern = new Regex("[\\s\\-_/\\.|]+", RegexOptions.Compiled | RegexOptions.CultureInvariant);
    private static readonly Regex AsciiDigitsRegex = new Regex("^[0-9]+$", RegexOptions.Compiled | RegexOptions.CultureInvariant);
    private static readonly Regex LettersThenDigitsRegex = new Regex("^[A-Za-zء-ي]{3}[0-9]{1,4}$", RegexOptions.Compiled | RegexOptions.CultureInvariant);
    private static readonly Regex DigitsThenLettersRegex = new Regex("^[0-9]{1,4}[A-Za-zء-ي]{3}$", RegexOptions.Compiled | RegexOptions.CultureInvariant);

    private static readonly IReadOnlyDictionary<char, char> ArabicInputFoldMap = new Dictionary<char, char>
    {
        ['أ'] = 'ا',
        ['إ'] = 'ا',
        ['آ'] = 'ا',
        ['ٱ'] = 'ا',
        ['ى'] = 'ي',
        ['ؤ'] = 'و',
        ['ئ'] = 'ي',
        ['ة'] = 'ه',
    };

    private sealed class Policy
    {
        public bool AllowMixedScripts { get; set; }
        public bool AllowReorderedInput { get; set; }
        public bool AllowShortDigits { get; set; }
    }

    private sealed class CleanInputResult
    {
        public string Cleaned { get; set; } = string.Empty;
        public List<Correction> Corrections { get; } = new List<Correction>();
    }

    private sealed class TokenizeResult
    {
        public List<char> Letters { get; } = new List<char>();
        public List<char> Digits { get; } = new List<char>();
        public List<char> Unknown { get; } = new List<char>();
    }

    public static string FoldArabicInputVariants(string text)
    {
        if (text == null) throw new ArgumentNullException(nameof(text));
        var builder = new StringBuilder(text.Length);
        foreach (var ch in text)
        {
            builder.Append(ArabicInputFoldMap.TryGetValue(ch, out var replacement) ? replacement : ch);
        }
        return builder.ToString();
    }

    private static Policy ResolvePolicy(Strictness strictness, bool? allowMixedScripts, bool? allowReorderedInput, bool? allowShortDigits)
    {
        var isStrict = strictness == Strictness.Strict;
        return new Policy
        {
            AllowMixedScripts = allowMixedScripts ?? !isStrict,
            AllowReorderedInput = allowReorderedInput ?? !isStrict,
            AllowShortDigits = allowShortDigits ?? !isStrict,
        };
    }

    private static string ReplaceChars(string text, string fromChars, string toChars)
    {
        var builder = new StringBuilder(text.Length);
        foreach (var ch in text)
        {
            var index = fromChars.IndexOf(ch);
            builder.Append(index >= 0 ? toChars[index] : ch);
        }
        return builder.ToString();
    }

    private static CleanInputResult CleanInput(string raw, Strictness strictness)
    {
        if (raw == null) throw new ArgumentNullException(nameof(raw));

        var result = new CleanInputResult();
        var cleaned = raw.Normalize(NormalizationForm.FormKC);
        if (!string.Equals(cleaned, raw, StringComparison.Ordinal))
        {
            result.Corrections.Add(new Correction("unicode_normalization", raw, cleaned));
        }

        var noBidiBuilder = new StringBuilder(cleaned.Length);
        foreach (var ch in cleaned)
        {
            if (!Mappings.BidiControlChars.Contains(ch))
            {
                noBidiBuilder.Append(ch);
            }
        }
        var noBidi = noBidiBuilder.ToString();
        if (!string.Equals(noBidi, cleaned, StringComparison.Ordinal))
        {
            result.Corrections.Add(new Correction("bidi_control_removal", cleaned, noBidi));
            cleaned = noBidi;
        }

        if (strictness != Strictness.Strict)
        {
            var folded = FoldArabicInputVariants(cleaned);
            if (!string.Equals(folded, cleaned, StringComparison.Ordinal))
            {
                result.Corrections.Add(new Correction("arabic_variant_folding", cleaned, folded));
                cleaned = folded;
            }
        }

        var digitNormalized = ReplaceChars(cleaned, Mappings.ArabicIndicDigits, Mappings.AsciiDigits);
        if (!string.Equals(digitNormalized, cleaned, StringComparison.Ordinal))
        {
            result.Corrections.Add(new Correction("digit_conversion", cleaned, digitNormalized));
            cleaned = digitNormalized;
        }

        var stripped = cleaned.Trim();
        if (!string.Equals(stripped, cleaned, StringComparison.Ordinal))
        {
            result.Corrections.Add(new Correction("trim", cleaned, stripped));
            cleaned = stripped;
        }

        var compacted = SeparatorPattern.Replace(cleaned, " ");
        compacted = Regex.Replace(compacted, "\\s+", " ", RegexOptions.CultureInvariant);
        if (!string.Equals(compacted, cleaned, StringComparison.Ordinal))
        {
            result.Corrections.Add(new Correction("separator_normalization", cleaned, compacted));
            cleaned = compacted;
        }

        result.Cleaned = cleaned;
        return result;
    }

    private static Script CharScript(char ch)
    {
        if (Mappings.ValidArabicLetters.Contains(ch.ToString())) return Script.Arabic;
        if (Mappings.ValidLatinLetters.Contains(char.ToUpperInvariant(ch).ToString())) return Script.Latin;
        return Script.Unknown;
    }

    public static Script DetectScript(string text)
    {
        if (text == null) throw new ArgumentNullException(nameof(text));
        var scripts = new HashSet<Script>();
        foreach (var ch in text)
        {
            var script = CharScript(ch);
            if (script != Script.Unknown) scripts.Add(script);
        }
        if (scripts.Count == 0) return Script.Unknown;
        if (scripts.Count == 1) return scripts.First();
        return Script.Mixed;
    }

    public static bool IsSupportedLetter(char ch)
    {
        return Mappings.ValidArabicLetters.Contains(ch.ToString()) || Mappings.ValidLatinLetters.Contains(char.ToUpperInvariant(ch).ToString());
    }

    public static string? ToLetterCode(char ch)
    {
        if (Mappings.ArabicToCode.TryGetValue(ch.ToString(), out var arabicCode)) return arabicCode;
        if (Mappings.LatinToCode.TryGetValue(char.ToUpperInvariant(ch).ToString(), out var latinCode)) return latinCode;
        return null;
    }

    public static string TransliterateLetters(string text, Script targetScript)
    {
        if (text == null) throw new ArgumentNullException(nameof(text));
        if (targetScript != Script.Arabic && targetScript != Script.Latin)
            throw new ArgumentException("targetScript must be Script.Arabic or Script.Latin", nameof(targetScript));

        var builder = new StringBuilder(text.Length);
        foreach (var ch in text)
        {
            var code = ToLetterCode(ch);
            if (code == null)
            {
                builder.Append(ch);
            }
            else if (targetScript == Script.Arabic)
            {
                builder.Append(Mappings.CodeToArabic[code]);
            }
            else
            {
                builder.Append(Mappings.CodeToLatin[code]);
            }
        }
        return builder.ToString();
    }

    public static string ConvertDigits(string text, DigitSet targetDigits)
    {
        if (text == null) throw new ArgumentNullException(nameof(text));
        var ascii = ReplaceChars(text, Mappings.ArabicIndicDigits, Mappings.AsciiDigits);
        if (targetDigits == DigitSet.Ascii) return ascii;
        if (targetDigits == DigitSet.ArabicIndic) return ReplaceChars(ascii, Mappings.AsciiDigits, Mappings.ArabicIndicDigits);
        throw new ArgumentException("unsupported target digit set", nameof(targetDigits));
    }

    private static TokenizeResult Tokenize(string cleaned)
    {
        var result = new TokenizeResult();
        foreach (var ch in cleaned.Replace(" ", string.Empty))
        {
            if (char.IsDigit(ch)) result.Digits.Add(ch);
            else if (IsSupportedLetter(ch)) result.Letters.Add(ch);
            else result.Unknown.Add(ch);
        }
        return result;
    }

    public static ParseResult ParsePlate(string rawInput, ParseOptions? options = null)
    {
        if (rawInput == null) throw new ArgumentNullException(nameof(rawInput));
        options ??= new ParseOptions();

        var policy = ResolvePolicy(options.Strictness, options.AllowMixedScripts, options.AllowReorderedInput, options.AllowShortDigits);
        var cleanedInput = CleanInput(rawInput, options.Strictness);
        var cleaned = cleanedInput.Cleaned;
        var tokens = Tokenize(cleaned);
        var warnings = new List<ValidationIssue>();
        var errors = new List<ValidationIssue>();

        var sourceScript = DetectScript(new string(tokens.Letters.ToArray()));
        if (sourceScript == Script.Mixed && !policy.AllowMixedScripts)
        {
            errors.Add(new ValidationIssue(
                code: "MIXED_SCRIPTS_NOT_ALLOWED",
                message: "Mixed Arabic and Latin plate letters are not allowed in strict mode.",
                field: "letters"));
        }

        if (tokens.Unknown.Count > 0)
        {
            errors.Add(new ValidationIssue(
                code: "UNSUPPORTED_CHARACTERS",
                message: $"Unsupported characters found: {new string(tokens.Unknown.ToArray())}",
                field: "input",
                metadata: new Dictionary<string, object> { ["characters"] = tokens.Unknown.Select(c => c.ToString()).ToArray() }));
        }

        var unsupportedCharactersPresent = tokens.Unknown.Count > 0;
        if (tokens.Letters.Count != 3)
        {
            var shouldReportLetterCount = !(unsupportedCharactersPresent && tokens.Letters.Count < 3);
            if (shouldReportLetterCount)
            {
                errors.Add(new ValidationIssue(
                    code: "INVALID_LETTER_COUNT",
                    message: $"Expected exactly 3 letters, found {tokens.Letters.Count}.",
                    field: "letters"));
            }
        }

        if (tokens.Digits.Count == 0)
        {
            errors.Add(new ValidationIssue(
                code: "MISSING_DIGITS",
                message: "Expected 1 to 4 digits, found none.",
                field: "digits"));
        }
        else if (tokens.Digits.Count > 4)
        {
            errors.Add(new ValidationIssue(
                code: "INVALID_DIGIT_COUNT",
                message: $"Expected at most 4 digits, found {tokens.Digits.Count}.",
                field: "digits"));
        }
        else if (tokens.Digits.Count < 4 && !policy.AllowShortDigits)
        {
            errors.Add(new ValidationIssue(
                code: "SHORT_DIGITS_NOT_ALLOWED",
                message: $"Expected exactly 4 digits in strict mode, found {tokens.Digits.Count}.",
                field: "digits"));
        }

        var compact = cleaned.Replace(" ", string.Empty);
        var lettersThenDigits = LettersThenDigitsRegex.IsMatch(compact);
        var digitsThenLetters = DigitsThenLettersRegex.IsMatch(compact);
        if (digitsThenLetters)
        {
            if (policy.AllowReorderedInput)
            {
                warnings.Add(new ValidationIssue(
                    code: "REORDERED_INPUT",
                    message: "Digits were entered before letters and were normalized.",
                    severity: "warning",
                    field: "order"));
            }
            else
            {
                errors.Add(new ValidationIssue(
                    code: "REORDERED_INPUT_NOT_ALLOWED",
                    message: "Digits before letters are not allowed in strict mode.",
                    field: "order"));
            }
        }
        else if (!lettersThenDigits && compact.Length > 0 && errors.Count == 0)
        {
            warnings.Add(new ValidationIssue(
                code: "NON_STANDARD_LAYOUT",
                message: "Input was accepted after normalization from a non-standard layout.",
                severity: "warning",
                field: "order"));
        }

        if (errors.Count > 0)
        {
            return new ParseResult(false, rawInput, cleaned, null, errors, warnings);
        }

        var letterCodes = tokens.Letters.Select(ToLetterCode).ToArray();
        if (letterCodes.Any(code => code == null))
        {
            errors.Add(new ValidationIssue(
                code: "UNKNOWN_LETTER",
                message: "One or more letters could not be mapped to Saudi plate codes.",
                field: "letters"));
            return new ParseResult(false, rawInput, cleaned, null, errors, warnings);
        }

        var plate = new Plate(
            country: "SA",
            letters: letterCodes.Where(code => code != null).Select(code => code!).ToArray(),
            digits: new string(tokens.Digits.ToArray()),
            sourceScript: sourceScript);

        return new ParseResult(true, rawInput, cleaned, plate, Array.Empty<ValidationIssue>(), warnings);
    }

    public static NormalizeResult NormalizePlate(string rawInput, NormalizeOptions? options = null)
    {
        if (rawInput == null) throw new ArgumentNullException(nameof(rawInput));
        options ??= new NormalizeOptions();

        var cleaned = CleanInput(rawInput, options.Strictness);
        var parseResult = ParsePlate(rawInput, new ParseOptions
        {
            Strictness = options.Strictness,
            AllowMixedScripts = options.AllowMixedScripts,
            AllowReorderedInput = options.AllowReorderedInput,
            AllowShortDigits = options.AllowShortDigits,
        });

        if (!parseResult.Success || parseResult.Plate == null)
        {
            return new NormalizeResult(false, null, null, cleaned.Corrections, parseResult.Errors, parseResult.Warnings);
        }

        return new NormalizeResult(true, parseResult.Plate.Canonical, parseResult.Plate, cleaned.Corrections, Array.Empty<ValidationIssue>(), parseResult.Warnings);
    }

    public static NormalizeResult NormalizePlate(Plate plate)
    {
        if (plate == null) throw new ArgumentNullException(nameof(plate));
        return new NormalizeResult(true, plate.Canonical, plate);
    }

    public static ValidationResult ValidatePlate(string rawInput, NormalizeOptions? options = null)
    {
        var result = NormalizePlate(rawInput, options);
        return new ValidationResult(result.Success, result.Plate, result.Errors.Concat(result.Warnings).ToArray());
    }

    public static ValidationResult ValidatePlate(Plate plate)
    {
        if (plate == null) throw new ArgumentNullException(nameof(plate));
        var issues = new List<ValidationIssue>();
        if (plate.Letters.Count != 3)
        {
            issues.Add(new ValidationIssue("INVALID_LETTER_COUNT", "Expected exactly 3 letters.", field: "letters"));
        }
        if (!AsciiDigitsRegex.IsMatch(plate.Digits))
        {
            issues.Add(new ValidationIssue("INVALID_DIGITS", "Digits must be ASCII digits.", field: "digits"));
        }
        if (plate.Digits.Length < 1 || plate.Digits.Length > 4)
        {
            issues.Add(new ValidationIssue("INVALID_DIGIT_COUNT", "Expected 1 to 4 digits.", field: "digits"));
        }
        return new ValidationResult(issues.Count == 0, plate, issues);
    }

    public static string FormatPlate(string input, FormatStyle style = FormatStyle.Canonical, NormalizeOptions? options = null)
    {
        var normalized = NormalizePlate(input, options);
        if (!normalized.Success || normalized.Plate == null)
        {
            var messages = string.Join("; ", normalized.Errors.Select(issue => issue.Message));
            throw new ArgumentException($"Cannot format invalid plate: {messages}", nameof(input));
        }
        return FormatPlate(normalized.Plate, style);
    }

    public static string FormatPlate(Plate plate, FormatStyle style = FormatStyle.Canonical)
    {
        if (plate == null) throw new ArgumentNullException(nameof(plate));

        var latin = string.Concat(plate.Letters.Select(code => Mappings.CodeToLatin[code]));
        var arabic = string.Join(" ", plate.Letters.Select(code => Mappings.CodeToArabic[code]));
        var arabicDigits = ConvertDigits(plate.Digits, DigitSet.ArabicIndic);

        switch (style)
        {
            case FormatStyle.Canonical:
            case FormatStyle.Storage:
                return latin + "-" + plate.Digits;
            case FormatStyle.DisplayEn:
                return latin + " " + plate.Digits;
            case FormatStyle.CompactEn:
                return latin + plate.Digits;
            case FormatStyle.DisplayAr:
                return arabicDigits + " " + arabic;
            case FormatStyle.CompactAr:
                return arabicDigits + string.Concat(plate.Letters.Select(code => Mappings.CodeToArabic[code]));
            default:
                throw new ArgumentOutOfRangeException(nameof(style), style, "Unsupported format style.");
        }
    }

    public static bool EqualsPlate(string a, string b, NormalizeOptions? options = null)
    {
        var aResult = NormalizePlate(a, options);
        var bResult = NormalizePlate(b, options);
        return aResult.Success && bResult.Success && string.Equals(aResult.Canonical, bResult.Canonical, StringComparison.Ordinal);
    }

    public static bool EqualsPlate(Plate a, Plate b)
    {
        if (a == null) throw new ArgumentNullException(nameof(a));
        if (b == null) throw new ArgumentNullException(nameof(b));
        return string.Equals(a.Canonical, b.Canonical, StringComparison.Ordinal);
    }
}
