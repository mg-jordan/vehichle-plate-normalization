using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace SaudiPlate;

public enum Strictness
{
    Strict,
    Standard,
    Lenient,
}

public enum Script
{
    Arabic,
    Latin,
    Mixed,
    Unknown,
}

public enum DigitSet
{
    Ascii,
    ArabicIndic,
}

public enum FormatStyle
{
    Canonical,
    Storage,
    DisplayEn,
    DisplayAr,
    CompactEn,
    CompactAr,
}

public sealed class Plate
{
    public Plate(string country, IReadOnlyList<string> letters, string digits, Script sourceScript)
    {
        Country = country ?? throw new ArgumentNullException(nameof(country));
        Letters = new ReadOnlyCollection<string>((letters ?? throw new ArgumentNullException(nameof(letters))).ToArray());
        Digits = digits ?? throw new ArgumentNullException(nameof(digits));
        SourceScript = sourceScript;
    }

    public string Country { get; }
    public IReadOnlyList<string> Letters { get; }
    public string Digits { get; }
    public Script SourceScript { get; }
    public string Canonical => string.Concat(Letters.Select(code => Mappings.CodeToLatin[code])) + "-" + Digits;
}

public sealed class ValidationIssue
{
    public ValidationIssue(string code, string message, string severity = "error", string? field = null, IDictionary<string, object>? metadata = null)
    {
        Code = code ?? throw new ArgumentNullException(nameof(code));
        Message = message ?? throw new ArgumentNullException(nameof(message));
        Severity = severity ?? throw new ArgumentNullException(nameof(severity));
        Field = field;
        Metadata = metadata == null ? null : new ReadOnlyDictionary<string, object>(metadata);
    }

    public string Code { get; }
    public string Message { get; }
    public string Severity { get; }
    public string? Field { get; }
    public IReadOnlyDictionary<string, object>? Metadata { get; }
}

public sealed class Correction
{
    public Correction(string type, string before, string after)
    {
        Type = type ?? throw new ArgumentNullException(nameof(type));
        Before = before ?? throw new ArgumentNullException(nameof(before));
        After = after ?? throw new ArgumentNullException(nameof(after));
    }

    public string Type { get; }
    public string Before { get; }
    public string After { get; }
}

public sealed class ParseOptions
{
    public Strictness Strictness { get; set; } = Strictness.Standard;
    public bool? AllowMixedScripts { get; set; }
    public bool? AllowReorderedInput { get; set; }
    public bool? AllowShortDigits { get; set; }
}

public sealed class NormalizeOptions
{
    public Strictness Strictness { get; set; } = Strictness.Standard;
    public bool? AllowMixedScripts { get; set; }
    public bool? AllowReorderedInput { get; set; }
    public bool? AllowShortDigits { get; set; }
}

public sealed class ParseResult
{
    public ParseResult(bool success, string rawInput, string? normalizedInput = null, Plate? plate = null, IReadOnlyList<ValidationIssue>? errors = null, IReadOnlyList<ValidationIssue>? warnings = null)
    {
        Success = success;
        RawInput = rawInput ?? throw new ArgumentNullException(nameof(rawInput));
        NormalizedInput = normalizedInput;
        Plate = plate;
        Errors = errors ?? Array.Empty<ValidationIssue>();
        Warnings = warnings ?? Array.Empty<ValidationIssue>();
    }

    public bool Success { get; }
    public string RawInput { get; }
    public string? NormalizedInput { get; }
    public Plate? Plate { get; }
    public IReadOnlyList<ValidationIssue> Errors { get; }
    public IReadOnlyList<ValidationIssue> Warnings { get; }
}

public sealed class NormalizeResult
{
    public NormalizeResult(bool success, string? canonical = null, Plate? plate = null, IReadOnlyList<Correction>? corrections = null, IReadOnlyList<ValidationIssue>? errors = null, IReadOnlyList<ValidationIssue>? warnings = null)
    {
        Success = success;
        Canonical = canonical;
        Plate = plate;
        Corrections = corrections ?? Array.Empty<Correction>();
        Errors = errors ?? Array.Empty<ValidationIssue>();
        Warnings = warnings ?? Array.Empty<ValidationIssue>();
    }

    public bool Success { get; }
    public string? Canonical { get; }
    public Plate? Plate { get; }
    public IReadOnlyList<Correction> Corrections { get; }
    public IReadOnlyList<ValidationIssue> Errors { get; }
    public IReadOnlyList<ValidationIssue> Warnings { get; }
}

public sealed class ValidationResult
{
    public ValidationResult(bool isValid, Plate? plate = null, IReadOnlyList<ValidationIssue>? issues = null)
    {
        IsValid = isValid;
        Plate = plate;
        Issues = issues ?? Array.Empty<ValidationIssue>();
    }

    public bool IsValid { get; }
    public Plate? Plate { get; }
    public IReadOnlyList<ValidationIssue> Issues { get; }
}
