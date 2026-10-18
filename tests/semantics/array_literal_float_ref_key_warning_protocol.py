#!/usr/bin/env python3
"""Reached reference-owner transfer, scalar retargeting, and throw cleanup."""
import base64
import json

import array_literal_float_ref_key_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_task(ARRAY_KEY_FLOAT_REF_RESULT n n_old poperand phpType13* z n_bits i) = true
def $list_warning_frontier(S, 10) = ($array_float_ref_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n n_old poperand phpType13* z n_bits i) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 13) = true
  -- if $array_float_ref_key_plan(S) = ((n, n_old, poperand, phpType13*, 16, n_bits, i))
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def driven(start, raw, result):
    return [f'{result}_found = $drive_steps({start}, 1)', f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in
              ('STORE', 'ARRAYS', 'TODO', 'RESULT', 'LITERALREFRETAINED')]]


def conditions(name, program, path, stdout):
    thrown = name.endswith('scalar-throw')
    repeated = name.endswith('repeated-scalar')
    line, key = (14, 1) if thrown else (12, 2)
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps'] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'S.TODO = (ARRAY_REF_VALUE n_builder (VARIABLE ($ptascii("key")) z_key) phpType13* z) :: ptask_tail*',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', f'i = {key}',
        'S.CELL = n_old', 'S.RESULT = KNOWN PNULL', 'S.ORIGIN = (porigin)',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)', '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        'S.STORE[n_old] = DEFINED (PINT 2)', 'n_old <- S.REFCELLS',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        f'$float_long(n_bits, true) = ({key}, [PRECISIONLOSS])',
        'S.LITERALREFRETAINED = eps', '$array_float_ref_key_pending(S)',
        '$array_float_ref_key_source(S, ' + args + ')',
        '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_builder) = 1',
        f'$heap_owners($heap_prune($heap_graph(S)), HCELL n_old) = {3 if thrown else 2}',
        '$heap_count(HARRAY n_builder, $pools_nodes(S.POOLS)) = 0',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$array_float_ref_key_plan(S[.STORE[n_key] = UNDEFINED]) = eps',
        '$array_float_ref_key_plan(S[.STORE[n_key] = DEFINED PNULL]) = eps',
        '$array_float_ref_key_plan(S[.STORE[n_key] = DEFINED (PINT 2)]) = eps',
        '$array_float_ref_key_plan(S[.STORE[n_key] = DEFINED (PFLOAT 4611686018427387904)]) = eps',
        '$array_float_ref_key_plan(S[.STORE[n_key] = DEFINED (PFLOAT 9218868437227405312)]) = eps',
        '$array_float_ref_key_plan(S[.STORE[n_key] = DEFINED (PFLOAT 9221120237041090560)]) = eps',
        '$array_float_ref_key_plan(S[.STORE[n_old] = DEFINED (PARRAY n_builder)]) = eps',
        '$array_float_ref_key_plan(S[.RESULT = REFERENCE n_old]) = eps',
        '$array_float_ref_key_plan(S[.BASE = BASE_VALUE (KNOWN (PINT 1))]) = eps',
        '~$array_float_ref_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_ref_key_source(S[.SOURCES = eps], ' + args + ')',
        '~$array_float_ref_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_ref_key_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '~$array_float_ref_key_source(S, (|S.ARRAYS|), n_old, poperand, phpType13*, z, n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, (|S.STORE|), poperand, phpType13*, z, n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, KNOWN PNULL, phpType13*, z, n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, z, n_bits, $(i + 1))',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, z, 18446744073709551616, i)',
    ]
    if thrown:
        checks += ['S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_old)]',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
                   'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
                   '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
                   '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)']
    else:
        checks += [f'S.ARRAYS[n_builder].ITEMS = {"eps" if repeated else "[ENTRY (KINT 0) (DIRECT (PINT 9))]"}']
    checks += ['PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" $list_float_key_message(n_bits) z',
        'S_dispatch.RESULT = KNOWN PNULL', 'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_dispatch.LITERALREFRETAINED = eps',
        f'$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_old) = {4 if thrown else 3}',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$error_call_valid(S_dispatch[.ENV = $unbind($unbind(S_dispatch.ENV, $ptascii("q")), $ptascii("key"))], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE z])',
        '~$error_call_valid(S_dispatch, perrorcall[.SITE = PORIGIN 999999 eps])',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_newref = S_dispatch[.ENV = (BIND ($ptascii("q")) n_key) :: $unbind(S_dispatch.ENV, $ptascii("q"))][.REFCELLS = S_dispatch.REFCELLS ++ [n_key]][.STORE[n_key] = DEFINED (PARRAY n_builder)]',
        '$call_task_valid(S_newref, ' + marker + ')',
        '$array_float_ref_key_value(S_newref, n_old, poperand) = eps',
        '~$array_float_ref_key_ready(S_newref, n_builder, n_old, poperand)',
        '$error_read_discard(S_newref, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 3, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_builder, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += ['S_object = S_dispatch[.STORE[n_old] = DEFINED (POBJECT n_second)]',
                   '$call_task_valid(S_object, ' + marker + ')',
                   '~$array_float_ref_key_ready(S_object, n_builder, n_old, poperand)',
                   '$error_read_discard(S_object, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key reference during throw"']
        checks += seek('S_entered', 12, 'S_pending') + [
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER', '$throwable_previous_id(S_pending, n_second) = eps',
            'S_pending.STORE[n_dest] = DEFINED (PINT 99)', 'S_pending.STORE[n_later] = DEFINED (PINT 7)',
            '$lookup(S_pending.ENV, $ptascii("q")) = (n_new)', 'n_new =/= n_old',
            'S_pending.STORE[n_new] = DEFINED (PINT 44)', '~(n_new <- S_pending.REFCELLS)',
            'S_pending.STORE[n_old] = DEFINED (PINT 33)',
            'S_pending.LITERALREFRETAINED = [n_old]',
            '~((HARRAY n_builder) <- S_pending.ALLOCATIONS)', '(HCELL n_old) <- S_pending.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_old) = 2',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)',
        ]
    else:
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$array_float_ref_key_source(S_resume, ' + args + ')',
            '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
            'S_resume.STORE[n_old] = DEFINED (PINT 33)' if not repeated else 'S_resume.STORE[n_old] = DEFINED (PINT 31)',
            'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
            'S_badline = S_resume[.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* $(z + 1) n_bits i) :: ptask_tail*]',
            '~$call_descriptors_valid(S_badline)',
            '$drive(S_badline, 1).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
            'S_insert.STORE = S_resume.STORE', 'S_insert.RESULT = KNOWN PNULL',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
        ]
        if repeated:
            checks += ['$lookup(S_resume.ENV, $ptascii("q")) = (n_new)', 'n_new =/= n_old',
                       'S_resume.STORE[n_new] = DEFINED (PINT 41)', '~(n_new <- S_resume.REFCELLS)',
                       '$array_float_ref_key_value(S_resume, n_old, poperand) = (DIRECT (PINT 41))',
                       'S_insert.LITERALREFRETAINED = [n_old]',
                       '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 2) = (DIRECT (PINT 41))']
        else:
            checks += ['$lookup(S_resume.ENV, $ptascii("q")) = (n_old)',
                       '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_old)',
                       'S_insert.LITERALREFRETAINED = eps',
                       '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 2) = (ALIAS n_old)']
        checks += driven('S_resume', 'S_insert', 'S_insert_driven')
        if repeated:
            checks += seek('S_insert_driven', 13, 'S_second') + [
                '$array_float_ref_key_plan(S_second) = ((n_builder_second, n_old, poperand_second, eps, 16, n_bits, i))',
                'n_builder_second =/= n_builder', 'S_second.LITERALREFRETAINED = [n_old]',
                '$lookup(S_second.ENV, $ptascii("q")) = (n_old)',
                '$heap_owners($heap_prune($heap_graph(S_second)), HCELL n_old) = 3',
            ] + seek('S_second', 11, 'S_second_resume') + [
                'S_second_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_builder_second n_old poperand_second eps 16 n_bits i) :: ptask_second*',
                '$array_float_ref_key_value(S_second_resume, n_old, poperand_second) = (DIRECT (PINT 42))',
                'S_second_resume.LITERALREFRETAINED = [n_old]',
                'PhpStep: S_second_resume ~> S_second_insert',
                'S_second_insert.LITERALREFRETAINED = [n_old, n_old]',
                '$entry_lookup(S_second_insert.ARRAYS[n_builder_second].ITEMS, KINT 2) = (DIRECT (PINT 42))',
                '$literal_reference_retained_nodes(S_second_insert.LITERALREFRETAINED) = [HCELL n_old, HCELL n_old]',
            ] + driven('S_second_resume', 'S_second_insert', 'S_second_driven') + [
                '$heap_owners($heap_prune($heap_graph(S_second_driven)), HCELL n_old) = 3',
                'S_done = $drive_steps(S_second_driven, 2000)',
            ]
        else:
            checks += ['S_done = $drive_steps(S_insert_driven, 2000)']
    checks += ['S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
               'S_done.FRAMES = eps', 'S_done.HELD = eps',
               '~((HARRAY n_builder) <- S_done.ALLOCATIONS)',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
               '$drive_steps(S, 2000) = S_done', '$drive_steps(S_dispatch_driven, 2000) = S_done']
    if thrown or repeated:
        retained = '[n_old, n_old]' if repeated else '[n_old]'
        count = 2 if repeated else 1
        checks += [f'S_done.LITERALREFRETAINED = {retained}', 'S_done.STORE[n_old] = DEFINED (PINT 66)',
                   '(HCELL n_old) <- S_done.ALLOCATIONS',
                   f'$heap_owners($heap_graph(S_done), HCELL n_old) = {count}',
                   f'$heap_count(HCELL n_old, $machine_roots(S_done)) = {count}',
                   '$release_temporaries(S_done).LITERALREFRETAINED = S_done.LITERALREFRETAINED',
                   '$heap_collect($heap_graph(S_done)).NODES = $heap_graph(S_done).NODES',
                   '$literal_reference_retained_valid(S_done, S_done.LITERALREFRETAINED)',
                   '~$literal_reference_retained_valid(S_done, [(|S_done.STORE|)])',
                   '$prune_allocations(S_done[.LITERALREFRETAINED = eps]).LITERALREFRETAINED = eps',
                   '~((HCELL n_old) <- $prune_allocations(S_done[.LITERALREFRETAINED = eps]).ALLOCATIONS)']
        if repeated:
            checks += ['P = $ppstart(0, ' + program + ', $base64(' + json.dumps(base64.b64encode(bytes(path)).decode()) + '))',
                       'P.COMPLETION = PPCNORMAL', '$ppimage(P, false) =/= eps',
                       'P_bad = P[.FOLD.MEMORY.LITERALREFRETAINED = [n_old]]', '$ppimage(P_bad, false) = eps']
    else:
        checks += ['S_done.LITERALREFRETAINED = eps', '~((HCELL n_old) <- S_done.ALLOCATIONS)']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
