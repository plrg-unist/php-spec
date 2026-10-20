#!/usr/bin/env python3
"""Reached live-CV/duplicate array insertion and supplied-throw cleanup."""
import base64
import json

import array_literal_float_key_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_task(ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i) = true
def $list_warning_frontier(S, 10) = ($array_float_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_RESULT n poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (ARRAY_VALUE n (VARIABLE n_name* z_key) eps z) :: ptask_tail*
def $list_warning_frontier(S, 13) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, result, raw):
    return [f'{result}_found = $drive_steps({start}, 1)', f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in ['STORE', 'ARRAYS', 'TODO', 'RESULT']]]


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    duplicate = name.endswith('duplicate')
    line = 13 if thrown else 16 if duplicate else 11
    args = 'n_builder, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_RESULT n_builder poperand phpType13* z n_bits i'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 10, 'S') + [
        '$array_float_key_plan(S) = ((' + args + '))',
        'S.TODO = (ARRAY_VALUE n_builder (VARIABLE ($ptascii("key")) z_key) phpType13* z) :: ptask_tail*',
        'S.RESULT = poperand', f'z = {line}', 'i = 1', 'S.ORIGIN = (porigin)',
        '$array_float_key_pending(S)', '$array_float_key_source(S, ' + args + ')',
        '$array_float_key_ready(S, n_builder, poperand)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$float_long(n_bits, true) = (1, [PRECISIONLOSS])',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_builder) = 1',
        '$heap_count(HARRAY n_builder, $pools_nodes(S.POOLS)) = 0',
        '~$array_immutable(S, n_builder)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$array_float_key_plan(S[.STORE[n_key] = UNDEFINED]) = eps',
        '$array_float_key_plan(S[.STORE[n_key] = DEFINED PNULL]) = eps',
        '$array_float_key_plan(S[.STORE[n_key] = DEFINED (PINT 1)]) = eps',
        '$array_float_key_plan(S[.STORE[n_key] = DEFINED (PFLOAT 4611686018427387904)]) = eps',
        '$array_float_key_plan(S[.STORE[n_key] = DEFINED (PFLOAT 9218868437227405312)]) = eps',
        '$array_float_key_plan(S[.STORE[n_key] = DEFINED (PFLOAT 9221120237041090560)]) = eps',
        '$array_float_key_plan(S[.STORE[n_key] = DEFINED (PFLOAT 18446744073709551616)]) = eps',
        '$array_float_key_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$array_float_key_plan(S[.BASE = BASE_VALUE (KNOWN (PINT 1))]) = eps',
        '~$array_float_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_key_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_float_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_key_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '~$array_float_key_source(S, (|S.ARRAYS|), poperand, phpType13*, z, n_bits, i)',
        '~$array_float_key_source(S, n_builder, poperand, eps, z, n_bits, i)',
        '~$array_float_key_source(S, n_builder, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_key_source(S, n_builder, poperand, phpType13*, z, n_bits, $(i + 1))',
        '~$array_float_key_source(S, n_builder, poperand, phpType13*, z, 18446744073709551616, i)',
        '~$array_float_key_source(S, n_builder, KNOWN (PARRAY n_builder), phpType13*, z, n_bits, i)',
    ]
    if thrown:
        checks += ['poperand = KNOWN (PARRAY n_value)', 'n_value =/= n_builder',
                   '$lookup(S.ENV, $ptascii("q")) = (n_q)', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
                   'S.STORE[n_q] = DEFINED (PINT 2)', 'S.STORE[n_r] = DEFINED (PINT 3)',
                   'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 1) (DIRECT (PARRAY n_prior))]',
                   'S.ARRAYS[n_prior].ITEMS = [ENTRY (KINT 0) (ALIAS n_q)]',
                   'S.ARRAYS[n_value].ITEMS = [ENTRY (KINT 1) (ALIAS n_r)]',
                   '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_value) = 1',
                   '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_prior) = 1',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_r) = 2',
                   '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
                   'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
                   '$task_nodes(' + marker + ') = [HARRAY n_builder, HARRAY n_value]']
    else:
        checks += ['poperand = VARIABLE ($ptascii("value")) z_value',
                   '$lookup(S.ENV, $ptascii("value")) = (n_value_cell)',
                   f'S.STORE[n_value_cell] = DEFINED (PINT {7 if duplicate else 20})',
                   '~(n_value_cell <- S.REFCELLS)', '$task_nodes(' + marker + ') = [HARRAY n_builder]',
                   '$array_float_key_plan(S[.REFCELLS = S.REFCELLS ++ [n_value_cell]][.STORE[n_value_cell] = DEFINED (PSTRING eps)]) = eps',
                   '$array_float_key_plan(S[.STORE[n_value_cell] = DEFINED (PARRAY n_builder)]) = eps']
        if duplicate:
            checks += ['$lookup(S.ENV, $ptascii("q")) = (n_q)', '$lookup(S.ENV, $ptascii("old")) = (n_q)',
                       'S.STORE[n_q] = DEFINED (PINT 2)',
                       'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 10)), ENTRY (KINT 1) (ALIAS n_q), ENTRY (KINT 2) (DIRECT (PINT 12))]',
                       'S.ARRAYS[n_builder].SERIAL = 3', 'S.ARRAYS[n_builder].NEXT = 3',
                       '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 3']
        else:
            checks += ['S.ARRAYS[n_builder] = $array_empty()']
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" $list_float_key_message(n_bits) z',
        'S_dispatch.RESULT = KNOWN PNULL', 'S_dispatch.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$error_call_valid(S_dispatch[.STORE[n_key] = UNDEFINED], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE z])',
        '~$error_call_valid(S_dispatch, perrorcall[.SITE = PORIGIN 999999 eps])',
        '~$call_task_valid(S_dispatch, ARRAY_KEY_FLOAT_RESULT n_builder poperand phpType13* z n_bits $(i + 1))',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ] + driven('S', 'S_dispatch_driven', 'S_dispatch') + seek('S_dispatch_driven', 3, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_builder, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entered)), HARRAY n_builder) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += ['S_object = S_dispatch[.STORE[n_q] = DEFINED (POBJECT n_second)]',
                   '$call_task_valid(S_object, ' + marker + ')',
                   '~$array_float_key_ready(S_object, n_builder, poperand)',
                   '$error_read_discard(S_object, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key element during throw"',
                   '$heap_count(HARRAY n_value, $tasks_nodes(pframe.TODO)) = 1',
                   '$heap_owners($heap_prune($heap_graph(S_entered)), HARRAY n_value) = 1']
        checks += seek('S_entered', 13, 'S_pending') + [
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER', '$throwable_previous_id(S_pending, n_second) = eps',
            'S_pending.STORE[n_dest] = DEFINED (PINT 99)', 'S_pending.STORE[n_later] = DEFINED (PINT 7)',
            '$lookup(S_pending.ENV, $ptascii("q")) = eps', '$lookup(S_pending.ENV, $ptascii("r")) = eps',
            '$lookup(S_pending.ENV, $ptascii("key")) = eps',
            '~((HARRAY n_builder) <- S_pending.ALLOCATIONS)', '~((HARRAY n_value) <- S_pending.ALLOCATIONS)',
            '~((HARRAY n_prior) <- S_pending.ALLOCATIONS)', '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            '~((HCELL n_r) <- S_pending.ALLOCATIONS)', '~((HCELL n_key) <- S_pending.ALLOCATIONS)',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)',
            'S_done.STORE[n_dest] = DEFINED (PINT 99)', 'S_done.STORE[n_later] = DEFINED (PINT 7)',
        ]
    else:
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$array_float_key_source(S_resume, ' + args + ')',
            '$array_float_key_ready(S_resume, n_builder, poperand)',
            f'S_resume.STORE[n_value_cell] = DEFINED (PINT {44 if duplicate else 33})',
            'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
            '$call_task_valid(S_resume[.STORE[n_value_cell] = UNDEFINED], ' + marker + ')',
            '$array_float_key_value(S_resume[.STORE[n_value_cell] = UNDEFINED], poperand) = eps',
            '$array_float_key_value(S_resume[.REFCELLS = S_resume.REFCELLS ++ [n_value_cell]], poperand) = eps',
            'S_unsupported = S_resume[.STORE[n_value_cell] = DEFINED (PARRAY n_builder)]',
            '$call_task_valid(S_unsupported, ' + marker + ')',
            '$array_float_key_value(S_unsupported, poperand) = eps',
            '~$array_float_key_ready(S_unsupported, n_builder, poperand)',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
            'S_insert.RESULT = KNOWN PNULL', 'S_insert.STORE = S_resume.STORE',
            f'$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 1) = (DIRECT (PINT {44 if duplicate else 33}))',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
        ]
        if duplicate:
            checks += ['S_resume.STORE[n_q] = DEFINED (PINT 33)',
                       '$lookup(S_resume.ENV, $ptascii("q")) = (n_q_new)', 'n_q_new =/= n_q',
                       'S_resume.STORE[n_q_new] = DEFINED (PINT 55)',
                       '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 2',
                       'S_insert.ARRAYS[n_builder].POSITIONS = S_resume.ARRAYS[n_builder].POSITIONS',
                       'S_insert.ARRAYS[n_builder].SERIAL = 3', 'S_insert.ARRAYS[n_builder].NEXT = 3']
        checks += driven('S_resume', 'S_insert_driven', 'S_insert')
        if duplicate:
            checks += ['$heap_owners($heap_prune($heap_graph(S_insert_driven)), HCELL n_q) = 1']
        checks += seek('S_insert_driven', 12, 'S_next') + [
            'S_next.TODO = (ARRAY_VALUE n_builder (VARIABLE ($ptascii("next")) z_next_key) eps z_next) :: ptask_next*',
            'S_next.RESULT = VARIABLE ($ptascii("tail")) z_tail',
            '$lookup(S_next.ENV, $ptascii("next")) = (n_next)', 'S_next.STORE[n_next] = DEFINED (PINT 4)',
            '$lookup(S_next.ENV, $ptascii("tail")) = (n_tail)',
            f'S_next.STORE[n_tail] = DEFINED (PINT {66 if duplicate else 44})',
            'S_done = $drive_steps(S_next, 2000)',
        ]
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HARRAY n_builder) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done', '$drive_steps(S_dispatch_driven, 2000) = S_done',
    ]


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
