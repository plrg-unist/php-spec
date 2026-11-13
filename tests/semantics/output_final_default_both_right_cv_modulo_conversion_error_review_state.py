#!/usr/bin/env python3
"""Both-noisy RHS CV capture retains its own read and original left CONST."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import time

from recorded_worker import Worker
import output_final_default_both_modulo_conversion_error_review_state as previous
import output_final_default_both_right_cv_modulo_conversion_error_sources as sources

ROOT = Path(__file__).resolve().parents[2]
division = previous.division
prior = previous.prior
PREFIX = previous.PREFIX
OWN = sources.CASES['native-default-both-right-cv-modulo-conversion-error-string-notices'].replace(
    b"        return '1.5x' % $right;", b"        $other = '0.5x';\n        return '1.5x' % $right;")
HANDLERS = sources.CASES['native-default-both-right-cv-modulo-conversion-error-string-notices'].replace(
    b'declare(strict_types=0);', b'declare(strict_types=0); function ob_both_right_cv_handler($level, $message) {}')
UNUSED = previous.sources.CASES['native-default-both-modulo-conversion-error-string-notices'].replace(
    b"        return '1.5x' % '0.5x';", b"        $unused = 0;\n        return '1.5x' % '0.5x';")
assert OWN != sources.CASES['native-default-both-right-cv-modulo-conversion-error-string-notices']
CASES = {'source': OWN, 'carrier': OWN, 'handlers': HANDLERS, 'unused-cv': UNUSED}
CASES['cv-pair'] = sources.CASES['native-default-both-right-cv-modulo-conversion-error-string-notices'].replace(
    b"        return '1.5x' % $right;", b"        $left = '1.5x';\n        return $left % $right;")
WARNING = r'DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered"))'
LEFT = r'DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float-string "1.5x" to int loses precision')
DEPRECATED = r'DIAGNOSTIC "Deprecated" ' + prior.value(b'Implicit conversion from float-string "0.5x" to int loses precision')
CAPTURE = r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'
LIVE = r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ $ob_object_return_error_live(S_generated, pobreturnerror)'


def authority(name, fixture, path):
    if name == 'cv-pair':
        bindings = division.start(fixture, path) + [
            'S.TODO = (BINARY_RIGHT MODULO (VARIABLE n_left* z_left) z) :: ptask_tail*',
            'S.RESULT = VARIABLE n_right* z_right', 'S.ORIGIN = (porigin_operator)',
            '$lookup(S.ENV, n_left*) = (n_cell_left)', 'S.STORE[n_cell_left] = DEFINED pvalue_left',
            '$lookup(S.ENV, n_right*) = (n_cell_right)', 'S.STORE[n_cell_right] = DEFINED pvalue_right',
            'S_left = $resolve_at($hold_task_inputs(S), VARIABLE n_left* z_left, z)',
            'S_right = $resolve_at(S_left, S.RESULT, z)',
            'S_integer_left = $integer_coerce(S_right, pvalue_left, z)',
            'S_integer_right = $integer_coerce(S_integer_left, pvalue_right, z)',
            'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
            'S_generated.COMPLETION = THROWING n_exception',
            'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}']
        return bindings, [
            ('genuine own noisy CV pairs satisfy both private readers and exact Error authority but remain outside the matrix',
             r'z = 8 /\ z_left = 8 /\ z_right = 8 /\ n_left* = $ptascii("left") /\ n_right* = $ptascii("right") /\ '
             r'pfunction.CVS = [$ptascii("right"), $ptascii("left")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 2 /\ '
             r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
             r'n_cell_left =/= n_cell_right /\ (HCELL n_cell_left) <- S.ALLOCATIONS /\ (HCELL n_cell_right) <- S.ALLOCATIONS /\ '
             r'~(n_cell_left <- S.REFCELLS) /\ ~(n_cell_right <- S.REFCELLS) /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S)) = 1 /\ $heap_count(HCELL n_cell_right, $machine_roots(S)) = 1 /\ '
             r'$heap_owners($heap_graph(S), HCELL n_cell_left) = 1 /\ $heap_owners($heap_graph(S), HCELL n_cell_right) = 1 /\ '
             r'$ob_object_error_operand_value(S, VARIABLE n_left* z_left, [PCFIELD 0], z) = (pvalue_left) /\ '
             r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], VARIABLE n_left* z_left) = (8) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
             r'$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = (8) /\ '
             r'$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = (8) /\ '
             r'$ob_object_modulo_integer(pvalue_left) = eps /\ $long_convertible(pvalue_left) /\ '
             r'$ob_object_modulo_integer(pvalue_right) = eps /\ $long_convertible(pvalue_right) /\ '
             r'$ob_object_string_value(S, pvalue_left) /\ $ob_object_string_value(S, pvalue_right) /\ '
             r'$value_nodes(pvalue_left) = eps /\ $value_nodes(pvalue_right) = eps /\ '
             r'S_left.RESULT = KNOWN pvalue_left /\ S_right.RESULT = KNOWN pvalue_right /\ '
             r'S_integer_left.COMPLETION = NORMAL /\ S_integer_left.RESULT = KNOWN (PINT 1) /\ '
             r'S_integer_right.COMPLETION = NORMAL /\ S_integer_right.RESULT = KNOWN (PINT 0) /\ '
             r'S_integer_left.EVENTS = S.EVENTS ++ [' + WARNING + ' 8, ' + LEFT + r' 8] /\ '
             r'S_integer_right.EVENTS = S_integer_left.EVENTS ++ [' + WARNING + ' 8, ' + DEPRECATED + r' 8] /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 8 /\ '
             r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S_integer_right.EVENTS /\ S_raw.STORE = S.STORE /\ '
             r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
             r'S.HELD = eps /\ $tasks_nodes(S.TODO) = eps /\ S.RETIREDOWNERS = eps /\ $base_nodes(S.BASE) = eps /\ '
             r'$call_current_valid(S) /\ $ob_object_final_native_method(S) = (pobobjectreturn) /\ '
             r'$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT) /\ '
             r'$ob_object_division_operator(S, porigin_operator) = (MODULO) /\ ' + LIVE + r' /\ '
             r'$ob_object_division_error_capture(S, S_generated) = eps')]
    bindings = division.start(fixture, path) + [
        'S.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left) z) :: ptask_tail*',
        'S.ORIGIN = (porigin_operator)']
    error = 'pobreturnerror = {SITE porigin_operator, OBJECT n_exception, MESSAGE $ptascii("Modulo by zero"), LINE z}'
    if name == 'handlers':
        bindings += [
            'S.RESULT = VARIABLE n_right* z_right',
            '$call_target(S, $ptascii("ob_both_right_cv_handler"), eps) = (pfunction_handler)',
            'S_silent = S[.REPORTING = 1][.REPORTINGINI = $ptascii("1")][.REPORTINGMODIFIED = true]',
            'S_silent_generated = $throwable_transition(S_silent, $dz_raw(S_silent))',
            'S_silent_generated.COMPLETION = THROWING n_exception', error,
            'S_warning = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_both_right_cv_handler"))), LEVELS 2}]',
            'S_deprecated = S_silent[.ERRORHANDLER = {CALLBACK (PSTRING ($ptascii("ob_both_right_cv_handler"))), LEVELS 8192}]',
            'S_warning_next = S_silent_generated[.ERRORHANDLER = S_warning.ERRORHANDLER]',
            'S_deprecated_next = S_silent_generated[.ERRORHANDLER = S_deprecated.ERRORHANDLER]']
        return bindings, [
            ('eligible Warning and Deprecated handlers stay excluded even with silent reporting and a live Error',
             r'z = 7 /\ z_right = 7 /\ n_right* = $ptascii("right") /\ '
             r'pfunction_handler.NAME = $ptascii("ob_both_right_cv_handler") /\ '
             r'$integer_operand_source(S_silent, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
             r'$integer_operand_source(S_silent, porigin_operator, [PCFIELD 1], S_silent.RESULT) /\ '
             r'$integer_slot_rank(S_silent, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
             r'$integer_slot_rank(S_silent, porigin_operator, [PCFIELD 1], S_silent.RESULT) = (8) /\ '
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
    bindings += [
        '$origin_child((porigin_operator), [PCFIELD 0]) = (porigin_left)',
        '$compiled_read(S, porigin_left) = (pvalue_left_compiled)',
        'S_raw = $dz_raw(S)', 'S_generated = $throwable_transition(S, S_raw)',
        'S_generated.COMPLETION = THROWING n_exception', error]
    line = '7' if name == 'unused-cv' else '8'
    notices = ', '.join([WARNING + ' ' + line, LEFT + ' ' + line, WARNING + ' ' + line, DEPRECATED + ' ' + line])
    if name == 'unused-cv':
        bindings += [
            'S.RESULT = KNOWN pvalue_right',
            '$lookup(S.ENV, $ptascii("unused")) = (n_unused)']
        return bindings, [
            ('an authentic unused private cell cannot broaden the old noisy CONST pair beyond its empty-CV bound',
             r'z = 7 /\ pfunction.CVS = [$ptascii("unused")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 1 /\ '
             r'S.STORE[n_unused] = DEFINED (PINT 0) /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
             r'~(n_unused <- S.REFCELLS) /\ $heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
             r'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ pvalue_left_compiled = PSTRING ($ptascii("1.5x")) /\ '
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
             r'$ob_object_modulo_integer(pvalue_left) = eps /\ $long_convertible(pvalue_left) /\ $ob_object_modulo_integer(pvalue_right) = eps /\ '
             r'$long_convertible(pvalue_right) /\ $ob_object_string_value(S, pvalue_right) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
             r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
             r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (1) /\ '
             r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 7 /\ '
             'S_raw.EVENTS = S.EVENTS ++ [' + notices + r'] /\ ' + LIVE + r' /\ '
             r'$ob_object_division_error_capture(S, S_generated) = eps')]
    bindings += [
        'S.RESULT = VARIABLE n_right* z_right',
        '$lookup(S.ENV, n_right*) = (n_cell)', 'S.STORE[n_cell] = DEFINED pvalue_right',
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'S.STORE[n_other] = DEFINED pvalue_right']
    genuine = (
        r'z = 8 /\ z_right = 8 /\ n_right* = $ptascii("right") /\ '
        r'pfunction.CVS = [$ptascii("right"), $ptascii("other")] /\ S.CVS = pfunction.CVS /\ |S.ENV| = 2 /\ '
        r'pvalue_left_compiled = PSTRING ($ptascii("1.5x")) /\ pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled) /\ pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5x")) /\ '
        r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x")) /\ '
        r'n_cell =/= n_other /\ (HCELL n_cell) <- S.ALLOCATIONS /\ ~(n_cell <- S.REFCELLS) /\ '
        r'$heap_count(HCELL n_cell, $machine_roots(S)) = 1 /\ $heap_owners($heap_graph(S), HCELL n_cell) = 1 /\ '
        r'$ob_object_error_operand_value(S, S.RESULT, [PCFIELD 1], z) = (pvalue_right) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) /\ '
        r'$integer_operand_source(S, porigin_operator, [PCFIELD 1], S.RESULT) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 0], KNOWN pvalue_left) = (1) /\ '
        r'$integer_slot_rank(S, porigin_operator, [PCFIELD 1], S.RESULT) = (8) /\ '
        r'$ob_object_modulo_integer(pvalue_left) = eps /\ $long_convertible(pvalue_left) /\ $ob_object_modulo_integer(pvalue_right) = eps /\ '
        r'$long_convertible(pvalue_right) /\ $ob_object_string_value(S, pvalue_right) /\ '
        r'~$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192) /\ '
        r'S_raw.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 8 /\ '
        r'S_raw.RESULT = KNOWN (PINT 0) /\ S_raw.EVENTS = S.EVENTS ++ [' + notices + r'] /\ ' + LIVE)
    if name == 'carrier':
        bindings += [
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0.5x"))',
            'S_request = S[.STORE = $set_cell(S.STORE, n_cell, DEFINED pvalue_request)][.STRINGDATA = S.STRINGDATA ++ [$ptascii("0.5x")]]',
            'S_request_raw = $dz_raw(S_request)',
            'S_request_generated = $throwable_transition(S_request, S_request_raw)',
            'S_invalid = S_request[.STRINGDATA = S.STRINGDATA]',
            'pvalue_left_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("1.5x"))',
            'S_left_request = S[.TODO = (BINARY_RIGHT MODULO (KNOWN pvalue_left_request) z) :: ptask_tail*][.STRINGDATA = S.STRINGDATA ++ [$ptascii("1.5x")]]',
            'S_left_raw = $dz_raw(S_left_request)',
            'S_left_generated = $throwable_transition(S_left_request, S_left_raw)']
        return bindings, [
            ('a valid current REQUEST carrier in the own RHS cell retains both actual conversion pairs and Error',
             genuine + r' /\ ' + CAPTURE + r' /\ '
             r'$call_current_valid(S_request) /\ $integer_operand_source(S_request, porigin_operator, [PCFIELD 1], S_request.RESULT) /\ '
             r'$ob_object_error_operand_value(S_request, S_request.RESULT, [PCFIELD 1], z) = (pvalue_request) /\ '
             r'$ob_object_string_value(S_request, pvalue_request) /\ '
             r'S_request_raw = S_raw[.STORE = S_request.STORE][.STRINGDATA = S_request.STRINGDATA] /\ '
             r'S_request_generated = S_generated[.STORE = S_request.STORE][.STRINGDATA = S_request.STRINGDATA] /\ '
             r'$ob_object_division_error_capture(S_request, S_request_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('the same RHS bytes without their REQUEST identity cannot pass the private read',
             r'$integer_operand_source(S_invalid, porigin_operator, [PCFIELD 1], S_invalid.RESULT) /\ '
             r'$integer_slot_rank(S_invalid, porigin_operator, [PCFIELD 1], S_invalid.RESULT) = (8) /\ '
             r'~$ob_object_string_value(S_invalid, pvalue_request) /\ '
             r'$ob_object_error_operand_value(S_invalid, S_invalid.RESULT, [PCFIELD 1], z) = eps'),
            ('a valid same-byte left REQUEST header retains the Error but cannot replace its original CONST',
             r'$call_current_valid(S_left_request) /\ $ob_object_string_value(S_left_request, pvalue_left_request) /\ '
             r'$ob_object_error_operand_value(S_left_request, KNOWN pvalue_left_request, [PCFIELD 0], z) = (pvalue_left_request) /\ '
             r'$integer_slot_rank(S_left_request, porigin_operator, [PCFIELD 0], KNOWN pvalue_left_request) = (1) /\ '
             r'~$integer_operand_source(S_left_request, porigin_operator, [PCFIELD 0], KNOWN pvalue_left_request) /\ '
             r'S_left_raw = S_raw[.STRINGDATA = S_left_request.STRINGDATA] /\ '
             r'S_left_generated = S_generated[.STRINGDATA = S_left_request.STRINGDATA] /\ '
             r'$ob_object_division_error_source(S_left_generated, pfunction, pobreturnerror) /\ '
             r'$ob_object_return_error_live(S_left_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_left_request, S_left_generated) = eps')]
    bindings += [
        'S_other = S[.RESULT = VARIABLE ($ptascii("other")) z_right]',
        'S_line = S[.RESULT = VARIABLE n_right* $(z_right + 1)]',
        'S_known = S[.RESULT = KNOWN pvalue_right]',
        'S_reference = S[.REFCELLS = S.REFCELLS ++ [n_cell]]',
        'S_reference_raw = $dz_raw(S_reference)',
        'S_reference_generated = $throwable_transition(S_reference, S_reference_raw)',
        'S_swapped = S_generated[.EVENTS = S.EVENTS ++ [' + WARNING + ' 8, ' + DEPRECATED + ' 8, ' + WARNING + ' 8, ' + LEFT + ' 8]]']
    checks = [('genuine noisy CONST and initialized own noisy RHS CV retain distinct ordered diagnostic pairs',
               genuine + r' /\ ' + CAPTURE)]
    for suffix, label in [('other', 'same-valued other CV'), ('line', 'forged RHS read line'), ('known', 'resolved value substituted for its CV')]:
        state = 'S_' + suffix
        checks.append((label + ' keeps the raw Error but lacks the original RHS source',
            '$integer_slot_rank(' + state + ', porigin_operator, [PCFIELD 1], ' + state + '.RESULT) = ' + ('eps' if suffix == 'known' else '(8)') + r' /\ ' +
            '~$integer_operand_source(' + state + ', porigin_operator, [PCFIELD 1], ' + state + r'.RESULT) /\ ' +
            '$ob_object_error_operand_value(' + state + ', ' + state + r'.RESULT, [PCFIELD 1], z) = ' + ('(pvalue_right)' if suffix == 'known' else 'eps') + r' /\ ' +
            '$dz_raw(' + state + r') = S_raw /\ $ob_object_division_error_capture(' + state + r', S_generated) = eps'))
    checks += [
        ('reference-marking the actual RHS cell retains the real Error while leaving the private reader boundary',
         r'$integer_operand_source(S_reference, porigin_operator, [PCFIELD 1], S_reference.RESULT) /\ '
         r'$ob_object_error_operand_value(S_reference, S_reference.RESULT, [PCFIELD 1], z) = eps /\ '
         r'S_reference_raw = S_raw[.REFCELLS = S_reference.REFCELLS] /\ '
         r'S_reference_generated = S_generated[.REFCELLS = S_reference.REFCELLS] /\ '
         r'$ob_object_division_error_source(S_reference_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_reference_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_reference, S_reference_generated) = eps'),
        ('a live same-source Error cannot swap the distinct left and right diagnostic pairs',
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
        'tests/semantics/output_final_default_both_right_cv_modulo_conversion_error_sources.py',
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
