#!/usr/bin/env python3
"""NaN array casting warns before copying the live float into a singleton."""
import base64
import json

import arraycast_nan_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $arraycast_nan_task(ptask) : bool
def $arraycast_nan_task(ARRAYCAST_NAN_WARNING pboolnotnanwarning n) = true
def $arraycast_nan_task(ERROR_HANDLER_INVOKE perrorcall) = $arraycast_nan_task(perrorcall.RESUME)
def $arraycast_nan_task(ERROR_HANDLER_RESULT perrorcall) = $arraycast_nan_task(perrorcall.RESUME)
def $arraycast_nan_task(ERROR_HANDLER_CLEAN perrorcall) = $arraycast_nan_task(perrorcall.RESUME)
def $arraycast_nan_task(ptask) = false -- otherwise
dec $arraycast_nan_tasks(ptask*) : bool
def $arraycast_nan_tasks(eps) = false
def $arraycast_nan_tasks(ptask :: ptask_tail*) = ($arraycast_nan_task(ptask) \/ $arraycast_nan_tasks(ptask_tail*))
dec $arraycast_nan_handler_frame(pframe) : bool
def $arraycast_nan_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAYCAST_NAN_WARNING pboolnotnanwarning 1
  -- if perrorcall.TARGET =/= eps
def $arraycast_nan_handler_frame(pframe) = false -- otherwise
dec $arraycast_nan_entered(pframe*) : bool
def $arraycast_nan_entered(eps) = false
def $arraycast_nan_entered(pframe :: pframe_tail*) = ($arraycast_nan_handler_frame(pframe) \/ $arraycast_nan_entered(pframe_tail*))
dec $arraycast_nan_frontier(pstate, nat) : bool
def $arraycast_nan_frontier(S, 0) = ($arraycast_nan_plan(S) =/= eps)
def $arraycast_nan_frontier(S, 1) = true
  -- if S.TODO = (ARRAYCAST_NAN_WARNING pboolnotnanwarning 0) :: ptask_tail*
def $arraycast_nan_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAYCAST_NAN_WARNING pboolnotnanwarning 1
  -- if perrorcall.TARGET = eps
def $arraycast_nan_frontier(S, 3) = (S.CURRENT =/= eps /\ $arraycast_nan_entered(S.FRAMES))
def $arraycast_nan_frontier(S, 4) = true
  -- if S.TODO = (ARRAYCAST_NAN_WARNING pboolnotnanwarning 1) :: ptask_tail*
def $arraycast_nan_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprCastArray expression metadata)
  -- if S.RESULT = KNOWN (PARRAY n)
  -- if ~$arraycast_nan_tasks(S.TODO)
def $arraycast_nan_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$arraycast_nan_tasks(S.TODO)
def $arraycast_nan_frontier(S, n) = false -- otherwise
dec $arraycast_nan_seek(pstate, nat, nat) : pstate
def $arraycast_nan_seek(S, n_stage, n) = S -- if $arraycast_nan_frontier(S, n_stage)
def $arraycast_nan_seek(S, n_stage, n) = S
  -- if ~$arraycast_nan_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $arraycast_nan_seek(S, n_stage, n) = S
  -- if ~$arraycast_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $arraycast_nan_seek(S, n_stage, n) = $arraycast_nan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$arraycast_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $arraycast_nan_diagnostic(pevent, text) : nat
def $arraycast_nan_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $arraycast_nan_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $arraycast_nan_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $arraycast_nan_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $arraycast_nan_diagnostic(pevent, text) = 0 -- otherwise
dec $arraycast_nan_diagnostics(pevent*, text) : nat
def $arraycast_nan_diagnostics(eps, text) = 0
def $arraycast_nan_diagnostics(pevent :: pevent_tail*, text) = $($arraycast_nan_diagnostic(pevent, text) + $arraycast_nan_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $arraycast_nan_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$arraycast_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arraycast_nan_plan(S_entry) = (pboolnotnanwarning)',
        'pboolnotnanwarning.LINE = 25',
        'pboolnotnanwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'S_entry.RESULT = pboolnotnanwarning.INPUT',
        'pboolnotnanwarning.BITS = 9221120237041090560',
        '$fparts_nan($float_decode(pboolnotnanwarning.BITS))',
        '$integer_operand_source(S_entry, pboolnotnanwarning.SITE, [PCFIELD 0], pboolnotnanwarning.INPUT)',
        '$arraycast_nan_source(S_entry, pboolnotnanwarning)',
        '$origin_node(S_entry.SOURCES, pboolnotnanwarning.SITE) = (NExprCastArray expression metadata)',
        '~$boolnot_nan_source(S_entry, pboolnotnanwarning)',
        '~$boolcast_nan_source(S_entry, pboolnotnanwarning)',
        '$boolcast_nan_plan(S_entry[.TODO = [CAST_RESULT CASTBOOL 25]]) = eps',
        '$arraycast_nan_plan(S_entry[.TODO = [CAST_RESULT CASTBOOL 25]]) = eps',
        '$boolnot_nan_plan(S_entry[.TODO = [TRUTH_RESULT true 25]]) = eps',
        '$arraycast_nan_plan(S_entry[.TODO = [TRUTH_RESULT true 25]]) = eps',
        '$arraycast_nan_plan(S_entry[.TODO = [TRUTH_RESULT false 25]]) = eps',
        'pboolnotnanwarning.SITE = PORIGIN n_unit pcpath',
        'S_entry.SOURCES[n_unit] = pcunit',
        'S_wrong_source = S_entry[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath (NExprBooleanNot expression metadata)) :: pcunit.OCCURRENCES]]',
        '~$arraycast_nan_source(S_wrong_source, pboolnotnanwarning)',
        'S_wrong_bool = S_entry[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath (NExprCastBool expression metadata)) :: pcunit.OCCURRENCES]]',
        '~$arraycast_nan_source(S_wrong_bool, pboolnotnanwarning)',
        '$boolnot_nan_snapshot(S_entry, pboolnotnanwarning)',
        '$boolnot_nan_ready(S_entry, pboolnotnanwarning) = (pboolnotnanwarning.BITS)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', 'pboolnotnanwarning.CELL = n_x',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)', '(HCELL n_x) <- S_entry.ALLOCATIONS',
        '$propref_at(S_entry.PROPREFS, n_x) = eps',
        '$reference_coercion_at(S_entry.REFCOERCIONS, n_x) = eps',
        '$parameter_backing_at(S_entry.PARAMETERBACKINGS, n_x) = eps',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.EVENTS = eps', '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$arraycast_nan_plan(S_entry[.ORIGIN = eps]) = eps',
        '$arraycast_nan_plan(S_entry[.CODE = eps]) = eps',
        '$arraycast_nan_plan(S_entry[.RESULT = KNOWN (PFLOAT pboolnotnanwarning.BITS)]) = eps',
        '$arraycast_nan_plan(S_entry[.TODO = [CAST_RESULT CASTINT 25]]) = eps',
        '$arraycast_nan_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$arraycast_nan_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '$arraycast_nan_plan(S_entry[.STORE[n_x] = DEFINED (PFLOAT 0)]) = eps',
        '$boolnot_nan_ready(S_entry[.STORE[n_x] = DEFINED (PINT 0)], pboolnotnanwarning) = eps',
        '$boolnot_nan_ready(S_entry[.ENV = eps], pboolnotnanwarning) = eps',
        '$boolnot_nan_ready(S_entry[.REFCELLS = [n_x]], pboolnotnanwarning) = eps',
        '$boolnot_nan_ready(S_entry[.ENV = [BIND ($ptascii("this")) n_x]], pboolnotnanwarning[.INPUT = VARIABLE ($ptascii("this")) 25]) = eps',
        '$boolnot_nan_ready(S_entry[.REFCOERCIONS = [{CELL n_x, SITE pboolnotnanwarning.SITE, LINE 25, VALUE eps}]], pboolnotnanwarning) = eps',
        '$boolnot_nan_ready(S_entry[.PARAMETERBACKINGS = [{FUNCTION pboolnotnanwarning.SITE, INDEX 0, CELL n_x, LINE 25, VALUE eps}]], pboolnotnanwarning) = eps',
        '~$arraycast_nan_source(S_entry, pboolnotnanwarning[.LINE = 24])',
        '~$arraycast_nan_source(S_entry, pboolnotnanwarning[.INPUT = VARIABLE ($ptascii("v")) 25])',
        '~$arraycast_nan_source(S_entry, pboolnotnanwarning[.BITS = 0])',
        '~$arraycast_nan_source(S_entry, pboolnotnanwarning[.BITS = 18446744073709551616])',
        '~$arraycast_nan_source(S_entry, pboolnotnanwarning[.CELL = |S_entry.STORE|])',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (ARRAYCAST_NAN_WARNING pboolnotnanwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$arraycast_nan_frontier(S_capture, 1)',
        '$arraycast_nan_warning_valid(S_capture, pboolnotnanwarning, 0)',
        '$arraycast_nan_warning_valid(S_capture, pboolnotnanwarning, 1)',
        '~$arraycast_nan_warning_valid(S_capture, pboolnotnanwarning, 2)',
        '$task_nodes(ARRAYCAST_NAN_WARNING pboolnotnanwarning 0) = eps',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$arraycast_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ARRAYCAST_NAN_WARNING pboolnotnanwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pboolnotnanwarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to array")',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
        'S_dispatch.EVENTS = eps', '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$arraycast_nan_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$arraycast_nan_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.TARGET =/= eps',
        'perrorcall_entered.RESUME = ARRAYCAST_NAN_WARNING pboolnotnanwarning 1',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (ARRAYCAST_NAN_WARNING pboolnotnanwarning 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("x")) = (n_x)',
        'S_return.STORE[n_x] = DEFINED (PFLOAT 0)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$arraycast_nan_source(S_return, pboolnotnanwarning)',
        '$boolnot_nan_ready(S_return, pboolnotnanwarning) = (0)',
        '~$boolnot_nan_snapshot(S_return, pboolnotnanwarning)',
        '~$arraycast_nan_warning_valid(S_return, pboolnotnanwarning, 0)',
        '$arraycast_nan_warning_valid(S_return, pboolnotnanwarning, 1)',
        '~$error_call_valid(S_return, perrorcall)',
        '$error_call_valid(S_return, perrorcall_entered)',
        '(HCELL n_x) <- S_return.ALLOCATIONS', '~(n_x <- S_return.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 1',
        '$task_nodes(ARRAYCAST_NAN_WARNING pboolnotnanwarning 1) = eps',
        '$arraycast_nan_diagnostics(S_return.EVENTS, "Warning") = 1',
        '$arraycast_nan_diagnostics(S_return.EVENTS, "Deprecated") = 0',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'n_array = |S_return.ARRAYS|',
        'parray = {ITEMS ([ENTRY (KINT 0) (DIRECT (PFLOAT 0))]), NEXT 1, POSITIONS ([POSITION (KINT 0) 0]), SERIAL 1}',
        'S_atomic = $allocate_array(S_return[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)], parray)',
        'S_atomic.RESULT = KNOWN (PARRAY n_array)',
        'S_atomic.STORE = S_return.STORE',
        'S_atomic.ARRAYS = S_return.ARRAYS ++ [parray]',
        'S_atomic.ALLOCATIONS = S_return.ALLOCATIONS ++ [HARRAY n_array]',
        '$heap_owners($heap_prune($heap_graph(S_atomic)), HARRAY n_array) = 1',
        '$operand_nodes(S_atomic.RESULT) = [HARRAY n_array]',
        '$heap_count(HARRAY n_array, $pools_nodes(S_atomic.POOLS)) = 0',
        '~$array_immutable(S_atomic, n_array)',
    ]
    step('S_result', 'S_return')
    checks += [
        '$arraycast_nan_frontier(S_result, 5)',
        'S_result.RESULT = S_atomic.RESULT', 'S_result.BASE = S_atomic.BASE',
        'S_result.TODO = S_atomic.TODO', 'S_result.ARRAYS = S_atomic.ARRAYS',
        'S_result.ALLOCATIONS = S_atomic.ALLOCATIONS',
        'S_result.STORE = S_return.STORE', 'S_result.ENV = S_return.ENV',
        'S_result.REFCELLS = S_return.REFCELLS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.STORE[n_v] = DEFINED (PINT 100)',
        '$operand_nodes(S_result.RESULT) = [HARRAY n_array]',
        '$heap_owners($heap_prune($heap_graph(S_result)), HARRAY n_array) = 1',
        '$heap_count(HARRAY n_array, $pools_nodes(S_result.POOLS)) = 0',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_same_nan = S_return[.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)]',
        'PhpStep: S_same_nan ~> S_same_nan_out',
        'S_same_nan_out = $allocate_array(S_same_nan[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)], parray[.ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT pboolnotnanwarning.BITS))]])',
        'S_same_nan_out.EVENTS = S_return.EVENTS',
        'S_done = $drive_steps(S_result, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x)', 'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PARRAY n_array)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("copy")) = (n_copy_cell)',
        'S_done.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_array',
        'S_done.ARRAYS[n_array] = parray',
        'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_copy) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
