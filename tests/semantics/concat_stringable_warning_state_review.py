#!/usr/bin/env python3
"""Throwing at the Warning or selected Stringable body cancels separate stages."""
import concat_stringable_warning_review_cases as cases
import concat_stringable_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    in_stringable = name == 'concat-array-left-stringable-throw'
    checks = shared.prefix(program, path)
    checks += [
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$throwable_previous_id(S_entry, n_second) = eps',
        '$throwable_field(S_entry, n_second, "line") = PINT 20',
    ]
    if in_stringable:
        shared.returned_h(checks)
        checks += [
            '$concat_stringable_diagnostics(S_return.EVENTS) = 1',
            '~$concat_array_left_fresh(S_return, poperand_left, poperand_right, n_right)',
            '~$error_call_valid(S_return, perrorcall)',
            '$error_call_valid(S_return, perrorcall_entered)',
            '~$concat_array_right_stringable(S_return[.PROPREFS = [{CELL n_right, SOURCES eps}]], poperand_right, n_right)',
            '~$concat_array_right_stringable(S_return[.REFCOERCIONS = [{CELL n_right, SITE porigin_right, LINE 25, VALUE eps}]], poperand_right, n_right)',
            '~$concat_array_right_stringable(S_return[.PARAMETERBACKINGS = [{FUNCTION porigin_right, INDEX 0, CELL n_right, LINE 25, VALUE eps}]], poperand_right, n_right)',
        ]
        shared.seek(checks, 'S_enteredS', 'S_pending', 8)
        checks += [
            'S_enteredS.CURRENT = (pcallcontext_s)',
            'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method',
            'pcallcontext_s.RECEIVER = (n_object)', 'pcallcontext_s.CALLSITE = (porigin_right)',
            'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
            'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_right 25) :: (CONCAT_AFTER_RIGHT porigin_parent pvalue_array 25) :: ptask_tail*',
            '$task_nodes(STRINGIFY_RESULT n_object porigin_right 25) = [HOBJECT n_object]',
            'S_enteredS.STORE[n_right] = DEFINED (POBJECT n_object)',
            'S_enteredS.STORE[n_v] = DEFINED (PINT 100)', 'S_enteredS.STORE[n_casts] = DEFINED (PINT 0)',
            '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
            '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
        ]
        shared.seek(checks, 'S_changed', 'S_enteredS', 9)
        checks += [
            '$lookup($global_table_view(S_changed).ENV, $ptascii("left")) = (n_changed_left)',
            'n_changed_left =/= n_left', 'S_changed.STORE[n_changed_left] = DEFINED (PINT 9)',
            'S_changed.STORE[n_right] = DEFINED pvalue_method', '$string_bytes(pvalue_method) = ($ptascii("method"))',
            'S_changed.STORE[n_calls] = DEFINED (PINT 1)', 'S_changed.STORE[n_casts] = DEFINED (PINT 1)',
            'S_changed.STORE[n_v] = DEFINED (PINT 100)',
            '(HOBJECT n_object) <- S_changed.ALLOCATIONS',
            '$($heap_owners($heap_prune($heap_graph(S_changed)), HOBJECT n_object) > 0)',
            '$stringify_chain_valid(S_changed, S_changed.CURRENT, S_changed.FRAMES)',
            '$call_descriptors_valid(S_changed)', '$heap_valid($heap_graph(S_changed))',
        ]
        shared.seek(checks, 'S_throw', 'S_changed', 6)
        checks += [
            '$lookup(S_throw.ENV, $ptascii("left")) = (n_changed_left)',
            'S_throw.STORE[n_changed_left] = DEFINED (PINT 9)',
            'S_throw.STORE[n_right] = DEFINED pvalue_method',
            'S_throw.STORE[n_casts] = DEFINED (PINT 1)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 0',
            '~((HOBJECT n_object) <- S_throw.ALLOCATIONS)',
            '$concat_stringable_diagnostics(S_throw.EVENTS) = 1',
        ]
    else:
        shared.seek(checks, 'S_throw', 'S_enteredH', 6)
        checks += [
            '$lookup(S_throw.ENV, $ptascii("left")) = eps',
            'S_throw.STORE[n_right] = DEFINED (POBJECT n_object)',
            '$stringable_instance(S_throw, n_object)',
            '$concat_array_right_stringable(S_throw, poperand_right, n_right)',
            'S_throw.STORE[n_casts] = DEFINED (PINT 0)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 1',
            '$heap_count(HOBJECT n_object, $tasks_nodes(S_throw.TODO)) = 0',
            '~$concat_stringable_frontier(S_throw, 7)', '~$concat_stringable_frontier(S_throw, 8)',
            '$concat_stringable_diagnostics(S_throw.EVENTS) = 0',
        ]
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
        '~$concat_array_tasks(S_throw.TODO)', '~$concat_array_legacy(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("right")) = (n_right)',
        '~(n_right <- S_throw.REFCELLS)', 'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
        '$throwable_field(S_throw, n_second, "line") = PINT 20',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left_end)', 'S_done.STORE[n_left_end] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_right)',
        'S_done.STORE[n_right] = DEFINED pvalue_end', '$string_bytes(pvalue_end) = ($ptascii("end"))',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_casts] = DEFINED (PINT ' + ('1' if in_stringable else '0') + ')',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$concat_stringable_diagnostics(S_done.EVENTS) = ' + ('1' if in_stringable else '0'),
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_throw, 0) = S_throw[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
