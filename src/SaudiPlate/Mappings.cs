using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace SaudiPlate;

internal static class Mappings
{
    public static readonly IReadOnlyDictionary<string, (string Ar, string En)> LetterTable =
        new ReadOnlyDictionary<string, (string Ar, string En)>(
            new Dictionary<string, (string Ar, string En)>
            {
                ["ALIF"] = ("ا", "A"),
                ["BA"] = ("ب", "B"),
                ["HA"] = ("ح", "J"),
                ["DAL"] = ("د", "D"),
                ["RA"] = ("ر", "R"),
                ["SIN"] = ("س", "S"),
                ["SAD"] = ("ص", "X"),
                ["TA"] = ("ط", "T"),
                ["AIN"] = ("ع", "E"),
                ["QAF"] = ("ق", "G"),
                ["KAF"] = ("ك", "K"),
                ["LAM"] = ("ل", "L"),
                ["MIM"] = ("م", "Z"),
                ["NUN"] = ("ن", "N"),
                ["HAH"] = ("ه", "H"),
                ["WAW"] = ("و", "U"),
                ["YA"] = ("ي", "V"),
            });

    public static readonly IReadOnlyDictionary<string, string> ArabicToCode =
        new ReadOnlyDictionary<string, string>(LetterTable.ToDictionary(kvp => kvp.Value.Ar, kvp => kvp.Key));

    public static readonly IReadOnlyDictionary<string, string> LatinToCode =
        new ReadOnlyDictionary<string, string>(LetterTable.ToDictionary(kvp => kvp.Value.En, kvp => kvp.Key));

    public static readonly IReadOnlyDictionary<string, string> CodeToArabic =
        new ReadOnlyDictionary<string, string>(LetterTable.ToDictionary(kvp => kvp.Key, kvp => kvp.Value.Ar));

    public static readonly IReadOnlyDictionary<string, string> CodeToLatin =
        new ReadOnlyDictionary<string, string>(LetterTable.ToDictionary(kvp => kvp.Key, kvp => kvp.Value.En));

    public static readonly HashSet<string> ValidArabicLetters = new HashSet<string>(ArabicToCode.Keys);
    public static readonly HashSet<string> ValidLatinLetters = new HashSet<string>(LatinToCode.Keys);

    public const string ArabicIndicDigits = "٠١٢٣٤٥٦٧٨٩";
    public const string AsciiDigits = "0123456789";

    public static readonly HashSet<char> BidiControlChars = new HashSet<char>
    {
        '‎', '‏', '‪', '‫', '‬', '‭', '‮', '⁦', '⁧', '⁨', '⁩',
    };
}
