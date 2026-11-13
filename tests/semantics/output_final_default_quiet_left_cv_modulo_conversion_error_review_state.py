#!/usr/bin/env python3
"""Quiet left CVs retain own reads before noisy CONST or own-CV MOD divisors."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_both_modulo_conversion_error_review_state as previous
import output_final_default_quiet_left_cv_modulo_conversion_error_sources as sources
import output_final_default_right_modulo_conversion_error_sources as constants

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
ORIGINAL = sources.CASES['native-default-quiet-left-cv-modulo-conversion-error-cv-both']
OWN = ORIGINAL.replace(b'        return $left % $right;',
                       b'        $other = 1;\n        return $left % $right;')
CONST = sources.CASES['native-default-quiet-left-cv-modulo-conversion-error-constant-both']
HANDLERS = ORIGINAL.replace(b'declare(strict_types=0);',
    b'declare(strict_types=0); function ob_quiet_left_cv_handler($level, $message) {}')
UNUSED = constants.CASES['native-default-right-modulo-conversion-error-both'].replace(
    b"        return 1 % '0.5x';", b"        $unused = 0;\n        return 1 % '0.5x';")
assert OWN != ORIGINAL
CASES = {'source': OWN, 'constant': CONST, 'carrier': ORIGINAL, 'quiet-values': CONST,
         'handlers': HANDLERS, 'unused-cv': UNUSED}
WARNING = r'DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered"))'
DEPRECATED = r'DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision')
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
LIVE = r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ $ob_object_return_error_live(S_generated, pobreturnerror)'


def authority(name, fixture, path):
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*',
        'S.RESULT = poperand_right', 'S.ORIGIN = (porigin_operator)']
    error = 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}'
    if name == 'handlers':
        bindings += [
            'poperand_left = VARIABLE n_left* z_left', 'poperand_right = VARIABLE n_right* z_right',
            '$call_target(S, $ptascii("ob_quiet_left_cv_handler"), eps) = (pfunction_handler)',
            'S_silent = S[.REPORTING = 1][.REPORTINGINI = $ptascii("1")][.REPORTINGMODIFIED = true]',
            'S_silent_generated = $throwable_transition(S_silent, $dz_raw(S_silent))',
            'S_silent_generated.COMPLETION = THROWING n_exception', error,
            'S_warning = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_quiet_left_cv_handler"))), LEVELS 2}]',
            'S_deprecated = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_quiet_left_cv_handler"))), LEVELS 8192}]',
            'S_warning_next = S_silent_generated[.ERRORHANDLER = S_warning.ERRORHANDLER]',
            'S_deprecated_next = S_silent_generated[.ERRORHANDLER = S_deprecated.ERRORHANDLER]']
        return bindings, [
            ('masked eligible Warning and Deprecated callbacks cannot borrow quiet-left CV-pair Error capture',
             r'z = 8 /\ z_left = 8 /\ z_right = 8 /\ n_left* = $ptascii("left") /\ n_right* = $ptascii("right") /\ '
             r'pfunction_handler.NAME = $ptascii("ob_quiet_left_cv_handler") /\ '
             r'$integer_operand_source(S_silent, porigin_operator, [PCFIELD 0], poperand_left) /\ '
             r'$integer_operand_source(S_silent, porigin_operator, [PCFIELD 1], poperand_right) /\ '
             r'$integer_slot_rank(S_silent, porigin_operator, [PCFIELD 0], poperand_left) = (8) /\ '
             r'$integer_slot_rank(S_silent, porigin_operator, [PCFIELD 1], poperand_right) = (8) /\ '
             r'$call_current_valid(S_warning) /\ $call_current_valid(S_deprecated) /\ '
             r'S_silent_generated.EVENTS = S.EVENTS /\ '
             r'$error_handler_eligible(S_warning, 2) /\ ~$error_handler_eligible(S_warning, 8192) /\ '
             r'~$error_handler_eligible(S_deprecated, 2) /\ $error_handler_eligible(S_deprecated, 8192) /\ '
             r'$ob_object_division_error_source(S_warning_next, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_warning_next, pobreturnerror) /\ '
             r'$ob_object_division_error_source(S_deprecated_next, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_deprecated_next, pobreturnerror) /\ '
             r'$machine_roots(S_warning_next) = $machine_roots(S_silent_generated) /\ '
             r'$machine_roots(S_deprecated_next) = $machine_roots(S_silent_generated) /\ '
             r'$ob_object_division_error_capture(S_warning, S_warning_next) = eps /\ '
             r'$ob_object_division_error_capture(S_deprecated, S_deprecated_next) = eps')]
    if name == 'unused-cv':
        bindings += [
            'poperand_left = KNOWN (PINT 1)', 'poperand_right = KNOWN pvalue_right',
            '$lookup(S.ENV, $ptascii("unused")) = (n_unused)',
            'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
            'S_generated.COMPLETION = THROWING n_exception', error]
        return bindings, [
            ('a genuine unused CV cannot widen the old quiet-CONST noisy-CONST empty-CV bound',
             r'z = 7 /\ pfunction.CVS = [$ptascii("unused")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 1 /\ '
             r'S.STORE[n_unused] = DEFINED (PINT 0) /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
             r'$heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], poperand_left) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], poperand_right) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (1) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (1) /\ '
             r'S_raw.RESULT = KNOWN (PINT 0) /\ '
             'S_raw.EVENTS = S.EVENTS ++ [' + WARNING + ' 7, ' + DEPRECATED + r' 7] /\ ' + LIVE + r' /\ '
             r'$ob_object_division_error_capture(S, S_generated) = eps')]
    right_const = name in ['constant', 'quiet-values']
    line = '7' if right_const else ('9' if name == 'source' else '8')
    bindings += [
        'poperand_left = VARIABLE n_left* z_left',
        '$lookup(S.ENV, n_left*) = (n_cell_left)', 'S.STORE[n_cell_left] = DEFINED pvalue_left']
    if right_const:
        bindings += ['poperand_right = KNOWN pvalue_right',
                     '$origin_child((porigin_operator), [PCFIELD 1]) = (porigin_right)',
                     '$compiled_read(S, porigin_right) = (pvalue_right_compiled)']
        topology = (r'pfunction.CVS = [$ptascii("left")] /\ |S.ENV| = 1 /\ '
                    r'pvalue_right_compiled = PSTRING ($ptascii("0.5x")) /\ '
                    r'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled)')
    else:
        bindings += ['poperand_right = VARIABLE n_right* z_right',
                     '$lookup(S.ENV, n_right*) = (n_cell_right)', 'S.STORE[n_cell_right] = DEFINED pvalue_right']
        topology = (
            r'n_right* = $ptascii("right") /\ z_right = ' + line + r' /\ n_cell_left =/= n_cell_right /\ '
            r'(HCELL n_cell_right) <- S.ALLOCATIONS /\ ~(n_cell_right <- S.REFCELLS) /\ '
            r'$heap_count(HCELL n_cell_right, $machine_roots(S)) = 1 /\ $heap_owners($heap_graph(S), HCELL n_cell_right) = 1 /\ ' +
            (r'pfunction.CVS = [$ptascii("left"), $ptascii("right"), $ptascii("other")] /\ |S.ENV| = 3'
             if name == 'source' else r'pfunction.CVS = [$ptascii("left"), $ptascii("right")] /\ |S.ENV| = 2'))
    bindings += [
        'S_left = $resolve_at($hold_task_inputs(S), poperand_left, z)',
        'S_right = $resolve_at(S_left, poperand_right, z)',
        'S_integer_left = $integer_coerce(S_right, pvalue_left, z)',
        'S_integer_right = $integer_coerce(S_integer_left, pvalue_right, z)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception', error]
    genuine = (
        'z = ' + line + ' /\\ z_left = ' + line + r' /\ n_left* = $ptascii("left") /\ S.CVS = pfunction.CVS /\ ' + topology + r' /\ '
        r'pvalue_left = PINT 1 /\ pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
        r'(HCELL n_cell_left) <- S.ALLOCATIONS /\ ~(n_cell_left <- S.REFCELLS) /\ '
        r'$heap_count(HCELL n_cell_left, $machine_roots(S)) = 1 /\ $heap_owners($heap_graph(S), HCELL n_cell_left) = 1 /\ '
        r'$ob_object_error_operand_value(S, poperand_left, [PCFIELD 0], z) = (pvalue_left) /\ '
        r'$ob_object_error_operand_value(S, poperand_right, [PCFIELD 1], z) = (pvalue_right) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], poperand_left) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], poperand_right) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], poperand_left) = (8) /\ '
        '$integer_slot_rank(S, porigin_operator, [PCFIELD 1], poperand_right) = (' + ('1' if right_const else '8') + r') /\ '
        r'$ob_object_modulo_integer(pvalue_left) = (1) /\ '
        r'$ob_object_modulo_integer(pvalue_right) = eps /\ $long_convertible(pvalue_right) /\ '
        r'$ob_object_string_value(S, pvalue_right) /\ $value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
        r'S_left.RESULT = KNOWN pvalue_left /\ S_right.RESULT = KNOWN pvalue_right /\ '
        r'S_left.EVENTS = S.EVENTS /\ S_right.EVENTS = S.EVENTS /\ '
        r'S_integer_left.COMPLETION = NORMAL /\ S_integer_left.RESULT = KNOWN (PINT 1) /\ S_integer_left.EVENTS = S.EVENTS /\ '
        r'S_integer_right.COMPLETION = NORMAL /\ S_integer_right.RESULT = KNOWN (PINT 0) /\ '
        'S_integer_right.EVENTS = S.EVENTS ++ [' + WARNING + ' ' + line + ', ' + DEPRECATED + ' ' + line + r'] /\ '
        'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) ' + line + r' /\ '
        r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.STORE = S.STORE /\ S_raw.EVENTS = S_integer_right.EVENTS /\ '
        r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
        r'S.HELD = eps /\ $tasks_nodes(S.TODO) = eps /\ S.RETIREDOWNERS = eps /\ $base_nodes(S.BASE) = eps /\ '
        r'$call_current_valid(S) /\ $ob_object_final_native_method(S) = (pobobjectreturn) /\ '
        r'$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT) /\ ' + LIVE)
    if name == 'quiet-values':
        parts = [genuine, CAPTURE]
        for suffix, value, integer in [('bool', 'PBOOL false', 0), ('null', 'PNULL', 0),
                                       ('float', 'PFLOAT 4607182418800017408', 1)]:
            state = 'S_' + suffix
            bindings += [state + ' = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (' + value + '))]',
                         state + '_raw = $dz_raw(' + state + ')',
                         state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
            parts += ['$call_current_valid(' + state + ')',
                      '$ob_object_error_operand_value(' + state + ', poperand_left, [PCFIELD 0], z) = (' + value + ')',
                      '$ob_object_modulo_integer(' + value + ') = (' + str(integer) + ')',
                      state + '_raw = S_raw[.STORE = ' + state + '.STORE]',
                      state + '_generated = S_generated[.STORE = ' + state + '.STORE]',
                      '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = ((pobobjectreturn, pobreturnerror))']
        return bindings, [('quiet current BOOL, NULL and exact FLOAT left values preserve original storage and right-only diagnostics', r' /\ '.join(parts))]
    if name == 'carrier':
        checks = []
        for side, text, cell in [(0, '1', 'n_cell_left'), (1, '0.5x', 'n_cell_right')]:
            state = 'S_request_' + str(side)
            operand = 'poperand_left' if side == 0 else state + '.RESULT'
            bindings += [
                'pvalue_request_' + str(side) + ' = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("' + text + '"))',
                state + ' = S[.STORE = $set_cell(S.STORE, ' + cell + ', DEFINED pvalue_request_' + str(side) + ')][.STRINGDATA = S.STRINGDATA ++ [$ptascii("' + text + '")]]',
                state + '_raw = $dz_raw(' + state + ')',
                state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)',
                state + '_invalid = ' + state + '[.STRINGDATA = S.STRINGDATA]']
            checks += [
                ('a current REQUEST header in the own ' + ('quiet left' if side == 0 else 'noisy right') + ' cell retains right-only conversion diagnostics',
                 genuine + r' /\ ' + CAPTURE + r' /\ ' +
                 '$ob_object_error_operand_value(' + state + ', ' + operand + ', [PCFIELD ' + str(side) + '], z) = (pvalue_request_' + str(side) + r') /\ ' +
                 state + '_raw = S_raw[.STORE = ' + state + '.STORE][.STRINGDATA = ' + state + r'.STRINGDATA] /\ ' +
                 state + '_generated = S_generated[.STORE = ' + state + '.STORE][.STRINGDATA = ' + state + r'.STRINGDATA] /\ ' +
                 '$ob_object_division_error_capture(' + state + ', ' + state + r'_generated) = ((pobobjectreturn, pobreturnerror))'),
                ('missing REQUEST identity refuses the own ' + ('left' if side == 0 else 'right') + ' private read',
                 '~$ob_object_string_value(' + state + '_invalid, pvalue_request_' + str(side) + r') /\ ' +
                 '$ob_object_error_operand_value(' + state + '_invalid, ' + ('poperand_left' if side == 0 else state + '_invalid.RESULT') + ', [PCFIELD ' + str(side) + r'], z) = eps')]
        return bindings, checks
    bindings += ['S_reference_left = S[.REFCELLS = S.REFCELLS ++ [n_cell_left]]',
                 'S_reference_left_raw = $dz_raw(S_reference_left)',
                 'S_reference_left_generated = $throwable_transition(S_reference_left, S_reference_left_raw)']
    ref_left = (
        r'$ob_object_error_operand_value(S_reference_left, poperand_left, [PCFIELD 0], z) = eps /\ '
        r'S_reference_left_raw = S_raw[.REFCELLS = S_reference_left.REFCELLS] /\ '
        r'S_reference_left_generated = S_generated[.REFCELLS = S_reference_left.REFCELLS] /\ '
        r'$ob_object_return_error_live(S_reference_left_generated, pobreturnerror) /\ '
        r'$ob_object_division_error_capture(S_reference_left, S_reference_left_generated) = eps')
    if name == 'constant':
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0.5x"))',
            'S_request = S[.RESULT = KNOWN pvalue_request][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0.5x")]]',
            'S_request_raw = $dz_raw(S_request)', 'S_request_generated = $throwable_transition(S_request, S_request_raw)']
        return bindings, [
            ('the own quiet left CV precedes its actual compiled noisy CONST divisor', genuine + r' /\ ' + CAPTURE),
            ('a valid same-byte REQUEST cannot replace the original noisy RHS CONST',
             r'$call_current_valid(S_request) /\ $ob_object_string_value(S_request, pvalue_request) /\ '
             r'$ob_object_error_operand_value(S_request, S_request.RESULT, [PCFIELD 1], z) = (pvalue_request) /\ '
             r'$integer_slot_rank(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) = (1) /\ '
             r'~$integer_operand_source(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) /\ '
             r'S_request_raw = S_raw[.STRINGDATA = S_request.STRINGDATA] /\ '
             r'S_request_generated = S_generated[.STRINGDATA = S_request.STRINGDATA] /\ '
             r'$ob_object_division_error_source(S_request_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_request_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_request, S_request_generated) = eps'),
            ('a reference-marked left cell retains the Error outside the private reader', ref_left)]
    bindings += [
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'S.STORE[n_other] = DEFINED pvalue_left',
        'S_other = S[.TODO = (BINARY_RIGHT MODULO (VARIABLE ($ptascii("other")) z_left) z) :: ptask_tail*]',
        'S_line_left = S[.TODO = (BINARY_RIGHT MODULO (VARIABLE n_left* $(z_left + 1)) z) :: ptask_tail*]',
        'S_line_right = S[.RESULT = VARIABLE n_right* $(z_right + 1)]',
        'S_known_left = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*]',
        'S_known_right = S[.RESULT = KNOWN pvalue_right]',
        'S_reference_right = S[.REFCELLS = S.REFCELLS ++ [n_cell_right]]',
        'S_reference_right_raw = $dz_raw(S_reference_right)',
        'S_reference_right_generated = $throwable_transition(S_reference_right, S_reference_right_raw)',
        'S_swapped = S_generated[.EVENTS = S.EVENTS ++ [' + DEPRECATED + ' 9, ' + WARNING + ' 9]]']
    checks = [('two own CVs retain the quiet left value and right-only ordered diagnostics', genuine + r' /\ ' + CAPTURE)]
    for suffix, side, operand in [
            ('other', 0, 'VARIABLE ($ptascii("other")) z_left'),
            ('line_left', 0, 'VARIABLE n_left* $(z_left + 1)'), ('line_right', 1, 'S_line_right.RESULT'),
            ('known_left', 0, 'KNOWN pvalue_left'), ('known_right', 1, 'S_known_right.RESULT')]:
        state = 'S_' + suffix
        checks.append((suffix + ' keeps the real raw Error without the original read authority',
            '~$integer_operand_source(' + state + ', porigin_operator, [PCFIELD ' + str(side) + '], ' + operand + r') /\ ' +
            '$ob_object_error_operand_value(' + state + ', ' + operand + ', [PCFIELD ' + str(side) + '], z) = ' +
            ('(pvalue_left)' if suffix == 'known_left' else '(pvalue_right)' if suffix == 'known_right' else 'eps') + r' /\ ' +
            '$dz_raw(' + state + r') = S_raw /\ $ob_object_division_error_capture(' + state + r', S_generated) = eps'))
    checks += [('a reference-marked left cell retains the real Error outside its private reader', ref_left),
               ('a reference-marked right cell retains the real Error outside its private reader',
                r'$ob_object_error_operand_value(S_reference_right, S_reference_right.RESULT, [PCFIELD 1], z) = eps /\ '
                r'S_reference_right_raw = S_raw[.REFCELLS = S_reference_right.REFCELLS] /\ '
                r'S_reference_right_generated = S_generated[.REFCELLS = S_reference_right.REFCELLS] /\ '
                r'$ob_object_return_error_live(S_reference_right_generated, pobreturnerror) /\ '
                r'$ob_object_division_error_capture(S_reference_right, S_reference_right_generated) = eps'),
               ('a live same-source Error cannot reverse the right Warning and Deprecated events',
                LIVE + r' /\ S_swapped.EVENTS =/= S_generated.EVENTS /\ '
                r'$ob_object_division_error_source(S_swapped, pfunction, pobreturnerror) /\ '
                r'$ob_object_return_error_live(S_swapped, pobreturnerror) /\ '
                r'$machine_roots(S_swapped) = $machine_roots(S_generated) /\ '
                r'$ob_object_division_error_capture(S, S_swapped) = eps')]
    return bindings, checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / p for p in [*modules, 'spec/php.watsup', 'spec/semantics/modules.json',
        'tests/semantics/output_final_default_quiet_left_cv_modulo_conversion_error_sources.py',
        'tests/semantics/output_final_default_both_modulo_conversion_error_sources.py',
        'tests/semantics/output_final_default_both_modulo_conversion_error_review_state.py',
        'tests/semantics/output_final_default_right_modulo_conversion_error_sources.py',
        'tests/semantics/output_final_default_right_modulo_conversion_error_review_state.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_sources.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_state.py',
        'tests/semantics/output_final_default_constant_modulo_warning_error_review_state.py',
        'tests/semantics/output_final_modulo_error_sources.py',
        'tests/semantics/output_final_modulo_error_review_state.py',
        'tests/semantics/output_final_division_error_sources.py',
        'tests/semantics/output_final_division_error_review_state.py',
        'tests/semantics/output_final_return_type_review_state.py', 'tests/semantics/output_api_failure_sources.py',
        'tests/semantics/output_deprecation_warning_review_state.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe']]
    watched += [Path(__file__)]
    fingerprint = lambda: {str(p): prior.common.sha(p) for p in watched}
    report = {'revision': head(), 'mode': 'fixture SL_mode/cache=false/det=true',
              'module_count': len(modules), 'fixture_timeout_seconds': 300,
              'source_agreement_credit': 0, 'before': fingerprint(), 'records': [], 'passed': False}
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
            bindings, checks = authority(name, checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' +
                ''.join('  -- if ' + binding + '\n' for binding in bindings))
            inputs = lambda: {str(p): prior.common.sha(p) for p in [path, cache, fixture]}
            record = {'id': name, 'groups': [label for label, _ in checks],
                      'inputs_before': inputs(), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, fixture_execution_credit=0)
                continue
            started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                    *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
                record['observed'] = json.loads(result.stdout)
                assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
            except subprocess.TimeoutExpired as error:
                (directory / 'state.stdout').write_bytes(error.stdout or b'')
                (directory / 'state.stderr').write_bytes(error.stderr or b'')
                (directory / 'state.exit').write_text('timeout\n')
                raise
            finally:
                record.update(seconds=time.monotonic() - started, inputs_after=inputs())
            assert record['inputs_before'] == record['inputs_after']
            record['passed'] = True
            (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(name, len(checks), record['seconds'], flush=True)
        report.update(after=fingerprint(), after_revision=head())
        report['passed'] = (not args.prepare_only and all(record['passed'] for record in report['records']) and
                            report['before'] == report['after'] and report['revision'] == report['after_revision'])
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if 'after' not in report:
            report['after'] = fingerprint()
        if 'after_revision' not in report:
            report['after_revision'] = head()
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
