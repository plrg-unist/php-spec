#!/usr/bin/env python3
"""XOR throws preserve the cached phase and finish required pending warnings."""
import base64
import json

import xor_nan_warning_review_cases as cases

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    first = name.endswith('-masked')
    nan = '9221120237041090560'
    message = '$ptascii("unexpected NAN value was coerced to bool")'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $boolxor_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$boolxor_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    def warning(state, label, phase):
        call = 'perrorcall_' + label
        checks.extend([
            f'{state}.TODO = (ERROR_HANDLER_INVOKE {call}) :: ptask_rest_{label}*',
            f'{call}.RESUME = BOOLXOR_WARNING pboolxoroperation {phase} 1',
            f'{call}.TARGET = eps', f'{call}.SITE = pboolxoroperation.LEFT.SITE',
            f'{call}.LEVEL = 2', f'{call}.LINE = 25',
            f'{call}.MESSAGE = {message}',
            f'{call}.EVENT = DIAGNOSTIC "Warning" ({message}) 25',
            f'$error_call_valid({state}, {call})', f'$call_descriptors_valid({state})',
        ])

    def entered(state, label, phase):
        frame, call = 'pframe_' + label, 'perrorcall_' + label + '_entered'
        checks.extend([
            f'{state}.CURRENT =/= eps', f'$boolxor_entered({state}.FRAMES, {phase})',
            f'{state}.FRAMES = {frame} :: pframe_tail_{label}*',
            f'$boolxor_handler_frame({frame}, {phase})',
            f'{frame}.TODO = (ERROR_HANDLER_RESULT {call}) :: ptask_saved_{label}*',
            f'{call}.RESUME = BOOLXOR_WARNING pboolxoroperation {phase} 1',
            f'{call}.TARGET =/= eps', f'$call_descriptors_valid({state})',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$boolxor_plan(S_entry) = (pboolxoroperation)',
        'S_entry.TODO = (BINARY_RIGHT LOGICALXOR pboolxoroperation.LEFT.INPUT 25) :: ptask_outer*',
        'S_entry.RESULT = pboolxoroperation.RIGHT.INPUT',
        'pboolxoroperation.LEFT.INPUT = VARIABLE ($ptascii("a")) 24',
        'pboolxoroperation.RIGHT.INPUT = VARIABLE ($ptascii("b")) 25',
        'pboolxoroperation.LEFT.LINE = 25', 'pboolxoroperation.RIGHT.LINE = 25',
        'pboolxoroperation.LEFT.BITS = ' + nan,
        'pboolxoroperation.RIGHT.BITS = ' + (nan if first else '0'),
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_entry.ENV, $ptascii("b")) = (n_b)', 'n_a =/= n_b',
        'pboolxoroperation.LEFT.CELL = n_a', 'pboolxoroperation.RIGHT.CELL = n_b',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_a] = DEFINED (PFLOAT pboolxoroperation.LEFT.BITS)',
        'S_entry.STORE[n_b] = DEFINED (PFLOAT pboolxoroperation.RIGHT.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$boolxor_source(S_entry, pboolxoroperation)', '$boolxor_snapshot(S_entry, pboolxoroperation)',
        '$boolxor_convert_valid(S_entry, pboolxoroperation, BOOLXOR_LEFT)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_b) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_second) = 1',
        '$task_nodes(BOOLXOR_CONVERT pboolxoroperation BOOLXOR_LEFT) = eps',
        'S_entry.EVENTS = eps', '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (BOOLXOR_CONVERT pboolxoroperation BOOLXOR_LEFT) :: ptask_outer*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += ['S_capture = S_capture_atomic', '$boolxor_frontier(S_capture, 1)']
    seek('S_left_dispatch', 'S_capture', 3)
    warning('S_left_dispatch', 'left', 'BOOLXOR_LEFT')
    seek('S_left_entered', 'S_left_dispatch', 4)
    entered('S_left_entered', 'left', 'BOOLXOR_LEFT')

    if first:
        seek('S_pending', 'S_left_entered', 12)
        checks += [
            'S_pending.TODO = (BOOLXOR_PENDING pboolxoroperation 0 n_second) :: ptask_pending_tail*',
            'S_pending.CURRENT = eps', 'S_pending.FRAMES = eps',
            'S_pending.STORE[n_a] = DEFINED (PFLOAT 0)',
            'S_pending.STORE[n_b] = DEFINED (PFLOAT ' + nan + ')',
            'S_pending.STORE[n_v] = DEFINED (PINT 100)', 'S_pending.STORE[n_calls] = DEFINED (PINT 1)',
            'S_pending.ERRORHANDLER.LEVELS = 8192', 'S_pending.ERRORHANDLER.CALLBACK =/= eps',
            '~$error_handler_eligible(S_pending, 2)',
            '$boolxor_source(S_pending, pboolxoroperation)',
            '~$boolxor_snapshot(S_pending, pboolxoroperation)',
            '~$boolxor_convert_valid(S_pending, pboolxoroperation, BOOLXOR_LEFT)',
            '$boolxor_ready(S_pending, pboolxoroperation, BOOLXOR_RIGHT false) = (' + nan + ')',
            '$boolxor_pending_valid(S_pending, pboolxoroperation, 0, n_second)',
            '~$boolxor_pending_valid(S_pending, pboolxoroperation, 2, n_second)',
            '$task_nodes(BOOLXOR_PENDING pboolxoroperation 0 n_second) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
            '$boolxor_diagnostics(S_pending.EVENTS, "Warning") = 0',
            '$throwable_previous_id(S_pending, n_second) = eps',
            '$throwable_field(S_pending, n_second, "line") = PINT 20',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_search = S_pending[.TODO = (THROW_SEARCH n_second) :: ptask_pending_tail*]',
            '$error_read_discard(S_search, BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 1) = S_pending',
            '$error_read_discard(S_search, BOOLXOR_WARNING pboolxoroperation (BOOLXOR_RIGHT true) 1) = S_search',
            '$error_read_discard(S_search, BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 0) = S_search',
            'PhpStep: S_pending ~> S_default_atomic',
            'S_default_atomic.TODO = (BOOLXOR_PENDING pboolxoroperation 1 n_second) :: ptask_pending_tail*',
            'S_default_atomic.STORE = S_pending.STORE',
            '$boolxor_diagnostics(S_default_atomic.EVENTS, "Warning") = 1',
            '$integer_outputs(S_default_atomic.EVENTS) = $integer_outputs(S_pending.EVENTS)',
            '$heap_owners($heap_prune($heap_graph(S_default_atomic)), HOBJECT n_second) = 2',
        ]
        step('S_default', 'S_pending')
        checks += [
            '$boolxor_frontier(S_default, 13)', 'S_default.TODO = S_default_atomic.TODO',
            'S_default.STORE = S_pending.STORE', 'S_default.ERRORHANDLER = S_pending.ERRORHANDLER',
            '$boolxor_diagnostics(S_default.EVENTS, "Warning") = 1',
            '$integer_outputs(S_default.EVENTS) = $integer_outputs(S_pending.EVENTS)',
            '$heap_owners($heap_prune($heap_graph(S_default)), HOBJECT n_second) = 2',
            'PhpStep: S_default ~> S_throw_atomic',
            'S_throw_atomic = S_default[.TODO = (THROW_SEARCH n_second) :: ptask_pending_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            'S_retyped = S_pending[.STORE[n_b] = DEFINED (PINT 0)]',
            'PhpStep: S_retyped ~> S_refused',
            'S_refused = S_retyped[.COMPLETION = UNSUPPORTED "logical XOR pending RIGHT representation"]',
            '$drive_steps(S_pending, 0) = S_pending[.COMPLETION = BUDGET]',
            '$drive_steps(S_default, 0) = S_default[.COMPLETION = BUDGET]',
        ]
        seek('S_throw', 'S_default', 14)
        checks += ['S_throw.TODO = S_throw_atomic.TODO']
    else:
        seek('S_left_return', 'S_left_entered', 5)
        checks += [
            'S_left_return.TODO = (BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 1) :: ptask_after_left*',
            'S_left_return.STORE[n_a] = DEFINED (PFLOAT 4607182418800017408)',
            'S_left_return.STORE[n_b] = DEFINED (PFLOAT ' + nan + ')',
            'S_left_return.STORE[n_v] = DEFINED (PINT 100)',
            'S_left_return.STORE[n_calls] = DEFINED (PINT 1)',
            '~$boolxor_snapshot(S_left_return, pboolxoroperation)',
            '$boolxor_ready(S_left_return, pboolxoroperation, BOOLXOR_LEFT) = (4607182418800017408)',
            '$boolxor_warning_valid(S_left_return, pboolxoroperation, BOOLXOR_LEFT, 1)',
            '$boolxor_diagnostics(S_left_return.EVENTS, "Warning") = 0',
            'PhpStep: S_left_return ~> S_cache_atomic',
            'S_cache_atomic = S_left_return[.TODO = (BOOLXOR_CONVERT pboolxoroperation (BOOLXOR_RIGHT true)) :: ptask_after_left*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        ]
        step('S_right_convert', 'S_left_return')
        checks += [
            '$boolxor_frontier(S_right_convert, 6)', 'S_right_convert.TODO = S_cache_atomic.TODO',
            'S_right_convert.STORE = S_left_return.STORE',
            '$boolxor_ready(S_right_convert, pboolxoroperation, BOOLXOR_RIGHT true) = (' + nan + ')',
            '$boolxor_warning_snapshot(S_right_convert, pboolxoroperation, BOOLXOR_RIGHT true)',
            '$task_nodes(BOOLXOR_CONVERT pboolxoroperation (BOOLXOR_RIGHT true)) = eps',
        ]
        seek('S_right_dispatch', 'S_right_convert', 8)
        warning('S_right_dispatch', 'right', '(BOOLXOR_RIGHT true)')
        seek('S_right_entered', 'S_right_dispatch', 9)
        entered('S_right_entered', 'right', '(BOOLXOR_RIGHT true)')
        seek('S_throw', 'S_right_entered', 14)
        checks += [
            'S_throw.STORE[n_b] = DEFINED (PFLOAT 0)',
            'S_throw.ERRORHANDLER.LEVELS = 2',
            '~$error_call_valid(S_throw, perrorcall_right)',
            '$error_call_valid(S_throw, perrorcall_right_entered)',
            '$boolxor_warning_valid(S_throw, pboolxoroperation, BOOLXOR_RIGHT true, 1)',
            '$drive_steps(S_right_dispatch, 0) = S_right_dispatch[.COMPLETION = BUDGET]',
        ]

    checks += [
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$boolxor_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_throw.ENV, $ptascii("b")) = (n_b)',
        'S_throw.STORE[n_a] = DEFINED (PFLOAT 0)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT ' + ('1' if first else '2') + ')',
        '$boolxor_source(S_throw, pboolxoroperation)',
        '~$error_call_valid(S_throw, perrorcall_left)',
        '$error_call_valid(S_throw, perrorcall_left_entered)',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_b) = 1',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
        '$throwable_field(S_throw, n_second, "line") = PINT 20',
        '$boolxor_diagnostics(S_throw.EVENTS, "Warning") = ' + ('1' if first else '0'),
        '$boolxor_diagnostics(S_throw.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_done.ENV, $ptascii("b")) = (n_b)',
        'S_done.STORE[n_a] = DEFINED (PINT 8)', 'S_done.STORE[n_b] = DEFINED (PINT 9)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('1' if first else '2') + ')',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_throw, 0) = S_throw[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
