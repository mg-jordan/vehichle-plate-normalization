# Saudi Plate Test Report

Generated at: 2026-04-20T08:02:08.834573+00:00

## Summary

- Total cases: 15
- Passed: 15
- Failed: 0
- Pass rate: 100.0%

## Case Results

| ID | Name | Input | Result | Notes |
|---|---|---|---|---|
| T001 | Canonical English compact | `ABJ1234` | PASS | All checks passed |
| T002 | English with separators | `ABJ-1234` | PASS | All checks passed |
| T003 | Arabic letters and Arabic-Indic digits | `ا ب ح ١٢٣٤` | PASS | All checks passed |
| T004 | Digits before letters allowed in standard mode | `1234 ABJ` | PASS | All checks passed |
| T005 | Digits before letters rejected in strict mode | `1234 ABJ` | PASS | All checks passed |
| T006 | Strict mode rejects short digits | `ABJ 123` | PASS | All checks passed |
| T007 | Standard mode accepts short digits | `ABJ 123` | PASS | All checks passed |
| T008 | Mixed Arabic and Latin letters allowed in standard mode | `AبJ1234` | PASS | All checks passed |
| T009 | Mixed Arabic and Latin letters rejected in strict mode | `AبJ1234` | PASS | All checks passed |
| T010 | Unsupported Latin letters are rejected | `ABC 1234` | PASS | All checks passed |
| T011 | Too many digits are rejected | `ABJ 12345` | PASS | All checks passed |
| T012 | Unsupported punctuation is cleaned | ` ABJ__1234 ` | PASS | All checks passed |
| T013 | Saudi H mapping uses H only for ه | `ABH 1234` | PASS | All checks passed |
| T014 | Saudi J mapping uses ح | `ABJ 1234` | PASS | All checks passed |
| T015 | equals works across Arabic and English forms | `ABJ1234` | PASS | All checks passed |

## Failed Checks

No failed checks.
