#!/usr/bin/env python3
"""Quiet negative-shift captures retain operands, source and string authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_quiet_shift_coercion_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
CASES = {'left': sources.LEFT, 'right': sources.RIGHT, 'noisy': sources.NOISY}
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
MESSAGE = 'Bit shift by negative number'


def authority(name, fixture, path):
    operator = 'SHIFTLEFT' if name == 'left' else 'SHIFTRIGHT'
    other = 'SHIFTRIGHT' if name == 'left' else 'SHIFTLEFT'
    bindings = division.start(fixture, path) + [
        f'S.TODO = (BINARY_RIGHT {operator} poperand_left z) :: ptask_tail*',
        'S.RESULT = poperand_right', 'S.ORIGIN = (porigin_operator)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right)',
        'S_inputs = $hold_task_inputs(S)',
        'S_left = $resolve_at(S_inputs, poperand_left, z)',
        'S_right = $resolve_at(S_left, poperand_right, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        f'pobreturnerror = {{SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("{MESSAGE}"), LINE z}}',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'pvalue_bad_left = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.0"))',
        'pvalue_bad_right = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("-1"))',
        f'S_bad_left = S[.TODO = (BINARY_RIGHT {operator} (KNOWN pvalue_bad_left) z) :: ptask_tail*]',
        'S_bad_right = S[.RESULT = KNOWN pvalue_bad_right]',
        'S_bad_left_generated = $throwable_transition(S_bad_left, $dz_raw(S_bad_left))',
        'S_bad_right_generated = $throwable_transition(S_bad_right, $dz_raw(S_bad_right))',
        'S_good_right = S_bad_right[.STRINGDATA = S.STRINGDATA ++ [$ptascii("-1")]]',
        'S_good_right_generated = $throwable_transition(S_good_right, $dz_raw(S_good_right))',
        f'S_plain_left = S[.TODO = (BINARY_RIGHT {operator} (KNOWN (PSTRING ($ptascii("1")))) z) :: ptask_tail*]',
        f'S_float_left = S[.TODO = (BINARY_RIGHT {operator} (KNOWN (PFLOAT 4607182418800017408)) z) :: ptask_tail*]',
        'S_float_right = S[.RESULT = KNOWN (PFLOAT 13830554455654793216)]',
        f'S_other = S[.TODO = (BINARY_RIGHT {other} poperand_left z) :: ptask_tail*]',
        'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))',
        'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]']
    values = (r'pvalue_left = PNULL /\ $string_bytes(pvalue_right) = ($ptascii("-1"))'
              if name == 'left' else
              r'$string_bytes(pvalue_left) = ($ptascii("1.0")) /\ $string_carrier_valid(S, pvalue_left) /\ pvalue_right = PFLOAT 13830554455654793216')
    checks = [
        ('real ordered reads preserve originals before RHS integer scratch',
         values + r' /\ S_left = S_inputs[.RESULT = KNOWN pvalue_left] /\ S_right = S_left[.RESULT = KNOWN pvalue_right] /\ '
         r'S_request.RESULT = KNOWN (PINT (-1)) /\ S_request.RESULT =/= S_right.RESULT /\ '
         r'S_request.TODO = ptask_tail* /\ S_request.HELD = S.HELD /\ S_request.EVENTS = S.EVENTS /\ '
         f'S_request.COMPLETION = THROWN "ArithmeticError" ($ptascii("{MESSAGE}")) z'),
        ('genuine shift capture retains source and native owners',
         r'$ob_object_shift_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$ob_object_shift_error_source(S_generated, pfunction, pobreturnerror) /\ '
         r'~$ob_object_shift_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
         r'pobobjectreturn_capture.SOURCE = (OBJECT_SHIFT_ERROR pobreturnerror) /\ '
         r'S_observed = $ob_object_final_capture(S_generated, pobobjectreturn, $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_SHIFT_ERROR pobreturnerror))) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture')),
        ('coherent KNOWN carriers still need both original string identities',
         r'$ob_object_modulo_integer(pvalue_bad_left) = (1) /\ $ob_object_modulo_integer(pvalue_bad_right) = ((-1)) /\ '
         r'$ob_object_error_operand_value(S_bad_left, KNOWN pvalue_bad_left, [PCFIELD 0], z) = (pvalue_bad_left) /\ '
         r'$ob_object_error_operand_value(S_bad_right, KNOWN pvalue_bad_right, [PCFIELD 1], z) = (pvalue_bad_right) /\ '
         r'~$string_carrier_valid(S_bad_left, pvalue_bad_left) /\ ~$string_carrier_valid(S_bad_right, pvalue_bad_right) /\ '
         r'$call_current_valid(S_bad_left) /\ $call_current_valid(S_bad_right) /\ '
         r'S_bad_left_generated = S_generated /\ S_bad_right_generated = S_generated /\ '
         r'$ob_object_shift_error_capture(S_bad_left, S_bad_left_generated) = eps /\ '
         r'$ob_object_shift_error_capture(S_bad_right, S_bad_right_generated) = eps'),
        ('a real rootless request carrier grants the existing capture',
         r'$string_carrier_valid(S_good_right, pvalue_bad_right) /\ $value_nodes(pvalue_bad_right) = eps /\ '
         r'S_good_right_generated.COMPLETION = THROWING n_exception /\ '
         r'$ob_object_shift_error_capture(S_good_right, S_good_right_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('earned legacy string and exact-float promotions use equal raw152 successors',
         r'$throwable_transition(S_plain_left, $dz_raw(S_plain_left)) = S_generated /\ '
         r'$throwable_transition(S_float_left, $dz_raw(S_float_left)) = S_generated /\ '
         r'$throwable_transition(S_float_right, $dz_raw(S_float_right)) = S_generated /\ '
         r'$ob_object_shift_error_capture(S_plain_left, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$ob_object_shift_error_capture(S_float_left, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$ob_object_shift_error_capture(S_float_right, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('equal opposite-opcode materialization cannot grant own-source capture',
         r'$call_current_valid(S_other) /\ S_other_generated = S_generated /\ '
         f'$ob_object_shift_operator(S_other, porigin_operator) = ({operator}) /\\ '
         r'$ob_object_shift_error_source(S_other_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_shift_error_capture(S_other, S_other_generated) = eps /\ '
         r'$ob_object_shift_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ '
         r'$ob_object_shift_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps')]
    return bindings, checks


def noisy(fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT SHIFTLEFT poperand_left z) :: ptask_tail*',
        'S.ORIGIN = (porigin_operator)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_two = S[.TODO = (BINARY_RIGHT SHIFTLEFT (KNOWN (PSTRING ($ptascii("1.5")))) z) :: ptask_tail*][.RESULT = KNOWN (PSTRING ($ptascii("-1.5")))]',
        'S_two_request = $dz_raw(S_two)',
        'S_two_generated = $throwable_transition(S_two, S_two_request)',
        'pevent_left = $event_source(S_two, DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float-string \\"1.5\\" to int loses precision")) z)',
        'pevent_right = $event_source(S_two, DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float-string \\"-1.5\\" to int loses precision")) z)']
    checks = [
        ('actual fractional count converts to negative integer with its diagnostic',
         r'pvalue_left = PNULL /\ $string_bytes(pvalue_right) = ($ptascii("-1.5")) /\ '
         r'$string_long($ptascii("-1.5")) = STRINT (-1) (STRINGPRECISIONLOSS :: eps) /\ '
         r'$ob_object_modulo_integer(pvalue_right) = eps /\ S_request.RESULT = KNOWN (PINT (-1)) /\ '
         r'S_request.EVENTS = S.EVENTS ++ [pevent_right] /\ '
         f'S_request.COMPLETION = THROWN "ArithmeticError" ($ptascii("{MESSAGE}")) z'),
        ('noisy source keeps its real error without FINAL capture',
         r'$ob_object_shift_error_capture(S, S_generated) = eps /\ S_observed = S_generated'),
        ('derived two-noisy operands report left then right before negative-shift error',
         r'pevent_left =/= pevent_right /\ S_two_request.EVENTS = S.EVENTS ++ [pevent_left, pevent_right] /\ '
         r'S_two_request.RESULT = KNOWN (PINT (-1)) /\ '
         f'S_two_request.COMPLETION = THROWN "ArithmeticError" ($ptascii("{MESSAGE}")) z /\\ '
         r'S_two_generated.COMPLETION = THROWING n_exception /\ '
         r'$ob_object_shift_error_capture(S_two, S_two_generated) = eps /\ '
         r'$source_exception_transition(S_two, S_two_generated) = S_two_generated')]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-quiet-shift-coercion-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    head = lambda: subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip()
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [ROOT / rel for rel in modules + ['spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_quiet_shift_coercion_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py',
        'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py']] + [Path(__file__)]
    fingerprint = lambda: {str(item): prior.common.sha(item) for item in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(CASES[name]).decode()})
            finally:
                frontend.close()
            assert parsed['accepted'], parsed
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            cache = directory / 'checked.json'; cache.write_text(json.dumps(checked) + '\n')
            bindings, checks = noisy(checked['fixture'], path) if name == 'noisy' else authority(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + binding + '\n' for binding in bindings))
            watched += [path, fixture, cache]
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'source_sha256': hashlib.sha256(CASES[name]).hexdigest(),
                      'fixture_sha256': prior.common.sha(fixture), 'before': fingerprint(), 'passed': False}
            report['records'].append(record)
            started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
                assert result.returncode == 0 and not result.stderr, (result.returncode, result.stderr)
                record['observed'] = json.loads(result.stdout)
                assert record['observed'] == [True] * len(checks), record['observed']
            except subprocess.TimeoutExpired as error:
                (directory / 'state.stdout').write_bytes(error.stdout or b'')
                (directory / 'state.stderr').write_bytes(error.stderr or b'')
                (directory / 'state.exit').write_text('timeout\n')
                raise
            finally:
                record.update(seconds=time.monotonic() - started, after=fingerprint())
            assert record['before'] == record['after'], 'watched inputs changed'
            assert report['revision'] == head(), 'revision changed'
            record['passed'] = True
        report['passed'] = all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
