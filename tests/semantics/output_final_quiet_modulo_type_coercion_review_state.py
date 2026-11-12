#!/usr/bin/env python3
"""Quiet modulo TypeErrors retain original types and both string authorities."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_quiet_modulo_type_coercion_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
CASES = {'null': sources.NULL, 'string': sources.STRING, 'noisy': sources.NOISY}
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')


def authority(name, fixture, path):
    message = 'Unsupported operand types: ' + ('null' if name == 'null' else 'string') + ' % string'
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*',
        'S.RESULT = poperand_right', 'S.ORIGIN = (porigin_operator)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right)',
        'S_inputs = $hold_task_inputs(S)',
        'S_left = $resolve_at(S_inputs, poperand_left, z)',
        'S_right = $resolve_at(S_left, poperand_right, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        f'pobreturnerror = {{SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("{message}"), LINE z}}',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'pvalue_bad_right = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("X"))',
        'S_bad_right = S[.RESULT = KNOWN pvalue_bad_right]',
        'S_bad_right_generated = $throwable_transition(S_bad_right, $dz_raw(S_bad_right))',
        'S_good_right = S_bad_right[.STRINGDATA = S.STRINGDATA ++ [$ptascii("X")]]',
        'S_good_right_generated = $throwable_transition(S_good_right, $dz_raw(S_good_right))',
        'S_other = S[.TODO = (BINARY_RIGHT DIVIDE poperand_left z) :: ptask_tail*]',
        'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))',
        'S_pint = S_bad_right[.TODO = (BINARY_RIGHT MODULO (KNOWN (PINT 1)) z) :: ptask_tail*]',
        'S_pint_generated = $throwable_transition(S_pint, $dz_raw(S_pint))',
        'pobreturnerror_pint = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Unsupported operand types: int % string"), LINE z}',
        'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]']
    original = (r'pvalue_left = PNULL /\ S_request.RESULT = KNOWN (PINT 0)'
                if name == 'null' else
                r'$string_bytes(pvalue_left) = ($ptascii("1.0")) /\ $ob_object_string_value(S, pvalue_left) /\ S_request.RESULT = KNOWN (PINT 1)')
    checks = [
        ('ordered reads and left integer scratch retain original TypeError names',
         original + r' /\ $string_bytes(pvalue_right) = ($ptascii("X")) /\ '
         r'S_left = S_inputs[.RESULT = KNOWN pvalue_left] /\ S_right = S_left[.RESULT = KNOWN pvalue_right] /\ '
         r'S_request.RESULT =/= S_right.RESULT /\ S_request.TODO = ptask_tail* /\ S_request.HELD = S.HELD /\ '
         f'S_request.COMPLETION = THROWN "TypeError" ($ptascii("{message}")) z /\\ '
         r'S_request.EVENTS = S.EVENTS /\ z = 7'),
        ('real54 and exact152 retain source authority and existing native owners',
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
         r'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror) /\ '
         r'S_observed = $ob_object_final_capture(S_generated, pobobjectreturn, $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror))) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture')),
        ('coherent rootless KNOWN bad right still needs its real string identity',
         r'$ob_object_error_operand_value(S_bad_right, KNOWN pvalue_bad_right, [PCFIELD 1], z) = (pvalue_bad_right) /\ '
         r'$coerce_number(pvalue_bad_right) = BADNUMBER /\ $value_nodes(pvalue_bad_right) = eps /\ '
         r'~$string_carrier_valid(S_bad_right, pvalue_bad_right) /\ $call_current_valid(S_bad_right) /\ '
         r'S_bad_right_generated = S_generated /\ $ob_object_arithmetic_type_error_capture(S_bad_right, S_bad_right_generated) = eps'),
        ('valid rootless request carrier grants the same original-type capture',
         r'$string_carrier_valid(S_good_right, pvalue_bad_right) /\ '
         r'S_good_right_generated.COMPLETION = THROWING n_exception /\ '
         r'$ob_object_arithmetic_type_error_capture(S_good_right, S_good_right_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('old PINT arm keeps its unfiltered KNOWN right authority pointwise',
         r'~$string_carrier_valid(S_pint, pvalue_bad_right) /\ $call_current_valid(S_pint) /\ '
         r'S_pint_generated.COMPLETION = THROWING n_exception /\ '
         r'$ob_object_return_error_live(S_pint_generated, pobreturnerror_pint) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_pint, S_pint_generated) = ((pobobjectreturn, pobreturnerror_pint))'),
        ('opcode own-line source and exact successor remain required',
         r'$call_current_valid(S_other) /\ S_other_generated.COMPLETION = THROWING n_exception /\ '
         r'$ob_object_arithmetic_type_operator(S_other, porigin_operator) = (MODULO) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_other, S_other_generated) = eps /\ '
         r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
         r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps')]
    if name == 'string':
        bindings += [
            'pvalue_bad_left = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.0"))',
            'S_bad_left = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_bad_left) z) :: ptask_tail*]',
            'S_bad_left_generated = $throwable_transition(S_bad_left, $dz_raw(S_bad_left))',
            'S_plain = S[.TODO = (BINARY_RIGHT MODULO (KNOWN (PSTRING ($ptascii("1")))) z) :: ptask_tail*]',
            'S_plain_generated = $throwable_transition(S_plain, $dz_raw(S_plain))',
            'S_true = S[.TODO = (BINARY_RIGHT MODULO (KNOWN (PBOOL true)) z) :: ptask_tail*]',
            'S_true_request = $dz_raw(S_true)',
            'S_true_generated = $throwable_transition(S_true, S_true_request)',
            'pobreturnerror_true = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Unsupported operand types: bool % string"), LINE z}',
            'S_float = S[.TODO = (BINARY_RIGHT MODULO (KNOWN (PFLOAT 4607182418800017408)) z) :: ptask_tail*]',
            'S_float_request = $dz_raw(S_float)',
            'S_float_generated = $throwable_transition(S_float, S_float_request)',
            'pobreturnerror_float = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Unsupported operand types: float % string"), LINE z}']
        checks += [
            ('quiet conversion and equal raw152 cannot authenticate a forged left string',
             r'$ob_object_modulo_integer(pvalue_bad_left) = (1) /\ $value_nodes(pvalue_bad_left) = eps /\ '
             r'$ob_object_error_operand_value(S_bad_left, KNOWN pvalue_bad_left, [PCFIELD 0], z) = (pvalue_bad_left) /\ '
             r'~$string_carrier_valid(S_bad_left, pvalue_bad_left) /\ $call_current_valid(S_bad_left) /\ '
             r'S_bad_left_generated = S_generated /\ $ob_object_arithmetic_type_error_capture(S_bad_left, S_bad_left_generated) = eps'),
            ('affected legacy plain-string guard earns its own exact capture',
             r'S_plain_generated = S_generated /\ '
             r'$ob_object_arithmetic_type_error_capture(S_plain, S_plain_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('quiet bool and exact-float conversions preserve their own original type names',
             r'S_true_request.RESULT = KNOWN (PINT 1) /\ S_float_request.RESULT = KNOWN (PINT 1) /\ '
             r'S_true_request.EVENTS = S.EVENTS /\ S_float_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_return_error_live(S_true_generated, pobreturnerror_true) /\ '
             r'$ob_object_return_error_live(S_float_generated, pobreturnerror_float) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_true, S_true_generated) = ((pobobjectreturn, pobreturnerror_true)) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_float, S_float_generated) = ((pobobjectreturn, pobreturnerror_float))')]
    return bindings, checks


def noisy(fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*',
        'S.ORIGIN = (porigin_operator)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pevent_lossy = $event_source(S, DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float-string \\"1.5\\" to int loses precision")) z)',
        'S_leading = S[.TODO = (BINARY_RIGHT MODULO (KNOWN (PSTRING ($ptascii("1x")))) z) :: ptask_tail*]',
        'S_leading_request = $dz_raw(S_leading)',
        'S_leading_generated = $throwable_transition(S_leading, S_leading_request)',
        'pevent_leading = $event_source(S_leading, DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) z)']
    checks = [
        ('left fractional conversion reports before the original string TypeError',
         r'$string_bytes(pvalue_left) = ($ptascii("1.5")) /\ $ob_object_string_value(S, pvalue_left) /\ '
         r'$string_long($ptascii("1.5")) = STRINT 1 (STRINGPRECISIONLOSS :: eps) /\ '
         r'S_request.RESULT = KNOWN (PINT 1) /\ S_request.EVENTS = S.EVENTS ++ [pevent_lossy] /\ '
         r'S_request.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: string % string")) z'),
        ('leading numeric string reports before the same right-string failure',
         r'S_leading_request.RESULT = KNOWN (PINT 1) /\ S_leading_request.EVENTS = S.EVENTS ++ [pevent_leading] /\ '
         r'S_leading_request.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: string % string")) z /\ '
         r'S_leading_generated.COMPLETION = THROWING n_exception'),
        ('neither noisy original earns a FINAL capture',
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = eps /\ '
         r'$source_exception_transition(S, S_generated) = S_generated /\ '
         r'$ob_object_arithmetic_type_error_capture(S_leading, S_leading_generated) = eps /\ '
         r'$source_exception_transition(S_leading, S_leading_generated) = S_leading_generated')]
    return bindings, checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / name for name in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_quiet_modulo_type_coercion_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py']] + [Path(__file__)]
    fingerprint = lambda: {str(item): prior.common.sha(item) for item in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False, 'before': fingerprint()}
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
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            inputs = {str(item): prior.common.sha(item) for item in [path, cache, fixture]}
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'source_sha256': hashlib.sha256(CASES[name]).hexdigest(),
                      'inputs_before': inputs, 'passed': False}
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
                record.update(seconds=time.monotonic() - started,
                              inputs_after={str(item): prior.common.sha(item) for item in [path, cache, fixture]})
            assert record['inputs_before'] == record['inputs_after'], 'fixture inputs changed'
            record['passed'] = True
        report['after'] = fingerprint()
        assert report['before'] == report['after'], 'watched inputs changed'
        assert report['revision'] == head(), 'revision changed'
        report['passed'] = all(record['passed'] for record in report['records'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if 'after' not in report:
            report['after'] = fingerprint()
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
