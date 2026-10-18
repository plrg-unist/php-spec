#!/usr/bin/env python3
"""Reached temporary-array ownership through literal key conversion callbacks."""
import base64
import json
from types import SimpleNamespace

import array_literal_float_key_warning_review_cases as cases
import list_missing_warning_protocol as shared

NORMAL = SimpleNamespace(__file__=cases.__file__, CASES={
    'array-literal-float-review-inner-array': cases.CASES['array-literal-float-review-inner-array'],
})
HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($array_float_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (ARRAY_VALUE n (VARIABLE ($ptascii("next")) z_key) eps z) :: ptask_tail*
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, raw, result):
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in ('STORE', 'ARRAYS', 'TODO', 'RESULT')]]


def conditions(name, program, path, stdout):
    args = 'n_builder, KNOWN (PARRAY n_inner), phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_RESULT n_builder (KNOWN (PARRAY n_inner)) phpType13* z n_bits i'
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_key_plan(S) = ((' + args + '))',
        'S.TODO = (ARRAY_VALUE n_builder (VARIABLE ($ptascii("key")) 16) phpType13* z) :: ptask_tail*',
        'S.RESULT = KNOWN (PARRAY n_inner)', 'z = 16', 'i = $(-2)',
        'S.ORIGIN = (porigin)', 'n_builder =/= n_inner',
        '$array_float_key_pending(S)', '$array_float_key_ready(S, n_builder, KNOWN (PARRAY n_inner))',
        '$array_float_key_source(S, ' + args + ')',
        '$array_float_key_item(S, phpType13*, z) = ((expression, VARIABLE ($ptascii("key")) 16))',
        '$array_float_key_input_source(S, expression, KNOWN (PARRAY n_inner))',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
        '$lookup(S.ENV, $ptascii("key_alias")) = (n_key_cell)',
        'S.STORE[n_key_cell] = DEFINED (PFLOAT n_bits)',
        '$float_long(n_bits, true) = (i, [PRECISIONLOSS])',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        '$lookup(S.ENV, $ptascii("new_q")) = (n_new_q)', 'S.STORE[n_new_q] = DEFINED (PINT 44)',
        '$lookup(S.ENV, $ptascii("new_key")) = (n_new_key)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("next")) = (n_next)', 'S.STORE[n_next] = DEFINED (PINT 1)',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 8)',
        'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        'S.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (ALIAS n_q)]',
        '$heap_count(HARRAY n_builder, $pools_nodes(S.POOLS)) = 0',
        '$heap_count(HARRAY n_inner, $pools_nodes(S.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_builder) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_inner) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        '$array_float_key_plan(S[.RESULT = KNOWN (PARRAY n_builder)]) = eps',
        '$array_float_key_plan(S[.STORE[n_key_cell] = DEFINED (PINT 2)]) = eps',
        '$array_float_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$array_float_key_plan(S[.ORIGIN = eps]) = eps',
        '$array_float_key_plan(S[.CODE = eps]) = eps',
        '~$array_float_key_input_source(S[.CODE = eps], expression, KNOWN (PARRAY n_inner))',
        '~$array_float_key_source(S, n_builder, KNOWN (PARRAY n_inner), phpType13*, z, n_bits, 0)',
        '~$array_float_key_source(S, n_builder, KNOWN (PARRAY n_inner), phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_key_source(S, n_builder, KNOWN (PARRAY n_inner), eps, z, n_bits, i)',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HARRAY n_inner]',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" $list_float_key_message(n_bits) z',
        'S_dispatch.RESULT = KNOWN PNULL', 'S_dispatch.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.STORE = S.STORE',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.ERRORHANDLER.CALLBACK = eps', 'S_entered.CURRENT = (pcallcontext)',
        'S_entered.FRAMES = pframe :: eps',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker, 'perrorcall_entered.TARGET =/= eps',
        '$heap_owners($heap_prune($heap_graph(S_entered)), HARRAY n_builder) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entered)), HARRAY n_inner) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ] + seek('S_entered', 11, 'S_return') + [
        'S_return.TODO = (' + marker + ') :: ptask_tail*',
        '$array_float_key_source(S_return, ' + args + ')',
        '$array_float_key_value(S_return, KNOWN (PARRAY n_inner)) = (PARRAY n_inner)',
        'S_return.ERRORHANDLER = S.ERRORHANDLER', 'S_return.FRAMES = eps',
        '~((HCELL n_key_cell) <- S_return.ALLOCATIONS)',
        '$lookup(S_return.ENV, $ptascii("key_alias")) = eps',
        '$lookup(S_return.ENV, $ptascii("key")) = (n_new_key)',
        '$lookup(S_return.ENV, $ptascii("q")) = (n_new_q)',
        'S_return.STORE[n_q] = DEFINED (PINT 33)', 'S_return.STORE[n_new_q] = DEFINED (PINT 44)',
        'S_return.STORE[n_dest] = DEFINED (PINT 200)',
        'S_return.STORE[n_next] = DEFINED (PINT 4)', 'S_return.STORE[n_tail] = DEFINED (PINT 66)',
        'S_return.ARRAYS[n_builder].ITEMS = S.ARRAYS[n_builder].ITEMS',
        '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_inner) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 1',
        'PhpStep: S_return ~> S_insert',
        'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
        'S_insert.RESULT = KNOWN PNULL', 'S_insert.STORE = S_return.STORE',
        'S_insert.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT $(-2)) (DIRECT (PARRAY n_inner))]',
        'S_insert.ARRAYS[n_builder].NEXT = 1',
        'S_insert.ARRAYS[n_inner] = S_return.ARRAYS[n_inner]',
        '$heap_owners($heap_prune($heap_graph(S_insert)), HARRAY n_inner) = 1',
    ] + driven('S_return', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 14, 'S_next_item') + [
        'S_next_item.TODO = (ARRAY_VALUE n_builder (VARIABLE ($ptascii("next")) 17) eps 17) :: ptask_tail*',
        'S_next_item.RESULT = VARIABLE ($ptascii("tail")) 17',
        '$array_float_key_plan(S_next_item) = eps',
        'S_next_item.STORE[n_next] = DEFINED (PINT 4)', 'S_next_item.STORE[n_tail] = DEFINED (PINT 66)',
        'PhpStep: S_next_item ~> S_later_insert',
        '$entry_lookup(S_later_insert.ARRAYS[n_builder].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        'S_later_insert.ARRAYS[n_builder].NEXT = 5',
        'S_done = $drive_steps(S_next_item, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HARRAY n_builder) <- S_done.ALLOCATIONS)', '~((HARRAY n_inner) <- S_done.ALLOCATIONS)',
        '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HCELL n_key_cell) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("dest")) = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 2000) = S_done',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(NORMAL, conditions, HELPERS) else 1)
