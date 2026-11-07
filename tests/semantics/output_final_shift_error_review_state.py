#!/usr/bin/env python3
"""Negative integer shifts retain authenticated ArithmeticError native cleanup."""
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
import output_final_shift_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
CASES = {'core': sources.LEFT, 'right': sources.RIGHT,
         'normal': sources.CASES['native-shift-normal'], 'catch': sources.CATCH,
         'override': sources.OVERRIDE, 'cleanup': sources.CLEANUP}
PREFIX = division.PREFIX.replace('DIVIDE', 'SHIFTLEFT')
PREFIX = PREFIX.replace('  -- if S.TODO = (BINARY_RIGHT SHIFTLEFT (KNOWN (PINT 1)) z) :: ptask_tail*',
    '  -- if S.TODO = (BINARY_RIGHT pbin (KNOWN (PINT 1)) z) :: ptask_tail*\n  -- if pbin = SHIFTLEFT \\/ pbin = SHIFTRIGHT')
PREFIX = PREFIX.replace('BINARY_RIGHT SHIFTLEFT poperand_left z', 'BINARY_RIGHT pbin poperand_left z').replace(
    '$binary_source_apply(S_right, SHIFTLEFT, poperand_left', '$binary_source_apply(S_right, pbin, poperand_left')
NORMAL_EXTRA = division.NORMAL_EXTRA.replace('NExprBinaryOpDiv ', 'NExprBinaryOpShiftLeft ')


def shift_text(text, operation):
    text = text.replace('DIVIDE', operation).replace('DivisionByZeroError', 'ArithmeticError')
    text = text.replace('OBJECT_DIVISION_ERROR', 'OBJECT_SHIFT_ERROR').replace(
        '$ob_object_division_error_', '$ob_object_shift_error_')
    text = text.replace('S.RESULT = KNOWN (PINT 0)', 'S.RESULT = KNOWN (PINT (-1))')
    def message(match):
        data = base64.b64decode(match[1]).replace(b'DivisionByZeroError', b'ArithmeticError').replace(b'Division by zero', b'Bit shift by negative number')
        return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'
    return re.sub(r'\$base64\("([A-Za-z0-9+/=]*)"\)', message, text)


def adapt(bindings, checks, operation='SHIFTLEFT'):
    return ([shift_text(binding, operation) for binding in bindings],
            [(label.replace('DivisionByZeroError', 'ArithmeticError').replace('division', 'shift'),
              shift_text(condition, operation)) for label, condition in checks])


def cross_bindings(opposite):
    return ['S_cross = S[.TODO = (BINARY_RIGHT ' + opposite + ' (KNOWN (PINT 1)) z) :: ptask_tail*]',
            'S_cross_request = $dz_request(S_cross, z)',
            'S_cross_generated = $throwable_transition(S_cross, S_cross_request)']


def cross_check(operation):
    return (r'$call_current_valid(S_cross) /\ $ob_object_final_native_method(S_cross) = (pobobjectreturn) /\ '
            r'$integer_operator_plan(S_cross) = eps /\ S_cross_request = S_request /\ S_cross_generated = S_generated /\ '
            '$ob_object_shift_operator(S_cross, porigin_operator) = (' + operation + r') /\ '
            r'$ob_object_shift_error_source(S_cross_generated, pfunction, pobreturnerror) /\ '
            r'$ob_object_return_error_live(S_cross_generated, pobreturnerror) /\ '
            r'$ob_object_shift_error_capture(S_cross, S_cross_generated) = eps')


def core(fixture, path):
    bindings, checks = adapt(*division.core(fixture, path))
    bindings += cross_bindings('SHIFTRIGHT') + [
        'pobobjectreturn_division = pobobjectreturn_capture[.SOURCE = (OBJECT_DIVISION_ERROR pobreturnerror)]',
        'S_division_tag = S_capture[.FRAMES = [pframe_capture[.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_division) :: ptask_native*]]]']
    checks[1] = (checks[1][0], checks[1][1] + r' /\ ' + cross_check('SHIFTLEFT') +
        r' /\ $ob_object_shift_error_capture(S[.TODO = (BINARY_RIGHT SHIFTLEFT (KNOWN (PFLOAT 4607182418800017408)) z) :: ptask_tail*], S_generated) = eps /\ '
        r'$ob_object_shift_error_capture(S[.RESULT = KNOWN (PFLOAT 13830554455654793216)], S_generated) = eps')
    checks[2] = (checks[2][0], checks[2][1] +
        r' /\ $ob_object_source_shift_error(pobobjectreturn_capture.SOURCE) = (pobreturnerror) /\ '
        r'$ob_object_source_division_error(pobobjectreturn_capture.SOURCE) = eps /\ $ob_object_final_saved_context(S_division_tag) = eps')
    return bindings, checks


def right(fixture, path):
    bindings, _ = adapt(division.start(fixture, path) + division.capture(), [], 'SHIFTRIGHT')
    bindings += cross_bindings('SHIFTLEFT') + [
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_zero = $drive_steps(S, 0)', 'S_pending_zero = $drive_steps(S_capture, 0)']
    checks = [
        ('actual RIGHT request and authenticated source', r'S.RESULT = KNOWN (PINT (-1)) /\ S.CVS = eps /\ S.ENV = eps /\ z = 6 /\ '
         r'$ob_object_shift_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         'S_request.COMPLETION = THROWN "ArithmeticError" ' + prior.value(b'Bit shift by negative number') + r' 6 /\ '
         r'$ob_object_shift_operator(S, porigin_operator) = (SHIFTRIGHT) /\ $ob_object_shift_error_source(S_generated, pfunction, pobreturnerror) /\ ' + prior.public('S')),
        ('same-message LEFT retarget refuses', cross_check('SHIFTRIGHT')),
        ('new fixed-kind metadata adds no owner', r'$ob_object_source_shift_error(pobobjectreturn_capture.SOURCE) = (pobreturnerror) /\ '
         r'$ob_object_source_generated_error(pobobjectreturn_capture.SOURCE) = (pobreturnerror) /\ '
         r'$ob_object_source_kind(pobobjectreturn_capture.SOURCE) = "ArithmeticError" /\ $ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$heap_graph(S_observed) = $heap_graph(S_generated) /\ S_observed.EVENTS = S_generated.EVENTS /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn)'),
        ('genuine RIGHT pending identity owners and budgets', r'$ob_object_final_saved_context(S_capture) = ((pcallcontext, pobobjectreturn_capture)) /\ '
         r'$output_final_cv_unwind(S_capture) /\ $ob_object_source_native_pending(pobobjectreturn_capture.SOURCE) = ((pobreturnerror.SITE, n_exception)) /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ '
         r'$throwable_field(S_capture, n_exception, "previous") = PNULL /\ S_zero = S[.COMPLETION = BUDGET] /\ '
         r'S_pending_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture'))]
    return bindings, checks


def normal(fixture, path):
    return adapt(*division.normal(fixture, path))


def catch(fixture, path):
    return adapt(*division.catch(fixture, path))


def override(fixture, path):
    return adapt(*division.override(fixture, path))


def cleanup(fixture, path):
    return adapt(*division.cleanup(fixture, path))


def fingerprint(fixture):
    result = division.fingerprint(fixture)
    for name in ('tests/semantics/output_final_shift_error_sources.py', 'tests/semantics/output_final_shift_error_review_state.py'):
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
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-shift-error-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'profile': prior.common.PROFILE, 'native_agreement_credit': 0, 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir(); source = CASES[name]
            if args.native_root and name in ('core', 'right', 'normal'):
                path = args.native_root / {'core': 'native-01', 'right': 'native-02', 'normal': 'native-03'}[name] / 'source.php'
                assert path.read_bytes() == source
            elif args.checked_root and name in ('normal', 'catch', 'override', 'cleanup'):
                path = args.checked_root / 'control-preparation-01' / name / 'source.php'
                assert path.read_bytes() == source
            else:
                path = directory / 'source.php'; path.write_bytes(source)
            if args.checked_root:
                cache = args.checked_root / ('left-baseline-01/checked.json' if name == 'core' else 'right-baseline-01/checked.json' if name == 'right' else f'control-preparation-01/{name}/checked.json')
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
