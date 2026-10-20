#!/usr/bin/env python3
"""Owning returned arrays remain frozen while their producer globals change."""
import base64
import json

import array_literal_float_return_array_value_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair

HELPERS = shared.HELPERS + r'''
def $list_warning_task(ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i) = true
def $list_warning_frontier(S, 10) = ($array_float_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i
def $list_warning_frontier(S, 15) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("R:")
'''


def conditions(name, program, path, stdout):
    reference = name.endswith('global-reference')
    line = 17 if reference else 15
    args = 'n_a, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_RESULT n_a poperand phpType13* z n_bits i'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 10, 'S') + [
        '$array_float_key_plan(S) = ((' + args + '))',
        'S.RESULT = poperand', 'poperand = KNOWN (PARRAY n_value)', f'z = {line}', 'i = 1',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE ($ptascii("key")) z_key) phpType13* z) :: ptask_tail*',
        'S.ORIGIN = (PORIGIN n_unit pcpath)', 'n_a =/= n_value',
        '$array_float_key_item(S, phpType13*, z) = ((expression, VARIABLE ($ptascii("key")) z_key))',
        'expression = NExprFuncCall name (SEQUENCE eps) metadata',
        '$code_at(S.CODE, n_unit) = (pcode)',
        'pcpath_call = pcpath ++ [PCFIELD 1]',
        '$code_expression(pcode.EXPRESSIONS, pcpath_call) = ((z, false))',
        '$code_name(pcode.NAMES, pcpath_call) = ((n_name*, eps))',
        '$call_target(S, n_name*, eps) = (pfunction)', '~pfunction.SIGNATURE.BYREF',
        '$array_float_key_input_source(S, expression, poperand)',
        '$array_float_key_source(S, ' + args + ')', '$array_float_key_ready(S, n_a, poperand)',
        '$array_float_array_key_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("produced")) = (n_produced)',
        'S.STORE[n_produced] = DEFINED (PINT 1)',
        '$lookup(S.ENV, $ptascii("source")) = (n_source)',
        'S.STORE[n_source] = DEFINED (PARRAY n_value)', pair('S', 'n_value', 2, 7),
        'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$operand_nodes(poperand) = [HARRAY n_value]',
        '$heap_owners($heap_graph(S), HARRAY n_value) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_a) = 1',
        '$heap_count(HARRAY n_value, $pools_nodes(S.POOLS)) = 0',
        '$array_float_key_retain(S, poperand) = S',
        '$array_float_key_plan(S[.FUNCTIONS = eps]) = eps',
        '$array_float_key_plan(S[.CALLABLES = eps]) = eps',
        'S_byref = S[.FUNCTIONS = [pfunction[.SIGNATURE = pfunction.SIGNATURE[.BYREF = true]]]]',
        '~$array_float_key_input_source(S_byref, expression, poperand)',
        'S_fallback = S[.CODE = [pcode[.NAMES = [CODENAME pcpath_call n_name* (n_name*)]]]]',
        '~$array_float_key_input_source(S_fallback, expression, poperand)',
        'S_constant = S[.CODE = [pcode[.EXPRESSIONS = [CODEEXPR pcpath_call z true]]]]',
        '~$array_float_key_input_source(S_constant, expression, poperand)',
        '~$array_float_key_input_source(S[.CODE = [pcode[.NAMES = eps]]], expression, poperand)',
        '~$array_float_key_input_source(S, NExprFuncCall name (SEQUENCE ([(NVariadicPlaceholder metadata)])) metadata, poperand)',
        '~$array_float_key_input_source(S, NExprFuncCall (NExprVariable (BYTES "c291cmNl") metadata) (SEQUENCE eps) metadata, poperand)',
        '~$array_float_key_input_source(S, expression, REFERENCE n_source)',
        '~$array_float_key_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_float_key_source(S, n_a, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_key_ready(S, n_a, KNOWN (PARRAY n_a))',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if reference:
        checks += [
            '$lookup(S.ENV, $ptascii("outside")) = (n_source)', 'n_source <- S.REFCELLS',
            '$heap_owners($heap_graph(S), HCELL n_source) = 2',
            '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
            'S.STORE[n_replacement] = DEFINED (PARRAY n_replacement_array)', pair('S', 'n_replacement_array', 33, 8),
        ]
    else:
        checks += ['~(n_source <- S.REFCELLS)', '$heap_owners($heap_graph(S), HCELL n_source) = 1']
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_value]',
        '$heap_count(HCELL n_source, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_value) = 2',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_value, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$array_float_key_source(S_resume, ' + args + ')',
        '$array_float_key_ready(S_resume, n_a, poperand)',
        '$array_float_key_completion_value(S_resume, poperand) = (PARRAY n_value)',
        '$array_float_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_key_ready(S_resume[.ENV = eps], n_a, poperand)',
        pair('S_resume', 'n_value', 2, 7),
        '$heap_owners($heap_graph(S_resume), HARRAY n_value) = 1',
        'S_resume.STORE[n_produced] = DEFINED (PINT 1)',
        '$array_float_key_retain(S_resume, poperand) = S_resume',
        '$error_read_discard(S_resume, ' + marker + ') = S_resume',
    ] + empty_biases('S_resume')
    if reference:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("outside")) = (n_source)',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_changed)', pair('S_resume', 'n_changed', 44, 88),
            '$lookup(S_resume.ENV, $ptascii("source")) = (n_new_source)', 'n_new_source =/= n_source',
            'S_resume.STORE[n_new_source] = DEFINED (PARRAY n_replacement_array)',
            '$heap_owners($heap_graph(S_resume), HCELL n_source) = 1',
        ]
    else:
        checks += ['S_resume.STORE[n_source] = DEFINED (PARRAY n_changed)', pair('S_resume', 'n_changed', 44, 88)]
    checks += [
        'n_changed =/= n_value',
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 1) = (DIRECT (PARRAY n_value))',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        'S_insert.ARRAYS[n_value] = S_resume.ARRAYS[n_value]',
        '$heap_owners($heap_graph(S_insert), HARRAY n_value) = 1',
    ] + empty_biases('S_insert') + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 1) = (DIRECT (PARRAY n_value))',
        '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_value', pair('S_read', 'n_value', 2, 7), pair('S_read', 'n_copy_child', 55, 7),
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 4) = (DIRECT (PINT 77))',
        '$lookup(S_read.ENV, $ptascii("fresh")) = (n_fresh_cell)',
        'S_read.STORE[n_fresh_cell] = DEFINED (PARRAY n_fresh)', 'n_fresh =/= n_value',
        'S_read.STORE[n_produced] = DEFINED (PINT 2)',
        '$heap_owners($heap_graph(S_read), HARRAY n_value) = 1',
        '$heap_owners($heap_graph(S_read), HARRAY n_copy_child) = 1',
    ] + empty_biases('S_read')
    if reference:
        checks += [
            'S_read.STORE[n_source] = DEFINED (PARRAY n_changed)', pair('S_read', 'n_changed', 66, 88),
            'S_read.STORE[n_new_source] = DEFINED (PARRAY n_current)', pair('S_read', 'n_current', 99, 8),
            'n_fresh = n_replacement_array', pair('S_read', 'n_fresh', 33, 8),
            '$heap_owners($heap_graph(S_read), HARRAY n_fresh) = 2',
        ]
    else:
        checks += [
            'S_read.STORE[n_source] = DEFINED (PARRAY n_current)', pair('S_read', 'n_current', 99, 88),
            'n_fresh = n_changed', pair('S_read', 'n_fresh', 44, 88),
            '$heap_owners($heap_graph(S_read), HARRAY n_fresh) = 1',
        ]
    checks += [
        'S_done = $drive_steps(S_read, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        '$drive_steps(S_read, 1) = $drive_steps($drive_steps(S_read, 0)[.COMPLETION = NORMAL], 1)',
    ] + empty_biases('S_done')
    for array in ('n_a', 'n_value', 'n_copy', 'n_copy_child', 'n_changed', 'n_fresh', 'n_current'):
        checks.append(f'~((HARRAY {array}) <- S_done.ALLOCATIONS)')
    checks.append('~((HCELL n_source) <- S_done.ALLOCATIONS)')
    if reference:
        checks.append('~((HCELL n_new_source) <- S_done.ALLOCATIONS)')
    else:
        checks.append('$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
