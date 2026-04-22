from iraqi_plate import AcceptanceMode, IraqiPlateService, PlateOptions


svc = IraqiPlateService()


test_cases = [
    {
        "name": "canonical_current_ascii",
        "input": "22A153",
        "standard": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": [],
        },
        "strict": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": [],
        },
    },
    {
        "name": "canonical_with_separators",
        "input": "22-A-153",
        "standard": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": [],
        },
        "strict": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": [],
        },
    },
    {
        "name": "canonical_with_spaces",
        "input": "22 A 153",
        "standard": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": [],
        },
        "strict": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": [],
        },
    },
    {
        "name": "canonical_with_eastern_arabic_digits",
        "input": "٢٢A١٥٣",
        "standard": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": [],
        },
        "strict": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": [],
        },
    },
    {
        "name": "standard_letter_first_shorthand",
        "input": "A22153",
        "standard": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": ["non_canonical_order_normalized"],
        },
        "strict": {
            "is_valid": False,
            "canonical": None,
            "errors": ["strict_requires_canonical_current_format"],
        },
    },
    {
        "name": "standard_digit_first_shorthand",
        "input": "22153A",
        "standard": {
            "is_valid": True,
            "canonical": "22A153",
            "warnings": ["non_canonical_order_normalized"],
        },
        "strict": {
            "is_valid": False,
            "canonical": None,
            "errors": ["strict_requires_canonical_current_format"],
        },
    },
    {
        "name": "legacy_arabic_letter",
        "input": "ا22153",
        "standard": {
            "is_valid": True,
            "canonical": "22ا153",
            "warnings": ["legacy_number"],
        },
        "strict": {
            "is_valid": False,
            "canonical": None,
            "errors": ["strict_requires_canonical_current_format"],
        },
    },
    {
        "name": "legacy_arabic_letter_with_eastern_digits_and_separator",
        "input": "ا-٢٢١٥٣",
        "standard": {
            "is_valid": True,
            "canonical": "22ا153",
            "warnings": ["legacy_number"],
        },
        "strict": {
            "is_valid": False,
            "canonical": None,
            "errors": ["strict_requires_canonical_current_format"],
        },
    },
    {
        "name": "invalid_governorate_out_of_range_high",
        "input": "31A153",
        "standard": {
            "is_valid": False,
            "canonical": None,
            "errors": ["invalid_structure"],
        },
        "strict": {
            "is_valid": False,
            "canonical": None,
            "errors": ["strict_requires_canonical_current_format"],
        },
    },
    {
        "name": "invalid_shorthand_governorate_out_of_range",
        "input": "A30153",
        "standard": {
            "is_valid": False,
            "canonical": None,
            "errors": ["governorate_out_of_range"],
        },
        "strict": {
            "is_valid": False,
            "canonical": None,
            "errors": ["strict_requires_canonical_current_format"],
        },
    },
]

import pytest
from iraqi_plate import IraqiPlateService, PlateOptions, AcceptanceMode

svc = IraqiPlateService()

@pytest.mark.parametrize("case", test_cases)
def test_standard(case):
    result = svc.normalize_plate(
        case["input"],
        PlateOptions(mode=AcceptanceMode.STANDARD),
    )

    expected = case["standard"]

    assert result.success == expected["is_valid"]

    if expected["is_valid"]:
        assert result.canonical == expected["canonical"]
        assert result.warnings == expected.get("warnings", [])
        print(f"TEST PASSED: {case['name']} in STANDARD mode for input '{case['input']}' -> canonical: '{result.canonical}', warnings: {result.warnings}")
    else:
        assert result.canonical is None
        print(f"TEST PASSED: {case['name']} in STANDARD mode for input '{case['input']}' -> canonical: None")

@pytest.mark.parametrize("case", test_cases)
def test_strict(case):
    result = svc.normalize_plate(
        case["input"],
        PlateOptions(mode=AcceptanceMode.STRICT),
    )

    expected = case["strict"]

    assert result.success == expected["is_valid"]

    if expected["is_valid"]:
        assert result.canonical == expected["canonical"]
        assert result.warnings == expected.get("warnings", [])
        print(f"TEST PASSED: {case['name']} in STRICT mode for input '{case['input']}' -> canonical: '{result.canonical}', warnings: {result.warnings}")
    else:
        assert result.canonical is None
        print(f"TEST PASSED: {case['name']} in STRICT mode for input '{case['input']}' -> canonical: None")