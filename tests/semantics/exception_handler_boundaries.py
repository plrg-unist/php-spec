#!/usr/bin/env python3
"""Explicit Unsupported controls; these receive no PHP agreement credit."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded

ROOT = Path(__file__).resolve().parents[2]
REASON = 'exception-handler keyword/compound callable ingress requires effectful API resolution'
CASES = {
    'keyword-registration': '<?php class C{static function reg(){set_exception_handler(["self","h"]);}'
                            'static function h($e){echo "BAD";}}C::reg();throw new Exception;',
    'compound-after-registration': '<?php class C{static function h($e){echo "BAD";}}'
                                   '$m="h";$raw=["C",&$m];set_exception_handler($raw);'
                                   '$m="self::h";throw new Exception;',
}


def main():
    out = Path(tempfile.mkdtemp(prefix='exceptions-boundaries-', dir=ROOT / '.tools'))
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    records = []
    print(out, flush=True)
    for name, source_bytes in CASES.items():
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_text(source_bytes)
        process = recorded([ROOT / 'bin/php-semantics', source, '--steps', '100000', '--timeout', '60'],
                           directory, 'model', environment, 75)
        actual = json.loads((directory / 'model.stdout').read_bytes())
        passed = (not process['timeout'] and process['exit'] == 1
                  and not (directory / 'model.stderr').read_bytes()
                  and actual.get('frontend') == 'accepted' and actual.get('checked') == 'program'
                  and actual.get('status') == 'unsupported' and actual.get('reason') == REASON
                  and actual.get('exit_status') is None)
        records.append({'id': name, 'process': process, 'observation': actual, 'passed': passed})
        print(name, passed, flush=True)
    passed = all(row['passed'] for row in records)
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'php_agreements': 0, 'records': records, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
