#!/usr/bin/env python3
"""Source removal and supplied throw keep the borrowed old reference distinct."""
import base64
import json

import boolnot_reference_nan_warning_review_cases as cases
import boolnot_reference_nan_warning_protocol as shared

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
            f'{state}_found = $boolnot_reference_nan_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$boolnot_reference_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$boolnot_reference_nan_plan(S_entry) = (pboolnotnanwarning)',
        'pboolnotnanwarning.LINE = 25',
        'pboolnotnanwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'S_entry.RESULT = pboolnotnanwarning.INPUT',
        'S_entry.TODO = (TRUTH_RESULT true 25) :: ptask_tail*',
        '$number_bool(NFLOAT pboolnotnanwarning.BITS) = (true, true)',
        '$integer_operand_source(S_entry, pboolnotnanwarning.SITE, [PCFIELD 0], pboolnotnanwarning.INPUT)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_old)',
        '$lookup(S_entry.ENV, $ptascii("alias")) = (n_old)',
        'pboolnotnanwarning.CELL = n_old',
        '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_replacement)',
        'n_replacement =/= n_old',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_old] = DEFINED (PFLOAT pboolnotnanwarning.BITS)',
        'S_entry.STORE[n_replacement] = DEFINED (PFLOAT 4607182418800017408)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'n_old <- S_entry.REFCELLS', '~(n_replacement <- S_entry.REFCELLS)',
        '(HCELL n_old) <- S_entry.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_replacement) = 1',
        '$boolnot_nan_source(S_entry, pboolnotnanwarning)',
        '$boolnot_reference_nan_ready(S_entry, pboolnotnanwarning) = (pboolnotnanwarning.BITS)',
        '$boolnot_reference_nan_snapshot(S_entry, pboolnotnanwarning)',
        '$boolnot_reference_nan_warning_valid(S_entry, pboolnotnanwarning, 0)',
        '$boolnot_reference_nan_warning_valid(S_entry, pboolnotnanwarning, 1)',
        '$boolnot_nan_plan(S_entry) = eps',
        '$boolnot_nan_ready(S_entry, pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_plan(S_entry[.ENV = $unbind(S_entry.ENV, $ptascii("x"))]) = eps',
        '$boolnot_reference_nan_ready(S_entry[.ENV = $unbind(S_entry.ENV, $ptascii("x"))], pboolnotnanwarning) = (pboolnotnanwarning.BITS)',
        '~$boolnot_reference_nan_snapshot(S_entry[.ENV = $unbind(S_entry.ENV, $ptascii("x"))], pboolnotnanwarning)',
        '~$boolnot_reference_nan_snapshot(S_entry, pboolnotnanwarning[.CELL = n_replacement])',
        '$boolnot_reference_nan_ready(S_entry[.REFCELLS = eps], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.PROPREFS = [{CELL n_old, SOURCES eps}]], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.REFCOERCIONS = [{CELL n_old, SITE pboolnotnanwarning.SITE, LINE 25, VALUE eps}]], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.PARAMETERBACKINGS = [{FUNCTION pboolnotnanwarning.SITE, INDEX 0, CELL n_old, LINE 25, VALUE eps}]], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.LITERALREFRETAINED = [n_old]], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.LITERALREFDEBTS = [n_old]], pboolnotnanwarning) = eps',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    if throws:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$boolnot_reference_nan_frontier(S_capture, 1)',
        '$task_nodes(BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 0) = eps',
        '$boolnot_reference_nan_warning_valid(S_capture, pboolnotnanwarning, 0)',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_old) = 2',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$boolnot_reference_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pboolnotnanwarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
        'S_dispatch.EVENTS = S_entry.EVENTS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$boolnot_reference_nan_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1',
        'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    seek('S_post', 'S_entered', 6 if throws else 4)
    checks += [
        'S_post.CURRENT = eps', 'S_post.FRAMES = eps', 'S_post.GLOBALTABLE = eps',
        '$lookup(S_post.ENV, $ptascii("alias")) = (n_old)',
        '$lookup(S_post.ENV, $ptascii("replacement")) = (n_replacement)',
        'S_post.STORE[n_old] = DEFINED (PFLOAT 0)',
        'S_post.STORE[n_replacement] = DEFINED (PFLOAT 4607182418800017408)',
        'S_post.STORE[n_v] = DEFINED (PINT 100)',
        'S_post.STORE[n_calls] = DEFINED (PINT 1)',
        'n_old <- S_post.REFCELLS', '(HCELL n_old) <- S_post.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_post)), HCELL n_old) = 1',
        '$boolnot_nan_source(S_post, pboolnotnanwarning)',
        '$boolnot_reference_nan_ready(S_post, pboolnotnanwarning) = (0)',
        '~$boolnot_reference_nan_snapshot(S_post, pboolnotnanwarning)',
        '~$boolnot_reference_nan_warning_valid(S_post, pboolnotnanwarning, 0)',
        '$boolnot_reference_nan_warning_valid(S_post, pboolnotnanwarning, 1)',
        '~$error_call_valid(S_post, perrorcall)',
        '$error_call_valid(S_post, perrorcall_entered)',
        '$task_nodes(BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1) = eps',
        '$boolnot_reference_nan_diagnostics(S_post.EVENTS, "Deprecated") = 0',
        'S_post.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_post)', '$heap_valid($heap_graph(S_post))',
    ]
    if throws:
        checks += [
            'S_post.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
            '~$boolnot_reference_nan_tasks(S_post.TODO)',
            '$lookup(S_post.ENV, $ptascii("x")) = (n_replacement)',
            'n_replacement <- S_post.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S_post)), HCELL n_replacement) = 2',
            '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_post)), HOBJECT n_second) = 2',
            '$throwable_live(S_post, n_second)',
            '$throwable_previous_id(S_post, n_second) = eps',
            '$throwable_field(S_post, n_second, "line") = PINT 20',
            '$boolnot_reference_nan_diagnostics(S_post.EVENTS, "Warning") = 0',
            'S_done = $drive_steps(S_post, 3000)',
        ]
    else:
        checks += [
            'S_post.TODO = (BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1) :: ptask_tail*',
            '$lookup(S_post.ENV, $ptascii("x")) = eps',
            '~(n_replacement <- S_post.REFCELLS)',
            '$heap_owners($heap_prune($heap_graph(S_post)), HCELL n_replacement) = 1',
            '$boolnot_reference_nan_diagnostics(S_post.EVENTS, "Warning") = 1',
            'PhpStep: S_post ~> S_result_atomic',
            'S_result_atomic = S_post[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        ]
        step('S_result', 'S_post')
        checks += [
            'S_result = S_result_atomic', '$boolnot_reference_nan_frontier(S_result, 5)',
            'S_result.STORE = S_post.STORE', 'S_result.ENV = S_post.ENV',
            'S_result.ALLOCATIONS = S_post.ALLOCATIONS', 'S_result.REFCELLS = S_post.REFCELLS',
            'S_result.EVENTS = S_post.EVENTS',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_old) = 1',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 3000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_old)',
        '$lookup(S_done.ENV, $ptascii("replacement")) = (n_replacement)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'n_old <- S_done.REFCELLS', '(HCELL n_old) <- S_done.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_old) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_post, 0) = S_post[.COMPLETION = BUDGET]',
    ]
    if throws:
        checks += [
            '$lookup(S_done.ENV, $ptascii("x")) = (n_replacement)',
            'S_done.STORE[n_old] = DEFINED (PINT 7)',
            'S_done.STORE[n_replacement] = DEFINED (PINT 8)',
            'S_done.STORE[n_v] = DEFINED (PINT 100)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement) = 2',
        ]
    else:
        checks += [
            '$lookup(S_done.ENV, $ptascii("x")) = eps',
            'S_done.STORE[n_old] = DEFINED (PINT 8)',
            'S_done.STORE[n_v] = DEFINED (PBOOL true)',
            'S_done.STORE[n_replacement] = DEFINED (PFLOAT 4607182418800017408)',
        ]
    # Derived controls: no native claim for losing the retained alias or retyping it.
    checks += [
        'S_lost = S_post[.ENV = $unbind(S_post.ENV, $ptascii("alias"))]',
        '$heap_owners($heap_prune($heap_graph(S_lost)), HCELL n_old) = 0',
        '$boolnot_reference_nan_ready(S_lost, pboolnotnanwarning) = eps',
        '$boolnot_nan_source(S_lost, pboolnotnanwarning)',
        '$call_task_valid(S_lost, BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1)',
        'S_lost_resume = S_lost[.TODO = [BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1]]',
        'PhpStep: S_lost_resume ~> S_lost_refused',
        'S_lost_refused = S_lost_resume[.COMPLETION = UNSUPPORTED "boolean NOT NaN changed reference representation"]',
        'S_retyped = S_post[.TODO = [BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1]][.STORE[n_old] = DEFINED (PINT 0)]',
        '$boolnot_reference_nan_ready(S_retyped, pboolnotnanwarning) = eps',
        'PhpStep: S_retyped ~> S_retyped_refused',
        'S_retyped_refused = S_retyped[.COMPLETION = UNSUPPORTED "boolean NOT NaN changed reference representation"]',
    ]
    assert len(checks) == len(set(checks))
    return checks
