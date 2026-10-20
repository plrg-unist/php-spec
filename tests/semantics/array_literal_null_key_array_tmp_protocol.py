#!/usr/bin/env python3
"""Array-constructor TMP capture has one owner and never resets producer CVs."""
import base64
import json

import array_literal_null_key_array_tmp_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair

HELPERS = shared.HELPERS + r'''
def $list_warning_task(ARRAY_KEY_NULL_TMP_RESULT n n_value phpType13* z) = true
def $list_warning_frontier(S, 10) = ($array_null_tmp_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_NULL_TMP_RESULT n n_value phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_NULL_TMP_RESULT n n_value phpType13* z
def $list_warning_frontier(S, 15) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("R:")
'''


def conditions(name, program, path, stdout):
    reference = name.endswith('reference-leaf')
    line = 12 if reference else 10
    args = 'n_a, n_value, phpType13*, z'
    marker = 'ARRAY_KEY_NULL_TMP_RESULT n_a n_value phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 10, 'S') + [
        '$array_null_tmp_plan(S) = ((' + args + '))', f'z = {line}',
        'S.RESULT = KNOWN (PARRAY n_value)', 'n_a =/= n_value',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE ($ptascii("key")) z_key) phpType13* z) :: ptask_tail*',
        'S.BASE = BASE_VALUE (KNOWN PNULL)', 'S.ORIGIN = (PORIGIN n_unit pcpath)',
        '$array_float_key_item(S, phpType13*, z) = ((expression, VARIABLE ($ptascii("key")) z_key))',
        'expression = NExprArray (SEQUENCE phpType13_child*) metadata',
        '$code_at(S.CODE, n_unit) = (pcode)', 'pcpath_value = pcpath ++ [PCFIELD 1]',
        '$code_expression(pcode.EXPRESSIONS, pcpath_value) = ((z, false))',
        '$array_float_key_input_source(S, expression, KNOWN (PARRAY n_value))',
        '$array_null_tmp_source(S, ' + args + ')', '$array_null_value_ready(S, n_a, n_value)',
        '$array_null_value_plan(S) = eps', '$array_null_key_plan(S) = eps',
        '$array_float_key_plan(S) = eps', '$array_float_array_key_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
        'S.STORE[n_key_cell] = DEFINED PNULL', '~(n_key_cell <- S.REFCELLS)',
        '$array_null_tmp_plan(S[.STORE[n_key_cell] = DEFINED (PINT 9)]) = eps',
        '$array_null_tmp_plan(S[.RESULT = KNOWN PNULL]) = eps',
        'S_constant = S[.CODE = [pcode[.EXPRESSIONS = [CODEEXPR pcpath_value z true]]]]',
        '~$array_float_key_input_source(S_constant, expression, KNOWN (PARRAY n_value))',
        '~$array_null_tmp_source(S_constant, ' + args + ')',
        '~$array_null_tmp_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_null_tmp_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_null_tmp_source(S, n_a, n_value, phpType13*, $(z + 1))',
        '~$array_null_tmp_source(S, n_a, (|S.ARRAYS|), phpType13*, z)',
        '~$array_null_value_ready(S, n_a, n_a)',
        '$lookup(S.ENV, $ptascii("seed")) = (n_seed)',
        f'S.STORE[n_seed] = DEFINED (PINT {2 if reference else 3})',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 7)',
        pair('S', 'n_value', 2, 7),
        'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$operand_nodes(S.RESULT) = [HARRAY n_value]',
        '$heap_count(HARRAY n_value, $machine_roots(S)) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_value) = 1',
        '$heap_count(HARRAY n_value, $pools_nodes(S.POOLS)) = 0',
        '$heap_owners($heap_graph(S), HARRAY n_a) = 1',
        '~$array_float_key_input_source(S, expression, REFERENCE n_seed)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if reference:
        checks += [
            '$lookup(S.ENV, $ptascii("outside")) = (n_seed)', 'n_seed <- S.REFCELLS',
            '$heap_owners($heap_graph(S), HCELL n_seed) = 2',
            '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'n_other =/= n_seed',
            'S.STORE[n_other] = DEFINED (PINT 33)',
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (PARRAY n_held)', 'n_held =/= n_value',
            pair('S', 'n_held', 2, 8), '$heap_owners($heap_graph(S), HARRAY n_held) = 1',
        ]
    else:
        checks += ['~(n_seed <- S.REFCELLS)', '$heap_owners($heap_graph(S), HCELL n_seed) = 1']
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_value]',
        '$heap_count(HCELL n_seed, $task_nodes(' + marker + ')) = 0',
        '$heap_count(HARRAY n_value, $machine_roots(S_dispatch)) = 1',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_value) = 1',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_value, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_seed, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$array_null_tmp_source(S_resume, ' + args + ')',
        '$array_null_value_ready(S_resume, n_a, n_value)',
        '$array_null_tmp_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_null_value_ready(S_resume[.ENV = eps], n_a, n_value)',
        pair('S_resume', 'n_value', 2, 7),
        '$heap_owners($heap_graph(S_resume), HARRAY n_value) = 1',
        'S_resume.STORE[n_tail] = DEFINED (PINT 66)',
        'S_resume.STORE[n_key_cell] = DEFINED (PINT 9)',
        '$error_read_discard(S_resume, ' + marker + ') = S_resume',
    ] + empty_biases('S_resume')
    if reference:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("outside")) = (n_seed)',
            'S_resume.STORE[n_seed] = DEFINED (PINT 44)',
            '$lookup(S_resume.ENV, $ptascii("seed")) = (n_other)',
            '$lookup(S_resume.ENV, $ptascii("other")) = (n_other)',
            'S_resume.STORE[n_other] = DEFINED (PINT 33)',
            '$heap_owners($heap_graph(S_resume), HCELL n_seed) = 1',
            '$heap_owners($heap_graph(S_resume), HCELL n_other) = 2',
        ]
    else:
        checks += ['S_resume.STORE[n_seed] = DEFINED (PINT 44)']
    checks += [
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        'S_insert.ARRAYS[n_value] = S_resume.ARRAYS[n_value]', 'S_insert.STORE = S_resume.STORE',
        '$heap_count(HARRAY n_value, $machine_roots(S_insert)) = 0',
        '$heap_owners($heap_graph(S_insert), HARRAY n_value) = 1',
    ] + empty_biases('S_insert') + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
        '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_value', pair('S_read', 'n_value', 2, 7), pair('S_read', 'n_copy_child', 55, 7),
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 4) = (DIRECT (PINT 77))',
        '$lookup(S_read.ENV, $ptascii("fresh")) = (n_fresh_cell)',
        'S_read.STORE[n_fresh_cell] = DEFINED (PARRAY n_fresh)', 'n_fresh =/= n_value',
        pair('S_read', 'n_fresh', 33 if reference else 44, 7),
        '$heap_owners($heap_graph(S_read), HARRAY n_value) = 1',
        '$heap_owners($heap_graph(S_read), HARRAY n_copy_child) = 1',
        '$heap_owners($heap_graph(S_read), HARRAY n_fresh) = 1',
    ] + empty_biases('S_read')
    if reference:
        checks += [
            'S_read.STORE[n_seed] = DEFINED (PINT 66)', 'S_read.STORE[n_other] = DEFINED (PINT 99)',
            pair('S_read', 'n_held', 88, 8), 'n_held =/= n_fresh',
            '$heap_owners($heap_graph(S_read), HARRAY n_held) = 1',
        ]
    else:
        checks += ['S_read.STORE[n_seed] = DEFINED (PINT 99)']
    checks += [
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
    ] + empty_biases('S_done')
    for array in ('n_a', 'n_value', 'n_copy', 'n_copy_child', 'n_fresh'):
        checks.append(f'~((HARRAY {array}) <- S_done.ALLOCATIONS)')
    checks.append('~((HCELL n_seed) <- S_done.ALLOCATIONS)')
    if reference:
        checks += ['~((HCELL n_other) <- S_done.ALLOCATIONS)', '~((HARRAY n_held) <- S_done.ALLOCATIONS)']
    else:
        checks.append('$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
