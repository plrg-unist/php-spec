#!/usr/bin/env python3
"""Reached old-reference retention versus same-cell ownership transfer."""
import base64
import json

import array_literal_float_ref_key_warning_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($array_float_ref_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n n_old poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_KEY_FLOAT_REF_RESULT n n_old poperand phpType13* z n_bits i
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (ARRAY_VALUE n (VARIABLE ($ptascii("next")) z_key) eps z) :: ptask_tail*
dec $literal_ref_review_echo(pstate, nat*) : bool
def $literal_ref_review_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = n_prefix*
def $literal_ref_review_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 15) = $literal_ref_review_echo(S, $ptascii("G:"))
def $list_warning_frontier(S, 16) = $literal_ref_review_echo(S, $ptascii("A:"))
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, raw, result):
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in
              ('STORE', 'ARRAYS', 'TODO', 'RESULT', 'LITERALREFRETAINED')]]


def conditions(name, program, path, stdout):
    retarget = name.endswith('scalar-retarget')
    line = 15 if retarget else 13
    converted = '$(-2)' if retarget else '1'
    value = f'VARIABLE ($ptascii("q")) {line}'
    args = f'n_builder, n_old, {value}, phpType13*, z, n_bits, i'
    marker = f'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old ({value}) phpType13* z n_bits i'
    retained = '[n_old]' if retarget else 'eps'
    item = 'DIRECT (PINT 44)' if retarget else 'ALIAS n_old'
    result = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        f'S.TODO = (ARRAY_REF_VALUE n_builder (VARIABLE ($ptascii("key")) {line}) phpType13* z) :: ptask_tail*',
        f'z = {line}', f'i = {converted}', 'S.CELL = n_old', 'S.RESULT = KNOWN PNULL',
        'S.BASE = BASE_VALUE (KNOWN PNULL)', 'S.LITERALREFRETAINED = eps',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)', '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        'S.STORE[n_old] = DEFINED (PINT 2)', 'n_old <- S.REFCELLS',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
        'S.STORE[n_key_cell] = DEFINED (PFLOAT n_bits)',
        '$lookup(S.ENV, $ptascii("next")) = (n_next)',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 8)',
        'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$heap_count(HARRAY n_builder, $pools_nodes(S.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_builder) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_old) = 2',
        '$array_float_ref_key_pending(S)', '$array_float_ref_key_source(S, ' + args + ')',
        '$array_float_ref_key_ready(S, n_builder, n_old, ' + value + ')',
        '$array_float_ref_key_value(S, n_old, ' + value + ') = (ALIAS n_old)',
        '$array_float_ref_key_item(S, phpType13*, z) = ((VARIABLE ($ptascii("key")) ' + str(line) + ', ' + value + '))',
        '$array_float_ref_key_plan(S[.STORE[n_key_cell] = DEFINED (PINT 2)]) = eps',
        '$array_float_ref_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$array_float_ref_key_plan(S[.RESULT = REFERENCE n_old]) = eps',
        '$array_float_ref_key_plan(S[.ORIGIN = eps]) = eps',
        '$array_float_ref_key_plan(S[.CODE = eps]) = eps',
        '~$array_float_ref_key_source(S, n_builder, n_old, ' + value + ', phpType13*, z, n_bits, 0)',
        '~$array_float_ref_key_source(S, n_builder, n_old, ' + value + ', phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, ' + value + ', eps, z, n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, VARIABLE ($ptascii("outside")) z, phpType13*, z, n_bits, i)',
        '$literal_reference_retained_valid(S, eps)',
        '$literal_reference_retained_valid(S, [n_old, n_old])',
        '~$literal_reference_retained_valid(S, [|S.STORE|])',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" $list_float_key_message(n_bits) z',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_dispatch.RESULT = KNOWN PNULL', 'S_dispatch.LITERALREFRETAINED = eps',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_old) = 3',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker, 'perrorcall_entered.TARGET =/= eps',
        '$heap_owners($heap_prune($heap_graph(S_entered)), HCELL n_old) = 3',
        '$heap_owners($heap_prune($heap_graph(S_entered)), HARRAY n_builder) = 1',
        '$call_descriptors_valid(S_entered)',
    ] + seek('S_entered', 11, 'S_return') + [
        'S_return.TODO = (' + marker + ') :: ptask_tail*',
        'S_return.FRAMES = eps', 'S_return.ERRORHANDLER = S.ERRORHANDLER',
        'S_return.LITERALREFRETAINED = eps', 'S_return.STORE[n_old] = DEFINED (PINT 33)',
        'S_return.STORE[n_next] = DEFINED (PINT 4)', 'S_return.STORE[n_tail] = DEFINED (PINT 66)',
        '$array_float_ref_key_source(S_return, ' + args + ')',
        '$array_float_ref_key_source(S_return[.ENV = eps], ' + args + ')',
        '$array_float_ref_key_ready(S_return, n_builder, n_old, ' + value + ')',
        'S_return.ARRAYS[n_builder] = S.ARRAYS[n_builder]',
    ]
    if retarget:
        result += [
            '$lookup(S.ENV, $ptascii("key_alias")) = (n_key_cell)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)',
            '$lookup(S_return.ENV, $ptascii("q")) = (n_current)', 'n_current =/= n_old',
            '~(n_current <- S_return.REFCELLS)', 'S_return.STORE[n_current] = DEFINED (PINT 44)',
            '$lookup(S_return.ENV, $ptascii("key")) = (n_new_key)',
            '~((HCELL n_key_cell) <- S_return.ALLOCATIONS)',
            '$lookup(S_return.ENV, $ptascii("key_alias")) = eps',
            'S_return.STORE[n_dest] = DEFINED (PINT 200)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old) = 2',
            'S_owning_ref = S_return[.STORE[n_current] = DEFINED (PARRAY n_builder)][.REFCELLS = n_current :: S_return.REFCELLS]',
            '~$array_float_ref_key_ready(S_owning_ref, n_builder, n_old, ' + value + ')',
            '$array_float_ref_key_source(S_owning_ref, ' + args + ')',
            'S_refused = $error_read_discard(S_owning_ref, ' + marker + ')',
            'S_refused.COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
            'S_refused.LITERALREFRETAINED = eps',
        ]
    else:
        result += [
            '$lookup(S_return.ENV, $ptascii("q")) = (n_old)',
            '$lookup(S_return.ENV, $ptascii("outside")) = (n_old)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old) = 3',
        ]
    result += [
        '$array_float_ref_key_value(S_return, n_old, ' + value + ') = (' + item + ')',
        'PhpStep: S_return ~> S_insert',
        'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
        'S_insert.RESULT = KNOWN PNULL', 'S_insert.STORE = S_return.STORE',
        'S_insert.LITERALREFRETAINED = ' + retained,
        'S_insert.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT ' + converted + ') (' + item + ')]',
        '$heap_owners($heap_prune($heap_graph(S_insert)), HCELL n_old) = ' + ('2' if retarget else '3'),
        '$literal_reference_retained_valid(S_insert, S_insert.LITERALREFRETAINED)',
    ] + driven('S_return', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 14, 'S_next_item') + [
        f'S_next_item.TODO = (ARRAY_VALUE n_builder (VARIABLE ($ptascii("next")) {line + 1}) eps {line + 1}) :: ptask_tail*',
        f'S_next_item.RESULT = VARIABLE ($ptascii("tail")) {line + 1}',
        '$array_float_ref_key_plan(S_next_item) = eps',
        'PhpStep: S_next_item ~> S_later_insert',
        '$entry_lookup(S_later_insert.ARRAYS[n_builder].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        'S_later_insert.ARRAYS[n_builder].NEXT = 5',
        'S_later_insert.LITERALREFRETAINED = ' + retained,
    ] + seek('S_next_item', 15 if retarget else 16, 'S_copy') + [
        '$lookup(S_copy.ENV, $ptascii("dest")) = (n_dest_cell)',
        'S_copy.STORE[n_dest_cell] = DEFINED (PARRAY n_builder)',
        '$lookup(S_copy.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_copy.STORE[n_copy_cell] = DEFINED (PARRAY n_copy_array)', 'n_copy_array =/= n_builder',
        'S_copy.LITERALREFRETAINED = ' + retained,
        '$lookup(S_copy.ENV, $ptascii("outside")) = eps',
        '$call_descriptors_valid(S_copy)', '$heap_valid($heap_graph(S_copy))',
    ]
    if retarget:
        result += [
            '$entry_lookup(S_copy.ARRAYS[n_builder].ITEMS, KINT $(-2)) = (DIRECT (PINT 44))',
            '$entry_lookup(S_copy.ARRAYS[n_copy_array].ITEMS, KINT $(-2)) = (DIRECT (PINT 88))',
            'S_copy.STORE[n_current] = DEFINED (PINT 55)',
            '$lookup(S_copy.ENV, $ptascii("probe")) = (n_probe_cell)',
            '$lookup(S_copy.ENV, $ptascii("probe_copy")) = (n_probe_copy_cell)',
            'S_copy.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
            'S_copy.STORE[n_probe_copy_cell] = DEFINED (PARRAY n_probe_copy)', 'n_probe =/= n_probe_copy',
            '$entry_lookup(S_copy.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_old)',
            '$entry_lookup(S_copy.ARRAYS[n_probe_copy].ITEMS, KINT 0) = (ALIAS n_old)',
            'S_copy.STORE[n_old] = DEFINED (PINT 77)',
            '$heap_owners($heap_prune($heap_graph(S_copy)), HCELL n_old) = 3',
        ]
    else:
        result += [
            '$lookup(S_copy.ENV, $ptascii("q")) = eps',
            '$entry_lookup(S_copy.ARRAYS[n_builder].ITEMS, KINT 1) = (ALIAS n_old)',
            '$entry_lookup(S_copy.ARRAYS[n_copy_array].ITEMS, KINT 1) = (DIRECT (PINT 55))',
            'S_copy.STORE[n_old] = DEFINED (PINT 33)',
            '$heap_owners($heap_prune($heap_graph(S_copy)), HCELL n_old) = 1',
        ]
    result += [
        'S_done = $drive_steps(S_copy, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = ' + retained,
        '~((HARRAY n_builder) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy_array) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("dest")) = eps', '$lookup(S_done.ENV, $ptascii("q")) = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 2000) = S_done',
        '$drive_steps(S_dispatch_driven, 2000) = S_done',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if retarget:
        result += [
            'S_done.STORE[n_old] = DEFINED (PINT 77)', '(HCELL n_old) <- S_done.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_old) = 1',
            '$literal_reference_retained_nodes(S_done.LITERALREFRETAINED) = [HCELL n_old]',
            '~((HARRAY n_probe) <- S_done.ALLOCATIONS)', '~((HARRAY n_probe_copy) <- S_done.ALLOCATIONS)',
            '~((HCELL n_current) <- S_done.ALLOCATIONS)', '~((HCELL n_key_cell) <- S_done.ALLOCATIONS)',
        ]
    else:
        result += ['~((HCELL n_old) <- S_done.ALLOCATIONS)']
    return result


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
