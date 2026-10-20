#!/usr/bin/env python3
"""Reached ordinary ADD failure preserves both selected array referents."""
import base64
import json
import arithmetic_warning_protocol as shared
import add_array_failure_cases as cases

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']

    def seek(state, before, stage):
        checks.extend([f'{state}_found = $arithmetic_seek({before}, {stage}, 5000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$arithmetic_frontier({state}, {stage})'])

    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_add_plan(S_entry) = (pintegeroperation)', '$arithmetic_add_valid(S_entry, pintegeroperation)',
        '$arithmetic_add_selected(S_entry, pintegeroperation)', 'pintegeroperation.OP = ADD',
        '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'n_left =/= n_right', 'n_left <- S_entry.REFCELLS', 'n_right <- S_entry.REFCELLS',
        'S_entry.STORE[n_left] = DEFINED pvalue_left',
        'pvalue_left = PSTRING_CARRIER (REQUEST_STRING n_left_string) ($ptascii("12.5tail"))',
        '$string_carrier_valid(S_entry, pvalue_left)', 'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_valid($heap_graph(S_entry))', '$call_descriptors_valid(S_entry)',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$task_nodes(ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
    ]
    step('S_capture', 'S_begin')
    checks += ['S_capture = S_begin[.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NFLOAT 4623226492472524800) 0) :: ptask_tail*]']
    step('S_first', 'S_capture')
    checks += [
        '$arithmetic_frontier(S_first, 3)', 'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NFLOAT 4623226492472524800) 1',
        '$error_call_valid(S_first, perrorcall)', '$call_descriptors_valid(S_first)',
    ]
    seek('S_return', 'S_first', 4)
    checks += [
        'S_return.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NFLOAT 4623226492472524800) 1) :: ptask_tail*',
        '$arithmetic_add_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NFLOAT 4623226492472524800, 1)',
        '~$arithmetic_add_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NFLOAT 4623226492472524800, 0)',
        'S_return.STORE[n_left] = DEFINED (PARRAY n_array_left)',
        'S_return.STORE[n_right] = DEFINED (PARRAY n_array_right)', 'n_array_left =/= n_array_right',
        'S_return.ARRAYS[n_array_left].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_return.ARRAYS[n_array_right].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    step('S_pending', 'S_return')
    phase = 'ARITHMETIC_RIGHT (NFLOAT 4623226492472524800)'
    helper = f'$arithmetic_add_array_failure_operands(S_pending, pintegeroperation, {phase})'
    checks += [
        'PhpStep: S_return ~> S_pending',
        f'S_pending = S_return[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation ({phase})) :: ptask_tail*][.RESULT = KNOWN PNULL]',
        f'$arithmetic_frontier(S_pending, 5)',
        f'$call_task_valid(S_pending, ARITHMETIC_ADD_CONVERT pintegeroperation ({phase}))',
        helper + ' = ((PARRAY n_array_left, PARRAY n_array_right))',
        f'$arithmetic_add_failure_operands(S_pending, pintegeroperation, {phase}) = eps',
        '$arithmetic_add_array_failure_operands(S_pending, pintegeroperation, ARITHMETIC_LEFT) = eps',
        helper.replace('S_pending,', 'S_pending[.ORIGIN = eps],', 1) + ' = eps',
        helper.replace('S_pending,', 'S_pending[.CODE = eps],', 1) + ' = eps',
        helper.replace('pintegeroperation,', 'pintegeroperation[.OP = MULTIPLY],', 1) + ' = eps',
        helper.replace('pintegeroperation,', 'pintegeroperation[.SWAPPED = true],', 1) + ' = eps',
        helper.replace('pintegeroperation,', 'pintegeroperation[.LINE = 24],', 1) + ' = eps',
        helper.replace('S_pending,', 'S_pending[.STORE[n_right] = UNDEFINED],', 1) + ' = eps',
        helper.replace('S_pending,', 'S_pending[.STORE[n_right] = DEFINED (PINT 5)],', 1) + ' = eps',
        helper.replace('S_pending,', 'S_pending[.REFCELLS = eps],', 1) + ' = eps',
        helper.replace('S_pending,', 'S_pending[.ALLOCATIONS = eps],', 1) + ' = eps',
        helper.replace('S_pending,', 'S_pending[.PROPREFS = [{CELL n_left, SOURCES eps}]],', 1) + ' = eps',
        helper.replace('S_pending,', 'S_pending[.ARRAYS[n_array_right].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array_left))]],', 1) + ' = eps',
        helper.replace('S_pending,', 'S_pending[.ARRAYS[n_array_right].ITEMS = [ENTRY (KINT 0) (ALIAS n_left)]],', 1) + ' = eps',
        'S_scalar = S_pending[.STORE[n_left] = DEFINED (PBOOL false)][.STORE[n_right] = DEFINED (PSTRING ($ptascii("bad")))]',
        f'$arithmetic_add_array_failure_operands(S_scalar, pintegeroperation, {phase}) = eps',
        f'$arithmetic_add_failure_operands(S_scalar, pintegeroperation, {phase}) = ((PBOOL false, PSTRING ($ptascii("bad"))))',
        'PhpStep: S_pending ~> S_atomic',
        'S_atomic = S_pending[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: array + array")) 25]',
    ]
    step('S_error', 'S_pending')
    checks += [
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*', 'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
        'S_error.RESULT = KNOWN PNULL', 'n_error = |S_pending.OBJECTS|',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'S_error.OBJECTS = S_pending.OBJECTS ++ [THROWABLE pthrowable]',
        'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        '$throwable_field(S_error, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Unsupported operand types: array + array"))',
        '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
        'S_error.STORE = S_pending.STORE', 'S_error.ENV = S_pending.ENV', 'S_error.REFCELLS = S_pending.REFCELLS',
        'S_error.EVENTS = S_pending.EVENTS', 'S_error.STRINGDATA = S_pending.STRINGDATA',
        'S_error.ARRAYS[0:|S_pending.ARRAYS|] = S_pending.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_right) = 2',
        '$heap_owners($heap_prune($heap_graph(S_error)), HARRAY n_array_left) = $heap_owners($heap_prune($heap_graph(S_pending)), HARRAY n_array_left)',
        '$heap_owners($heap_prune($heap_graph(S_error)), HARRAY n_array_right) = $heap_owners($heap_prune($heap_graph(S_pending)), HARRAY n_array_right)',
        '~$arithmetic_tasks(S_error.TODO)', '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_done = $drive_steps(S_error, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)',
        'S_done.STORE[n_left] = DEFINED (PARRAY n_array_left)', 'S_done.STORE[n_right] = DEFINED (PARRAY n_array_right)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 7000) = S_done', '$drive_steps(S_pending, 0) = S_pending[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
