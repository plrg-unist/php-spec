#!/usr/bin/env python3
"""Captured mixed slots preserve borrowed identity and reciprocal table counts."""
import base64
import json

import array_literal_float_wrapped_mixed_cv_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_wrapped_mixed_cv_state_review import HELPERS, empty_biases
from array_literal_float_array_cv_state_review import driven, seek


def table(state, array, *values):
    entries = ', '.join(f'ENTRY (KINT {i}) (DIRECT (PINT {value}))' for i, value in enumerate(values))
    return f'{state}.ARRAYS[{array}].ITEMS = [{entries}]'


def bias(state, scalar_first):
    return [f'{state}.LITERALREFRETAINED = eps', f'{state}.LITERALREFDEBTS = eps',
            f'{state}.LITERALARRAYRETAINED = ' + ('eps' if scalar_first else '[n_old]'),
            f'{state}.LITERALARRAYDEBTS = ' + ('[n_new]' if scalar_first else 'eps')]


def conditions(name, program, path, stdout):
    scalar = name.endswith('scalar-first')
    stage, resume, entered = (20, 21, 23) if scalar else (10, 11, 13)
    args = ('n_a, poperand, phpType13*, z, n_bits, i' if scalar else
            'n_a, n_old, poperand, phpType13*, z, n_bits, i')
    marker = ('ARRAY_KEY_FLOAT_RESULT n_a poperand phpType13* z n_bits i' if scalar else
              'ARRAY_KEY_FLOAT_ARRAY_RESULT n_a n_old poperand phpType13* z n_bits i')
    inverse = ('ARRAY_KEY_FLOAT_ARRAY_RESULT n_b n_new poperand_inverse eps 20 n_inverse_bits 3' if scalar else
               'ARRAY_KEY_FLOAT_RESULT n_b poperand_inverse eps 20 n_inverse_bits 3')
    source = 'array_float_key_source' if scalar else 'array_float_array_key_source'
    ready = '$array_float_key_ready(S_resume, n_a, poperand)' if scalar else '$array_float_array_key_ready(S_resume, n_a, n_old, poperand)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', stage, 'S') + [
        f'$array_float_{"key" if scalar else "array_key"}_plan(S) = ((' + args + '))',
        'z = 13', 'i = 1', 'S.RESULT = VARIABLE ($ptascii("q")) z',
        '$lookup(S.ENV, $ptascii("q")) = (n_capture)',
        '$lookup(S.ENV, $ptascii("outside")) = (n_capture)', 'n_capture <- S.REFCELLS',
        'poperand = BORROWED (ROOT n_capture)' if scalar else 'poperand = REFERENCE n_capture',
        '$lookup(S.ENV, $ptascii("other")) = (n_other)', 'n_other =/= n_capture',
        'S.STORE[n_other] = DEFINED (PINT 99)', '~(n_other <- S.REFCELLS)',
        '$lookup(S.ENV, $ptascii("old_hold")) = (n_hold)', 'n_hold =/= n_capture', '~(n_hold <- S.REFCELLS)',
        '$array_float_key_value(S, S.RESULT) = eps', '$array_float_key_live_value(S, poperand) = eps',
        f'${source}(S, ' + args + ')',
        f'~${source}(S[.ORIGIN = eps], ' + args + ')', f'~${source}(S[.CODE = eps], ' + args + ')',
        '$heap_owners($heap_graph(S), HCELL n_capture) = 2',
    ]
    if scalar:
        checks += [
            'S.STORE[n_capture] = DEFINED (PINT 2)', 'S.STORE[n_hold] = DEFINED (PINT 2)',
            '$array_float_array_key_plan(S) = eps', '$array_float_array_key_reference(S, n_capture) = eps',
            '$array_float_key_completion_value(S, poperand) = (PINT 2)', '$operand_nodes(poperand) = eps',
            '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
            'S.STORE[n_replacement] = DEFINED (PARRAY n_new)', table('S', 'n_new', 44),
            '$heap_owners($heap_graph(S), HARRAY n_new) = 1',
        ]
    else:
        checks += [
            'S.STORE[n_capture] = DEFINED (PARRAY n_old)', 'S.STORE[n_hold] = DEFINED (PARRAY n_old)',
            table('S', 'n_old', 2, 7), '$array_float_key_plan(S) = eps',
            '$array_float_array_key_reference(S, n_capture) = (n_old)',
            '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        ]
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 13',
        '$error_call_valid(S_dispatch, perrorcall)', '~$error_call_valid(S_dispatch, perrorcall[.LINE = 14])',
        '$task_nodes(' + marker + ') = ' + ('[HARRAY n_a]' if scalar else '[HARRAY n_a, HARRAY n_old]'),
        '$heap_count(HCELL n_capture, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HCELL n_capture) = 2',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', entered, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker, '$heap_count(HCELL n_capture, $tasks_nodes(pframe.TODO)) = 0',
    ] + seek('S_entered', resume, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$lookup(S_resume.ENV, $ptascii("q")) = (n_other)', '$lookup(S_resume.ENV, $ptascii("outside")) = (n_capture)',
        'n_other <- S_resume.REFCELLS', 'S_resume.STORE[n_other] = DEFINED (PINT 99)',
        '$heap_owners($heap_graph(S_resume), HCELL n_capture) = 1',
        f'${source}(S_resume[.ENV = eps], ' + args + ')', ready,
        'S_resume.GLOBALTABLE = eps', 'S_unrooted = $unset_name(S_resume, $ptascii("outside"))',
        'H_unrooted = $heap_prune($heap_graph(S_unrooted)[.DEBTS = eps])',
        '(HCELL n_capture) <- S_unrooted.ALLOCATIONS', '~((HCELL n_capture) <- H_unrooted.NODES)',
        f'${source}(S_unrooted, ' + args + ')', '$call_task_valid(S_unrooted, ' + marker + ')',
        '$array_float_key_borrowed_value(S_unrooted, n_capture) = eps',
        ready.replace('S_resume', 'S_unrooted').replace('$', '~$', 1),
        '$error_read_discard(S_unrooted, ' + marker + ').COMPLETION = UNSUPPORTED "array literal float-key ' + ('element' if scalar else 'array CV') + ' during throw"',
        'S_string = S_resume[.STORE[n_capture] = DEFINED (PSTRING eps)]',
        '$array_float_key_borrowed_value(S_string, n_capture) = eps',
        'S_typed = S_resume[.PROPREFS = [{CELL n_capture, SOURCES eps}]]',
        '$array_float_key_borrowed_value(S_typed, n_capture) = eps',
        'S_cell_debt = S_resume[.LITERALREFDEBTS = [n_capture]]',
        '$array_float_key_borrowed_value(S_cell_debt, n_capture) = eps',
        'S_builder = S_resume[.STORE[n_capture] = DEFINED (PARRAY n_a)]',
        ready.replace('S_resume', 'S_builder').replace('$', '~$', 1),
        'S_discard = $error_read_discard(S_resume, ' + marker + ')',
        'S_discard.STORE = S_resume.STORE', 'S_discard.ARRAYS = S_resume.ARRAYS',
    ] + bias('S_discard', scalar)
    if scalar:
        checks += [
            'S_resume.STORE[n_capture] = DEFINED (PARRAY n_new)',
            '$array_float_key_completion_value(S_resume, poperand) = (PARRAY n_new)',
        ]
    else:
        checks += [
            'S_resume.STORE[n_capture] = DEFINED (PINT 44)',
            '$array_float_array_key_item(S_resume, poperand) = (DIRECT (PINT 44))',
            '$array_float_array_key_reference(S_resume, n_capture) = eps',
        ]
    checks += [
        'PhpStep: S_resume ~> S_insert', 'S_insert.STORE = S_resume.STORE',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 1) = ' + ('(DIRECT (PARRAY n_new))' if scalar else '(DIRECT (PINT 44))'),
    ] + bias('S_insert', scalar) + driven('S_resume', 'S_insert', 'S_start') + seek('S_start', 15, 'S_read') + bias('S_read', scalar) + [
        '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
        '$heap_owners($heap_graph(S_read), HCELL n_capture) = 1',
        '$heap_owners($heap_graph(S_read), HCELL n_other) = 2',
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
    ]
    if scalar:
        checks += [
            '$lookup(S_read.ENV, $ptascii("replacement")) = eps',
            'S_read.STORE[n_capture] = DEFINED (PARRAY n_new)', table('S_read', 'n_new', 55),
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_child))',
            'n_copy_child =/= n_new', table('S_read', 'n_copy_child', 66),
            '$heap_owners($heap_graph(S_read), HARRAY n_new) = 1',
            '$heap_owners($heap_graph(S_read)[.DEBTS = eps], HARRAY n_new) = 2',
            '$literal_reference_debt_safe(S_read, $heap_graph(S_read))',
        ]
    else:
        checks += [
            'S_read.STORE[n_capture] = DEFINED (PINT 66)', '$node_children(S_read, HCELL n_capture) = eps',
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KINT 1) = (DIRECT (PINT 44))',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KINT 1) = (DIRECT (PINT 55))',
            '$heap_owners($heap_graph(S_read), HARRAY n_old) = 2',
            '$heap_owners($heap_graph(S_read[.LITERALARRAYRETAINED = eps]), HARRAY n_old) = 1',
        ]
    checks += seek('S_read', 10 if scalar else 20, 'S_inverse') + [
        ('$array_float_array_key_plan(S_inverse) = ((n_b, n_new, poperand_inverse, eps, 20, n_inverse_bits, 3))' if scalar else
         '$array_float_key_plan(S_inverse) = ((n_b, poperand_inverse, eps, 20, n_inverse_bits, 3))'),
        'poperand_inverse = ' + ('REFERENCE n_capture' if scalar else 'BORROWED (ROOT n_capture)'),
        '$lookup(S_inverse.ENV, $ptascii("q")) = (n_capture)',
        '$heap_owners($heap_graph(S_inverse), HCELL n_capture) = 2',
        'PhpStep: S_inverse ~> S_inverse_dispatch',
        'S_inverse_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_inverse) :: ptask_inverse*',
        'perrorcall_inverse.RESUME = ' + inverse,
        '$task_nodes(' + inverse + ') = ' + ('[HARRAY n_b, HARRAY n_new]' if scalar else '[HARRAY n_b]'),
        '$heap_owners($heap_graph(S_inverse_dispatch), HCELL n_capture) = 2',
    ] + driven('S_inverse', 'S_inverse_dispatch', 'S_inverse_driven') + seek('S_inverse_driven', 11 if scalar else 21, 'S_inverse_resume') + [
        'S_inverse_resume.TODO = (' + inverse + ') :: ptask_inverse_after*',
        '$lookup(S_inverse_resume.ENV, $ptascii("q")) = (n_other)',
        'S_inverse_discard = $error_read_discard(S_inverse_resume, ' + inverse + ')',
        'S_inverse_discard.STORE = S_inverse_resume.STORE', 'S_inverse_discard.ARRAYS = S_inverse_resume.ARRAYS',
    ] + empty_biases('S_inverse_discard')
    if scalar:
        checks += [
            'S_inverse_resume.STORE[n_capture] = DEFINED (PBOOL true)',
            '$array_float_array_key_item(S_inverse_resume, poperand_inverse) = (DIRECT (PBOOL true))',
            '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_new) = 1',
        ]
    else:
        checks += [
            'S_inverse_resume.STORE[n_capture] = DEFINED (PARRAY n_old)',
            '$array_float_key_completion_value(S_inverse_resume, poperand_inverse) = (PARRAY n_old)',
            '$heap_owners($heap_graph(S_inverse_resume), HARRAY n_old) = 3',
        ]
    checks += [
        'PhpStep: S_inverse_resume ~> S_balanced',
        '$entry_lookup(S_balanced.ARRAYS[n_b].ITEMS, KINT 3) = ' + ('(DIRECT (PBOOL true))' if scalar else '(DIRECT (PARRAY n_old))'),
    ] + empty_biases('S_balanced') + driven('S_inverse_resume', 'S_balanced', 'S_balanced_driven') + seek('S_balanced_driven', 16, 'S_cow') + [
        '$lookup(S_cow.ENV, $ptascii("shared")) = (n_shared_cell)',
        'S_cow.STORE[n_shared_cell] = DEFINED (PARRAY n_shared)',
        '$heap_owners($heap_graph(S_cow), HCELL n_capture) = 1',
        '$heap_owners($heap_graph(S_cow), HCELL n_other) = 2',
    ] + empty_biases('S_cow')
    if scalar:
        checks += [
            'n_shared =/= n_a', 'S_cow.STORE[n_capture] = DEFINED (PBOOL false)',
            '$entry_lookup(S_cow.ARRAYS[n_b].ITEMS, KINT 3) = (DIRECT (PBOOL true))',
            '$entry_lookup(S_cow.ARRAYS[n_shared].ITEMS, KINT 1) = (DIRECT (PARRAY n_shared_child))',
            'n_shared_child =/= n_new', table('S_cow', 'n_shared_child', 77),
            table('S_cow', 'n_new', 55), table('S_cow', 'n_copy_child', 66),
            '$heap_owners($heap_graph(S_cow), HARRAY n_new) = 1',
        ]
        retired = ['n_new', 'n_copy_child', 'n_shared_child']
    else:
        checks += [
            'n_shared =/= n_b', 'S_cow.STORE[n_capture] = DEFINED (PARRAY n_outside)',
            'n_outside =/= n_old', table('S_cow', 'n_outside', 88, 7), table('S_cow', 'n_old', 2, 7),
            '$entry_lookup(S_cow.ARRAYS[n_shared].ITEMS, KINT 3) = (DIRECT (PARRAY n_shared_child))',
            'n_shared_child =/= n_old', table('S_cow', 'n_shared_child', 77, 7),
            '$lookup(S_cow.ENV, $ptascii("balance_copy")) = (n_balance_copy_cell)',
            'S_cow.STORE[n_balance_copy_cell] = DEFINED (PARRAY n_balance_copy)', 'n_balance_copy =/= n_b',
            '$entry_lookup(S_cow.ARRAYS[n_balance_copy].ITEMS, KINT 3) = (DIRECT (PARRAY n_balance_copy_child))',
            'n_balance_copy_child =/= n_old', table('S_cow', 'n_balance_copy_child', 99, 7),
            '$heap_owners($heap_graph(S_cow), HARRAY n_old) = 2',
        ]
        retired = ['n_old', 'n_outside', 'n_shared_child', 'n_balance_copy', 'n_balance_copy_child']
    checks += [
        'S_done = $drive_steps(S_cow, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '~((HCELL n_capture) <- S_done.ALLOCATIONS)', '~((HCELL n_other) <- S_done.ALLOCATIONS)',
        *[f'~((HARRAY {node}) <- S_done.ALLOCATIONS)' for node in ['n_a', 'n_b', 'n_copy', 'n_shared', *retired]],
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_inverse, 0) = S_inverse[.COMPLETION = BUDGET]',
        'S_split_found = $drive_steps(S_cow, 1)', 'S_split_found.COMPLETION = BUDGET',
        '$drive_steps(S_split_found[.COMPLETION = NORMAL], 2000) = S_done',
    ] + empty_biases('S_done')
    if scalar:
        checks += ['$drive_steps(S_initial[.COMPLETION = NORMAL], 2000) = S_done']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
