#!/usr/bin/env python3
"""Reached table debts outlive literal entries and cancel before ordinary COW."""
import base64
import json

import array_literal_float_array_cv_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($array_float_array_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_ARRAY_RESULT n n_old poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_FLOAT_ARRAY_RESULT n n_old poperand phpType13* z n_bits i
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
dec $array_cv_review_echo(pstate, nat*) : bool
def $array_cv_review_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = n_prefix*
def $array_cv_review_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 15) = $array_cv_review_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 16) = $array_cv_review_echo(S, $ptascii("B:"))
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, raw, result):
    fields = ('STORE', 'ARRAYS', 'TODO', 'RESULT', 'LITERALREFRETAINED',
              'LITERALREFDEBTS', 'LITERALARRAYRETAINED', 'LITERALARRAYDEBTS')
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in fields]]


def payload(state, array, value):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line, inverse_line, key = (19, 27, '1') if thrown else (17, 23, '$(-2)')
    args = 'n_a, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_a n_old poperand phpType13* z n_bits i'
    inverse = 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_b n_new poperand_inverse eps z_inverse n_bits_inverse 3'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALARRAYRETAINED = eps',
        'S_initial.LITERALARRAYDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_array_key_plan(S) = ((' + args + '))',
        f'z = {line}', f'i = {key}', 'poperand = VARIABLE ($ptascii("q")) z',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)',
        '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)', 'n_q =/= n_hold',
        'S.STORE[n_q] = DEFINED (PARRAY n_old)', 'S.STORE[n_hold] = DEFINED (PARRAY n_old)',
        '~(n_q <- S.REFCELLS)', '~(n_hold <- S.REFCELLS)', payload('S', 'n_old', 2),
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
        'S.STORE[n_replacement] = DEFINED (PARRAY n_new)', 'n_new =/= n_old',
        payload('S', 'n_new', 44), '$array_float_array_key_value(S, poperand) = (n_old)',
        '$array_float_array_key_source(S, ' + args + ')',
        '$array_float_array_key_ready(S, n_a, n_old, poperand)',
        '~$array_float_array_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_array_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_array_key_source(S, n_a, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        '$heap_owners($heap_graph(S), HARRAY n_old) = ' + ('3' if thrown else '2'),
        '$heap_owners($heap_graph(S), HARRAY n_new) = 1',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_old]',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_old) = ' + ('4' if thrown else '3'),
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HCELL n_q, $tasks_nodes(pframe.TODO)) = 0',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (DIRECT (PARRAY n_old))]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)',
        ] + seek('S_entered', 14, 'S_start') + [
            'S_start.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_start, n_second) = eps',
            'S_start.ERRORHANDLER = S.ERRORHANDLER', 'S_start.STORE[n_dest] = DEFINED (PINT 99)',
            'S_start.STORE[n_later] = DEFINED (PINT 7)',
            '~((HARRAY n_a) <- S_start.ALLOCATIONS)',
            'S_start.LITERALARRAYRETAINED = [n_old]', 'S_start.LITERALARRAYDEBTS = [n_new]',
            'S_start.STORE[n_q] = DEFINED (PARRAY n_new)', payload('S_start', 'n_new', 44),
            '$heap_owners($heap_graph(S_start), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_start), HARRAY n_new) = 1',
            '$literal_reference_debt_safe(S_start, $heap_graph(S_start))',
        ]
    else:
        checks += ['S.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8))]']
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            'S_resume.STORE[n_q] = DEFINED (PARRAY n_new)',
            '$array_float_array_key_value(S_resume, poperand) = (n_new)',
            '$array_float_array_key_ready(S_resume, n_a, n_old, poperand)',
            '$array_float_array_key_source(S_resume[.ENV = eps], ' + args + ')',
            '~$array_float_array_key_ready(S_resume[.REFCELLS = n_q :: S_resume.REFCELLS][.STORE[n_q] = DEFINED (PSTRING eps)], n_a, n_old, poperand)',
            '~$array_float_array_key_ready(S_resume[.STORE[n_q] = DEFINED (PARRAY n_a)], n_a, n_old, poperand)',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.STORE = S_resume.STORE',
            'S_insert.LITERALARRAYRETAINED = [n_old]', 'S_insert.LITERALARRAYDEBTS = [n_new]',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT $(-2)) = (DIRECT (PARRAY n_new))',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
            '$heap_owners($heap_graph(S_insert), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_insert), HARRAY n_new) = 2',
            '$heap_owners($heap_graph(S_insert)[.DEBTS = eps], HARRAY n_new) = 3',
        ] + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 15, 'S_read') + [
        'S_read.LITERALARRAYRETAINED = [n_old]', 'S_read.LITERALARRAYDEBTS = [n_new]',
        'S_read.LITERALREFRETAINED = eps', 'S_read.LITERALREFDEBTS = eps',
        'S_read.GLOBALTABLE = eps', 'S_read.FRAMES = eps', 'S_read.CURRENT = eps',
        '$lookup(S_read.ENV, $ptascii("q")) = (n_q)',
        '$lookup(S_read.ENV, $ptascii("replacement")) = (n_replacement)',
        'S_read.STORE[n_q] = DEFINED (PARRAY n_new)',
        'S_read.STORE[n_replacement] = DEFINED (PARRAY n_new)', payload('S_read', 'n_new', 55),
        payload('S_read', 'n_old', 2), '$heap_graph(S_read).DEBTS = [HARRAY n_new]',
        '$heap_owners($heap_graph(S_read), HARRAY n_new) = 1',
        '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_new) = 2',
        '$heap_owners($heap_graph(S_read), HARRAY n_old) = 2',
        '$heap_count(HARRAY n_new, $machine_roots(S_read)) = 0',
        '$heap_count(HARRAY n_old, $literal_array_retained_nodes(S_read.LITERALARRAYRETAINED)) = 1',
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
        'S_zero = S_read[.ENV = $unbind(S_read.ENV, $ptascii("replacement"))]',
        'H_zero = $heap_graph(S_zero)', 'H_zero_live = $heap_prune(H_zero[.DEBTS = eps])',
        '$heap_owners(H_zero_live, HARRAY n_new) = 1',
        '(HARRAY n_new) <- H_zero_live.NODES', '~$literal_reference_debt_safe(S_zero, H_zero)',
        '(S_blocked, H_blocked) = $prune_allocations_observed(S_zero)',
        'S_blocked.COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
        'S_blocked.ALLOCATIONS = S_zero.ALLOCATIONS', 'H_blocked = H_zero',
        '$drive_checked(S_zero, 1).COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
        '$drive_steps(S_blocked, 50) = S_blocked',
    ]
    if not thrown:
        checks += ['$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT $(-2)) = eps']
    checks += seek('S_read', 10, 'S_inverse') + [
        '$array_float_array_key_plan(S_inverse) = ((n_b, n_new, poperand_inverse, eps, z_inverse, n_bits_inverse, 3))',
        f'z_inverse = {inverse_line}', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
        'n_b =/= n_a', 'S_inverse.LITERALARRAYRETAINED = [n_old]',
        'S_inverse.LITERALARRAYDEBTS = [n_new]',
        '$heap_owners($heap_graph(S_inverse), HARRAY n_new) = 1',
        'PhpStep: S_inverse ~> S_inverse_dispatch',
        'S_inverse_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_inverse) :: ptask_tail_inverse*',
        'perrorcall_inverse.RESUME = ' + inverse,
        '$error_call_valid(S_inverse_dispatch, perrorcall_inverse)',
        '$heap_owners($heap_graph(S_inverse_dispatch), HARRAY n_new) = 2',
    ] + driven('S_inverse', 'S_inverse_dispatch', 'S_inverse_driven') + seek('S_inverse_driven', 13, 'S_inverse_entered') + [
        'S_inverse_entered.FRAMES = pframe_inverse :: pframe_tail_inverse*',
        'pframe_inverse.TODO = (ERROR_HANDLER_RESULT perrorcall_inverse_entered) :: ptask_caller_inverse*',
        'perrorcall_inverse_entered.RESUME = ' + inverse,
    ] + seek('S_inverse_entered', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_after_inverse*',
        'S_inverse_resume.STORE[n_q] = DEFINED (PARRAY n_old)',
        '$array_float_array_key_value(S_inverse_resume, poperand_inverse) = (n_old)',
        '$array_float_array_key_ready(S_inverse_resume, n_b, n_new, poperand_inverse)',
        '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_new) = 1',
        '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_old) = 3',
        'PhpStep: S_inverse_resume ~> S_balance',
        'S_balance.LITERALARRAYRETAINED = eps', 'S_balance.LITERALARRAYDEBTS = eps',
        'S_balance.LITERALREFRETAINED = eps', 'S_balance.LITERALREFDEBTS = eps',
        '$entry_lookup(S_balance.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
        '$heap_graph(S_balance).DEBTS = eps',
        '$heap_owners($heap_graph(S_balance), HARRAY n_old) = 3',
        '$heap_owners($heap_graph(S_balance), HARRAY n_new) = 1',
    ] + driven('S_inverse_resume', 'S_balance', 'S_balanced') + seek('S_balanced', 16, 'S_cow') + [
        'S_cow.LITERALARRAYRETAINED = eps', 'S_cow.LITERALARRAYDEBTS = eps',
        'S_cow.STORE[n_q] = DEFINED (PARRAY n_q_array)', 'n_q_array =/= n_old',
        payload('S_cow', 'n_q_array', 77), payload('S_cow', 'n_old', 2),
        'S_cow.STORE[n_hold] = DEFINED (PARRAY n_old)',
        '$entry_lookup(S_cow.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT (PARRAY n_old))',
        'S_cow.STORE[n_replacement] = DEFINED (PARRAY n_new)', payload('S_cow', 'n_new', 55),
        '$lookup(S_cow.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_cow.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_new',
        payload('S_cow', 'n_copy', 66), '$heap_graph(S_cow).DEBTS = eps',
        '$heap_owners($heap_graph(S_cow), HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S_cow), HARRAY n_new) = 1',
        '$heap_owners($heap_graph(S_cow), HARRAY n_q_array) = 1',
        '$heap_owners($heap_graph(S_cow), HARRAY n_copy) = 1',
        'S_done = $drive_steps(S_cow, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        '~((HARRAY n_old) <- S_done.ALLOCATIONS)', '~((HARRAY n_new) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_a) <- S_done.ALLOCATIONS)', '~((HARRAY n_b) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_q_array) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("q")) = eps', '$lookup(S_done.ENV, $ptascii("replacement")) = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_inverse, 0) = S_inverse[.COMPLETION = BUDGET]',
        '$drive_steps(S_balanced, 2000) = S_done',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
