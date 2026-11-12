#!/usr/bin/env python3
"""Quiet left-string failures preserve physical slots and exact successors."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_left_arithmetic_type_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
CASES = {'add': sources.ADD, 'string-right': sources.STRING_RIGHT,
         'multiply-order': sources.SWAPPED_MULTIPLY}


def authority(name, fixture, path):
    swapped = name == 'multiply-order'
    message = ('Unsupported operand types: float * string' if swapped else
               'Unsupported operand types: string + ' + ('string' if name == 'string-right' else 'int'))
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
    right = ('pvalue_right = PFLOAT 4609434218613702656' if swapped else
             r'$string_bytes(pvalue_right) = ($ptascii("2"))' if name == 'string-right' else
             'pvalue_right = PINT 1')
    checks = [
        ('source-reached BAD left keeps original RHS scratch and native type names',
         r'$string_bytes(pvalue_left) = ($ptascii("X")) /\ $coerce_number(pvalue_left) = BADNUMBER /\ '
         r'$ob_object_string_value(S, pvalue_left) /\ $value_nodes(pvalue_left) = eps /\ ' +
         right + r' /\ $ob_object_division_number(pvalue_right) /\ $value_nodes(pvalue_right) = eps /\ '
         r'S_left = S_inputs[.RESULT = KNOWN pvalue_left] /\ S_right = S_left[.RESULT = KNOWN pvalue_right] /\ '
         r'S_request.RESULT = KNOWN pvalue_right /\ S_request.TODO = ptask_tail* /\ S_request.HELD = S.HELD /\ '
         'S_request.COMPLETION = THROWN "TypeError" ($ptascii("' + message + r'")) z /\ '
         r'S_request.EVENTS = S.EVENTS /\ z = 7 /\ '
         r'$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror)'),
        ('exact152 capture and real driver retain native owners without a metadata root',
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
            'pobreturnerror_other = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string - int")]',
            'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
            'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
            'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("X"))',
            'S_bad = S[.STORE[n_cell] = DEFINED pvalue_bad]',
            'S_bad_request = $dz_raw(S_bad)',
            'S_bad_generated = $throwable_transition(S_bad, S_bad_request)',
            'S_good = S_bad[.STRINGDATA = S_bad.STRINGDATA ++ [$ptascii("X")]]',
            'S_good_generated = $throwable_transition(S_good, $dz_raw(S_good))',
            'S_noisy = S[.RESULT = KNOWN (PSTRING ($ptascii("2x")))]',
            'S_noisy_request = $dz_raw(S_noisy)',
            'S_noisy_generated = $throwable_transition(S_noisy, S_noisy_request)',
            'pobreturnerror_noisy = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string + string")]']
        checks += [
            ('present physical slots refuse a coherent KNOWN replacement of the source CV',
             r'pbin = ADD /\ $arithmetic_copy_swap(S, porigin_operator, pbin, poperand_left, poperand_right) = (false) /\ '
             r'$ob_object_error_operand_value(S_copy, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'$integer_slot_rank(S_copy, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = eps /\ '
             r'$arithmetic_copy_swap(S_copy, porigin_operator, ADD, KNOWN pvalue_left, poperand_right) = eps /\ '
             r'S_copy_generated = S_generated /\ $ob_object_return_error_live(S_copy_generated, pobreturnerror) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_copy, S_copy_generated) = eps'),
            ('coherent opcode source line and altered exact successor refuse',
             r'$call_current_valid(S_other) /\ S_other_generated.COMPLETION = THROWING n_exception /\ '
             r'$ob_object_arithmetic_type_error_source(S_other_generated, pfunction, pobreturnerror_other) /\ '
             r'$ob_object_return_error_live(S_other_generated, pobreturnerror_other) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_other, S_other_generated) = eps /\ '
             r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
             r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
             r'$ob_object_arithmetic_type_error_capture(S, S_generated[.RESULT = KNOWN PNULL]) = eps /\ '
             r'$ob_object_arithmetic_type_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps'),
            ('BAD bytes do not forge a live private left string identity',
             r'$coerce_number(pvalue_bad) = BADNUMBER /\ $value_nodes(pvalue_bad) = eps /\ '
             r'~$string_carrier_valid(S_bad, pvalue_bad) /\ '
             r'$ob_object_error_operand_value(S_bad, poperand_left, [PCFIELD 0], z) = eps /\ '
             r'S_bad_request.COMPLETION = S_request.COMPLETION /\ S_bad_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_return_error_live(S_bad_generated, pobreturnerror) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_bad, S_bad_generated) = eps /\ '
             r'$string_carrier_valid(S_good, pvalue_bad) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_good, S_good_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('quiet-right scope refuses a leading-number candidate even when left fails first',
             r'$coerce_number(PSTRING ($ptascii("2x"))) = COERCED (NINT 2) true /\ '
             r'~$ob_object_division_number(PSTRING ($ptascii("2x"))) /\ '
             r'S_noisy_request.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: string + string")) z /\ '
             r'S_noisy_request.EVENTS = S.EVENTS /\ S_noisy_generated.COMPLETION = THROWING n_exception /\ '
             r'$ob_object_arithmetic_type_error_source(S_noisy_generated, pfunction, pobreturnerror_noisy) /\ '
             r'$ob_object_return_error_live(S_noisy_generated, pobreturnerror_noisy) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_noisy, S_noisy_generated) = eps')]
    if name == 'string-right':
        bindings += [
            'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("2"))',
            'S_bad = S[.RESULT = KNOWN pvalue_bad]',
            'S_bad_generated = $throwable_transition(S_bad, $dz_raw(S_bad))',
            'S_good = S_bad[.STRINGDATA = S_bad.STRINGDATA ++ [$ptascii("2")]]',
            'S_good_generated = $throwable_transition(S_good, $dz_raw(S_good))']
        checks.append(('pure quiet numeric right classification needs its own live string identity',
                       r'$coerce_number(pvalue_bad) = COERCED (NINT 2) false /\ $value_nodes(pvalue_bad) = eps /\ '
                       r'$ob_object_error_operand_value(S_bad, KNOWN pvalue_bad, [PCFIELD 1], z) = (pvalue_bad) /\ '
                       r'~$string_carrier_valid(S_bad, pvalue_bad) /\ '
                       r'S_bad_generated.COMPLETION = THROWING n_exception /\ '
                       r'$ob_object_return_error_live(S_bad_generated, pobreturnerror) /\ '
                       r'$ob_object_arithmetic_type_error_capture(S_bad, S_bad_generated) = eps /\ '
                       r'$string_carrier_valid(S_good, pvalue_bad) /\ '
                       r'$ob_object_arithmetic_type_error_capture(S_good, S_good_generated) = ((pobobjectreturn, pobreturnerror))'))
    if swapped:
        bindings += [
            'S_ast_request = $binary_apply(S_right, MULTIPLY, pvalue_left, pvalue_right, z)[.HELD = S.HELD]',
            'S_ast_generated = $throwable_transition(S, S_ast_request)',
            'pobreturnerror_ast = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string * float")]']
        checks.append(('genuine COMMUTATIVE order refuses an otherwise equal AST-order152 successor',
                       r'pbin = MULTIPLY /\ '
                       r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
                       r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (8) /\ '
                       r'$arithmetic_copy_swap(S, porigin_operator, pbin, poperand_left, poperand_right) = (true) /\ '
                       r'$quiet_multiply_error(S, poperand_left, poperand_right, pvalue_left, pvalue_right, z) /\ '
                       r'S_ast_request = S_request[.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: string * float")) z] /\ '
                       r'S_ast_generated.COMPLETION = THROWING n_exception /\ '
                       r'$ob_object_arithmetic_type_error_source(S_ast_generated, pfunction, pobreturnerror_ast) /\ '
                       r'$ob_object_return_error_live(S_ast_generated, pobreturnerror_ast) /\ '
                       r'$ob_object_arithmetic_type_error_capture(S, S_ast_generated) = eps'))
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
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_left_arithmetic_type_error_sources.py',
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
