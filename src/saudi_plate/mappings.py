from __future__ import annotations

LETTER_TABLE = {
    "ALIF": {"ar": "ا", "en": "A"},
    "BA": {"ar": "ب", "en": "B"},
    "HA": {"ar": "ح", "en": "J"},
    "DAL": {"ar": "د", "en": "D"},
    "RA": {"ar": "ر", "en": "R"},
    "SIN": {"ar": "س", "en": "S"},
    "SAD": {"ar": "ص", "en": "X"},
    "TA": {"ar": "ط", "en": "T"},
    "AIN": {"ar": "ع", "en": "E"},
    "QAF": {"ar": "ق", "en": "G"},
    "KAF": {"ar": "ك", "en": "K"},
    "LAM": {"ar": "ل", "en": "L"},
    "MIM": {"ar": "م", "en": "Z"},
    "NUN": {"ar": "ن", "en": "N"},
    "HAH": {"ar": "ه", "en": "H"},
    "WAW": {"ar": "و", "en": "U"},
    "YA": {"ar": "ي", "en": "V"},
}

ARABIC_TO_CODE = {row["ar"]: code for code, row in LETTER_TABLE.items()}
LATIN_TO_CODE = {row["en"]: code for code, row in LETTER_TABLE.items()}
CODE_TO_ARABIC = {code: row["ar"] for code, row in LETTER_TABLE.items()}
CODE_TO_LATIN = {code: row["en"] for code, row in LETTER_TABLE.items()}
VALID_ARABIC_LETTERS = set(ARABIC_TO_CODE.keys())
VALID_LATIN_LETTERS = set(LATIN_TO_CODE.keys())

ARABIC_INDIC_TO_ASCII = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
ASCII_TO_ARABIC_INDIC = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

BIDI_CONTROL_CHARS = {
    "\u200e",  # LRM
    "\u200f",  # RLM
    "\u202a",  # LRE
    "\u202b",  # RLE
    "\u202c",  # PDF
    "\u202d",  # LRO
    "\u202e",  # RLO
    "\u2066",  # LRI
    "\u2067",  # RLI
    "\u2068",  # FSI
    "\u2069",  # PDI
}
