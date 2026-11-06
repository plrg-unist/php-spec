#!/usr/bin/env python3
"""Weak return rejection uses the real return decision rather than a strict flag."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_final_empty_return_review_state as base
import output_final_weak_return_sources as sources

prior = base.prior
ROOT = Path(__file__).resolve().parents[2]
MESSAGE = b'T::__toString(): Return value must be of type string, null returned'
CASES = {'core': sources.WEAK, 'weak': sources.CASES['weak-bool-return-coercion'],
         'catch': sources.CATCH, 'override': sources.OVERRIDE}
PREFIX = base.PREFIX.replace('  -- if S.RESULT = KNOWN (PINT 42)',
                            '  -- if S.RESULT = KNOWN pvalue\n' +
                            r'  -- if pvalue = PNULL \/ pvalue = PBOOL true')


def core(fixture, path):
    bindings, checks = base.core(fixture, path)
    old_fatal = (b'Fatal error: Uncaught TypeError: ' + prior.MESSAGE + b' in ' + os.fsencode(path) +
                 b':6\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' +
                 os.fsencode(path) + b' on line 6\n')
    checks = [(label, condition.replace(prior.value(prior.MESSAGE), prior.value(MESSAGE)).replace(
        prior.value(old_fatal), prior.value(old_fatal.replace(prior.MESSAGE, MESSAGE))))
              for label, condition in checks]
    label, condition = checks[0]
    checks[0] = ('genuine weak rejection rather than strict-mode mint', condition +
                 r' /\ ~pfunction.CODE.STRICT /\ S.RESULT = KNOWN PNULL /\ $typed_reference_conversion(S, pfunction.SIGNATURE.RETURNS, PNULL, false, false) = TYPEREJECT')
    return bindings, checks


def control(name, fixture, path):
    bindings, checks = base.control(name, fixture, path)
    if name == 'weak':
        checks = [(label.replace('weak scalar', 'weak TRUE'),
                   condition.replace('$ptascii("42")', '$ptascii("1")'))
                  for label, condition in checks]
        label, condition = checks[0]
        checks[0] = (label, condition + r' /\ S.RESULT = KNOWN (PBOOL true) /\ S_value.COMPLETION = NORMAL /\ $ob_object_return_error_capture(S, S_value) = eps')
    return bindings, checks


def fingerprint(fixture):
    values = base.fingerprint(fixture)
    for name in ('tests/semantics/output_final_weak_return_sources.py',
                 'tests/semantics/output_final_weak_return_review_state.py'):
        values[name] = prior.common.sha(ROOT / name)
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--checked-root', type=Path)
    parser.add_argument('--native-root', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-weak-return-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'profile': prior.common.PROFILE, 'native_agreement_credit': 0, 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir(); source = CASES[name]
            if args.native_root and name in ('core', 'weak'):
                path = args.native_root / ('native-01' if name == 'core' else 'native-02') / 'source.php'
                assert path.read_bytes() == source
            elif args.checked_root and name != 'core':
                path = args.checked_root / 'control-preparation-01' / name / 'source.php'; assert path.read_bytes() == source
            else:
                path = directory / 'source.php'; path.write_bytes(source)
            if args.checked_root:
                cache = args.checked_root / ('baseline-01/checked.json' if name == 'core' else f'control-preparation-01/{name}/checked.json')
                checked = json.loads(cache.read_text())
            else:
                frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': prior.common.base64.b64encode(source).decode()})
                finally:
                    frontend.close()
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                finally:
                    adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            bindings, checks = core(checked['fixture'], path) if name == 'core' else control(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + b + '\n' for b in bindings))
            record = {'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(), 'fixture_sha256': prior.common.sha(fixture), 'groups': [label for label, _ in checks], 'before': fingerprint(fixture), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, application_credit=0); continue
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text()); started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            finally:
                record['seconds'] = round(time.monotonic() - started, 3); record['after'] = fingerprint(fixture)
            record['observed'] = [value == b'true' for value in re.findall(rb'true|false', result.stdout)]
            assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
            assert record['before'] == record['after'], 'watched inputs changed'
            record['passed'] = True
        assert report['records'], 'no fixture selected'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
        report['prepared'] = args.prepare_only
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}; raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n'); print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
