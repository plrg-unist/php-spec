#!/usr/bin/env python3
"""A float cast delivers its saved scalar after its borrowed object retires."""
import base64
import json

import object_numeric_cast_warning_review_cases as cases
import object_numeric_cast_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    marker = lambda stage: f'OBJECT_NUMERIC_CAST_WARNING porigin_cast pcast poperand z {stage}'
    valid = lambda state, stage: f'$object_numeric_cast_warning_valid({state}, porigin_cast, pcast, poperand, z, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $object_numeric_cast_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$object_numeric_cast_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$object_numeric_cast_plan(S_entry) = (porigin_cast, pcast, poperand, z)',
        'pcast = CASTFLOAT', 'poperand = VARIABLE ($ptascii("x")) 25', 'z = 25',
        'S_entry.TODO = (CAST_RESULT pcast z) :: ptask_tail*',
        'S_entry.RESULT = poperand',
        '$object_numeric_cast_source(S_entry, porigin_cast, pcast, poperand, z)',
        '$object_numeric_cast_snapshot(S_entry, poperand)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("weak")) = (n_weak_cell)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_x] = DEFINED (POBJECT n_object)',
        'S_entry.OBJECTS[n_object] = STDINSTANCE',
        '$objectprops_at(S_entry.OBJECTPROPS, n_object) = (eps)',
        '$object_table_at(S_entry.OBJECTTABLES, n_object) = eps',
        'S_entry.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        'S_entry.OBJECTS[n_weak] = WEAKREFERENCE (n_object)',
        '$weakref_get(S_entry, n_weak) = POBJECT n_object',
        '$node_children(S_entry, HOBJECT n_weak) = eps',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_weak) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw = S_entry[.TODO = (' + marker(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        '$object_numeric_cast_frontier(S_capture, 1)',
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        valid('S_capture', 0), '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$object_numeric_cast_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1),
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Object of class stdClass could not be converted to float")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$object_numeric_cast_snapshot(S_dispatch, poperand)',
        '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$object_numeric_cast_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("x")) = eps',
        'S_return.STORE[n_x] = DEFINED (PINT 99)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("x"))) = eps',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 0',
        '$heap_owners($heap_prune($heap_graph(S_return)), HOBJECT n_object) = 0',
        '~((HCELL n_x) <- S_return.ALLOCATIONS)',
        '~((HOBJECT n_object) <- S_return.ALLOCATIONS)',
        'S_return.OBJECTS[n_weak] = WEAKREFERENCE (n_object)',
        '$weakref_get(S_return, n_weak) = PNULL',
        '$heap_owners($heap_prune($heap_graph(S_return)), HOBJECT n_weak) = 1',
        '~$object_numeric_cast_snapshot(S_return, poperand)',
        valid('S_return', 1), '~' + valid('S_return', 0),
        '~$error_call_valid(S_return, perrorcall)',
        '$task_nodes(' + marker(1) + ') = eps',
        '$object_numeric_cast_diagnostics(S_return.EVENTS, "Warning") = 1',
        '$object_numeric_cast_diagnostics(S_return.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_result_raw',
        'S_result_raw = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 4607182418800017408)][.BASE = BASE_VALUE (KNOWN (PFLOAT 4607182418800017408))]',
    ]
    step('S_result', 'S_return')
    checks += [
        '$object_numeric_cast_frontier(S_result, 5)',
        'S_result = S_result_raw',
        'S_result.RESULT = KNOWN (PFLOAT 4607182418800017408)',
        'S_result.STORE = S_return.STORE', 'S_result.ENV = S_return.ENV',
        'S_result.REFCELLS = S_return.REFCELLS',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.OBJECTS = S_return.OBJECTS', 'S_result.OBJECTPROPS = S_return.OBJECTPROPS',
        'S_result.ARRAYS = S_return.ARRAYS', 'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.EVENTS = S_return.EVENTS',
        '$weakref_get(S_result, n_weak) = PNULL',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 4000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_new)', 'n_new =/= n_x',
        'S_done.STORE[n_new] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PFLOAT 4607182418800017408)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_new) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '$weakref_get(S_done, n_weak) = PNULL',
        '$object_numeric_cast_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$object_numeric_cast_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
