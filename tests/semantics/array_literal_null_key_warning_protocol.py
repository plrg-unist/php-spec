#!/usr/bin/env python3
"""NULL-key callbacks restore their captured CV and transfer both array owners."""
import base64
import json

import array_literal_null_key_warning_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair

HELPERS = shared.HELPERS + r'''
def $list_warning_task(ARRAY_KEY_NULL_RESULT n n_capture poperand pvalue phpType13* z) = true
def $list_warning_frontier(S, 10) = ($array_null_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_NULL_RESULT n n_capture poperand pvalue phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_NULL_RESULT n n_capture poperand pvalue phpType13* z
dec $array_null_warning_echo(pstate, nat*) : bool
def $array_null_warning_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = n_prefix*
def $array_null_warning_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 15) = $array_null_warning_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 16) = $array_null_warning_echo(S, $ptascii("B:"))
'''


def conditions(name, program, path, stdout):
    array = name.endswith('array-snapshot')
    line = 12 if array else 10
    args = 'n_a, n_q, poperand, pvalue, phpType13*, z'
    marker = 'ARRAY_KEY_NULL_RESULT n_a n_q poperand pvalue phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 10, 'S') + [
        '$array_null_key_plan(S) = ((' + args + '))', f'z = {line}',
        'poperand = VARIABLE ($ptascii("q")) z', 'S.RESULT = poperand',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED pvalue',
        '~(n_q <- S.REFCELLS)', '$propref_at(S.PROPREFS, n_q) = eps',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE n_key* z_key) phpType13* z) :: ptask_tail*',
        'S.BASE = BASE_VALUE (KNOWN PNULL)', '$array_float_key_value(S, VARIABLE n_key* z_key) = (PNULL)',
        'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$array_null_key_payload(S, pvalue, S.ALLOCATIONS)',
        '$array_null_key_slot(S, n_q, poperand) = (pvalue)',
        '$array_null_key_source(S, ' + args + ')', '$array_null_key_ready(S, n_a, n_q, poperand, pvalue)',
        '$array_float_key_plan(S) = eps', '$array_float_array_key_plan(S) = eps',
        '$array_null_key_plan(S[.RESULT = KNOWN pvalue]) = eps',
        '$array_null_key_plan(S[.BASE = BASE_VALUE (KNOWN (PINT 0))]) = eps',
        '~$array_null_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_null_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_null_key_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_null_key_source(S, n_a, n_q, poperand, pvalue, phpType13*, $(z + 1))',
        '~$array_null_key_source(S, n_a, (|S.STORE|), poperand, pvalue, phpType13*, z)',
        '~$array_null_key_payload(S, PSTRING eps, S.ALLOCATIONS)',
        '~$array_null_key_ready(S, n_a, n_q, poperand, PARRAY n_a)',
        '$heap_owners($heap_graph(S), HCELL n_q) = 1',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
    ]
    if array:
        checks += [
            'pvalue = PARRAY n_old', 'n_key* = $ptascii("key")',
            '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'n_key =/= n_q',
            'S.STORE[n_key] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)',
            'S.STORE[n_hold] = DEFINED (PARRAY n_old)', 'n_hold =/= n_q',
            pair('S', 'n_old', 2, 7), '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        ]
    else:
        checks += ['pvalue = PNULL', 'n_key* = $ptascii("q")', 'z_key = z']
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_null_key_message()',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.SITE = PORIGIN 9 eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE z])',
        '$task_nodes(' + marker + ') = ' + ('[HARRAY n_a, HARRAY n_old, HARRAY n_old]' if array else '[HARRAY n_a]'),
        '$heap_count(HCELL n_q, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_q) = 1',
    ] + empty_biases('S_dispatch')
    if array:
        checks += ['$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = 4']
    checks += driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_q, $tasks_nodes(pframe.TODO)) = 0',
    ]
    if array:
        checks += ['$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 2']
    checks += seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_q)',
        '$array_null_key_source(S_resume, ' + args + ')', '$call_task_valid(S_resume, ' + marker + ')',
        '$array_null_key_ready(S_resume, n_a, n_q, poperand, pvalue)',
        'S_resume.STORE[n_tail] = DEFINED (PINT 66)', 'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.GLOBALTABLE = eps',
        'S_unrooted = $unset_name(S_resume, $ptascii("q"))',
        '(HCELL n_q) <- S_unrooted.ALLOCATIONS',
        'H_unrooted = $heap_prune($heap_graph(S_unrooted)[.DEBTS = eps])',
        '~((HCELL n_q) <- H_unrooted.NODES)',
        '$array_null_key_source(S_unrooted, ' + args + ')', '$call_task_valid(S_unrooted, ' + marker + ')',
        '~$array_null_key_ready(S_unrooted, n_a, n_q, poperand, pvalue)',
        '$error_read_discard(S_unrooted, ' + marker + ').COMPLETION = UNSUPPORTED "array literal null-key value reset during throw"',
        'S_marked = S_resume[.REFCELLS = n_q :: S_resume.REFCELLS]',
        '~$array_null_key_ready(S_marked, n_a, n_q, poperand, pvalue)',
        'S_typed = S_resume[.PROPREFS = [{CELL n_q, SOURCES eps}]]',
        '~$array_null_key_ready(S_typed, n_a, n_q, poperand, pvalue)',
        'S_string = S_resume[.STORE[n_q] = DEFINED (PSTRING eps)]',
        '~$array_null_key_ready(S_string, n_a, n_q, poperand, pvalue)',
        'S_cell_debt = S_resume[.LITERALREFDEBTS = [n_q]]',
        '~$array_null_key_ready(S_cell_debt, n_a, n_q, poperand, pvalue)',
        'S_builder = S_resume[.STORE[n_q] = DEFINED (PARRAY n_a)]',
        '~$array_null_key_ready(S_builder, n_a, n_q, poperand, pvalue)',
        'S_discard = $error_read_discard(S_resume, ' + marker + ')',
        'S_discard.STORE[n_q] = DEFINED pvalue',
        'S_discard.STORE[n_tail] = DEFINED (PINT 66)',
    ] + empty_biases('S_resume') + empty_biases('S_discard')
    if array:
        checks += [
            'S_resume.STORE[n_q] = DEFINED (PARRAY n_changed)', 'n_changed =/= n_old',
            pair('S_resume', 'n_changed', 55, 88), pair('S_resume', 'n_old', 2, 7),
            '$lookup(S_resume.ENV, $ptascii("changed")) = (n_changed_cell)',
            'S_resume.STORE[n_changed_cell] = DEFINED (PARRAY n_held_changed)',
            'n_held_changed =/= n_changed', pair('S_resume', 'n_held_changed', 44, 88),
            'S_resume.STORE[n_key] = DEFINED (PINT 9)',
            '$heap_owners($heap_graph(S_resume), HARRAY n_old) = 3',
            '$heap_owners($heap_graph(S_resume), HARRAY n_changed) = 1',
            '$heap_owners($heap_graph(S_resume), HARRAY n_held_changed) = 1',
        ]
    else:
        checks += [
            'S_resume.STORE[n_q] = DEFINED (PINT 44)',
            '$array_null_key_slot(S_resume, n_q, poperand) = (PINT 44)',
        ]
    checks += [
        'PhpStep: S_resume ~> S_insert',
        'S_insert.STORE[n_q] = DEFINED pvalue',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT pvalue)',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        'S_insert.STORE[n_tail] = DEFINED (PINT 66)', 'S_insert.RESULT = KNOWN PNULL',
        '$heap_count(HCELL n_q, $tasks_nodes(S_insert.TODO)) = 0',
    ] + empty_biases('S_insert')
    if array:
        checks += [
            'S_insert.STORE[n_key] = DEFINED (PINT 9)',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 3',
            '$heap_owners($heap_graph(S_insert), HARRAY n_changed) = 0',
        ]
    checks += driven('S_resume', 'S_insert', 'S_insert_driven')
    if array:
        checks += ['~((HARRAY n_changed) <- S_insert_driven.ALLOCATIONS)', '(HARRAY n_held_changed) <- S_insert_driven.ALLOCATIONS']
    checks += seek('S_insert_driven', 15, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT pvalue)',
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        'S_read.STORE[n_q] = DEFINED pvalue',
    ] + empty_biases('S_read')
    if array:
        checks += [
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_old', pair('S_read', 'n_copy_child', 66, 7), pair('S_read', 'n_old', 2, 7),
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 3',
        ]
    else:
        checks += ['$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PINT 55))']
    checks += seek('S_read', 16, 'S_cow') + empty_biases('S_cow')
    if array:
        checks += [
            'S_cow.STORE[n_q] = DEFINED (PARRAY n_q_child)', 'n_q_child =/= n_old',
            pair('S_cow', 'n_q_child', 77, 7),
            '$entry_lookup(S_cow.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_entry_child))',
            'n_entry_child =/= n_old', pair('S_cow', 'n_entry_child', 2, 99),
            pair('S_cow', 'n_old', 2, 7), pair('S_cow', 'n_copy_child', 66, 7),
            pair('S_cow', 'n_held_changed', 44, 88),
            '$heap_owners($heap_graph(S_cow), HARRAY n_old) = 1',
        ]
    else:
        checks += ['S_cow.STORE[n_q] = DEFINED (PINT 77)', '$entry_lookup(S_cow.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT PNULL)']
    checks += [
        '$drive_steps(S_cow, 0) = S_cow[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_cow, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HARRAY n_a) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
    ] + empty_biases('S_done')
    if array:
        checks += [f'~((HARRAY {n}) <- S_done.ALLOCATIONS)' for n in ('n_old', 'n_changed', 'n_held_changed', 'n_copy_child', 'n_q_child', 'n_entry_child')]
    else:
        checks += ['$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
