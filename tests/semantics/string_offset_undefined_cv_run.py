#!/usr/bin/env python3
"""Compare initially undefined string keys through staged Warning continuations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from string_offset_undefined_cv_cases import CASES as AUTHOR
from string_offset_undefined_cv_review_cases import CASES as REVIEW
from string_offset_current_string_cv_cases import CASES as CURRENT_STRINGS
from string_offset_current_request_cv_cases import CASES as CURRENT_REQUESTS
from string_offset_current_array_cv_cases import CASES as CURRENT_ARRAYS
from string_offset_current_array_alias_cv_cases import CASES as CURRENT_ARRAY_ALIASES
from string_offset_current_array_mixed_cv_cases import CASES as CURRENT_ARRAY_MIXED
from string_offset_current_array_string_alias_cv_cases import CASES as CURRENT_ARRAY_STRING_ALIASES
from string_offset_current_array_child_cv_cases import CASES as CURRENT_ARRAY_CHILDREN
from string_offset_current_array_alias_child_cv_cases import CASES as CURRENT_ARRAY_ALIAS_CHILDREN
from string_offset_current_marked_cv_cases import CASES as CURRENT_MARKED
from string_offset_current_marked_string_cv_cases import CASES as CURRENT_MARKED_STRINGS
from string_offset_current_marked_array_cv_cases import CASES as CURRENT_MARKED_ARRAYS
from string_offset_variable_base_cv_cases import CASES as VARIABLE_BASES
from string_offset_undefined_throw_cases import CASES as UNDEFINED_THROWS
from string_offset_variable_throw_cases import CASES as VARIABLE_THROWS
from string_offset_request_base_cv_cases import CASES as REQUEST_BASES
from string_offset_request_throw_cases import CASES as REQUEST_THROWS
from string_offset_request_release_cv_cases import CASES as REQUEST_RELEASES
from string_offset_request_release_registered_cv_cases import CASES as REGISTERED_RELEASES
from string_offset_request_release_prior_cv_cases import CASES as PRIOR_RELEASES
from string_offset_request_release_distinct_cv_cases import CASES as DISTINCT_RELEASES
from string_offset_request_release_key_cv_cases import CASES as KEY_RELEASES
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
CASES = AUTHOR + REVIEW + CURRENT_STRINGS + CURRENT_REQUESTS + CURRENT_ARRAYS + CURRENT_ARRAY_ALIASES + CURRENT_ARRAY_MIXED + CURRENT_ARRAY_STRING_ALIASES + CURRENT_ARRAY_CHILDREN + CURRENT_ARRAY_ALIAS_CHILDREN + CURRENT_MARKED + CURRENT_MARKED_STRINGS + CURRENT_MARKED_ARRAYS + VARIABLE_BASES + UNDEFINED_THROWS + VARIABLE_THROWS + REQUEST_BASES + REQUEST_THROWS + REQUEST_RELEASES + REGISTERED_RELEASES + PRIOR_RELEASES + DISTINCT_RELEASES + KEY_RELEASES


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), Path(__file__).with_name('string_offset_undefined_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_undefined_cv_review_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_string_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_request_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_array_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_array_alias_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_array_mixed_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_array_string_alias_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_array_child_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_array_alias_child_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_marked_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_marked_string_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_current_marked_array_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_variable_base_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_undefined_throw_cases.py')]
    watched += [Path(__file__).with_name('string_offset_variable_throw_cases.py')]
    watched += [Path(__file__).with_name('string_offset_request_base_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_request_throw_cases.py')]
    watched += [Path(__file__).with_name('string_offset_request_release_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_request_release_registered_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_request_release_prior_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_request_release_distinct_cv_cases.py')]
    watched += [Path(__file__).with_name('string_offset_request_release_key_cv_cases.py')]
    watched += [ROOT / name for name in (
        'spec/semantics/modules.json', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py',
        'bin/php-semantics', 'frontend/worker.php', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', '.tools/spectec/bin/p4spectec')]
    before = {str(path): digest(path) for path in watched}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    report = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'inputs': before, 'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'records': [], 'agreements': 0, 'passed': False}
    try:
        for stage in ('algo', 'struct'):
            result = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), stage, *map(str, modules)], out / stage, 120)
            assert result['exit'] == 0 and not result['timeout'] and not (out / (stage + '.stderr')).read_bytes()
            assert b'def $string_read_cv_plan' in (out / (stage + '.stdout')).read_bytes()
            report[stage] = result
            print(stage, 'pass', flush=True)
        for case in CASES:
            target = out / case['id']
            target.mkdir()
            source = target / 'original.php'
            source.write_text(case['source'])
            row = {'id': case['id'], 'source_sha256': digest(source)}
            report['records'].append(row)
            row['native'] = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], target / 'native', 20)
            stdout = (target / 'native.stdout').read_bytes()
            stderr = (target / 'native.stderr').read_bytes()
            expected_stderr = ''.join('Warning: ' + message + ' in ' + str(source) + ' on line '
                + str(case['read_line']) + '\n' for message in case.get('expected_warnings', [])).encode()
            assert row['native']['exit'] == 0 and not row['native']['timeout'] and stderr == expected_stderr
            assert stdout == case['expected_stdout'].encode(), (case['id'], stdout)
            row['model'] = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000',
                '--timeout', '60'], target / 'model', 80)
            observed = json.loads((target / 'model.stdout').read_bytes())
            row['observed'] = observed
            row['passed'] = (row['model']['exit'] == 0 and not row['model']['timeout']
                and not (target / 'model.stderr').read_bytes() and observed.get('frontend') == 'accepted'
                and observed.get('checked') == 'program' and observed.get('status') == 'normal'
                and observed.get('exit_status') == 0 and observed.get('reason') is None
                and observed.get('stdout') == base64.b64encode(stdout).decode()
                and observed.get('stderr') == base64.b64encode(stderr).decode())
            report['agreements'] += int(row['passed'])
            print(case['id'], 'pass' if row['passed'] else 'fail', flush=True)
            assert row['passed'], observed
        report['passed'] = report['agreements'] == len(CASES)
    finally:
        report['inputs_stable'] = before == {str(path): digest(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
