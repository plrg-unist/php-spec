#!/usr/bin/env python3
"""A leading RHS needs live strings and genuine unswapped physical slots."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_leading_right_arithmetic_type_error_sources as sources
import output_final_left_arithmetic_type_error_sources as left
import output_final_both_string_arithmetic_type_error_sources as both

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
CASES = {'add': sources.ADD, 'multiply-order': sources.SWAPPED_MULTIPLY,
         'legacy59': left.ADD, 'legacy60': both.ADD}


def start(fixture, path):
    return division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT pbin poperand_left z) :: ptask_tail*',
        'S.RESULT = poperand_right', 'S.ORIGIN = (porigin_operator)',
        '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
        '$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left)',
        '$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right)',
        'S_inputs = $hold_task_inputs(S)',
        'S_left = $resolve_at(S_inputs, poperand_left, z)',
        'S_right = $resolve_at(S_left, poperand_right, z)']


def authority(name, fixture, path):
    if name.startswith('legacy'):
        bindings = start(fixture, path) + [
            'S_candidate = S[.RESULT = KNOWN (PSTRING ($ptascii("2x")))]',
            'S_request = $dz_raw(S_candidate)',
            'S_generated = $throwable_transition(S_candidate, S_request)',
            'S_generated.COMPLETION = THROWING n_exception',
            'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Unsupported operand types: string + string"), LINE z}',
            'S_charged = $drive_steps(S_candidate, 1)',
            'S_charged.COMPLETION = BUDGET',
            'S_capture = S_charged[.COMPLETION = NORMAL]',
            'S_capture.FRAMES = [pframe_capture]',
            'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*']
        return bindings, [
            ('fresh coherent old leading-RHS candidate has a real unswapped receipt',
             r'pbin = ADD /\ z = 7 /\ $coerce_number(pvalue_left) = BADNUMBER /\ '
             r'$arithmetic_copy_swap(S_candidate, porigin_operator, ADD, poperand_left, S_candidate.RESULT) = (false) /\ '
             r'$coerce_number(PSTRING ($ptascii("2x"))) = COERCED (NINT 2) true /\ '
             r'S_request.RESULT = KNOWN (PSTRING ($ptascii("2x"))) /\ '
             r'S_request.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: string + string")) z /\ '
             r'S_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_candidate, S_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('changed legacy guard retains actual charged native owners and source',
             r'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror) /\ '
             r'$heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ '
             r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture'))]

    operator, symbol = ('MULTIPLY', '*') if name == 'multiply-order' else ('ADD', '+')
    message = 'Unsupported operand types: string ' + symbol + ' string'
    bindings = start(fixture, path) + [
        'S_request = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_request)',
        'S_generated.COMPLETION = THROWING n_exception',
        'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("' + message + '"), LINE z}']
    common = (r'pbin = ' + operator + r' /\ z = 7 /\ '
              r'$string_bytes(pvalue_left) = ($ptascii("X")) /\ '
              r'$string_bytes(pvalue_right) = ($ptascii("2x")) /\ '
              r'$coerce_number(pvalue_left) = BADNUMBER /\ '
              r'$coerce_number(pvalue_right) = COERCED (NINT 2) true /\ '
              r'~$ob_object_division_number(pvalue_right) /\ '
              r'$ob_object_string_value(S, pvalue_left) /\ $ob_object_string_value(S, pvalue_right) /\ '
              r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ ')
    if name == 'multiply-order':
        bindings += [
            'S_physical = $binary_apply(S_right, MULTIPLY, pvalue_right, pvalue_left, z)[.HELD = S.HELD]',
            'S_physical_generated = $throwable_transition(S, S_physical)']
        return bindings, [
            ('genuine swapped slots put the leading string first in native conversion',
             common + r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (8) /\ '
             r'$arithmetic_copy_swap(S, porigin_operator, MULTIPLY, poperand_left, poperand_right) = (true) /\ '
             r'~$error_handler_eligible(S, 2) /\ $arithmetic_copy_plan(S) = eps /\ $arithmetic_owned_plan(S) = eps /\ '
             r'~$quiet_multiply_error(S, poperand_left, poperand_right, pvalue_left, pvalue_right, z)'),
            ('a quiet AST raw successor cannot authorize the genuinely swapped source',
             r'S_request.COMPLETION = THROWN "TypeError" ($ptascii("' + message + r'")) z /\ '
             r'S_request.RESULT = KNOWN pvalue_right /\ S_request.EVENTS = S.EVENTS /\ '
             r'$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
             r'$ob_object_arithmetic_type_error_capture(S, S_generated) = eps'),
            ('the distinct physical conversion has a Warning and also refuses this quiet arm',
             r'S_physical.COMPLETION = THROWN "TypeError" ($ptascii("' + message + r'")) z /\ '
             r'S_physical.RESULT = KNOWN pvalue_right /\ '
             r'S_physical.EVENTS = $leading_warning(S, true, z).EVENTS /\ S_physical.EVENTS =/= S.EVENTS /\ '
             r'$ob_object_return_error_live(S_physical_generated, pobreturnerror) /\ '
             r'$ob_object_arithmetic_type_error_capture(S, S_physical_generated) = eps')]

    bindings += [
        'S_charged = $drive_steps(S, 1)', 'S_charged.COMPLETION = BUDGET',
        'S_capture = S_charged[.COMPLETION = NORMAL]', 'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'S_bad = S[.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("2x")))]',
        'S_bad_generated = $throwable_transition(S_bad, $dz_raw(S_bad))',
        'S_good = S_bad[.STRINGDATA = S_bad.STRINGDATA ++ [$ptascii("2x")]]',
        'S_good_generated = $throwable_transition(S_good, $dz_raw(S_good))',
        'S_copy = S[.TODO = (BINARY_RIGHT ADD (KNOWN pvalue_left) z) :: ptask_tail*]',
        'S_copy_generated = $throwable_transition(S_copy, $dz_raw(S_copy))',
        'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
        'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
        'S_zero = $drive_steps(S_capture, 0)']
    return bindings, [
        ('BAD first physical operand skips the authenticated leading RHS conversion',
         common + r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (8) /\ '
         r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (1) /\ '
         r'$arithmetic_copy_swap(S, porigin_operator, ADD, poperand_left, poperand_right) = (false) /\ '
         r'S_left = S_inputs[.RESULT = KNOWN pvalue_left] /\ S_right = S_left[.RESULT = KNOWN pvalue_right] /\ '
         r'S_request.RESULT = KNOWN pvalue_right /\ S_request.EVENTS = S.EVENTS /\ '
         r'S_request.COMPLETION = THROWN "TypeError" ($ptascii("' + message + r'")) z'),
        ('real charged capture preserves native ownership and zero-budget state',
         r'$ob_object_arithmetic_type_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ '
         r'S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture')),
        ('numeric classification and a live TypeError cannot forge RHS carrier identity',
         r'$ob_object_return_error_live(S_bad_generated, pobreturnerror) /\ '
         r'~$string_carrier_valid(S_bad, PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("2x"))) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_bad, S_bad_generated) = eps /\ '
         r'$string_carrier_valid(S_good, PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("2x"))) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_good, S_good_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('a coherent equal KNOWN copy loses the actual private-CV slot proof',
         r'S_copy_generated = S_generated /\ '
         r'$ob_object_error_operand_value(S_copy, KNOWN pvalue_left, [PCFIELD 0], z) = (pvalue_left) /\ '
         r'$arithmetic_copy_swap(S_copy, porigin_operator, ADD, KNOWN pvalue_left, poperand_right) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S_copy, S_copy_generated) = eps'),
        ('own line site scratch and exact successor remain necessary',
         r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
         r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.RESULT = KNOWN pvalue_left]) = eps /\ '
         r'$ob_object_arithmetic_type_error_capture(S, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output; out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / name for name in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_leading_right_arithmetic_type_error_sources.py',
        'tests/semantics/output_final_left_arithmetic_type_error_sources.py',
        'tests/semantics/output_final_both_string_arithmetic_type_error_sources.py',
        'tests/semantics/output_final_left_arithmetic_type_error_review_state.py',
        'tests/semantics/output_final_both_string_arithmetic_type_error_review_state.py',
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
            inputs = lambda: {str(item): prior.common.sha(item) for item in [path, cache, fixture]}
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'inputs_before': inputs(), 'passed': False}
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
                record.update(seconds=time.monotonic() - started, inputs_after=inputs())
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
