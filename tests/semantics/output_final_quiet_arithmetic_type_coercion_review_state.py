#!/usr/bin/env python3
"""Quiet arithmetic rejection keeps original operands and native slot authority."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_quiet_arithmetic_type_coercion_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
MULTIPLY_ORDER = sources.MULTIPLY.replace(b'$a = 1.5', b"$a = 'X'").replace(
    b"$a * 'X'", b'1.5 * $a')
CASES = {'add': sources.ADD, 'subtract': sources.SUBTRACT,
         'multiply': sources.MULTIPLY, 'divide': sources.DIVIDE,
         'multiply-order': MULTIPLY_ORDER, 'normal': sources.NORMAL,
         'noisy': sources.NOISY, 'reference': sources.REFERENCE}
OPERATORS = {'add': ('ADD', '+', 'string'), 'subtract': ('SUBTRACT', '-', 'null'),
             'multiply': ('MULTIPLY', '*', 'float'), 'divide': ('DIVIDE', '/', 'bool')}


def inputs(fixture, path):
    return division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT pbin poperand_left z) :: ptask_tail*',
        'S.RESULT = poperand_right', 'S.ORIGIN = (porigin_operator)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right)',
        'S_inputs = $hold_task_inputs(S)',
        'S_left = $resolve_at(S_inputs, poperand_left, z)',
        'S_right = $resolve_at(S_left, poperand_right, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)']


def authority(name, fixture, path):
    ordered = name == 'multiply-order'
    operator, symbol, kind = OPERATORS['multiply' if ordered else name]
    message = ('Unsupported operand types: string * float' if ordered else
               f'Unsupported operand types: {kind} {symbol} string')
    bindings = inputs(fixture, path) + [
        'S_generated.COMPLETION = THROWING n_exception',
        '$coerce_number(pvalue_left) = COERCED pnumber_left false',
        f'pobreturnerror = {{SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("{message}"), LINE z}}',
        'S_observed = $source_exception_transition(S, S_generated)',
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*']
    original = {
        'add': r'$string_bytes(pvalue_left) = ($ptascii("1.5")) /\ $ob_object_string_value(S, pvalue_left)',
        'subtract': 'pvalue_left = PNULL',
        'multiply': 'pvalue_left = PFLOAT 4609434218613702656',
        'divide': 'pvalue_left = PBOOL true',
        'multiply-order': 'pvalue_left = PFLOAT 4609434218613702656'}[name]
    checks = [
        ('ordered reads keep RHS scratch and original TypeError names',
         original + f' /\\ pbin = {operator} /\\ ' +
         r'$coerce_number(pvalue_left) = COERCED pnumber_left false /\ '
         r'$string_bytes(pvalue_right) = ($ptascii("X")) /\ $coerce_number(pvalue_right) = BADNUMBER /\ '
         r'S_left = S_inputs[.RESULT = KNOWN pvalue_left] /\ S_right = S_left[.RESULT = KNOWN pvalue_right] /\ '
         r'S_request.RESULT = S_right.RESULT /\ S_request.TODO = ptask_tail* /\ S_request.HELD = S.HELD /\ '
         f'S_request.COMPLETION = THROWN "TypeError" ($ptascii("{message}")) z /\\ '
         r'S_request.EVENTS = S.EVENTS /\ z = 7'),
        ('exact152 source capture retains real native owners without new roots',
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
         r'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror) /\ '
         r'S_observed = $ob_object_final_capture(S_generated, pobobjectreturn, $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror))) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture'))]
    if name in ('add', 'subtract', 'divide'):
        bindings += [
            f'S_plain = S[.TODO = (BINARY_RIGHT {operator} (KNOWN (PSTRING ($ptascii("1")))) z) :: ptask_tail*]',
            'S_plain_generated = $throwable_transition(S_plain, $dz_raw(S_plain))',
            f'pobreturnerror_plain = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string {symbol} string")]']
        checks.append(('affected legacy plain-string expectation has its own coherent successor',
                       r'S_plain_generated.COMPLETION = THROWING n_exception /\ '
                       r'$ob_object_arithmetic_type_error_source(S_plain_generated, pfunction, pobreturnerror_plain) /\ '
                       r'$ob_object_return_error_live(S_plain_generated, pobreturnerror_plain) /\ '
                       r'$ob_object_arithmetic_type_error_capture(S_plain, S_plain_generated) = ((pobobjectreturn, pobreturnerror_plain))'))
    if name == 'add':
        bindings += [
            'pvalue_bad_right = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("X"))',
            'S_bad_right = S[.RESULT = KNOWN pvalue_bad_right]',
            'S_bad_right_generated = $throwable_transition(S_bad_right, $dz_raw(S_bad_right))',
            'S_good_right = S_bad_right[.STRINGDATA = S.STRINGDATA ++ [$ptascii("X")]]',
            'S_good_right_generated = $throwable_transition(S_good_right, $dz_raw(S_good_right))',
            'S_pint = S_bad_right[.TODO = (BINARY_RIGHT ADD (KNOWN (PINT 1)) z) :: ptask_tail*]',
            'S_pint_generated = $throwable_transition(S_pint, $dz_raw(S_pint))',
            'pobreturnerror_pint = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: int + string")]',
            'pvalue_bad_left = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5"))',
            'S_bad_left = S[.TODO = (BINARY_RIGHT ADD (KNOWN pvalue_bad_left) z) :: ptask_tail*]',
            'S_bad_left_generated = $throwable_transition(S_bad_left, $dz_raw(S_bad_left))',
            'S_good_left = S_bad_left[.STRINGDATA = S.STRINGDATA ++ [$ptascii("1.5")]]',
            'S_good_left_generated = $throwable_transition(S_good_left, $dz_raw(S_good_left))']
        checks += [
            ('new right-string identity guard preserves the old PINT arm pointwise',
             r'$ob_object_error_operand_value(S_bad_right, KNOWN pvalue_bad_right, [PCFIELD 1], z) = (pvalue_bad_right) /\ '
             r'$coerce_number(pvalue_bad_right) = BADNUMBER /\ $value_nodes(pvalue_bad_right) = eps /\ '
             r'~$string_carrier_valid(S_bad_right, pvalue_bad_right) /\ $call_current_valid(S_bad_right) /\ '
             r'S_bad_right_generated.COMPLETION = THROWING n_exception /\ '
             r'$ob_object_arithmetic_type_error_capture(S_bad_right, S_bad_right_generated) = eps /\ '
             r'$string_carrier_valid(S_good_right, pvalue_bad_right) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_good_right, S_good_right_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
             r'~$string_carrier_valid(S_pint, pvalue_bad_right) /\ $call_current_valid(S_pint) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_pint, S_pint_generated) = ((pobobjectreturn, pobreturnerror_pint))'),
            ('quiet numeric bytes and equal raw152 cannot forge left string identity',
             r'$coerce_number(pvalue_bad_left) = COERCED (NFLOAT 4609434218613702656) false /\ '
             r'$value_nodes(pvalue_bad_left) = eps /\ '
             r'$ob_object_error_operand_value(S_bad_left, KNOWN pvalue_bad_left, [PCFIELD 0], z) = (pvalue_bad_left) /\ '
             r'~$string_carrier_valid(S_bad_left, pvalue_bad_left) /\ $call_current_valid(S_bad_left) /\ '
             r'S_bad_left_generated = S_generated /\ '
             r'$ob_object_arithmetic_type_error_capture(S_bad_left, S_bad_left_generated) = eps /\ '
             r'$string_carrier_valid(S_good_left, pvalue_bad_left) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_good_left, S_good_left_generated) = ((pobobjectreturn, pobreturnerror))')]
    if name == 'subtract':
        bindings += [
            'S_other = S[.TODO = (BINARY_RIGHT ADD poperand_left z) :: ptask_tail*]',
            'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))',
            'pobreturnerror_other = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: null + string")]',
            'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
            'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]']
        checks.append(('coherent opcode line source and exact successor remain required',
                       r'$call_current_valid(S_other) /\ S_other_generated.COMPLETION = THROWING n_exception /\ '
                       r'$ob_object_arithmetic_type_error_source(S_other_generated, pfunction, pobreturnerror_other) /\ '
                       r'$ob_object_return_error_live(S_other_generated, pobreturnerror_other) /\ '
                       r'$ob_object_arithmetic_type_operator(S_other, porigin_operator) = (SUBTRACT) /\ '
                       r'$ob_object_arithmetic_type_error_capture(S_other, S_other_generated) = eps /\ '
                       r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
                       r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
                       r'$ob_object_arithmetic_type_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ '
                       r'$ob_object_arithmetic_type_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps'))
    if ordered:
        bindings += [
            'S_ast_request = $binary_apply(S_right, MULTIPLY, pvalue_left, pvalue_right, z)[.HELD = S.HELD]',
            'S_ast_generated = $throwable_transition(S, S_ast_request)',
            'pobreturnerror_ast = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: float * string")]']
        checks.append(('COMMUTATIVE slot order authenticates the real swapped native message',
                       r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
                       r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (8) /\ '
                       r'$quiet_multiply_error(S, poperand_left, poperand_right, pvalue_left, pvalue_right, z) /\ '
                       r'S_ast_request.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: float * string")) z /\ '
                       r'S_ast_request.EVENTS = S.EVENTS /\ S_ast_generated.COMPLETION = THROWING n_exception /\ '
                       r'$ob_object_arithmetic_type_error_source(S_ast_generated, pfunction, pobreturnerror_ast) /\ '
                       r'$ob_object_return_error_live(S_ast_generated, pobreturnerror_ast) /\ '
                       r'$ob_object_arithmetic_type_error_capture(S, S_ast_generated) = eps'))
    return bindings, checks


def normal(fixture, path):
    bindings = inputs(fixture, path)
    checks = [
        ('quiet numeric success retains its result and cannot mint an error receipt',
         r'pbin = ADD /\ $string_bytes(pvalue_left) = ($ptascii("1.5")) /\ '
         r'$string_bytes(pvalue_right) = ($ptascii("2")) /\ '
         r'S_request.COMPLETION = NORMAL /\ S_request.RESULT = KNOWN (PFLOAT 4615063718147915776) /\ '
         r'S_request.EVENTS = S.EVENTS /\ S_generated = S_request /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = eps /\ '
         r'$source_exception_transition(S, S_generated) = S_generated /\ pobobjectreturn.SOURCE = eps')]
    return bindings, checks


def noisy(fixture, path):
    bindings = inputs(fixture, path) + [
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Unsupported operand types: string - string"), LINE z}',
        'pevent_warning = $event_source(S, DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) z)']
    checks = [
        ('leading numeric conversion reports before the original string TypeError',
         r'$string_bytes(pvalue_left) = ($ptascii("1.5x")) /\ '
         r'$coerce_number(pvalue_left) = COERCED (NFLOAT 4609434218613702656) true /\ '
         r'S_request.RESULT = S_right.RESULT /\ S_request.EVENTS = S.EVENTS ++ [pevent_warning] /\ '
         r'S_request.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: string - string")) z'),
        ('default leading arithmetic retains the genuine FINAL capture',
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$source_exception_transition(S, S_generated) = $ob_object_final_capture(S_generated, pobobjectreturn, $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror)))')]
    return bindings, checks


def reference(fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT SUBTRACT (VARIABLE n_left* z_left) z) :: ptask_tail*',
        'S.RESULT = KNOWN pvalue_right',
        '$lookup(S.ENV, n_left*) = (n_cell_left)',
        'S_read = $resolve_at(S, VARIABLE n_left* z_left, z)',
        'S_raw = $binary_apply(S_read[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_right], SUBTRACT, PNULL, pvalue_right, z)',
        'S_candidate = $throwable_transition(S, S_raw)',
        'S_candidate.COMPLETION = THROWING n_exception']
    checks = [
        ('actual shared reference CV has no private-read capture authority',
         r'z = 8 /\ n_cell_left <- S.REFCELLS /\ S.STORE[n_cell_left] = DEFINED PNULL /\ '
         r'$heap_count(HCELL n_cell_left, $machine_roots(S)) = 2 /\ '
         r'S_read = S[.RESULT = KNOWN PNULL] /\ '
         r'$ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 0], z) = eps /\ '
         r'S_raw.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: null - string")) z /\ '
         r'S_candidate.COMPLETION = THROWING n_exception /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_candidate) = eps /\ '
         r'$source_exception_transition(S, S_candidate) = S_candidate /\ pobobjectreturn.SOURCE = eps')]
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
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_quiet_arithmetic_type_coercion_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py',
        'tests/semantics/output_final_arithmetic_type_error_review_state.py',
        'tests/semantics/output_final_arithmetic_operator_review_state.py',
        'tests/semantics/output_final_divide_type_error_review_state.py']] + [Path(__file__)]
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
            controls = {'normal': normal, 'noisy': noisy, 'reference': reference}
            bindings, checks = (controls[name](checked['fixture'], path) if name in controls else
                                authority(name, checked['fixture'], path))
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            inputs_before = {str(item): prior.common.sha(item) for item in [path, cache, fixture]}
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'inputs_before': inputs_before, 'passed': False}
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
