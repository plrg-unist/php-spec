#!/usr/bin/env python3
"""Reached reference deficits after entry deletion and abrupt builder cleanup."""
import base64
import json

import array_literal_float_ref_deficit_review_cases as cases
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
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
dec $literal_deficit_review_echo(pstate, nat*) : bool
def $literal_deficit_review_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = n_prefix*
def $literal_deficit_review_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 15) = $literal_deficit_review_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 16) = $literal_deficit_review_echo(S, $ptascii("B:"))
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
              ('STORE', 'ARRAYS', 'TODO', 'RESULT', 'LITERALREFRETAINED', 'LITERALREFDEBTS')]]


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line, converted, inverse_line = (21, '1', 32) if thrown else (18, '$(-2)', 26)
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps',
        'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', f'i = {converted}',
        'S.RESULT = KNOWN PNULL', 'S.CELL = n_old', 'S.ORIGIN = (porigin)',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)', '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        'S.STORE[n_old] = DEFINED (PINT 2)', 'n_old <- S.REFCELLS',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)',
        'S.STORE[n_new] = DEFINED (PINT 44)', '~(n_new <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
        '$array_float_ref_key_pending(S)', '$array_float_ref_key_source(S, ' + args + ')',
        '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$heap_owners($heap_graph(S), HCELL n_old) = ' + ('3' if thrown else '2'),
        '$heap_graph(S).DEBTS = eps', '$heap_valid($heap_graph(S))',
        '$call_descriptors_valid(S)',
        '~$array_float_ref_key_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_float_ref_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, VARIABLE ($ptascii("outside")) z, phpType13*, z, n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, z, n_bits, $(i + 1))',
        '$array_float_ref_key_plan(S[.STORE[n_key] = DEFINED (PINT 2)]) = eps',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_dispatch.RESULT = KNOWN PNULL', 'S_dispatch.LITERALREFRETAINED = eps',
        'S_dispatch.LITERALREFDEBTS = eps', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old) = ' + ('4' if thrown else '3'),
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker, 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_builder, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            'S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KINT 1) (ALIAS n_old)]',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
        ] + seek('S_entered', 14, 'S_start') + [
            'S_start.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            '$throwable_previous_id(S_start, n_second) = eps',
            'S_start.ERRORHANDLER = S.ERRORHANDLER', 'S_start.STORE[n_dest] = DEFINED (PINT 99)',
            'S_start.STORE[n_later] = DEFINED (PINT 7)',
            '~((HARRAY n_builder) <- S_start.ALLOCATIONS)',
            '$lookup(S_start.ENV, $ptascii("q")) = (n_new)', 'n_new <- S_start.REFCELLS',
            'S_start.STORE[n_old] = DEFINED (PINT 33)', 'S_start.STORE[n_new] = DEFINED (PINT 44)',
            'S_start.LITERALREFRETAINED = [n_old]', 'S_start.LITERALREFDEBTS = [n_new]',
            '$heap_owners($heap_graph(S_start), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_start), HCELL n_new) = 1',
            '$heap_count(HCELL n_new, $machine_roots(S_start)) = 2',
            '$call_descriptors_valid(S_start)', '$heap_valid($heap_graph(S_start))',
        ]
    else:
        checks += ['S.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]']
        checks += seek('S_entered', 11, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)', 'n_new <- S_resume.REFCELLS',
            'S_resume.STORE[n_old] = DEFINED (PINT 33)', 'S_resume.STORE[n_new] = DEFINED (PINT 44)',
            'S_resume.STORE[n_dest] = DEFINED (PINT 200)',
            'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
            'S_resume.LITERALREFRETAINED = eps', 'S_resume.LITERALREFDEBTS = eps',
            '$array_float_ref_key_source(S_resume, ' + args + ')',
            '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
            '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
            '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
            '~$literal_reference_plain_cell(S_resume[.PROPREFS = [{CELL n_new, SOURCES eps}]], n_new)',
            '~$array_float_ref_key_ready(S_resume[.PROPREFS = [{CELL n_new, SOURCES eps}]], n_builder, n_old, poperand)',
            '~$array_float_ref_key_ready(S_resume[.STORE[n_new] = DEFINED (PARRAY n_builder)], n_builder, n_old, poperand)',
            'S_owning = $error_read_discard(S_resume[.STORE[n_new] = DEFINED (PARRAY n_builder)], ' + marker + ')',
            'S_owning.COMPLETION = UNSUPPORTED "array literal float-key reference during throw"',
            'PhpStep: S_resume ~> S_insert',
            'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
            'S_insert.STORE = S_resume.STORE', 'S_insert.RESULT = KNOWN PNULL',
            'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = [n_new]',
            'S_insert.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT $(-2)) (ALIAS n_new)]',
            '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
            '$heap_owners($heap_graph(S_insert), HCELL n_old) = 2',
            '$heap_owners($heap_graph(S_insert), HCELL n_new) = 2',
            '$heap_graph(S_insert).DEBTS = [HCELL n_new]',
        ] + driven('S_resume', 'S_insert', 'S_start')
    checks += seek('S_start', 15, 'S_copy') + [
        'S_copy.LITERALREFRETAINED = [n_old]', 'S_copy.LITERALREFDEBTS = [n_new]',
        '$lookup(S_copy.ENV, $ptascii("q")) = eps',
        'S_copy.STORE[n_new] = DEFINED (PINT 44)', 'S_copy.STORE[n_old] = DEFINED (PINT 33)',
        '$lookup(S_copy.ENV, $ptascii("probe")) = (n_probe_cell)',
        '$lookup(S_copy.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_copy.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
        'S_copy.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_probe =/= n_copy',
        '$entry_lookup(S_copy.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_new)',
        '$entry_lookup(S_copy.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PINT 55))',
        '$heap_count(HCELL n_new, $machine_roots(S_copy)) = 1',
        '$heap_count(HCELL n_old, $machine_roots(S_copy)) = 2',
        '$heap_owners($heap_graph(S_copy), HCELL n_new) = 1',
        '$heap_owners($heap_graph(S_copy), HCELL n_old) = 2',
        '$heap_owners($heap_graph(S_copy)[.DEBTS = eps], HCELL n_new) = 2',
        '$heap_graph(S_copy).DEBTS = [HCELL n_new]',
        '(HCELL n_new) <- $heap_prune($heap_graph(S_copy)).NODES',
        '$call_descriptors_valid(S_copy)', '$heap_valid($heap_graph(S_copy))',
    ]
    if not thrown:
        checks += ['S_copy.STORE[n_dest] = DEFINED (PARRAY n_builder)',
                   'S_copy.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
                   '$literal_reference_debt_safe(S_copy, $heap_graph(S_copy))',
                   'S_exhausted = S_copy[.LITERALREFDEBTS = [n_new, n_new]]',
                   '$heap_owners($heap_graph(S_exhausted), HCELL n_new) = 0',
                   '~$literal_reference_debt_safe(S_exhausted, $heap_graph(S_exhausted))',
                   'S_refused = $prune_allocations(S_exhausted)',
                   'S_refused.COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
                   'S_refused.ALLOCATIONS = S_exhausted.ALLOCATIONS',
                   'S_refused.LITERALREFDEBTS = [n_new, n_new]',
                   '$drive(S_exhausted, 1).COMPLETION = S_refused.COMPLETION',
                   '$drive_steps(S_refused, 2000) = S_refused']
    checks += seek('S_copy', 10, 'S_inverse') + [
        '$array_float_ref_key_plan(S_inverse) = ((n_balance, n_new, poperand_inverse, eps, z_inverse, n_inverse_bits, 3))',
        f'z_inverse = {inverse_line}', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
        'n_balance =/= n_builder', '$lookup(S_inverse.ENV, $ptascii("q")) = (n_new)',
        'S_inverse.LITERALREFRETAINED = [n_old]', 'S_inverse.LITERALREFDEBTS = [n_new]',
        '$heap_owners($heap_graph(S_inverse), HCELL n_new) = 2',
    ] + seek('S_inverse', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps z_inverse n_inverse_bits 3) :: ptask_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
        'S_inverse_resume.LITERALREFRETAINED = [n_old]', 'S_inverse_resume.LITERALREFDEBTS = [n_new]',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S_inverse_resume, n_balance, n_new, poperand_inverse)',
        '$heap_owners($heap_graph(S_inverse_resume), HCELL n_new) = 2',
        'PhpStep: S_inverse_resume ~> S_balanced',
        'S_balanced.TODO = (ARRAY_NEXT n_balance eps) :: ptask_inverse*',
        'S_balanced.LITERALREFRETAINED = eps', 'S_balanced.LITERALREFDEBTS = eps',
        'S_balanced.STORE = S_inverse_resume.STORE',
        '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S_balanced), HCELL n_new) = 2',
        '$heap_owners($heap_graph(S_balanced), HCELL n_old) = 3',
        '$heap_graph(S_balanced).DEBTS = eps',
    ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_shared') + [
        'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        'S_shared.STORE[n_new] = DEFINED (PINT 77)', 'S_shared.STORE[n_old] = DEFINED (PINT 33)',
        '$lookup(S_shared.ENV, $ptascii("balanced_copy")) = (n_balanced_cell)',
        'S_shared.STORE[n_balanced_cell] = DEFINED (PARRAY n_balanced)',
        'n_balanced =/= n_probe', 'n_balanced =/= n_copy',
        '$entry_lookup(S_shared.ARRAYS[n_balanced].ITEMS, KINT 0) = (ALIAS n_new)',
        '$entry_lookup(S_shared.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_new)',
        '$entry_lookup(S_shared.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PINT 55))',
        '$entry_lookup(S_shared.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S_shared), HCELL n_new) = 3',
        '$heap_owners($heap_graph(S_shared), HCELL n_old) = 3',
        '$heap_valid($heap_graph(S_shared))', '$call_descriptors_valid(S_shared)',
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        '~((HCELL n_old) <- S_done.ALLOCATIONS)', '~((HCELL n_new) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_builder) <- S_done.ALLOCATIONS)', '~((HARRAY n_balance) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_probe) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_balanced) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("q")) = eps', '$lookup(S_done.ENV, $ptascii("outside")) = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_start, 2000) = S_done', '$drive_steps(S_balanced_driven, 2000) = S_done',
        '$drive_steps(S_dispatch_driven, 2000) = S_done',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
