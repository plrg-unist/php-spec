#!/usr/bin/env python3
"""Reached delayed += failure does not retry array union or store a result."""
import base64
import json
import addassign_cv_warning_protocol as shared
import addassign_rhs_failure_cases as cases

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $addassign_cv_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$addassign_cv_frontier({state}, {stage})',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_addassign_cv_plan(S_entry) = ((pintegeroperation, pvalue_left, NFLOAT 4623226492472524800))',
        '$arithmetic_addassign_plan(S_entry) = eps', '$arithmetic_addassign_cv_source(S_entry, pintegeroperation)',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'n_left =/= n_right', '~(n_left <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        'S_entry.STORE[n_left] = DEFINED pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("12.5tail"))',
        '$string_carrier_valid(S_entry, pvalue_left)', 'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 1',
        '$heap_valid($heap_graph(S_entry))', '$call_descriptors_valid(S_entry)',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
    ]
    seek('S_first', 'S_begin', 2)
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.RESUME = ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 1',
        '$error_call_valid(S_first, perrorcall)', '$call_descriptors_valid(S_first)',
    ]
    seek('S_enter', 'S_first', 3)
    checks += ['$addassign_cv_entered(S_enter.FRAMES)', '$call_descriptors_valid(S_enter)']
    seek('S_return', 'S_enter', 4)
    checks += [
        'S_return.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 1) :: ptask_tail*',
        '$arithmetic_addassign_cv_warning_valid(S_return, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, 1)',
        '~$arithmetic_addassign_cv_warning_valid(S_return, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, 0)',
        'S_return.STORE[n_left] = DEFINED (PARRAY n_array_left)',
        'S_return.STORE[n_right] = DEFINED (PARRAY n_array_right)', 'n_array_left =/= n_array_right',
        '~(n_left <- S_return.REFCELLS)', '~(n_right <- S_return.REFCELLS)',
        'S_return.ARRAYS[n_array_left].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_return.ARRAYS[n_array_right].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
        '(HARRAY n_array_left) <- S_return.ALLOCATIONS', '(HARRAY n_array_right) <- S_return.ALLOCATIONS',
        '$array_string_cast_items(S_return.ARRAYS[n_array_left].ITEMS)',
        '$arithmetic_addassign_cv_ready(S_return, pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_return, pintegeroperation) = eps',
        '$arithmetic_addassign_cv_failure_operands(S_return, pintegeroperation) = ((PARRAY n_array_left, PARRAY n_array_right))',
        '$arithmetic_addassign_cv_failure_operands(S_return[.ORIGIN = eps], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_failure_operands(S_return[.CODE = eps], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_failure_operands(S_return, pintegeroperation[.OP = DIVIDE]) = eps',
        '$arithmetic_addassign_cv_failure_operands(S_return, pintegeroperation[.LINE = 24]) = eps',
        '$arithmetic_addassign_cv_failure_operands(S_return[.STORE[n_right] = UNDEFINED], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_failure_operands(S_return[.STORE[n_right] = DEFINED (PINT 5)], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_failure_operands(S_return[.REFCELLS = [n_right]], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_failure_operands(S_return[.PROPREFS = [{CELL n_left, SOURCES eps}]], pintegeroperation) = eps',
        '~$arithmetic_addassign_cv_failure_value(S_return, PUNDEFINED)',
        '~$arithmetic_addassign_cv_failure_value(S_return, POBJECT 0)',
        '~$arithmetic_addassign_cv_failure_value(S_return, PARRAY (|S_return.ARRAYS|))',
        '~$arithmetic_addassign_cv_failure_value(S_return[.ALLOCATIONS = eps], PARRAY n_array_left)',
        '~$arithmetic_addassign_cv_failure_value(S_return[.ARRAYS[n_array_left].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array_right))]], PARRAY n_array_left)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_valid($heap_graph(S_return))', '$call_descriptors_valid(S_return)',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: array + array")) 25]',
        'S_error_budget = $drive_steps(S_return, 1)', 'S_error_budget.COMPLETION = BUDGET',
        'S_error = S_error_budget[.COMPLETION = NORMAL]',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*', 'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
        'S_error.RESULT = KNOWN PNULL', 'n_error = |S_return.OBJECTS|',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'S_error.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
        'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        '$throwable_field(S_error, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Unsupported operand types: array + array"))',
        '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
        'S_error.STORE = S_return.STORE', 'S_error.ENV = S_return.ENV', 'S_error.REFCELLS = S_return.REFCELLS',
        'S_error.EVENTS = S_return.EVENTS', 'S_error.STRINGDATA = S_return.STRINGDATA',
        'S_error.ARRAYS[0:|S_return.ARRAYS|] = S_return.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_error)), HARRAY n_array_left) = $heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array_left)',
        '$heap_owners($heap_prune($heap_graph(S_error)), HARRAY n_array_right) = $heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array_right)',
        '~$addassign_cv_tasks(S_error.TODO)', '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_done = $drive_steps(S_error, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_left] = DEFINED (PARRAY n_array_left)', 'S_done.STORE[n_right] = DEFINED (PARRAY n_array_right)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 7000) = S_done',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
