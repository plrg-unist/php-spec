#!/usr/bin/env python3
"""Check promoted parent/interface boundaries by status without renewing native credit."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    # Historical boundaries now checked by status, without a new native comparison.
    'forward-parent': (b'<?php $o = new class extends Base143 {}; class Base143 {}', 'normal'),
    'dynamic-unit': (b"<?php class Base143 {} eval('$o = new class extends Base143 {};');", 'normal'),
    'interface': (b'<?php interface I143 {} $o = new class implements I143 {};', 'normal'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    out = Path(tempfile.mkdtemp(prefix='anonymous-parent-unsupported-', dir=ROOT / '.tools'))
    watched = [ROOT / 'spec/semantics/383-anonymous-classes.watsup',
               ROOT / 'tests/semantics/anonymous_parent_unsupported.py',
               ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'passed': False, 'inputs_before': before, 'cases': [], 'raw': str(out)}
    try:
        for name, (code, expected) in CASES.items():
            case = out / name
            case.mkdir()
            source = case / 'source.php'
            source.write_bytes(code)
            result = cross.invoke.process([str(ROOT / 'bin/php-semantics'), str(source),
                                           '--steps', '100000', '--timeout', '45'],
                                          case / 'model', 55, case)
            observed = json.loads(result.stdout)
            passed = (result.returncode == (1 if expected == 'unsupported' else 0) and not result.stderr and
                      observed.get('frontend') == 'accepted' and
                      observed.get('checked') == 'program' and
                      observed.get('status') == expected)
            if expected == 'normal':
                passed = passed and observed.get('reason') is None and observed.get('exit_status') == 0 and observed.get('stdout') == '' and observed.get('stderr') == ''
            report['cases'].append({'id': name, 'source_sha256': sha(source),
                                    'status': observed.get('status'), 'expected': expected,
                                    'reason': observed.get('reason'), 'passed': passed})
            print(name, observed.get('status'), passed, flush=True)
            assert passed
        report['passed'] = True
    finally:
        report['inputs_after'] = {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
