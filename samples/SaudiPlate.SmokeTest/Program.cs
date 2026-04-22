using SaudiPlate;

var samples = new[]
{
    "ABJ1234",
    "ا ب ح ١٢٣٤",
    "1234 ABJ",
    "أ ب ح ١٢٣٤",
};

foreach (var sample in samples)
{
    var standard = SaudiPlateApi.NormalizePlate(sample, new NormalizeOptions { Strictness = Strictness.Standard });
    var strict = SaudiPlateApi.NormalizePlate(sample, new NormalizeOptions { Strictness = Strictness.Strict });

    Console.WriteLine($"input={sample}");
    Console.WriteLine($"  standard: success={standard.Success}, canonical={standard.Canonical ?? "—"}, errors=[{string.Join(",", standard.Errors.Select(e => e.Code))}], warnings=[{string.Join(",", standard.Warnings.Select(w => w.Code))}]");
    Console.WriteLine($"  strict:   success={strict.Success}, canonical={strict.Canonical ?? "—"}, errors=[{string.Join(",", strict.Errors.Select(e => e.Code))}], warnings=[{string.Join(",", strict.Warnings.Select(w => w.Code))}]");
}
