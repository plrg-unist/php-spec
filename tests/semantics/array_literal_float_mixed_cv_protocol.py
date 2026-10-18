#!/usr/bin/env python3
"""Both mixed-CV inverse cycles restore table counts before ordinary COW."""
import base64
import json

import array_literal_float_mixed_cv_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_mixed_cv_state_review import HELPERS, driven, payload, seek


def conditions(name, program, path, stdout):
    array_first = name.endswith('array-scalar-array')
    first_args = ('n_a, n_table, poperand, phpType13*, z, n_bits, i' if array_first
                  else 'n_a, poperand, phpType13*, z, n_bits, i')
    first_marker = ('ARRAY_KEY_FLOAT_ARRAY_RESULT n_a n_table poperand phpType13* z n_bits i' if array_first
                    else 'ARRAY_KEY_FLOAT_RESULT n_a poperand phpType13* z n_bits i')
    first_plan = '$array_float_array_key_plan' if array_first else '$array_float_key_plan'
    first_source = '$array_float_array_key_source' if array_first else '$array_float_key_source'
    first_ready = ('$array_float_array_key_ready(S_resume, n_a, n_table, poperand)' if array_first
                   else '$array_float_key_ready(S_resume, n_a, poperand)')
    reason = ('array literal float-key array CV during throw' if array_first
              else 'array literal float-key element during throw')
    inverse_line = 18 if array_first else 19
    inverse_args = ('n_b, poperand_inverse, eps, z_inverse, n_bits_inverse, 3' if array_first
                    else 'n_b, n_table, poperand_inverse, eps, z_inverse, n_bits_inverse, 3')
    inverse_marker = ('ARRAY_KEY_FLOAT_RESULT n_b poperand_inverse eps z_inverse n_bits_inverse 3' if array_first
                      else 'ARRAY_KEY_FLOAT_ARRAY_RESULT n_b n_table poperand_inverse eps z_inverse n_bits_inverse 3')
    inverse_plan = '$array_float_key_plan' if array_first else '$array_float_array_key_plan'
    retained, debts = ('[n_table]', 'eps') if array_first else ('eps', '[n_table]')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_initial.LITERALARRAYRETAINED = eps',
        'S_initial.LITERALARRAYDEBTS = eps',
    ] + seek('S_initial', 20 if array_first else 10, 'S') + [
        first_plan + '(S) = ((' + first_args + '))',
        'z = 12', 'i = 1', 'poperand = VARIABLE ($ptascii("q")) z',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', '~(n_q <- S.REFCELLS)',
        first_source + '(S, ' + first_args + ')',
        'S.LITERALREFRETAINED = eps', 'S.LITERALREFDEBTS = eps',
    ]
    if array_first:
        checks += [
            '$array_float_key_plan(S) = eps', '$array_float_key_value(S, poperand) = eps',
            '$array_float_array_key_value(S, poperand) = (n_table)',
            'S.STORE[n_q] = DEFINED (PARRAY n_table)', payload('S', 'n_table', 2),
            '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)', 'n_hold =/= n_q',
            'S.STORE[n_hold] = DEFINED (PARRAY n_table)',
            '$heap_owners($heap_graph(S), HARRAY n_table) = 2',
            'S_scalar_initial = S[.STORE[n_q] = DEFINED (PINT 33)]',
            '$array_float_array_key_plan(S_scalar_initial) = eps',
            '$array_float_key_plan(S_scalar_initial) = ((n_a, poperand, phpType13*, z, n_bits, i))',
        ]
    else:
        checks += [
            '$array_float_array_key_plan(S) = eps', '$array_float_key_value(S, poperand) = (PINT 33)',
            'S.STORE[n_q] = DEFINED (PINT 33)',
            '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
            'S.STORE[n_replacement] = DEFINED (PARRAY n_table)', payload('S', 'n_table', 44),
            '$heap_owners($heap_graph(S), HARRAY n_table) = 1',
        ]
    checks += [
        '$array_float_key_live_value(S, KNOWN (PARRAY n_table)) = (PARRAY n_table)',
        '$array_float_key_retain(S, KNOWN (PARRAY n_table)) = S',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + first_marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        '$error_call_valid(S_dispatch, perrorcall)', '$error_call_valid(S_dispatch[.ENV = eps], perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '$task_nodes(' + first_marker + ') = ' + ('[HARRAY n_a, HARRAY n_table]' if array_first else '[HARRAY n_a]'),
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_table) = ' + ('3' if array_first else '1'),
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 23 if array_first else 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + first_marker,
        '$heap_count(HCELL n_q, $tasks_nodes(pframe.TODO)) = 0',
        '$heap_count(HARRAY n_table, $tasks_nodes(pframe.TODO)) = ' + ('1' if array_first else '0'),
    ] + seek('S_entered', 21 if array_first else 11, 'S_resume') + [
        'S_resume.TODO = (' + first_marker + ') :: ptask_tail*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_q)',
        first_source + '(S_resume[.ENV = eps], ' + first_args + ')',
        first_ready,
        '$array_float_key_live_value(S_resume, poperand) = ' + ('(PINT 44)' if array_first else '(PARRAY n_table)'),
        'S_resume.STORE[n_q] = DEFINED ' + ('(PINT 44)' if array_first else '(PARRAY n_table)'),
        'S_resume.STORE[n_key] = DEFINED (PFLOAT n_live_bits)',
        '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
        'S_wrapped = S_resume[.REFCELLS = n_q :: S_resume.REFCELLS]',
        '$call_task_valid(S_wrapped, ' + first_marker + ')',
        '$array_float_key_live_value(S_wrapped, poperand) = eps',
        '$error_read_discard(S_wrapped, ' + first_marker + ').COMPLETION = UNSUPPORTED ' + json.dumps(reason),
        '$array_float_key_live_value(S_resume[.STORE[n_q] = DEFINED (PSTRING eps)], poperand) = eps',
        ('~$array_float_array_key_ready(S_resume[.STORE[n_q] = DEFINED (PARRAY n_a)], n_a, n_table, poperand)' if array_first
         else '~$array_float_key_ready(S_resume[.STORE[n_q] = DEFINED (PARRAY n_a)], n_a, poperand)'),
        'PhpStep: S_resume ~> S_insert', 'S_insert.STORE = S_resume.STORE',
        'S_insert.TODO = (ARRAY_NEXT n_a phpType13*) :: ptask_tail*',
        'S_insert.LITERALARRAYRETAINED = ' + retained, 'S_insert.LITERALARRAYDEBTS = ' + debts,
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 1) = (DIRECT ' + ('(PINT 44))' if array_first else '(PARRAY n_table))'),
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps',
        '$heap_owners($heap_graph(S_insert), HARRAY n_table) = 2',
    ] + driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + [
        'S_read.LITERALARRAYRETAINED = ' + retained, 'S_read.LITERALARRAYDEBTS = ' + debts,
        '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 4) = (DIRECT (PINT 66))',
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
    ]
    if array_first:
        checks += [
            'S_read.STORE[n_q] = DEFINED (PINT 44)', payload('S_read', 'n_table', 2),
            '$heap_owners($heap_graph(S_read), HARRAY n_table) = 2',
            '$heap_owners($heap_graph(S_read[.LITERALARRAYRETAINED = eps]), HARRAY n_table) = 1',
        ]
    else:
        checks += [
            '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
            'S_read.STORE[n_q] = DEFINED (PARRAY n_table)', payload('S_read', 'n_table', 55),
            '$heap_graph(S_read).DEBTS = [HARRAY n_table]',
            '$heap_owners($heap_graph(S_read), HARRAY n_table) = 1',
            '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_table) = 2',
            '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
        ]
    checks += seek('S_read', 10 if array_first else 20, 'S_inverse') + [
        inverse_plan + '(S_inverse) = ((' + inverse_args + '))',
        ('$array_float_array_key_plan(S_inverse) = eps' if array_first else '$array_float_key_plan(S_inverse) = eps'),
        f'z_inverse = {inverse_line}', 'poperand_inverse = VARIABLE ($ptascii("q")) z_inverse',
        'S_inverse.LITERALARRAYRETAINED = ' + retained, 'S_inverse.LITERALARRAYDEBTS = ' + debts,
        'PhpStep: S_inverse ~> S_inverse_dispatch',
        'S_inverse_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_inverse) :: ptask_inverse*',
        'perrorcall_inverse.RESUME = ' + inverse_marker, '$error_call_valid(S_inverse_dispatch, perrorcall_inverse)',
    ] + driven('S_inverse', 'S_inverse_dispatch', 'S_inverse_driven') + seek('S_inverse_driven', 11 if array_first else 21, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse_marker + ') :: ptask_after_inverse*',
        '$array_float_key_live_value(S_inverse_resume, poperand_inverse) = ' + ('(PARRAY n_table)' if array_first else '(PINT 99)'),
        ('$array_float_key_value(S_inverse_resume, poperand_inverse) = eps' if array_first
         else '$array_float_array_key_value(S_inverse_resume, poperand_inverse) = eps'),
        'S_discard = $error_read_discard(S_inverse_resume, ' + inverse_marker + ')',
        'S_discard.STORE = S_inverse_resume.STORE', 'S_discard.ARRAYS = S_inverse_resume.ARRAYS',
        'S_discard.LITERALARRAYRETAINED = eps', 'S_discard.LITERALARRAYDEBTS = eps',
        'PhpStep: S_inverse_resume ~> S_balance',
        'S_balance.LITERALARRAYRETAINED = eps', 'S_balance.LITERALARRAYDEBTS = eps',
        '$entry_lookup(S_balance.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT ' + ('(PARRAY n_table))' if array_first else '(PINT 99))'),
        '$heap_owners($heap_graph(S_balance), HARRAY n_table) = ' + ('3' if array_first else '1'),
    ] + driven('S_inverse_resume', 'S_balance', 'S_balanced') + seek('S_balanced', 16, 'S_final') + [
        'S_final.LITERALARRAYRETAINED = eps', 'S_final.LITERALARRAYDEBTS = eps',
        '$lookup(S_final.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_final.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
    ]
    if array_first:
        checks += [
            '$lookup(S_final.ENV, $ptascii("old_hold")) = eps',
            'S_final.STORE[n_q] = DEFINED (PARRAY n_q_child)', 'n_q_child =/= n_table',
            payload('S_final', 'n_q_child', 55), payload('S_final', 'n_table', 2),
            '$entry_lookup(S_final.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT (PARRAY n_table))',
            '$entry_lookup(S_final.ARRAYS[n_copy].ITEMS, KINT 3) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_table', payload('S_final', 'n_copy_child', 77),
        ]
    else:
        checks += [
            'S_final.STORE[n_q] = DEFINED (PINT 99)',
            '$entry_lookup(S_final.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT (PINT 99))',
            '$entry_lookup(S_final.ARRAYS[n_a].ITEMS, KINT 1) = (DIRECT (PARRAY n_table))',
            payload('S_final', 'n_table', 55),
            '$entry_lookup(S_final.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_table', payload('S_final', 'n_copy_child', 66),
        ]
    checks += [
        '$heap_owners($heap_graph(S_final), HARRAY n_table) = 1',
        '$heap_owners($heap_graph(S_final), HARRAY n_copy_child) = 1',
        'S_done = $drive_steps(S_final, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        '~((HARRAY n_table) <- S_done.ALLOCATIONS)', '~((HARRAY n_a) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_b) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_copy_child) <- S_done.ALLOCATIONS)', '$lookup(S_done.ENV, $ptascii("q")) = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_inverse, 0) = S_inverse[.COMPLETION = BUDGET]',
        '$drive_steps(S_final, 1) = $drive_steps($drive_steps(S_final, 0)[.COMPLETION = NORMAL], 1)',
        '$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done',
    ]
    if array_first:
        checks += ['~((HARRAY n_q_child) <- S_done.ALLOCATIONS)']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
