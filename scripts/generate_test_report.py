from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from saudi_plate import (  # noqa: E402
    FormatStyle,
    NormalizeOptions,
    Strictness,
    equals,
    format_plate,
    normalize_plate,
    validate_plate,
)


TEST_CASES: List[Dict[str, Any]] = [
    {
        'id': 'T001',
        'name': 'Canonical English compact',
        'input': 'ABJ1234',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-1234',
        'expect_display_en': 'ABJ 1234',
        'expect_display_ar': '١٢٣٤ ا ب ح',
        'expect_warning_codes': [],
    },
    {
        'id': 'T002',
        'name': 'English with separators',
        'input': 'ABJ-1234',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-1234',
        'expect_display_en': 'ABJ 1234',
        'expect_warning_codes': [],
    },
    {
        'id': 'T003',
        'name': 'Arabic letters and Arabic-Indic digits',
        'input': 'ا ب ح ١٢٣٤',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-1234',
        'expect_display_en': 'ABJ 1234',
        'expect_display_ar': '١٢٣٤ ا ب ح',
        'expect_warning_codes': [],
    },
    {
        'id': 'T004',
        'name': 'Digits before letters allowed in standard mode',
        'input': '1234 ABJ',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-1234',
        'expect_warning_codes': ['REORDERED_INPUT'],
    },
    {
        'id': 'T005',
        'name': 'Digits before letters rejected in strict mode',
        'input': '1234 ABJ',
        'options': {'strictness': 'strict'},
        'expect_success': False,
        'expect_error_codes': ['REORDERED_INPUT_NOT_ALLOWED'],
    },
    {
        'id': 'T006',
        'name': 'Strict mode rejects short digits',
        'input': 'ABJ 123',
        'options': {'strictness': 'strict'},
        'expect_success': False,
        'expect_error_codes': ['SHORT_DIGITS_NOT_ALLOWED'],
    },
    {
        'id': 'T007',
        'name': 'Standard mode accepts short digits',
        'input': 'ABJ 123',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-123',
    },
    {
        'id': 'T008',
        'name': 'Mixed Arabic and Latin letters allowed in standard mode',
        'input': 'AبJ1234',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-1234',
    },
    {
        'id': 'T009',
        'name': 'Mixed Arabic and Latin letters rejected in strict mode',
        'input': 'AبJ1234',
        'options': {'strictness': 'strict'},
        'expect_success': False,
        'expect_error_codes': ['MIXED_SCRIPTS_NOT_ALLOWED'],
    },
    {
        'id': 'T010',
        'name': 'Unsupported Latin letters are rejected',
        'input': 'ABC 1234',
        'options': {'strictness': 'standard'},
        'expect_success': False,
        'expect_error_codes': ['UNSUPPORTED_CHARACTERS'],
    },
    {
        'id': 'T011',
        'name': 'Too many digits are rejected',
        'input': 'ABJ 12345',
        'options': {'strictness': 'standard'},
        'expect_success': False,
        'expect_error_codes': ['INVALID_DIGIT_COUNT'],
    },
    {
        'id': 'T012',
        'name': 'Unsupported punctuation is cleaned',
        'input': ' ABJ__1234 ',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-1234',
    },
    {
        'id': 'T013',
        'name': 'Saudi H mapping uses H only for ه',
        'input': 'ABH 1234',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABH-1234',
        'expect_display_ar': '١٢٣٤ ا ب ه',
    },
    {
        'id': 'T014',
        'name': 'Saudi J mapping uses ح',
        'input': 'ABJ 1234',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-1234',
        'expect_display_ar': '١٢٣٤ ا ب ح',
    },
    {
        'id': 'T015',
        'name': 'equals works across Arabic and English forms',
        'input': 'ABJ1234',
        'compare_to': 'ا ب ح ١٢٣٤',
        'options': {'strictness': 'standard'},
        'expect_success': True,
        'expect_canonical': 'ABJ-1234',
        'expect_equals': True,
    },
]


def build_options(payload: Dict[str, Any]) -> NormalizeOptions:
    strictness = Strictness(payload.get('strictness', 'standard'))
    return NormalizeOptions(
        strictness=strictness,
        allow_mixed_scripts=payload.get('allow_mixed_scripts'),
        allow_reordered_input=payload.get('allow_reordered_input'),
        allow_short_digits=payload.get('allow_short_digits'),
    )


def issue_codes(items: List[Any]) -> List[str]:
    return [item.code for item in items]


def run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    options = build_options(case.get('options', {}))
    normalize_result = normalize_plate(case['input'], options)
    validation_result = validate_plate(case['input'], options)

    actual: Dict[str, Any] = {
        'success': normalize_result.success,
        'canonical': normalize_result.canonical,
        'error_codes': issue_codes(list(normalize_result.errors)),
        'warning_codes': issue_codes(list(normalize_result.warnings)),
        'is_valid': validation_result.is_valid,
        'validation_issue_codes': issue_codes(list(validation_result.issues)),
        'display_en': None,
        'display_ar': None,
        'equals': None,
    }

    if normalize_result.success and normalize_result.plate is not None:
        actual['display_en'] = format_plate(normalize_result.plate, FormatStyle.DISPLAY_EN)
        actual['display_ar'] = format_plate(normalize_result.plate, FormatStyle.DISPLAY_AR)

    if 'compare_to' in case:
        actual['equals'] = equals(case['input'], case['compare_to'], options)

    checks: List[Dict[str, Any]] = []

    def add_check(name: str, expected: Any, observed: Any) -> None:
        checks.append({
            'check': name,
            'expected': expected,
            'observed': observed,
            'passed': expected == observed,
        })

    add_check('success', case['expect_success'], actual['success'])

    if 'expect_canonical' in case:
        add_check('canonical', case['expect_canonical'], actual['canonical'])
    if 'expect_error_codes' in case:
        add_check('error_codes', case['expect_error_codes'], actual['error_codes'])
    if 'expect_warning_codes' in case:
        add_check('warning_codes', case['expect_warning_codes'], actual['warning_codes'])
    if 'expect_display_en' in case:
        add_check('display_en', case['expect_display_en'], actual['display_en'])
    if 'expect_display_ar' in case:
        add_check('display_ar', case['expect_display_ar'], actual['display_ar'])
    if 'expect_equals' in case:
        add_check('equals', case['expect_equals'], actual['equals'])

    passed = all(item['passed'] for item in checks)

    return {
        'id': case['id'],
        'name': case['name'],
        'input': case['input'],
        'compare_to': case.get('compare_to'),
        'options': asdict(options),
        'expected': {k: v for k, v in case.items() if k.startswith('expect_')},
        'actual': actual,
        'checks': checks,
        'passed': passed,
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append('# Saudi Plate Test Report')
    lines.append('')
    lines.append(f"Generated at: {report['generated_at_utc']}")
    lines.append('')
    lines.append('## Summary')
    lines.append('')
    lines.append(f"- Total cases: {report['summary']['total_cases']}")
    lines.append(f"- Passed: {report['summary']['passed_cases']}")
    lines.append(f"- Failed: {report['summary']['failed_cases']}")
    lines.append(f"- Pass rate: {report['summary']['pass_rate_percent']}%")
    lines.append('')
    lines.append('## Case Results')
    lines.append('')
    lines.append('| ID | Name | Input | Result | Notes |')
    lines.append('|---|---|---|---|---|')
    for case in report['cases']:
        status = 'PASS' if case['passed'] else 'FAIL'
        failures = [c['check'] for c in case['checks'] if not c['passed']]
        note = ', '.join(failures) if failures else 'All checks passed'
        safe_input = str(case['input']).replace('|', '\\|')
        safe_name = str(case['name']).replace('|', '\\|')
        safe_note = note.replace('|', '\\|')
        lines.append(f"| {case['id']} | {safe_name} | `{safe_input}` | {status} | {safe_note} |")
    lines.append('')
    lines.append('## Failed Checks')
    lines.append('')
    failed_cases = [case for case in report['cases'] if not case['passed']]
    if not failed_cases:
        lines.append('No failed checks.')
    else:
        for case in failed_cases:
            lines.append(f"### {case['id']} — {case['name']}")
            lines.append('')
            lines.append(f"Input: `{case['input']}`")
            if case.get('compare_to'):
                lines.append(f"Compare to: `{case['compare_to']}`")
            lines.append('')
            for check in case['checks']:
                if not check['passed']:
                    lines.append(f"- {check['check']}: expected `{check['expected']}` but got `{check['observed']}`")
            lines.append('')
    return '\n'.join(lines) + '\n'


def main() -> int:
    case_results = [run_case(case) for case in TEST_CASES]
    passed_cases = sum(1 for case in case_results if case['passed'])
    total_cases = len(case_results)
    failed_cases = total_cases - passed_cases
    report = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total_cases': total_cases,
            'passed_cases': passed_cases,
            'failed_cases': failed_cases,
            'pass_rate_percent': round((passed_cases / total_cases) * 100, 2) if total_cases else 0.0,
        },
        'cases': case_results,
    }

    reports_dir = ROOT / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    json_path = reports_dir / 'test_report.json'
    md_path = reports_dir / 'test_report.md'

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    md_path.write_text(render_markdown(report), encoding='utf-8')

    print(f'Wrote JSON report to {json_path}')
    print(f'Wrote Markdown report to {md_path}')
    print(json.dumps(report['summary'], indent=2))
    return 0 if failed_cases == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
