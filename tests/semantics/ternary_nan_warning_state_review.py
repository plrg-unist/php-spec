#!/usr/bin/env python3
"""Shorthand fallback preserves an integer value; a pending throw selects none."""
import base64
import json

import ternary_nan_warning_review_cases as cases

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    throws = name.endswith('supplied-throw')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $ternary_nan_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$ternary_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$ternary_nan_plan(S_entry) = ((pboolnotnanwarning, ptask_original))',
        'ptask_original = SELECT_VALUE ABSENT expression_false 24 0 25',
        'S_entry.TODO = ptask_original :: ptask_tail*',
        'pboolnotnanwarning.LINE = 24',
        'pboolnotnanwarning.INPUT = VARIABLE ($ptascii("x")) 24',
        'S_entry.RESULT = pboolnotnanwarning.INPUT',
        '$number_bool(NFLOAT pboolnotnanwarning.BITS) = (true, true)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', 'pboolnotnanwarning.CELL = n_x',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("rhs")) = (n_rhs)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_rhs] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)', '(HCELL n_x) <- S_entry.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$ternary_nan_source(S_entry, pboolnotnanwarning, ptask_original)',
        '$boolnot_nan_ready(S_entry, pboolnotnanwarning) = (pboolnotnanwarning.BITS)',
        '$boolnot_nan_snapshot(S_entry, pboolnotnanwarning)',
        '$ternary_nan_warning_valid(S_entry, pboolnotnanwarning, ptask_original, 0)',
        '$ternary_nan_warning_valid(S_entry, pboolnotnanwarning, ptask_original, 1)',
        '~$ternary_nan_warning_valid(S_entry, pboolnotnanwarning, ptask_original, 2)',
        '$short_nan_plan(S_entry) = eps', '$boolnot_nan_plan(S_entry) = eps',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning, SELECT_VALUE ABSENT expression_false 24 1 25)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning, SELECT_VALUE ABSENT expression_false 24 0 24)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning, SHORT_RESULT false expression_false 24 25)',
        '$ternary_nan_plan(S_entry[.RESULT = KNOWN (PFLOAT pboolnotnanwarning.BITS)]) = eps',
        '$ternary_nan_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        'S_entry.EVENTS = eps', '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    if throws:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$ternary_nan_frontier(S_capture, 1)',
        '$task_nodes(TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$ternary_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pboolnotnanwarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 24',
        'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 24',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 25])',
        'S_dispatch.EVENTS = S_entry.EVENTS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$ternary_nan_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1',
        'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    seek('S_post', 'S_entered', 7 if throws else 4)
    checks += [
        'S_post.CURRENT = eps', 'S_post.FRAMES = eps',
        '$lookup(S_post.ENV, $ptascii("x")) = (n_x)',
        'S_post.STORE[n_x] = DEFINED (PFLOAT 0)',
        'S_post.STORE[n_v] = DEFINED (PINT 100)',
        'S_post.STORE[n_calls] = DEFINED (PINT 1)', 'S_post.STORE[n_rhs] = DEFINED (PINT 0)',
        '~(n_x <- S_post.REFCELLS)', '(HCELL n_x) <- S_post.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_post)), HCELL n_x) = 1',
        '$ternary_nan_source(S_post, pboolnotnanwarning, ptask_original)',
        '$boolnot_nan_ready(S_post, pboolnotnanwarning) = (0)',
        '~$boolnot_nan_snapshot(S_post, pboolnotnanwarning)',
        '~$ternary_nan_warning_valid(S_post, pboolnotnanwarning, ptask_original, 0)',
        '$ternary_nan_warning_valid(S_post, pboolnotnanwarning, ptask_original, 1)',
        '~$error_call_valid(S_post, perrorcall)', '$error_call_valid(S_post, perrorcall_entered)',
        '$task_nodes(TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1) = eps',
        '$ternary_nan_diagnostics(S_post.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_post)', '$heap_valid($heap_graph(S_post))',
    ]
    if throws:
        checks += [
            'S_post.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
            '~$ternary_nan_tasks(S_post.TODO)',
            '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_post)), HOBJECT n_second) = 2',
            '$throwable_live(S_post, n_second)', '$throwable_previous_id(S_post, n_second) = eps',
            '$throwable_field(S_post, n_second, "line") = PINT 20',
            '$ternary_nan_diagnostics(S_post.EVENTS, "Warning") = 0',
            'S_done = $drive_steps(S_post, 3000)',
        ]
    else:
        checks += [
            'S_post.TODO = (TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1) :: ptask_tail*',
            '$ternary_nan_diagnostics(S_post.EVENTS, "Warning") = 1',
            'PhpStep: S_post ~> S_schedule_atomic',
            'S_schedule_atomic = S_post[.TODO = [$at_task($origin_child((pboolnotnanwarning.SITE), [PCFIELD 2]), EVAL expression_false), VALUE_COPY 25] ++ ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        ]
        step('S_schedule', 'S_post')
        checks += [
            'S_schedule = S_schedule_atomic', '$ternary_nan_frontier(S_schedule, 6)',
            'S_schedule.STORE[n_v] = DEFINED (PINT 100)', 'S_schedule.STORE[n_rhs] = DEFINED (PINT 0)',
            'S_schedule.EVENTS = S_post.EVENTS',
            '$call_descriptors_valid(S_schedule)', '$heap_valid($heap_graph(S_schedule))',
        ]
        seek('S_k', 'S_schedule', 8)
        checks += [
            'S_k.CURRENT =/= eps', 'S_k.FRAMES =/= eps',
            '$lookup($global_table_view(S_k).ENV, $ptascii("x")) = (n_x)',
            'S_k.STORE[n_x] = DEFINED (PFLOAT 0)',
            'S_k.STORE[n_calls] = DEFINED (PINT 1)', 'S_k.STORE[n_rhs] = DEFINED (PINT 0)',
            'S_k.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_k)', '$heap_valid($heap_graph(S_k))',
        ]
        seek('S_rhs', 'S_k', 9)
        checks += [
            'S_rhs.TODO = (VALUE_COPY 25) :: ptask_tail*', 'S_rhs.CURRENT = eps', 'S_rhs.FRAMES = eps',
            'S_rhs.RESULT = KNOWN (PINT 7)',
            'S_rhs.STORE[n_x] = DEFINED (PFLOAT 4611686018427387904)',
            'S_rhs.STORE[n_rhs] = DEFINED (PINT 1)', 'S_rhs.STORE[n_calls] = DEFINED (PINT 1)',
            'S_rhs.STORE[n_v] = DEFINED (PINT 100)',
            '$ternary_nan_diagnostics(S_rhs.EVENTS, "Warning") = 1',
            'PhpStep: S_rhs ~> S_result_atomic',
            'S_result_atomic.TODO = ptask_tail*', 'S_result_atomic.RESULT = KNOWN (PINT 7)',
            'S_result_atomic.STORE = S_rhs.STORE', 'S_result_atomic.EVENTS = S_rhs.EVENTS',
        ]
        step('S_result', 'S_rhs')
        checks += [
            '$ternary_nan_frontier(S_result, 5)', 'S_result.TODO = ptask_tail*',
            'S_result.RESULT = KNOWN (PINT 7)', 'S_result.STORE = S_rhs.STORE',
            'S_result.EVENTS = S_rhs.EVENTS', '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 3000)',
            # Derived refusals do not claim additional native histories.
            'S_retyped = S_post[.STORE[n_x] = DEFINED (PINT 0)]',
            '$boolnot_nan_ready(S_retyped, pboolnotnanwarning) = eps',
            'PhpStep: S_retyped ~> S_refused',
            'S_refused = S_retyped[.COMPLETION = UNSUPPORTED "shorthand ternary NaN changed CV representation"]',
            'S_rebound = S_post[.ENV = [BIND ($ptascii("x")) n_v]][.STORE[n_v] = DEFINED (PFLOAT 0)]',
            '$boolnot_nan_ready(S_rebound, pboolnotnanwarning) = eps',
            'PhpStep: S_rebound ~> S_rebound_refused',
            'S_rebound_refused = S_rebound[.COMPLETION = UNSUPPORTED "shorthand ternary NaN changed CV representation"]',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x)', 'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_rhs] = DEFINED (PINT ' + ('0' if throws else '1') + ')',
        'S_done.STORE[n_v] = DEFINED (PINT ' + ('100' if throws else '7') + ')',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_post, 0) = S_post[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
