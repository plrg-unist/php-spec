#!/usr/bin/env python3
"""Reached biased sharing, stable transfer and canonical deficit cancellation."""
import base64
import json

import array_literal_float_ref_deficit_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = ($array_float_ref_key_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n n_old poperand phpType13* z n_bits i) :: ptask_tail*
dec $literal_deficit_echo(pstate, nat*) : bool
def $literal_deficit_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = n_prefix*
def $literal_deficit_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 50) = $literal_deficit_echo(S, $ptascii("A:"))
def $list_warning_frontier(S, 51) = $literal_deficit_echo(S, $ptascii("M:"))
def $list_warning_frontier(S, 52) = $literal_deficit_echo(S, $ptascii("B:"))
def $list_warning_frontier(S, 53) = $literal_deficit_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 54) = $literal_deficit_echo(S, $ptascii("G:"))
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


def array_at(state, name, ident):
    return [f'$lookup({state}.ENV, $ptascii("{name}")) = (n_{ident}_cell)',
            f'{state}.STORE[n_{ident}_cell] = DEFINED (PARRAY n_{ident})']


def conditions(name, program, path, stdout):
    stable = name.endswith('stable-bias')
    repeated = name.endswith('multiplicity')
    first_line = 14 if repeated else 15
    first_key = 1 if stable or repeated else 2
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    old_value = 31 if repeated else 33
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps',
        'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {first_line}', f'i = {first_key}',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)', '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        'S.STORE[n_old] = DEFINED (PINT 2)', 'n_old <- S.REFCELLS',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)', 'n_new =/= n_old',
        'S.STORE[n_new] = DEFINED (PINT 44)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        f'$float_long(n_bits, true) = ({first_key}, [PRECISIONLOSS])',
        'S.RESULT = KNOWN PNULL', 'S.CELL = n_old',
        '$array_float_ref_key_source(S, ' + args + ')', '$array_float_ref_key_pending(S)',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$heap_owners($heap_graph(S), HCELL n_old) = 2', '$heap_graph(S).DEBTS = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$array_float_ref_key_source(S[.CODE = eps], ' + args + ')',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, $(z + 1), n_bits, i)',
        '~$array_float_ref_key_source(S, n_builder, n_old, poperand, phpType13*, z, n_bits, $(i + 1))',
        '$array_float_ref_key_plan(S[.STORE[n_key] = DEFINED (PFLOAT 18446744073709551616)]) = eps',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_dispatch.LITERALREFRETAINED = eps', 'S_dispatch.LITERALREFDEBTS = eps',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_old) = 3',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$error_call_valid(S_dispatch[.ENV = $unbind($unbind(S_dispatch.ENV, $ptascii("q")), $ptascii("key"))], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)', 'n_new <- S_resume.REFCELLS',
        f'S_resume.STORE[n_old] = DEFINED (PINT {old_value})', 'S_resume.STORE[n_new] = DEFINED (PINT 44)',
        '$array_float_ref_key_source(S_resume, ' + args + ')',
        '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
        '$literal_reference_plain_cell(S_resume, n_old)', '$literal_reference_plain_cell(S_resume, n_new)',
        '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
        '~$array_float_ref_key_ready(S_resume[.STORE[n_new] = DEFINED (PARRAY n_builder)], n_builder, n_old, poperand)',
        '~$array_float_ref_key_ready(S_resume[.STORE[n_old] = DEFINED (PARRAY n_builder)], n_builder, n_old, poperand)',
        'S_resume.LITERALREFRETAINED = eps', 'S_resume.LITERALREFDEBTS = eps',
        'PhpStep: S_resume ~> S_insert',
        'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
        'S_insert.STORE = S_resume.STORE', 'S_insert.RESULT = KNOWN PNULL',
        'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = [n_new]',
        f'$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT {first_key}) = (ALIAS n_new)',
        '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
        '$heap_graph(S_insert).DEBTS = [HCELL n_new]',
        '$literal_reference_retain(S_insert, n_new).LITERALREFDEBTS = eps',
        '$literal_reference_retain(S_insert, n_new).LITERALREFRETAINED = [n_old]',
        '$literal_reference_owe(S_insert, n_old).LITERALREFRETAINED = eps',
        '$literal_reference_owe(S_insert, n_old).LITERALREFDEBTS = [n_new]',
        '$literal_reference_owe($literal_reference_retain(S_insert, n_new), n_new) = S_insert',
        '$literal_reference_retain($literal_reference_owe(S_insert, n_old), n_old) = S_insert',
        '$literal_reference_debts_valid(S_insert, S_insert.LITERALREFDEBTS)',
        '~$literal_reference_debts_valid(S_insert, [n_old])',
        '~$literal_reference_debts_valid(S_insert, [(|S_insert.STORE|)])',
        '$literal_reference_debt_safe(S_insert, $heap_graph(S_insert))',
    ] + driven('S_resume', 'S_insert', 'S_insert_driven')
    if stable or repeated:
        second_line = 18 if repeated else 19
        second_key = 2
        checks += seek('S_insert_driven', 10, 'S_second') + [
            f'$array_float_ref_key_plan(S_second) = ((n_second, n_acquired, poperand_second, eps, {second_line}, n_second_bits, {second_key}))',
            'S_second.LITERALREFRETAINED = [n_old]', 'S_second.LITERALREFDEBTS = [n_new]',
            f'n_acquired = {"n_old" if repeated else "n_new"}',
        ] + seek('S_second', 11, 'S_second_resume') + [
            f'S_second_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_second n_acquired poperand_second eps {second_line} n_second_bits {second_key}) :: ptask_second*',
            '$lookup(S_second_resume.ENV, $ptascii("q")) = (n_new)',
            '$array_float_ref_key_value(S_second_resume, n_acquired, poperand_second) = (ALIAS n_new)',
            'S_second_resume.LITERALREFRETAINED = [n_old]', 'S_second_resume.LITERALREFDEBTS = [n_new]',
            'PhpStep: S_second_resume ~> S_second_insert',
            f'S_second_insert.TODO = (ARRAY_NEXT n_second eps) :: ptask_second*',
            f'S_second_insert.LITERALREFRETAINED = {"[n_old, n_old]" if repeated else "[n_old]"}',
            f'S_second_insert.LITERALREFDEBTS = {"[n_new, n_new]" if repeated else "[n_new]"}',
            '$entry_lookup(S_second_insert.ARRAYS[n_second].ITEMS, KINT 2) = (ALIAS n_new)',
        ] + driven('S_second_resume', 'S_second_insert', 'S_second_driven')
        start = 'S_second_driven'
    else:
        start = 'S_insert_driven'
    checks += seek(start, 50, 'S_a') + array_at('S_a', 'a', 'a') + array_at('S_a', 'copy', 'copy') + [
        'n_a = n_builder', 'n_copy =/= n_a', '$lookup(S_a.ENV, $ptascii("q")) = eps',
        f'S_a.STORE[n_old] = DEFINED (PINT {32 if repeated else 33})',
        f'S_a.STORE[n_new] = DEFINED (PINT {44 if stable or repeated else 55})',
        f'S_a.LITERALREFRETAINED = {"[n_old, n_old]" if repeated else "[n_old]"}',
        f'S_a.LITERALREFDEBTS = {"[n_new, n_new]" if repeated else "[n_new]"}',
        f'$entry_lookup(S_a.ARRAYS[n_a].ITEMS, KINT {first_key}) = (ALIAS n_new)',
        f'$entry_lookup(S_a.ARRAYS[n_copy].ITEMS, KINT {first_key}) = ({"DIRECT (PINT 55)" if stable or repeated else "ALIAS n_new"})',
        '$heap_valid($heap_graph(S_a))', '$call_descriptors_valid(S_a)',
        '$literal_reference_debt_safe(S_a, $heap_graph(S_a))',
        '$heap_owners($heap_graph(S_a), HCELL n_new) = 1' if stable or repeated else '$($heap_owners($heap_graph(S_a), HCELL n_new) > 1)',
    ]
    if stable:
        checks += [
            '~((HARRAY n_second) <- S_a.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_a)[.DEBTS = eps], HCELL n_new) = 2',
            'S_zero = S_a[.LITERALREFDEBTS = [n_new, n_new]]',
            '$literal_reference_debts_valid(S_zero, S_zero.LITERALREFDEBTS)',
            '$heap_valid($heap_graph(S_zero))', '$heap_owners($heap_graph(S_zero), HCELL n_new) = 0',
            '~$literal_reference_debt_safe(S_zero, $heap_graph(S_zero))',
            'S_blocked = $literal_reference_debt_check(S_zero)',
            'S_blocked.COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
            'S_blocked.STORE = S_zero.STORE', 'S_blocked.ALLOCATIONS = S_zero.ALLOCATIONS',
            '$prune_allocations(S_zero) = S_blocked', '$drive_steps(S_blocked, 2000) = S_blocked',
            '$drive(S_blocked, 2000) = S_blocked',
            'S_terminal = S_a[.TODO = eps][.FRAMES = eps][.CURRENT = eps]',
            '~$literal_reference_debt_safe(S_terminal, $heap_graph(S_terminal))',
            '$literal_reference_debt_check(S_terminal).COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
            'S_owning = S_a[.STORE[n_new] = DEFINED (PARRAY n_a)]',
            '$literal_reference_debts_valid(S_owning, S_owning.LITERALREFDEBTS)',
            '~$literal_reference_debt_safe(S_owning, $heap_graph(S_owning))',
            '$prune_allocations(S_owning).ALLOCATIONS = S_owning.ALLOCATIONS',
            '$prune_allocations(S_owning).COMPLETION = UNSUPPORTED "array literal reference deficit lifetime"',
            'H_debt = {NODES ([HARRAY 0, HARRAY 1, HCELL 2]), EDGES ([HEDGE (HARRAY 0) (HCELL 2), HEDGE (HARRAY 1) (HCELL 2)]), ROOTS ([HARRAY 1, HCELL 2]), DEBTS ([HCELL 2])}',
            '$heap_valid(H_debt)', '$heap_owners(H_debt, HCELL 2) = 2',
            'H_pruned = $heap_prune(H_debt)', 'H_pruned.NODES = [HARRAY 1, HCELL 2]',
            'H_pruned.EDGES = [HEDGE (HARRAY 1) (HCELL 2)]', 'H_pruned.ROOTS = H_debt.ROOTS',
            'H_pruned.DEBTS = [HCELL 2]', '$heap_owners(H_pruned, HCELL 2) = 1',
            '$heap_prune(H_pruned) = H_pruned', '$heap_owners(H_debt[.DEBTS = eps], HCELL 2) = 3',
            '$heap_prune(H_debt[.DEBTS = eps]) = H_pruned[.DEBTS = eps]',
            '~$heap_valid(H_debt[.DEBTS = [HCELL 99]])',
            '~$heap_valid(H_debt[.DEBTS = [HCELL 2, HCELL 2, HCELL 2, HCELL 2]])',
        ]
    if repeated:
        checks += seek('S_a', 10, 'S_scalar') + [
            '$array_float_ref_key_plan(S_scalar) = ((n_scalar, n_new, poperand_scalar, eps, 24, n_scalar_bits, 3))',
        ] + seek('S_scalar', 11, 'S_scalar_resume') + [
            'S_scalar_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_scalar n_new poperand_scalar eps 24 n_scalar_bits 3) :: ptask_scalar*',
            '$array_float_ref_key_value(S_scalar_resume, n_new, poperand_scalar) = (DIRECT (PINT 99))',
            'S_scalar_resume.LITERALREFRETAINED = [n_old, n_old]', 'S_scalar_resume.LITERALREFDEBTS = [n_new, n_new]',
            'PhpStep: S_scalar_resume ~> S_scalar_insert',
            'S_scalar_insert.LITERALREFRETAINED = [n_old, n_old]', 'S_scalar_insert.LITERALREFDEBTS = [n_new]',
            '$entry_lookup(S_scalar_insert.ARRAYS[n_scalar].ITEMS, KINT 3) = (DIRECT (PINT 99))',
            '$literal_reference_retained_nodes(S_scalar_insert.LITERALREFDEBTS) = [HCELL n_new]',
        ] + driven('S_scalar_resume', 'S_scalar_insert', 'S_scalar_driven') + seek('S_scalar_driven', 51, 'S_middle') + array_at('S_middle', 'middle', 'middle') + [
            'S_middle.LITERALREFRETAINED = [n_old, n_old]', 'S_middle.LITERALREFDEBTS = [n_new]',
            'S_middle.STORE[n_new] = DEFINED (PINT 66)',
            '$entry_lookup(S_middle.ARRAYS[n_middle].ITEMS, KINT 1) = (ALIAS n_new)',
            '$entry_lookup(S_middle.ARRAYS[n_scalar].ITEMS, KINT 3) = (DIRECT (PINT 99))',
            '$($heap_owners($heap_graph(S_middle), HCELL n_new) > 1)',
        ]
        inverse_start, inverse_line, inverse_key = 'S_middle', 30, 4
    else:
        inverse_start, inverse_line, inverse_key = 'S_a', (25 if stable else 22), 3
    checks += seek(inverse_start, 10, 'S_inverse') + [
        f'$array_float_ref_key_plan(S_inverse) = ((n_inverse, n_new, poperand_inverse, eps, {inverse_line}, n_inverse_bits, {inverse_key}))',
        f'S_inverse.LITERALREFRETAINED = {"[n_old, n_old]" if repeated else "[n_old]"}',
        'S_inverse.LITERALREFDEBTS = [n_new]',
    ] + seek('S_inverse', 11, 'S_inverse_resume') + [
        f'S_inverse_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_inverse n_new poperand_inverse eps {inverse_line} n_inverse_bits {inverse_key}) :: ptask_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
        'PhpStep: S_inverse_resume ~> S_balanced',
        f'S_balanced.LITERALREFRETAINED = {"[n_old]" if repeated else "eps"}',
        'S_balanced.LITERALREFDEBTS = eps',
        f'$entry_lookup(S_balanced.ARRAYS[n_inverse].ITEMS, KINT {inverse_key}) = (ALIAS n_old)',
        '$heap_graph(S_balanced).DEBTS = eps',
    ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 52, 'S_b')
    balanced_name = 'again' if not stable and not repeated else 'balanced'
    checks += array_at('S_b', balanced_name, 'balanced') + [
        'S_b.LITERALREFDEBTS = eps', f'S_b.LITERALREFRETAINED = {"[n_old]" if repeated else "eps"}',
        'S_b.STORE[n_new] = DEFINED (PINT 77)', f'S_b.STORE[n_old] = DEFINED (PINT {32 if repeated else 33})',
        f'$entry_lookup(S_b.ARRAYS[n_balanced].ITEMS, KINT {first_key}) = (ALIAS n_new)',
        '$heap_valid($heap_graph(S_b))', '$call_descriptors_valid(S_b)',
    ]
    if repeated:
        checks += seek('S_b', 54, 'S_ghost') + array_at('S_ghost', 'old_probe', 'probe') + array_at('S_ghost', 'old_copy', 'oldcopy') + [
            'S_ghost.LITERALREFRETAINED = [n_old]', 'S_ghost.LITERALREFDEBTS = eps',
            '$lookup(S_ghost.ENV, $ptascii("q")) = eps', '$lookup(S_ghost.ENV, $ptascii("outside")) = eps',
            '$entry_lookup(S_ghost.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_old)',
            '$entry_lookup(S_ghost.ARRAYS[n_oldcopy].ITEMS, KINT 0) = (ALIAS n_old)',
            'S_ghost.STORE[n_old] = DEFINED (PINT 88)', '$heap_owners($heap_graph(S_ghost), HCELL n_old) = 3',
            'S_done = $drive_steps(S_ghost, 2000)',
        ]
    elif not stable:
        checks += seek('S_b', 53, 'S_oldwrite') + [
            'S_oldwrite.STORE[n_old] = DEFINED (PINT 88)', 'S_oldwrite.STORE[n_new] = DEFINED (PINT 77)',
            f'$entry_lookup(S_oldwrite.ARRAYS[n_inverse].ITEMS, KINT {inverse_key}) = (ALIAS n_old)',
            'S_done = $drive_steps(S_oldwrite, 2000)',
        ]
    else:
        checks += ['S_done = $drive_steps(S_b, 2000)']
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps',
        'S_done.HELD = eps', 'S_done.LITERALREFDEBTS = eps',
        f'S_done.LITERALREFRETAINED = {"[n_old]" if repeated else "eps"}',
        '~((HCELL n_new) <- S_done.ALLOCATIONS)', '~((HARRAY n_builder) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_inverse) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S_a, 0) = S_a[.COMPLETION = BUDGET]',
        '$drive_steps(S_balanced_driven, 2000) = S_done',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if not repeated:
        checks += ['$drive_steps(S_dispatch_driven, 2000) = S_done']
    if repeated:
        checks += ['(HCELL n_old) <- S_done.ALLOCATIONS', 'S_done.STORE[n_old] = DEFINED (PINT 88)',
                   '$heap_owners($heap_graph(S_done), HCELL n_old) = 1',
                   '$heap_count(HCELL n_old, $machine_roots(S_done)) = 1']
    else:
        checks += ['~((HCELL n_old) <- S_done.ALLOCATIONS)']
    if stable:
        checks += ['P = $ppstart(0, ' + program + ', $base64(' + json.dumps(base64.b64encode(bytes(path)).decode()) + '))',
                   'P.COMPLETION = PPCNORMAL', '$ppimage(P, false) =/= eps',
                   '$ppimage(P[.FOLD.MEMORY.LITERALREFDEBTS = [n_new]], false) = eps']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
