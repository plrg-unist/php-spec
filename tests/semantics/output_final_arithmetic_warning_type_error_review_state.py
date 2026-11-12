#!/usr/bin/env python3
"""Returning arithmetic Warning handlers preserve FINAL error authority."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_division_error_review_state as division
import output_final_arithmetic_warning_type_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
prior = division.prior
PREFIX = division.PREFIX.replace('BINARY_RIGHT DIVIDE (KNOWN (PINT 1)) z',
                                 'BINARY_RIGHT pbin poperand_left z')
PREFIX = PREFIX.replace('def $dp_phase(S, n) = false -- otherwise', r'''
def $dp_phase(S, 10) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
def $dp_phase(S, 11) = true
  -- if S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
def $dp_phase(S, 12) = true
  -- if S.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber)) :: ptask_tail*
def $dp_phase(S, n) = false -- otherwise''')
MULTIPLY_ORDER = sources.MULTIPLY.replace(b"$a * 'X'", b"'X' * $a")
REFERENCE = sources.ADD.replace(b"        return $a + 'X';",
                                 b"        $r =& $a;\n        return $a + 'X';")
CASES = {'add': sources.ADD, 'multiply-order': MULTIPLY_ORDER,
         'normal': sources.NORMAL, 'fallback': sources.FALLBACK, 'reference': REFERENCE,
         'empty-cleanup': sources.ADD + b'class D { function __destruct() {} }\n'}


def step(target, before):
    return [f'{target}_found = $drive_steps({before}, 1)',
            f'{target}_found.COMPLETION = BUDGET',
            f'{target} = {target}_found[.COMPLETION = NORMAL]']


def returning(fixture, path, cleanup=False):
    bindings = division.start(fixture, path) + [
        '$arithmetic_copy_plan(S) = (pintegeroperation)',
        'S.ORIGIN = (porigin_operator)', 'z = pintegeroperation.LINE',
        '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
        *step('S_left', 'S'),
        'S_left.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*',
        *step('S_warning', 'S_left'),
        'S_warning.TODO = (ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_leading pnumber_saved 0) :: ptask_tail*',
        *prior.seek('S_handler', 'S_warning', 10),
        'S_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_handler*',
        'perrorcall.RESUME = ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_leading pnumber_saved 1']
    if cleanup:
        bindings += [*prior.seek('S_restored_handler', 'S_handler', 11),
            'S_restored_handler.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_handler*',
            'S_restored_handler.DESTRUCTION.CLEANUPS = [pdestructioncleanup]']
    else:
        bindings += [*step('S_restored_handler', 'S_handler'),
            'S_restored_handler.TODO = perrorcall.RESUME :: ptask_handler*']
    return bindings + [*prior.seek('S_right', 'S_restored_handler', 12),
        'S_right.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber_saved)) :: ptask_tail*']


def request():
    return ['$arithmetic_cv_failure_operands(S_right, pintegeroperation, ARITHMETIC_RIGHT pnumber_saved) = ((pvalue_first, pvalue_second))',
            'S_request = $dz_raw(S_right)',
            'S_generated = $throwable_transition(S_right, S_request)',
            'S_generated.COMPLETION = THROWING n_exception',
            'S_request.COMPLETION = THROWN "TypeError" preqbytes_message z',
            'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE preqbytes_message, LINE z}']


def handler_check(fallback=False, cleanup=False):
    events = ('S_restored_handler.EVENTS = S_handler.EVENTS ++ [$event_source(S_handler, perrorcall.EVENT)]'
              if fallback else 'S_restored_handler.EVENTS = S_handler.EVENTS')
    branch = (r'$destructor_operational(S_handler) /\ '
              r'$error_cleanup_valid(S_restored_handler, perrorcall) /\ '
              r'$eager_cleanup_valid(S_restored_handler, pdestructioncleanup)'
              if cleanup else r'~$destructor_operational(S_handler) /\ '
              r'S_restored_handler.DESTRUCTION.CLEANUPS = eps /\ '
              r'S_restored_handler.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)')
    return (r'$string_bytes(pvalue_leading) = ($ptascii("1.5x")) /\ '
            r'pnumber_saved = NFLOAT 4609434218613702656 /\ '
            r'$arithmetic_add_conversion(pvalue_leading) = ((pnumber_saved, true)) /\ '
            f'S_handler.RESULT = KNOWN (PBOOL {str(not fallback).lower()}) /\\ ' +
            r'$error_selected_roots(perrorcall.TARGET) = eps /\ '
            r'$operand_nodes(S_handler.RESULT) = eps /\ '
            r'S_handler.ERRORHANDLER.CALLBACK = eps /\ '
            r'$call_task_valid(S_handler, ERROR_HANDLER_RESULT perrorcall) /\ ' +
            branch + r' /\ ' + events + r' /\ '
            r'S_right.EVENTS = S_restored_handler.EVENTS /\ S_right.DESTRUCTION.CLEANUPS = eps /\ '
            r'S_right.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK) /\ '
            r'$heap_count(HOBJECT n_object, $machine_roots(S_right)) = 2 /\ ' + prior.public('S_right'))


def authority(name, fixture, path):
    bindings = returning(fixture, path, name == 'empty-cleanup') + request() + [
        '$ob_object_error_operand_value(S_right, pintegeroperation.LEFT, [PCFIELD 0], z) = (pvalue_lexical_left)',
        '$ob_object_error_operand_value(S_right, pintegeroperation.RIGHT, [PCFIELD 1], z) = (pvalue_lexical_right)',
        *step('S_capture', 'S_right'),
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*']
    symbol = '*' if name == 'multiply-order' else '+'
    checks = [
        ('returning handler follows its actual cleanup branch',
         handler_check(name == 'fallback', name == 'empty-cleanup')),
        ('RIGHT failure preserves PNULL scratch, original types and exact152 capture',
         r'S_request.RESULT = KNOWN PNULL /\ S_request.TODO = ptask_tail* /\ '
         r'S_request.EVENTS = S_right.EVENTS /\ S_request.HELD = S_right.HELD /\ '
         f'preqbytes_message = $ptascii("Unsupported operand types: string {symbol} string") /\\ '
         r'$ob_object_arithmetic_type_error_capture(S_right, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'pobobjectreturn_capture.SOURCE = (OBJECT_ARITHMETIC_TYPE_ERROR pobreturnerror) /\ '
         r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
         r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
         r'$heap_count(HCELL n_cell, $machine_roots(S_capture)) = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ ' + prior.public('S_capture'))]
    if name == 'add':
        bindings += [
            'pintegeroperation_other = pintegeroperation[.OP = SUBTRACT]',
            'S_other = S_right[.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation_other (ARITHMETIC_RIGHT pnumber_saved)) :: ptask_tail*]',
            'S_other_raw = $type_failure(S_other[.TODO = ptask_tail*][.RESULT = KNOWN PNULL], SUBTRACT, pvalue_first, pvalue_second, z)',
            'S_other_generated = $throwable_transition(S_other, S_other_raw)',
            'S_other_generated.COMPLETION = THROWING n_exception',
            'pobreturnerror_other = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string - string")]',
            'pobreturnerror_line = pobreturnerror[.LINE = $(z + 1)]',
            'pobreturnerror_site = pobreturnerror[.SITE = pfunction.ORIGIN]',
            'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S_right.STRINGDATA|)) ($ptascii("1.5x"))',
            'S_bad = S_right[.STORE[n_cell] = DEFINED pvalue_bad]',
            'S_bad_request = $dz_raw(S_bad)',
            'S_bad_raw = $type_failure(S_bad[.TODO = ptask_tail*][.RESULT = KNOWN PNULL], ADD, pvalue_bad, pvalue_second, z)',
            'S_bad_generated = $throwable_transition(S_bad, S_bad_raw)',
            'S_good = S_bad[.STRINGDATA = S_bad.STRINGDATA ++ [$ptascii("1.5x")]]',
            'S_good_generated = $throwable_transition(S_good, $dz_raw(S_good))']
        checks += [
            ('coherent wrong opcode cannot borrow source and exact materialization',
             r'$call_current_valid(S_other) /\ '
             r'$ob_object_arithmetic_type_error_source(S_other_generated, pfunction, pobreturnerror_other) /\ '
             r'$ob_object_return_error_live(S_other_generated, pobreturnerror_other) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_other, S_other_generated) = eps /\ '
             r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_line) /\ '
             r'~$ob_object_arithmetic_type_error_source(S_generated, pfunction, pobreturnerror_site) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_left, S_generated) = eps'),
            ('failure-step result and events cannot be substituted',
             r'$ob_object_arithmetic_type_error_capture(S_right, S_generated[.RESULT = KNOWN (PINT 9)]) = eps /\ '
             r'$ob_object_arithmetic_type_error_capture(S_right, S_generated[.EVENTS = S_generated.EVENTS ++ [OUTPUT ($ptascii("x"))]]) = eps'),
            ('live CV string bytes do not replace current identity authority',
             r'$call_task_valid(S_bad, ARITHMETIC_CV_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber_saved)) /\ '
             r'~$string_carrier_valid(S_bad, pvalue_bad) /\ '
             r'$ob_object_return_error_live(S_bad_generated, pobreturnerror) /\ '
             r'$arithmetic_cv_failure_operands(S_bad, pintegeroperation, ARITHMETIC_RIGHT pnumber_saved) = eps /\ '
             r'S_bad_request.COMPLETION = UNSUPPORTED "plain arithmetic CV selected conversion context" /\ '
             r'$ob_object_arithmetic_type_error_capture(S_bad, S_bad_generated) = eps /\ '
             r'$string_carrier_valid(S_good, pvalue_bad) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_good, S_good_generated) = ((pobobjectreturn, pobreturnerror))')]
    if name == 'multiply-order':
        bindings += [
            'S_live = S_right[.STORE[n_cell] = DEFINED (PBOOL false)]',
            'S_live_raw = $dz_raw(S_live)',
            'S_live_generated = $throwable_transition(S_live, S_live_raw)',
            'S_live_generated.COMPLETION = THROWING n_exception',
            'pobreturnerror_live = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: bool * string")]',
            'S_ast_raw = $type_failure(S_live[.TODO = ptask_tail*][.RESULT = KNOWN PNULL], MULTIPLY, pvalue_lexical_left, PBOOL false, z)',
            'S_ast_generated = $throwable_transition(S_live, S_ast_raw)',
            'pobreturnerror_ast = pobreturnerror[.MESSAGE = $ptascii("Unsupported operand types: string * bool")]']
        checks += [
            ('physical selected pointers preserve the native COMMUTATIVE swap',
             r'pintegeroperation.SWAPPED /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], pintegeroperation.LEFT) = (1) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], pintegeroperation.RIGHT) = (8) /\ '
             r'pvalue_first = pvalue_lexical_right /\ pvalue_second = pvalue_lexical_left /\ '
             r'$arithmetic_cv_failure_operands(S_live, pintegeroperation, ARITHMETIC_RIGHT pnumber_saved) = ((PBOOL false, pvalue_second)) /\ '
             r'S_live_raw.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: bool * string")) z /\ '
             r'$ob_object_arithmetic_type_error_capture(S_live, S_live_generated) = ((pobobjectreturn, pobreturnerror_live))'),
            ('a live normalized AST-order TypeError is not the physical successor',
             r'S_ast_generated.COMPLETION = THROWING n_exception /\ '
             r'$ob_object_arithmetic_type_error_source(S_ast_generated, pfunction, pobreturnerror_ast) /\ '
             r'$ob_object_return_error_live(S_ast_generated, pobreturnerror_ast) /\ '
             r'$ob_object_arithmetic_type_error_capture(S_live, S_ast_generated) = eps')]
    return bindings, checks


def normal(fixture, path):
    bindings = returning(fixture, path) + [
        'S_request = $dz_raw(S_right)',
        'S_generated = $throwable_transition(S_right, S_request)',
        *prior.seek('S_restored', 'S_right', 5),
        '$rt_normal(S_restored.TODO) = (pobobjectreturn_restored)']
    return bindings, [
        ('normal leading numeric conversion completes the same handler cleanup', handler_check()),
        ('captured 1.5 plus2 yields3.5 without a generated-error receipt',
         r'S_request.RESULT = KNOWN (PFLOAT 4615063718147915776) /\ '
         r'S_request.COMPLETION = NORMAL /\ S_request.EVENTS = S_right.EVENTS /\ '
         r'S_generated = S_request /\ '
         r'$ob_object_arithmetic_type_error_capture(S_right, S_generated) = eps /\ '
         r'$rt_result(S_restored, pobobjectreturn_restored) = ($ptascii("3.5")) /\ '
         r'pobobjectreturn_restored.SOURCE = eps /\ |S_restored.OBJECTS| = 1 /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S_restored)) = 1 /\ ' + prior.public('S_restored'))]


def reference(fixture, path):
    bindings = returning(fixture, path) + request()
    return bindings, [
        ('real shared-reference conversion does not gain private-CV capture authority',
         r'n_cell <- S_right.REFCELLS /\ '
         r'$heap_count(HCELL n_cell, $machine_roots(S_right)) = 2 /\ '
         r'$ob_object_error_operand_value(S_right, pintegeroperation.LEFT, [PCFIELD 0], z) = eps /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
         r'$ob_object_arithmetic_type_error_capture(S_right, S_generated) = eps /\ '
         r'$source_exception_transition(S_right, S_generated) = S_generated /\ '
         r'pobobjectreturn.SOURCE = eps')]


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
        'tests/semantics/recorded_worker.py', 'tests/semantics/output_final_arithmetic_warning_type_error_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py']] + [Path(__file__)]
    fingerprint = lambda: {str(item): prior.common.sha(item) for item in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'native_agreement_credit': 0, 'fixture_timeout_seconds': 300,
              'module_count': len(modules), 'records': [], 'passed': False, 'before': fingerprint()}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES[name])
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
            cache = directory / 'checked.json'
            cache.write_text(json.dumps(checked) + '\n')
            controls = {'normal': normal, 'reference': reference}
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
            print(name, len(checks), record['seconds'], flush=True)
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
