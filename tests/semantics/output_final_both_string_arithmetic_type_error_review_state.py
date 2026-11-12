#!/usr/bin/env python3
"""Both BAD strings require live identities, source slots and exact RHS scratch."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_both_string_arithmetic_type_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
CASES = {'add': sources.ADD, 'multiply-order': sources.SWAPPED_MULTIPLY}


def authority(name, fixture, path):
    swapped = name == 'multiply-order'
    operator, symbol = ('MULTIPLY', '*') if swapped else ('ADD', '+')
    message = 'Unsupported operand types: string ' + symbol + ' string'
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT pbin poperand_left z) :: ptask_tail*',
        'S.RESULT = poperand_right', 'S.ORIGIN = (porigin_operator)',
        '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right)',
        'S_inputs = $hold_task_inputs(S)',
        'S_left = $resolve_at(S_inputs, poperand_left, z)',
        'S_right = $resolve_at(S_left, poperand_right, z)',
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("' + message + '"), LINE z}',
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*']
    checks = [
        ('actual distinct BAD strings retain original RHS scratch and quiet failure',
         'pbin = ' + operator + r' /\ z = 7 /\ '
         r'$string_bytes(pvalue_left) = ($ptascii("X")) /\ $string_bytes(pvalue_right) = ($ptascii("Y")) /\ '
         r'$coerce_number(pvalue_left) = BADNUMBER /\ $coerce_number(pvalue_right) = BADNUMBER /\ '
         r'$ob_object_string_value(S, pvalue_left) /\ $ob_object_string_value(S, pvalue_right) /\ '
         r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
         r'~$ob_object_division_number(pvalue_right) /\ '
         r'S_left = S_inputs[.RESULT = KNOWN pvalue_left] /\ S_right = S_left[.RESULT = KNOWN pvalue_right] /\ '
         r'S_request.RESULT = KNOWN pvalue_right /\ S_request.TODO = ptask_tail* /\ S_request.HELD = S.HELD /\ '
         'S_request.COMPLETION = THROWN "TypeError" ($ptascii("' + message + r'")) z /\ '
         r'S_request.EVENTS = S.EVENTS /\ $ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror)'),
        ('real charged capture retains nonowning source and native owners',
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror) /\ '
         r'$source_exception_transition(S, S_generated) = $ob_object_final_capture(S_generated, pobobjectreturn, $ob_object_cv_preserve(pobobjectreturn.SOURCE, (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror))) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture'))]
    if name == 'add':
        bindings += [
            'S_copy = S[.TODO = (BINARY_RIGHT ADD (KNOWN pvalue_left) z) :: ptask_tail*]',
            'S_copy_generated = $throwable_transition(S_copy, $dz_raw(S_copy))',
            'S_other = S[.TODO = (BINARY_RIGHT SUBTRACT poperand_left z) :: ptask_tail*]',
            'S_other_generated = $throwable_transition(S_other, $dz_raw(S_other))',
            'pobreturnerror_other = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string - string")]',
            'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
            'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
            'pvalue_bad_left = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("X"))',
            'S_bad_left = S[.STORE[n_cell] = DEFINED pvalue_bad_left]',
            'S_bad_left_generated = $throwable_transition(S_bad_left, $dz_raw(S_bad_left))',
            'S_good_left = S_bad_left[.STRINGDATA = S_bad_left.STRINGDATA ++ [$ptascii("X")]]',
            'S_good_left_generated = $throwable_transition(S_good_left, $dz_raw(S_good_left))',
            'pvalue_bad_right = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("Y"))',
            'S_bad_right = S[.RESULT = KNOWN pvalue_bad_right]',
            'S_bad_right_generated = $throwable_transition(S_bad_right, $dz_raw(S_bad_right))',
            'S_good_right = S_bad_right[.STRINGDATA = S_bad_right.STRINGDATA ++ [$ptascii("Y")]]',
            'S_good_right_generated = $throwable_transition(S_good_right, $dz_raw(S_good_right))',
            'S_noisy = S[.RESULT = KNOWN (PSTRING ($ptascii("2x")))]',
            'S_noisy_request = $dz_raw(S_noisy)',
            'S_noisy_generated = $throwable_transition(S_noisy, S_noisy_request)',
            'S_object = S[.RESULT = KNOWN (POBJECT n_object)]',
            'S_object_request = $dz_raw(S_object)',
            'S_object_request.COMPLETION = THROWN "TypeError" preqbytes_object z',
            'S_object_generated = $throwable_transition(S_object, S_object_request)',
            'pobreturnerror_object = pobreturnerror[.MESSAGE = preqbytes_object]']
        checks += [
            ('coherent own-CV replacement and wrong opcode cannot mint a source receipt',
             r'$arithmetic_copy_swap(S, porigin_operator, ADD, poperand_left, poperand_right) = (false) /\ '
             r'S_copy_generated = S_generated /\ $ob_object_error_operand_value(S_copy, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'$arithmetic_copy_swap(S_copy, porigin_operator, ADD, KNOWN pvalue_left, poperand_right) = eps /\ '
             r'$ob_object_arithmetic_type_error_capture(S_copy, S_copy_generated) = eps /\ '
             r'S_other_generated.COMPLETION = THROWING n_exception /\ '
             r'$ob_object_arithmetic_type_error_source(S_other_generated, pfunction, pobreturnerror_other) /\ '
             r'$ob_object_return_error_live(S_other_generated, pobreturnerror_other) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_other, S_other_generated) = eps'),
            ('equal BAD bytes on either side need their own live string identities',
             r'$coerce_number(pvalue_bad_left) = BADNUMBER /\ $coerce_number(pvalue_bad_right) = BADNUMBER /\ '
             r'~$string_carrier_valid(S_bad_left, pvalue_bad_left) /\ '
             r'$ob_object_error_operand_value(S_bad_left, poperand_left, [PCFIELD 0], z) = eps /\ '
             r'$ob_object_return_error_live(S_bad_left_generated, pobreturnerror) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_bad_left, S_bad_left_generated) = eps /\ '
             r'$string_carrier_valid(S_good_left, pvalue_bad_left) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_good_left, S_good_left_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
             r'~$string_carrier_valid(S_bad_right, pvalue_bad_right) /\ '
             r'$ob_object_error_operand_value(S_bad_right, KNOWN pvalue_bad_right, [PCFIELD 1], z) = (pvalue_bad_right) /\ '
             r'$ob_object_return_error_live(S_bad_right_generated, pobreturnerror) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_bad_right, S_bad_right_generated) = eps /\ '
             r'$string_carrier_valid(S_good_right, pvalue_bad_right) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_good_right, S_good_right_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('leading right and nonstring BADNUMBER remain outside this source law',
             r'$coerce_number(PSTRING ($ptascii("2x"))) = COERCED (NINT 2) true /\ '
             r'S_noisy_request.COMPLETION = S_request.COMPLETION /\ S_noisy_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_return_error_live(S_noisy_generated, pobreturnerror) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_noisy, S_noisy_generated) = eps /\ '
             r'$coerce_number(POBJECT n_object) = BADNUMBER /\ ~$ob_object_string_value(S_object, POBJECT n_object) /\ '
             r'S_object_request.EVENTS = S.EVENTS /\ S_object_generated.COMPLETION = THROWING n_exception /\ '
             r'$ob_object_arithmetic_type_error_source(S_object_generated, pfunction, pobreturnerror_object) /\ '
             r'$ob_object_return_error_live(S_object_generated, pobreturnerror_object) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_object, S_object_generated) = eps'),
            ('source site line and exact materialization remain necessary',
             r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
             r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
             r'$ob_object_arithmetic_type_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ '
             r'$ob_object_arithmetic_type_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps')]
    if swapped:
        bindings += ['S_ast_request = $binary_apply(S_right, MULTIPLY, pvalue_left, pvalue_right, z)[.HELD = S.HELD]',
                     'S_wrong_scratch = S_generated[.RESULT = KNOWN pvalue_left]']
        checks.append(('true-swap slots and distinct bytes retain RHS even when type names coincide',
                       r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
                       r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (8) /\ '
                       r'$arithmetic_copy_swap(S, porigin_operator, MULTIPLY, poperand_left, poperand_right) = (true) /\ '
                       r'$quiet_multiply_error(S, poperand_left, poperand_right, pvalue_left, pvalue_right, z) /\ '
                       r'pvalue_left =/= pvalue_right /\ S_ast_request = S_request /\ '
                       r'$ob_object_arithmetic_type_error_source(S_wrong_scratch, pfunction, pobreturnerror) /\ '
                       r'$ob_object_return_error_live(S_wrong_scratch, pobreturnerror) /\ '
                       r'$ob_object_arithmetic_type_error_capture(S, S_wrong_scratch) = eps'))
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
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_both_string_arithmetic_type_error_sources.py',
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
            bindings, checks = authority(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            fingerprint_inputs = lambda: {str(item): prior.common.sha(item) for item in [path, cache, fixture]}
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'inputs_before': fingerprint_inputs(), 'passed': False}
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
                record.update(seconds=time.monotonic() - started, inputs_after=fingerprint_inputs())
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
