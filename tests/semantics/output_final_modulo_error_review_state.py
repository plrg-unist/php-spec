#!/usr/bin/env python3
"""Integer modulo errors retain actual native source, owners and clearing."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_modulo_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
CASES = {'core': sources.MODULO, 'normal': sources.CASES['native-modulo-normal'],
         'catch': sources.CATCH, 'override': sources.OVERRIDE, 'cleanup': sources.CLEANUP}
PREFIX = division.PREFIX.replace('DIVIDE', 'MODULO')
PREFIX = PREFIX.replace('BINARY_RIGHT MODULO poperand_left z', 'BINARY_RIGHT pbin poperand_left z').replace(
    '$binary_source_apply(S_right, MODULO, poperand_left', '$binary_source_apply(S_right, pbin, poperand_left')
NORMAL_EXTRA = division.NORMAL_EXTRA.replace('NExprBinaryOpDiv ', 'NExprBinaryOpMod ')


def modulo_text(text):
    """Reuse the same lifecycle assertions for the new operator and message."""
    text = text.replace('DIVIDE', 'MODULO')
    def message(match):
        data = base64.b64decode(match[1]).replace(b'Division by zero', b'Modulo by zero')
        return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'
    return re.sub(r'\$base64\("([A-Za-z0-9+/=]*)"\)', message, text)


def adapt(bindings, checks):
    return ([modulo_text(binding) for binding in bindings],
            [(label.replace('division', 'modulo'), modulo_text(condition)) for label, condition in checks])


def core(fixture, path):
    bindings, checks = adapt(*division.core(fixture, path))
    bindings += ['S_cross = S[.TODO = (BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z) :: ptask_tail*]',
                 'S_cross_request = $dz_request(S_cross, z)',
                 'S_cross_generated = $throwable_transition(S_cross, S_cross_request)',
                 'pobreturnerror_cross = {SITE porigin_operator, OBJECT n_exception, MESSAGE ' + prior.value(b'Division by zero') + ', LINE z}']
    checks[1] = (checks[1][0], checks[1][1] +
        r' /\ $ob_object_division_operator(S, porigin_operator) = (MODULO) /\ '
        r'$ob_object_division_operands(MODULO, PINT 1, PINT 0) /\ '
        r'~$ob_object_division_operands(MODULO, PFLOAT 4607182418800017408, PINT 0) /\ '
        r'~$ob_object_division_operands(MODULO, PINT 1, PFLOAT 0) /\ '
        r'$ob_object_division_operands(DIVIDE, PFLOAT 4607182418800017408, PINT 0) /\ '
        r'$call_current_valid(S_cross) /\ $ob_object_final_native_method(S_cross) = (pobobjectreturn) /\ '
        r'$integer_operator_plan(S_cross) = eps /\ $arithmetic_div_plan(S_cross) = eps /\ $arithmetic_div_repair_plan(S_cross) = eps /\ '
        r'S_cross_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) z /\ S_cross_request.TODO = ptask_tail* /\ '
        r'S_cross_generated.COMPLETION = THROWING n_exception /\ '
        r'$ob_object_division_operator(S_cross, porigin_operator) = (MODULO) /\ '
        r'$ob_object_division_error_source(S_cross_generated, pfunction, pobreturnerror_cross) /\ '
        r'$ob_object_return_error_live(S_cross_generated, pobreturnerror_cross) /\ '
        r'$ob_object_division_error_capture(S_cross, S_cross_generated) = eps')
    return bindings, checks


def normal(fixture, path):
    bindings, checks = adapt(*division.normal(fixture, path))
    checks = [(label.replace('publishes1', 'publishes0'), condition.replace('KNOWN (PINT 1)', 'KNOWN (PINT 0)').replace('$ptascii("1")', '$ptascii("0")')) for label, condition in checks]
    return bindings, checks


def catch(fixture, path):
    return adapt(*division.catch(fixture, path))


def override(fixture, path):
    return adapt(*division.override(fixture, path))


def cleanup(fixture, path):
    return adapt(*division.cleanup(fixture, path))


def fingerprint(fixture):
    result = division.fingerprint(fixture)
    for name in ('tests/semantics/output_final_modulo_error_sources.py',
                 'tests/semantics/output_final_modulo_error_review_state.py'):
        result[name] = prior.common.sha(ROOT / name)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--checked-root', type=Path)
    parser.add_argument('--native-root', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-modulo-error-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'profile': prior.common.PROFILE, 'native_agreement_credit': 0, 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir(); source = CASES[name]
            if args.native_root and name in ('core', 'normal'):
                path = args.native_root / ('native-01' if name == 'core' else 'native-02') / 'source.php'
                assert path.read_bytes() == source
            elif args.checked_root and name != 'core':
                path = args.checked_root / 'control-preparation-01' / name / 'source.php'
                assert path.read_bytes() == source
            else:
                path = directory / 'source.php'; path.write_bytes(source)
            if args.checked_root:
                cache = args.checked_root / ('baseline-02/checked.json' if name == 'core' else f'control-preparation-01/{name}/checked.json')
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
            bindings, checks = globals()[name](checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + (NORMAL_EXTRA if name == 'normal' else '') + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + binding + '\n' for binding in bindings))
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
