#!/usr/bin/env python3
"""Reached typed old owners and two-property shared reference deficits."""
import base64
import json

import array_literal_float_ref_types_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_ref_deficit_state_review import HELPERS as BASE_HELPERS, seek

HELPERS = BASE_HELPERS + r'''
dec $literal_types_remove(pnode*, pnode) : pnode*
def $literal_types_remove(eps, pnode) = eps
def $literal_types_remove(pnode :: pnode_tail*, pnode) = $literal_types_remove(pnode_tail*, pnode)
def $literal_types_remove(pnode_head :: pnode_tail*, pnode) = pnode_head :: $literal_types_remove(pnode_tail*, pnode)
  -- if pnode_head =/= pnode
'''


def driven(start, raw, result):
    return [f'{result}_found = $drive_steps({start}, 1)',
            f'{result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]',
            *[f'{result}.{field} = {raw}.{field}' for field in
              ('STORE', 'ARRAYS', 'TODO', 'RESULT', 'PROPREFS',
               'LITERALREFRETAINED', 'LITERALREFDEBTS')]]


def typed_sources(state, pair):
    if pair:
        return [
            f'$lookup({state}.ENV, $ptascii("left")) = (n_left_cell)',
            f'$lookup({state}.ENV, $ptascii("right")) = (n_right_cell)',
            f'{state}.STORE[n_left_cell] = DEFINED (POBJECT n_left)',
            f'{state}.STORE[n_right_cell] = DEFINED (POBJECT n_right)',
            'n_left =/= n_right',
            f'$propref_at({state}.PROPREFS, n_new) = (ppropref_new)',
            'ppropref_new.SOURCES = [OBJECT_PROP_SOURCE n_left ($ptascii("slot")) porigin_left, OBJECT_PROP_SOURCE n_right ($ptascii("slot")) porigin_right]',
            f'$propref_sources_valid({state}, n_new, ppropref_new.SOURCES)',
            f'(HOBJECT n_left) <- {state}.ALLOCATIONS',
            f'(HOBJECT n_right) <- {state}.ALLOCATIONS',
        ]
    return [
        f'$lookup({state}.ENV, $ptascii("box")) = (n_box_cell)',
        f'{state}.STORE[n_box_cell] = DEFINED (POBJECT n_box)',
        f'$propref_at({state}.PROPREFS, n_old) = (ppropref_old)',
        'ppropref_old.SOURCES = [OBJECT_PROP_SOURCE n_box ($ptascii("slot")) porigin_box]',
        f'$propref_sources_valid({state}, n_old, ppropref_old.SOURCES)',
        f'(HOBJECT n_box) <- {state}.ALLOCATIONS',
    ]


def conditions(name, program, path, stdout):
    pair = name.endswith('two-property-sources')
    line = 21 if pair else 20
    converted = '1' if pair else '$(-2)'
    args = 'n_builder, n_old, poperand, phpType13*, z, n_bits, i'
    marker = 'ARRAY_KEY_FLOAT_REF_RESULT n_builder n_old poperand phpType13* z n_bits i'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALREFRETAINED = eps',
        'S_initial.LITERALREFDEBTS = eps',
    ] + seek('S_initial', 10, 'S') + [
        '$array_float_ref_key_plan(S) = ((' + args + '))',
        'poperand = VARIABLE ($ptascii("q")) z', f'z = {line}', f'i = {converted}',
        '$lookup(S.ENV, $ptascii("q")) = (n_old)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_old)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_new)',
        'n_old =/= n_new', 'S.STORE[n_old] = DEFINED (PINT 2)',
        'S.STORE[n_new] = DEFINED (PINT 44)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)',
        'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)',
        'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$array_float_ref_key_source(S, ' + args + ')',
        '$array_float_ref_key_ready(S, n_builder, n_old, poperand)',
        '$array_float_ref_key_value(S, n_old, poperand) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S), HCELL n_old) = ' + ('2' if pair else '3'),
        '$call_descriptors_valid(S)', '$class_state_valid(S)', '$heap_valid($heap_graph(S))',
    ] + typed_sources('S', pair) + [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LINE = z', 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.PROPREFS = S.PROPREFS',
        '$task_nodes(' + marker + ') = [HARRAY n_builder, HCELL n_old]',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker, 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_old, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_tail*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_new)',
        'S_resume.STORE[n_old] = DEFINED (PINT 33)',
        'S_resume.STORE[n_new] = DEFINED (PINT 44)',
        'S_resume.STORE[n_dest] = DEFINED (PINT 200)',
        'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
        '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
        '$array_float_ref_key_source(S_resume[.ENV = eps], ' + args + ')',
        '$array_float_ref_key_value(S_resume, n_old, poperand) = (ALIAS n_new)',
        '$array_float_ref_key_ready(S_resume, n_builder, n_old, poperand)',
        'S_resume.PROPREFS = S.PROPREFS',
        'S_resume.LITERALREFRETAINED = eps', 'S_resume.LITERALREFDEBTS = eps',
        'PhpStep: S_resume ~> S_insert',
        'S_insert.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*',
        'S_insert.STORE = S_resume.STORE', 'S_insert.PROPREFS = S_resume.PROPREFS',
        'S_insert.LITERALREFRETAINED = [n_old]', 'S_insert.LITERALREFDEBTS = [n_new]',
        'S_insert.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT ' + converted + ') (ALIAS n_new)]',
        '$entry_lookup(S_insert.ARRAYS[n_builder].ITEMS, KINT 9) = eps',
        '$heap_owners($heap_graph(S_insert), HCELL n_old) = ' + ('2' if pair else '3'),
        '$heap_owners($heap_graph(S_insert), HCELL n_new) = ' + ('4' if pair else '2'),
        '$literal_reference_debt_safe(S_insert, $heap_graph(S_insert))',
    ] + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 15, 'S_copy') + [
        'S_copy.LITERALREFRETAINED = [n_old]', 'S_copy.LITERALREFDEBTS = [n_new]',
        '$lookup(S_copy.ENV, $ptascii("q")) = eps',
        '$lookup(S_copy.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_copy.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        'n_copy =/= n_builder', 'S_copy.STORE[n_old] = DEFINED (PINT 33)',
        '$heap_owners($heap_graph(S_copy), HCELL n_old) = ' + ('2' if pair else '3'),
        '$heap_owners($heap_graph(S_copy), HCELL n_new) = ' + ('3' if pair else '1'),
        '$heap_owners($heap_graph(S_copy)[.DEBTS = eps], HCELL n_new) = ' + ('4' if pair else '2'),
        '$literal_reference_debt_safe(S_copy, $heap_graph(S_copy))',
        '$class_state_valid(S_copy)', '$call_descriptors_valid(S_copy)',
        '$heap_valid($heap_graph(S_copy))',
    ] + typed_sources('S_copy', pair)
    if pair:
        checks += [
            'S_copy.STORE[n_new] = DEFINED (PINT 55)',
            '$lookup(S_copy.ENV, $ptascii("replacement")) = eps',
            '$heap_count(HCELL n_new, $machine_roots(S_copy)) = 0',
            '$entry_lookup(S_copy.ARRAYS[n_builder].ITEMS, KINT 1) = (ALIAS n_new)',
            '$entry_lookup(S_copy.ARRAYS[n_copy].ITEMS, KINT 1) = (ALIAS n_new)',
            '$literal_reference_cell(S_copy, n_new, S_copy.ALLOCATIONS)',
            'H_unrooted = $heap_graph(S_copy)[.ROOTS = $literal_types_remove($machine_roots(S_copy), HCELL n_right_cell)]',
            '$heap_valid(H_unrooted)',
            'H_logical = $heap_prune(H_unrooted[.DEBTS = eps])',
            '~((HOBJECT n_right) <- H_logical.NODES)',
            '(HOBJECT n_left) <- H_logical.NODES',
            '$heap_owners(H_logical, HCELL n_new) = 3',
            '~$literal_reference_cell(S_copy, n_new, H_logical.NODES)',
            '~$literal_reference_debt_safe(S_copy, H_unrooted)',
        ]
    else:
        checks += [
            'S_copy.STORE[n_new] = DEFINED (PINT 44)',
            '$lookup(S_copy.ENV, $ptascii("probe")) = (n_probe_cell)',
            'S_copy.STORE[n_probe_cell] = DEFINED (PARRAY n_probe)',
            '$entry_lookup(S_copy.ARRAYS[n_probe].ITEMS, KINT 0) = (ALIAS n_new)',
            '$entry_lookup(S_copy.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PINT 55))',
            'S_copy.ARRAYS[n_builder].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        ]
    checks += seek('S_copy', 10, 'S_inverse') + [
        '$array_float_ref_key_plan(S_inverse) = ((n_balance, n_new, poperand_inverse, eps, z_inverse, n_inverse_bits, 3))',
        'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
        'S_inverse.LITERALREFRETAINED = [n_old]', 'S_inverse.LITERALREFDEBTS = [n_new]',
        '$heap_owners($heap_graph(S_inverse), HCELL n_new) = ' + ('4' if pair else '2'),
    ] + seek('S_inverse', 11, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (ARRAY_KEY_FLOAT_REF_RESULT n_balance n_new poperand_inverse eps z_inverse n_inverse_bits 3) :: ptask_inverse*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_old)',
        '$array_float_ref_key_value(S_inverse_resume, n_new, poperand_inverse) = (ALIAS n_old)',
        '$array_float_ref_key_ready(S_inverse_resume, n_balance, n_new, poperand_inverse)',
        'PhpStep: S_inverse_resume ~> S_balanced',
        'S_balanced.TODO = (ARRAY_NEXT n_balance eps) :: ptask_inverse*',
        'S_balanced.LITERALREFRETAINED = eps', 'S_balanced.LITERALREFDEBTS = eps',
        'S_balanced.PROPREFS = S_inverse_resume.PROPREFS',
        '$entry_lookup(S_balanced.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
        '$heap_owners($heap_graph(S_balanced), HCELL n_new) = ' + ('4' if pair else '2'),
        '$heap_owners($heap_graph(S_balanced), HCELL n_old) = ' + ('3' if pair else '4'),
    ] + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_shared') + [
        'S_shared.LITERALREFRETAINED = eps', 'S_shared.LITERALREFDEBTS = eps',
        'S_shared.STORE[n_new] = DEFINED (PINT 77)',
        'S_shared.STORE[n_old] = DEFINED (PINT ' + ('33' if pair else '77') + ')',
        '$lookup(S_shared.ENV, $ptascii("balanced_copy")) = (n_balanced_cell)',
        'S_shared.STORE[n_balanced_cell] = DEFINED (PARRAY n_balanced)',
        'n_balanced =/= n_copy', 'n_balanced =/= n_builder',
        '$entry_lookup(S_shared.ARRAYS[n_balance].ITEMS, KINT 3) = (ALIAS n_old)',
    ] + typed_sources('S_shared', pair)
    if pair:
        checks += [
            '$entry_lookup(S_shared.ARRAYS[n_balanced].ITEMS, KINT 1) = (ALIAS n_new)',
            '$entry_lookup(S_shared.ARRAYS[n_copy].ITEMS, KINT 1) = (ALIAS n_new)',
            '$heap_owners($heap_graph(S_shared), HCELL n_new) = 5',
        ]
    else:
        checks += [
            '$entry_lookup(S_shared.ARRAYS[n_balanced].ITEMS, KINT 0) = (ALIAS n_new)',
            '$entry_lookup(S_shared.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PINT 55))',
            '$heap_owners($heap_graph(S_shared), HCELL n_new) = 3',
        ]
    checks += [
        'S_done = $drive_steps(S_shared, 2000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps', 'S_done.PROPREFS = eps',
        '~((HCELL n_old) <- S_done.ALLOCATIONS)', '~((HCELL n_new) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_builder) <- S_done.ALLOCATIONS)', '~((HARRAY n_balance) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_copy) <- S_done.ALLOCATIONS)', '~((HARRAY n_balanced) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
        '$drive_steps(S_balanced_driven, 2000) = S_done',
    ]
    checks += (['~((HOBJECT n_left) <- S_done.ALLOCATIONS)',
                '~((HOBJECT n_right) <- S_done.ALLOCATIONS)'] if pair else
               ['~((HOBJECT n_box) <- S_done.ALLOCATIONS)'])
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
