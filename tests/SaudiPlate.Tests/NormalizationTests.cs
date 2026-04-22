using System;
using System.Collections.Generic;
using System.Linq;
using SaudiPlate;
using Xunit;

namespace SaudiPlate.Tests;

public sealed class NormalizationTests
{
    public static IEnumerable<object?[]> Scenarios()
    {
        yield return Case("ABJ1234", Strictness.Standard, true, "ABJ-1234", "ABJ 1234", "١٢٣٤ ا ب ح", Array.Empty<string>(), null, null, null);
        yield return Case("ABJ1234", Strictness.Strict, true, "ABJ-1234", "ABJ 1234", "١٢٣٤ ا ب ح", Array.Empty<string>(), null, null, null);

        yield return Case("ABJ-1234", Strictness.Standard, true, "ABJ-1234", "ABJ 1234", null, Array.Empty<string>(), null, null, null);
        yield return Case("ABJ-1234", Strictness.Strict, true, "ABJ-1234", "ABJ 1234", null, Array.Empty<string>(), null, null, null);

        yield return Case("ا ب ح ١٢٣٤", Strictness.Standard, true, "ABJ-1234", "ABJ 1234", "١٢٣٤ ا ب ح", Array.Empty<string>(), null, null, null);
        yield return Case("ا ب ح ١٢٣٤", Strictness.Strict, true, "ABJ-1234", "ABJ 1234", "١٢٣٤ ا ب ح", Array.Empty<string>(), null, null, null);

        yield return Case("1234 ABJ", Strictness.Standard, true, "ABJ-1234", null, null, new[] { "REORDERED_INPUT" }, null, null, null);
        yield return Case("1234 ABJ", Strictness.Strict, false, null, null, null, null, new[] { "REORDERED_INPUT_NOT_ALLOWED" }, null, null);

        yield return Case("ABJ 123", Strictness.Standard, true, "ABJ-123", null, null, Array.Empty<string>(), null, null, null);
        yield return Case("ABJ 123", Strictness.Strict, false, null, null, null, null, new[] { "SHORT_DIGITS_NOT_ALLOWED" }, null, null);

        yield return Case("AبJ1234", Strictness.Standard, true, "ABJ-1234", null, null, null, null, null, null);
        yield return Case("AبJ1234", Strictness.Strict, false, null, null, null, null, new[] { "MIXED_SCRIPTS_NOT_ALLOWED" }, null, null);

        yield return Case("ABC 1234", Strictness.Standard, false, null, null, null, null, new[] { "UNSUPPORTED_CHARACTERS" }, null, null);
        yield return Case("ABC 1234", Strictness.Strict, false, null, null, null, null, new[] { "UNSUPPORTED_CHARACTERS" }, null, null);

        yield return Case("ABJ 12345", Strictness.Standard, false, null, null, null, null, new[] { "INVALID_DIGIT_COUNT" }, null, null);
        yield return Case("ABJ 12345", Strictness.Strict, false, null, null, null, null, new[] { "INVALID_DIGIT_COUNT" }, null, null);

        yield return Case(" ABJ__1234 ", Strictness.Standard, true, "ABJ-1234", null, null, null, null, null, null);
        yield return Case(" ABJ__1234 ", Strictness.Strict, true, "ABJ-1234", null, null, null, null, null, null);

        yield return Case("ABH 1234", Strictness.Standard, true, "ABH-1234", null, "١٢٣٤ ا ب ه", null, null, null, null);
        yield return Case("ABH 1234", Strictness.Strict, true, "ABH-1234", null, "١٢٣٤ ا ب ه", null, null, null, null);

        yield return Case("ABJ 1234", Strictness.Standard, true, "ABJ-1234", null, "١٢٣٤ ا ب ح", null, null, null, null);
        yield return Case("ABJ 1234", Strictness.Strict, true, "ABJ-1234", null, "١٢٣٤ ا ب ح", null, null, null, null);

        yield return Case("ABJ1234", Strictness.Standard, true, "ABJ-1234", null, null, null, null, "ا ب ح ١٢٣٤", true);
        yield return Case("ABJ1234", Strictness.Strict, true, "ABJ-1234", null, null, null, null, "ا ب ح ١٢٣٤", true);

        yield return Case("أ ب ح ١٢٣٤", Strictness.Standard, true, "ABJ-1234", null, "١٢٣٤ ا ب ح", Array.Empty<string>(), null, null, null);
        yield return Case("أ ب ح ١٢٣٤", Strictness.Strict, false, null, null, null, null, new[] { "UNSUPPORTED_CHARACTERS" }, null, null);

        yield return Case("إ ب ح ١٢٣٤", Strictness.Standard, true, "ABJ-1234", null, "١٢٣٤ ا ب ح", Array.Empty<string>(), null, null, null);
        yield return Case("إ ب ح ١٢٣٤", Strictness.Strict, false, null, null, null, null, new[] { "UNSUPPORTED_CHARACTERS" }, null, null);

        yield return Case("آ ب ح ١٢٣٤", Strictness.Standard, true, "ABJ-1234", null, "١٢٣٤ ا ب ح", Array.Empty<string>(), null, null, null);
        yield return Case("آ ب ح ١٢٣٤", Strictness.Strict, false, null, null, null, null, new[] { "UNSUPPORTED_CHARACTERS" }, null, null);

        yield return Case("ا ب ة ١٢٣٤", Strictness.Standard, true, "ABH-1234", null, "١٢٣٤ ا ب ه", Array.Empty<string>(), null, null, null);
        yield return Case("ا ب ة ١٢٣٤", Strictness.Strict, false, null, null, null, null, new[] { "UNSUPPORTED_CHARACTERS" }, null, null);

        yield return Case("ا ب ى ١٢٣٤", Strictness.Standard, true, "ABV-1234", null, "١٢٣٤ ا ب ي", Array.Empty<string>(), null, null, null);
        yield return Case("ا ب ى ١٢٣٤", Strictness.Strict, false, null, null, null, null, new[] { "UNSUPPORTED_CHARACTERS" }, null, null);

        yield return Case("ا ب ئ ١٢٣٤", Strictness.Standard, true, "ABV-1234", null, "١٢٣٤ ا ب ي", Array.Empty<string>(), null, null, null);
        yield return Case("ا ب ئ ١٢٣٤", Strictness.Strict, false, null, null, null, null, new[] { "UNSUPPORTED_CHARACTERS" }, null, null);
    }

    [Theory]
    [MemberData(nameof(Scenarios))]
    public void NormalizePlate_MatchesExpectedBehavior(
        string input,
        Strictness strictness,
        bool expectSuccess,
        string? expectCanonical,
        string? expectDisplayEn,
        string? expectDisplayAr,
        string[]? expectWarningCodes,
        string[]? expectErrorCodes,
        string? compareTo,
        bool? expectEquals)
    {
        var options = new NormalizeOptions { Strictness = strictness };
        var result = SaudiPlateApi.NormalizePlate(input, options);

        var debugInfo = $"""
    INPUT: "{input}"
    MODE: {strictness}
    SUCCESS: {result.Success}
    CANONICAL: {result.Canonical ?? "—"}
    WARNINGS: [{string.Join(", ", result.Warnings.Select(w => w.Code))}]
    ERRORS: [{string.Join(", ", result.Errors.Select(e => e.Code))}]
    """;

        Assert.True(result.Success == expectSuccess, debugInfo);

        if (expectSuccess)
        {
            Assert.True(result.Canonical == expectCanonical, debugInfo);

            if (expectDisplayEn != null)
            {
                var actual = SaudiPlateApi.FormatPlate(result.Plate!, FormatStyle.DisplayEn);
                Assert.True(actual == expectDisplayEn, debugInfo + $"\nDISPLAY_EN: {actual}");
            }

            if (expectDisplayAr != null)
            {
                var actual = SaudiPlateApi.FormatPlate(result.Plate!, FormatStyle.DisplayAr);
                Assert.True(actual == expectDisplayAr, debugInfo + $"\nDISPLAY_AR: {actual}");
            }

            if (expectWarningCodes != null)
            {
                var actual = result.Warnings.Select(x => x.Code).OrderBy(x => x);
                Assert.True(actual.SequenceEqual(expectWarningCodes.OrderBy(x => x)), debugInfo);
            }

            if (expectEquals.HasValue && compareTo != null)
            {
                var eq = SaudiPlateApi.EqualsPlate(input, compareTo, options);
                Assert.True(eq == expectEquals.Value, debugInfo + $"\nCOMPARE_TO: {compareTo} => {eq}");
            }
        }
        else
        {
            Assert.Null(result.Canonical);
            Assert.Null(result.Plate);

            if (expectErrorCodes != null)
            {
                var actual = result.Errors.Select(x => x.Code).OrderBy(x => x);
                Assert.True(actual.SequenceEqual(expectErrorCodes.OrderBy(x => x)), debugInfo);
            }
        }
    }
    [Fact]
    public void StrictMode_RejectsFoldedArabicCharacters_ButStandardAcceptsThem()
    {
        var standard = SaudiPlateApi.NormalizePlate("أ ب ح ١٢٣٤", new NormalizeOptions { Strictness = Strictness.Standard });
        var strict = SaudiPlateApi.NormalizePlate("أ ب ح ١٢٣٤", new NormalizeOptions { Strictness = Strictness.Strict });

        Assert.True(standard.Success);
        Assert.Equal("ABJ-1234", standard.Canonical);

        Assert.False(strict.Success);
        Assert.Contains(strict.Errors, issue => issue.Code == "UNSUPPORTED_CHARACTERS");
    }

    private static object?[] Case(
        string input,
        Strictness strictness,
        bool expectSuccess,
        string? expectCanonical,
        string? expectDisplayEn,
        string? expectDisplayAr,
        string[]? expectWarningCodes,
        string[]? expectErrorCodes,
        string? compareTo,
        bool? expectEquals)
    {
        return new object?[]
        {
            input,
            strictness,
            expectSuccess,
            expectCanonical,
            expectDisplayEn,
            expectDisplayAr,
            expectWarningCodes,
            expectErrorCodes,
            compareTo,
            expectEquals,
        };
    }
}
