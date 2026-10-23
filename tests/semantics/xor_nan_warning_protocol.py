#!/usr/bin/env python3
"""Logical XOR reads each float after its callback and retains LEFT truth."""
import base64
import json

import xor_nan_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $boolxor_task(ptask) : bool
def $boolxor_task(BOOLXOR_CONVERT pboolxoroperation pboolxorphase) = true
def $boolxor_task(BOOLXOR_WARNING pboolxoroperation pboolxorphase n) = true
def $boolxor_task(BOOLXOR_PENDING pboolxoroperation n_stage n_exception) = true
def $boolxor_task(ERROR_HANDLER_INVOKE perrorcall) = $boolxor_task(perrorcall.RESUME)
def $boolxor_task(ERROR_HANDLER_RESULT perrorcall) = $boolxor_task(perrorcall.RESUME)
def $boolxor_task(ERROR_HANDLER_CLEAN perrorcall) = $boolxor_task(perrorcall.RESUME)
def $boolxor_task(ptask) = false -- otherwise
dec $boolxor_tasks(ptask*) : bool
def $boolxor_tasks(eps) = false
def $boolxor_tasks(ptask :: ptask_tail*) = ($boolxor_task(ptask) \/ $boolxor_tasks(ptask_tail*))
dec $boolxor_handler_frame(pframe, pboolxorphase) : bool
def $boolxor_handler_frame(pframe, pboolxorphase) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOOLXOR_WARNING pboolxoroperation pboolxorphase 1
  -- if perrorcall.TARGET =/= eps
def $boolxor_handler_frame(pframe, pboolxorphase) = false -- otherwise
dec $boolxor_entered(pframe*, pboolxorphase) : bool
def $boolxor_entered(eps, pboolxorphase) = false
def $boolxor_entered(pframe :: pframe_tail*, pboolxorphase) = ($boolxor_handler_frame(pframe, pboolxorphase) \/ $boolxor_entered(pframe_tail*, pboolxorphase))
dec $boolxor_frontier(pstate, nat) : bool
def $boolxor_frontier(S, 0) = ($boolxor_plan(S) =/= eps)
def $boolxor_frontier(S, 1) = true
  -- if S.TODO = (BOOLXOR_CONVERT pboolxoroperation BOOLXOR_LEFT) :: ptask_tail*
def $boolxor_frontier(S, 2) = true
  -- if S.TODO = (BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 0) :: ptask_tail*
def $boolxor_frontier(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 1
  -- if perrorcall.TARGET = eps
def $boolxor_frontier(S, 4) = (S.CURRENT =/= eps /\ $boolxor_entered(S.FRAMES, BOOLXOR_LEFT))
def $boolxor_frontier(S, 5) = true
  -- if S.TODO = (BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 1) :: ptask_tail*
def $boolxor_frontier(S, 6) = true
  -- if S.TODO = (BOOLXOR_CONVERT pboolxoroperation (BOOLXOR_RIGHT b)) :: ptask_tail*
def $boolxor_frontier(S, 7) = true
  -- if S.TODO = (BOOLXOR_WARNING pboolxoroperation (BOOLXOR_RIGHT b) 0) :: ptask_tail*
def $boolxor_frontier(S, 8) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOOLXOR_WARNING pboolxoroperation (BOOLXOR_RIGHT b) 1
  -- if perrorcall.TARGET = eps
def $boolxor_frontier(S, 9) = (S.CURRENT =/= eps /\ $boolxor_entered(S.FRAMES, BOOLXOR_RIGHT true))
def $boolxor_frontier(S, 10) = true
  -- if S.TODO = (BOOLXOR_WARNING pboolxoroperation (BOOLXOR_RIGHT b) 1) :: ptask_tail*
def $boolxor_frontier(S, 11) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprBinaryOpLogicalXor expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PBOOL b)
  -- if ~$boolxor_tasks(S.TODO)
def $boolxor_frontier(S, 12) = true
  -- if S.TODO = (BOOLXOR_PENDING pboolxoroperation 0 n_exception) :: ptask_tail*
def $boolxor_frontier(S, 13) = true
  -- if S.TODO = (BOOLXOR_PENDING pboolxoroperation 1 n_exception) :: ptask_tail*
def $boolxor_frontier(S, 14) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if ~$boolxor_tasks(S.TODO)
def $boolxor_frontier(S, n) = false -- otherwise
dec $boolxor_seek(pstate, nat, nat) : pstate
def $boolxor_seek(S, n_stage, n) = S -- if $boolxor_frontier(S, n_stage)
def $boolxor_seek(S, n_stage, n) = S
  -- if ~$boolxor_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $boolxor_seek(S, n_stage, n) = S
  -- if ~$boolxor_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $boolxor_seek(S, n_stage, n) = $boolxor_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$boolxor_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $boolxor_diagnostic(pevent, text) : nat
def $boolxor_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $boolxor_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $boolxor_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $boolxor_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $boolxor_diagnostic(pevent, text) = 0 -- otherwise
dec $boolxor_diagnostics(pevent*, text) : nat
def $boolxor_diagnostics(eps, text) = 0
def $boolxor_diagnostics(pevent :: pevent_tail*, text) = $($boolxor_diagnostic(pevent, text) + $boolxor_diagnostics(pevent_tail*, text))
'''

def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $boolxor_seek({before}, {stage}, 3000)',
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

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$boolxor_plan(S_entry) = (pboolxoroperation)',
        'pboolxoroperation.LEFT.LINE = 25', 'pboolxoroperation.RIGHT.LINE = 25',
        'pboolxoroperation.LEFT.INPUT = VARIABLE ($ptascii("a")) 24',
        'pboolxoroperation.RIGHT.INPUT = VARIABLE ($ptascii("b")) 25',
        'S_entry.RESULT = pboolxoroperation.RIGHT.INPUT',
        'S_entry.TODO = (BINARY_RIGHT LOGICALXOR pboolxoroperation.LEFT.INPUT 25) :: ptask_tail*',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_entry.ENV, $ptascii("b")) = (n_b)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'pboolxoroperation.LEFT.CELL = n_a', 'pboolxoroperation.RIGHT.CELL = n_b', 'n_a =/= n_b',
        'S_entry.STORE[n_a] = DEFINED (PFLOAT pboolxoroperation.LEFT.BITS)',
        'S_entry.STORE[n_b] = DEFINED (PFLOAT 0)', 'pboolxoroperation.RIGHT.BITS = 0',
        '$fparts_nan($float_decode(pboolxoroperation.LEFT.BITS))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$integer_operand_source(S_entry, pboolxoroperation.LEFT.SITE, [PCFIELD 0], pboolxoroperation.LEFT.INPUT)',
        '$integer_operand_source(S_entry, pboolxoroperation.LEFT.SITE, [PCFIELD 1], pboolxoroperation.RIGHT.INPUT)',
        '$boolxor_source(S_entry, pboolxoroperation)', '$boolxor_snapshot(S_entry, pboolxoroperation)',
        '$boolxor_ready(S_entry, pboolxoroperation, BOOLXOR_LEFT) = (pboolxoroperation.LEFT.BITS)',
        '$boolxor_ready(S_entry, pboolxoroperation, BOOLXOR_RIGHT false) = (0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_b) = 1',
        'S_entry.EVENTS = eps', '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$boolxor_plan(S_entry[.ORIGIN = eps]) = eps',
        '$boolxor_plan(S_entry[.CODE = eps]) = eps',
        '$boolxor_plan(S_entry[.TODO = [BINARY_RIGHT BITXOR pboolxoroperation.LEFT.INPUT 25]]) = eps',
        '$boolxor_plan(S_entry[.RESULT = KNOWN (PFLOAT 0)]) = eps',
        '$boolxor_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$boolxor_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '$boolxor_plan(S_entry[.STORE[n_a] = DEFINED (PFLOAT 0)]) = eps',
        '~$boolxor_source(S_entry, pboolxoroperation[.LEFT.LINE = 24])',
        '~$boolxor_source(S_entry, pboolxoroperation[.LEFT.CELL = n_b])',
        '~$boolxor_source(S_entry, pboolxoroperation[.RIGHT.INPUT = pboolxoroperation.LEFT.INPUT])',
        '~$boolxor_source(S_entry, pboolxoroperation[.LEFT.BITS = 0])',
        '~$boolxor_source(S_entry, pboolxoroperation[.RIGHT.BITS = 18446744073709551616])',
        '$boolxor_ready(S_entry[.ENV = eps], pboolxoroperation, BOOLXOR_LEFT) = eps',
        '$boolxor_ready(S_entry[.REFCELLS = [n_a]], pboolxoroperation, BOOLXOR_LEFT) = eps',
        '$boolxor_ready(S_entry[.STORE[n_a] = DEFINED (PINT 0)], pboolxoroperation, BOOLXOR_LEFT) = eps',
        '$boolnot_nan_plan(S_entry) = eps', '$boolcast_nan_plan(S_entry) = eps', '$arraycast_nan_plan(S_entry) = eps',
        '~$boolnot_nan_source(S_entry, pboolxoroperation.LEFT)',
        '~$boolcast_nan_source(S_entry, pboolxoroperation.LEFT)',
        '~$arraycast_nan_source(S_entry, pboolxoroperation.LEFT)',
        'PhpStep: S_entry ~> S_begin_atomic',
        'S_begin_atomic = S_entry[.TODO = (BOOLXOR_CONVERT pboolxoroperation BOOLXOR_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_begin', 'S_entry')
    checks += [
        'S_begin = S_begin_atomic', '$boolxor_frontier(S_begin, 1)',
        '$boolxor_convert_valid(S_begin, pboolxoroperation, BOOLXOR_LEFT)',
        '$task_nodes(BOOLXOR_CONVERT pboolxoroperation BOOLXOR_LEFT) = eps',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))',
        'PhpStep: S_begin ~> S_capture_atomic',
        'S_capture_atomic = S_begin[.TODO = (BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 0) :: ptask_tail*]',
    ]
    step('S_capture', 'S_begin')
    checks += [
        'S_capture = S_capture_atomic', '$boolxor_frontier(S_capture, 2)',
        '$boolxor_warning_valid(S_capture, pboolxoroperation, BOOLXOR_LEFT, 0)',
        '$boolxor_warning_valid(S_capture, pboolxoroperation, BOOLXOR_LEFT, 1)',
        '~$boolxor_warning_valid(S_capture, pboolxoroperation, BOOLXOR_LEFT, 2)',
        '$task_nodes(BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 0) = eps',
    ]
    step('S_dispatch_left', 'S_capture')
    checks += [
        '$boolxor_frontier(S_dispatch_left, 3)',
        'S_dispatch_left.TODO = (ERROR_HANDLER_INVOKE perrorcall_left) :: ptask_tail*',
        'perrorcall_left.RESUME = BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 1',
        'perrorcall_left.TARGET = eps', 'perrorcall_left.SITE = pboolxoroperation.LEFT.SITE',
        'perrorcall_left.LEVEL = 2', 'perrorcall_left.LINE = 25',
        'perrorcall_left.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
        'perrorcall_left.EVENT = DIAGNOSTIC "Warning" perrorcall_left.MESSAGE 25',
        '$error_call_valid(S_dispatch_left, perrorcall_left)',
        '~$error_call_valid(S_dispatch_left, perrorcall_left[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch_left, perrorcall_left[.LINE = 24])',
        'S_dispatch_left.EVENTS = eps', '$call_descriptors_valid(S_dispatch_left)',
    ]
    seek('S_entered_left', 'S_dispatch_left', 4)
    checks += [
        'S_entered_left.FRAMES = pframe_left :: pframe_tail*',
        '$boolxor_handler_frame(pframe_left, BOOLXOR_LEFT)',
        'pframe_left.TODO = (ERROR_HANDLER_RESULT perrorcall_left_entered) :: ptask_saved*',
        'perrorcall_left_entered.RESUME = BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 1',
        'perrorcall_left_entered.TARGET =/= eps', '$call_descriptors_valid(S_entered_left)',
    ]
    seek('S_return_left', 'S_entered_left', 5)
    checks += [
        'S_return_left.TODO = (BOOLXOR_WARNING pboolxoroperation BOOLXOR_LEFT 1) :: ptask_tail*',
        'S_return_left.STORE[n_a] = DEFINED (PFLOAT 4607182418800017408)',
        'S_return_left.STORE[n_b] = DEFINED (PFLOAT pboolxoroperation.LEFT.BITS)',
        'S_return_left.STORE[n_v] = DEFINED (PINT 100)', 'S_return_left.STORE[n_calls] = DEFINED (PINT 1)',
        '$boolxor_source(S_return_left, pboolxoroperation)', '~$boolxor_snapshot(S_return_left, pboolxoroperation)',
        '$boolxor_ready(S_return_left, pboolxoroperation, BOOLXOR_LEFT) = (4607182418800017408)',
        '$boolxor_nan(S_return_left, pboolxoroperation, BOOLXOR_RIGHT true)',
        '~$boolxor_warning_valid(S_return_left, pboolxoroperation, BOOLXOR_LEFT, 0)',
        '$boolxor_warning_valid(S_return_left, pboolxoroperation, BOOLXOR_LEFT, 1)',
        '~$error_call_valid(S_return_left, perrorcall_left)',
        '$error_call_valid(S_return_left, perrorcall_left_entered)',
        '$boolxor_diagnostics(S_return_left.EVENTS, "Warning") = 0',
        '$heap_owners($heap_prune($heap_graph(S_return_left)), HCELL n_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return_left)), HCELL n_b) = 1',
        '$call_descriptors_valid(S_return_left)', '$heap_valid($heap_graph(S_return_left))',
        'PhpStep: S_return_left ~> S_left_atomic',
        'S_left_atomic = S_return_left[.TODO = (BOOLXOR_CONVERT pboolxoroperation (BOOLXOR_RIGHT true)) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Derived controls distinguish the post-warning live read from initial NaN.
        'S_live_zero = S_return_left[.STORE[n_a] = DEFINED (PFLOAT 0)]',
        'PhpStep: S_live_zero ~> S_zero_cached',
        'S_zero_cached = S_live_zero[.TODO = (BOOLXOR_CONVERT pboolxoroperation (BOOLXOR_RIGHT false)) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_live_nan = S_return_left[.STORE[n_a] = DEFINED (PFLOAT pboolxoroperation.LEFT.BITS)]',
        'PhpStep: S_live_nan ~> S_nan_cached',
        'S_nan_cached = S_live_nan[.TODO = (BOOLXOR_CONVERT pboolxoroperation (BOOLXOR_RIGHT true)) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_nan_cached.EVENTS = S_return_left.EVENTS',
        'S_left_retyped = S_return_left[.STORE[n_a] = DEFINED (PINT 0)]',
        'PhpStep: S_left_retyped ~> S_left_boundary',
        'S_left_boundary = S_left_retyped[.COMPLETION = UNSUPPORTED "logical XOR changed CV representation"]',
    ]
    step('S_cached', 'S_return_left')
    checks += [
        'S_cached = S_left_atomic', '$boolxor_frontier(S_cached, 6)',
        'S_cached.STORE = S_return_left.STORE', 'S_cached.EVENTS = S_return_left.EVENTS',
        '$boolxor_convert_valid(S_cached, pboolxoroperation, BOOLXOR_RIGHT true)',
        '$task_nodes(BOOLXOR_CONVERT pboolxoroperation (BOOLXOR_RIGHT true)) = eps',
        '$call_descriptors_valid(S_cached)', '$heap_valid($heap_graph(S_cached))',
        'PhpStep: S_cached ~> S_right_capture_atomic',
        'S_right_capture_atomic = S_cached[.TODO = (BOOLXOR_WARNING pboolxoroperation (BOOLXOR_RIGHT true) 0) :: ptask_tail*]',
    ]
    step('S_capture_right', 'S_cached')
    checks += [
        'S_capture_right = S_right_capture_atomic', '$boolxor_frontier(S_capture_right, 7)',
        '$boolxor_warning_valid(S_capture_right, pboolxoroperation, BOOLXOR_RIGHT true, 0)',
    ]
    step('S_dispatch_right', 'S_capture_right')
    checks += [
        '$boolxor_frontier(S_dispatch_right, 8)',
        'S_dispatch_right.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_tail*',
        'perrorcall_right.RESUME = BOOLXOR_WARNING pboolxoroperation (BOOLXOR_RIGHT true) 1',
        'perrorcall_right.TARGET = eps', 'perrorcall_right.SITE = pboolxoroperation.LEFT.SITE',
        'perrorcall_right.LEVEL = 2', 'perrorcall_right.LINE = 25',
        'perrorcall_right.MESSAGE = perrorcall_left.MESSAGE',
        'perrorcall_right.EVENT = DIAGNOSTIC "Warning" perrorcall_right.MESSAGE 25',
        '$error_call_valid(S_dispatch_right, perrorcall_right)',
        'S_dispatch_right.EVENTS = S_return_left.EVENTS', '$call_descriptors_valid(S_dispatch_right)',
    ]
    seek('S_entered_right', 'S_dispatch_right', 9)
    checks += [
        'S_entered_right.FRAMES = pframe_right :: pframe_tail*',
        '$boolxor_handler_frame(pframe_right, BOOLXOR_RIGHT true)',
        'pframe_right.TODO = (ERROR_HANDLER_RESULT perrorcall_right_entered) :: ptask_saved*',
        'perrorcall_right_entered.RESUME = BOOLXOR_WARNING pboolxoroperation (BOOLXOR_RIGHT true) 1',
        'perrorcall_right_entered.TARGET =/= eps', '$call_descriptors_valid(S_entered_right)',
    ]
    seek('S_return_right', 'S_entered_right', 10)
    checks += [
        'S_return_right.TODO = (BOOLXOR_WARNING pboolxoroperation (BOOLXOR_RIGHT true) 1) :: ptask_tail*',
        'S_return_right.STORE[n_a] = DEFINED (PFLOAT 0)', 'S_return_right.STORE[n_b] = DEFINED (PFLOAT 0)',
        'S_return_right.STORE[n_v] = DEFINED (PINT 100)', 'S_return_right.STORE[n_calls] = DEFINED (PINT 2)',
        '$boolxor_source(S_return_right, pboolxoroperation)',
        '$boolxor_ready(S_return_right, pboolxoroperation, BOOLXOR_RIGHT true) = (0)',
        '~$boolxor_warning_valid(S_return_right, pboolxoroperation, BOOLXOR_RIGHT true, 0)',
        '$boolxor_warning_valid(S_return_right, pboolxoroperation, BOOLXOR_RIGHT true, 1)',
        '~$error_call_valid(S_return_right, perrorcall_right)',
        '$error_call_valid(S_return_right, perrorcall_right_entered)',
        '$boolxor_diagnostics(S_return_right.EVENTS, "Warning") = 1',
        '$boolxor_diagnostics(S_return_right.EVENTS, "Deprecated") = 0',
        '$heap_owners($heap_prune($heap_graph(S_return_right)), HCELL n_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return_right)), HCELL n_b) = 1',
        '$call_descriptors_valid(S_return_right)', '$heap_valid($heap_graph(S_return_right))',
        'PhpStep: S_return_right ~> S_result_atomic',
        'S_result_atomic = S_return_right[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Derived RIGHT controls preserve the cache and do not rewarn after a resume.
        'S_left_changed = S_return_right[.STORE[n_a] = DEFINED (PFLOAT pboolxoroperation.LEFT.BITS)]',
        'PhpStep: S_left_changed ~> S_cached_result',
        'S_cached_result = S_left_changed[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_right_nan = S_return_right[.STORE[n_b] = DEFINED (PFLOAT pboolxoroperation.LEFT.BITS)]',
        'PhpStep: S_right_nan ~> S_nan_result',
        'S_nan_result = S_right_nan[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_nan_result.EVENTS = S_return_right.EVENTS',
        'S_right_retyped = S_return_right[.STORE[n_b] = DEFINED (PINT 0)]',
        'PhpStep: S_right_retyped ~> S_right_boundary',
        'S_right_boundary = S_right_retyped[.COMPLETION = UNSUPPORTED "logical XOR changed CV representation"]',
    ]
    step('S_result', 'S_return_right')
    checks += [
        'S_result = S_result_atomic', '$boolxor_frontier(S_result, 11)',
        'S_result.STORE = S_return_right.STORE', 'S_result.ENV = S_return_right.ENV',
        'S_result.ALLOCATIONS = S_return_right.ALLOCATIONS', 'S_result.REFCELLS = S_return_right.REFCELLS',
        'S_result.EVENTS = S_return_right.EVENTS', 'S_result.STRINGDATA = S_return_right.STRINGDATA',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("a")) = (n_a)', '$lookup(S_done.ENV, $ptascii("b")) = (n_b)',
        'S_done.STORE[n_a] = DEFINED (PINT 8)', 'S_done.STORE[n_b] = DEFINED (PINT 9)',
        'S_done.STORE[n_v] = DEFINED (PBOOL true)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_b) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$boolxor_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$boolxor_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return_left, 0) = S_return_left[.COMPLETION = BUDGET]',
        '$drive_steps(S_return_right, 0) = S_return_right[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
