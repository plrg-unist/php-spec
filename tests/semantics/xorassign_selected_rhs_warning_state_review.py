#!/usr/bin/env python3
"""Protected XOR text and cached longs survive removal of the selected RHS."""
import base64
import json

import xorassign_selected_rhs_warning_review_cases as cases
import xorassign_selected_rhs_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    left = lambda stage: f'XOR_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left {stage}'
    marker = lambda cursor: f'XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion {cursor}'
    valid = lambda state, cursor: f'$xorassign_selected_rhs_warning_valid({state}, pintegeroperation, n_bits, i_left, pintegerconversion, {cursor})'
    warning = '$ptascii("A non-numeric value encountered")'
    precision = '$ptascii(' + json.dumps('Implicit conversion from float-string "5.5tail" to int loses precision') + ')'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $xorassign_selected_rhs_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$xorassign_selected_rhs_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$xorassign_selected_warning_plan(S_entry) = (' + left(0) + ')',
        '$xorassign_selected_warning_source(S_entry, pintegeroperation)',
        '$xorassign_selected_warning_snapshot(S_entry, pintegeroperation, n_bits)',
        '$xorassign_selected_rhs_warning_plan(S_entry) = eps',
        'n_bits = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = BITXOR', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_target',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_old_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_target)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_old_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_target] = DEFINED (PFLOAT n_bits)',
        'S_entry.STORE[n_old_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    step('S_first_capture', 'S_entry')
    checks += [
        'S_first_capture.TODO = (' + left(0) + ') :: ptask_tail*',
        'S_first_capture.LOCATION = ROOT n_target',
        'S_first_capture.STORE = S_entry.STORE', 'S_first_capture.ENV = S_entry.ENV',
        '$task_nodes(' + left(0) + ') = eps',
    ]
    step('S_first_notice', 'S_first_capture')
    checks += [
        'S_first_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_left) :: ptask_tail*',
        'perrorcall_left.RESUME = ' + left(1), 'perrorcall_left.TARGET = eps',
        'perrorcall_left.LEVEL = 8192', 'perrorcall_left.LINE = 25',
        'perrorcall_left.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_first_notice, perrorcall_left)',
    ]
    seek('S_first_entered', 'S_first_notice', 3)
    checks += [
        'S_first_entered.CURRENT =/= eps', '$xorassign_selected_rhs_entered(S_first_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_first_entered)',
    ]
    seek('S_first_return', 'S_first_entered', 4)
    checks += [
        'S_first_return.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_first_return.CURRENT = eps', 'S_first_return.FRAMES = eps',
        'S_first_return.STORE[n_target] = DEFINED (PINT 99)',
        'S_first_return.STORE[n_old_right] = DEFINED pvalue_saved',
        '$string_bytes(pvalue_saved) = ($ptascii("5.5tail"))',
        '$string_carrier_valid(S_first_return, pvalue_saved)',
        'S_first_return.STORE[n_calls] = DEFINED (PINT 1)',
        'S_first_return.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_first_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_first_return.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_first_return.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$integer_pointer_value(S_first_return, pintegeroperation.RIGHTPOINTER) = (pvalue_saved)',
        '$integer_pointer_value(S_first_return, INTEGER_CV ($ptascii("right"))) = (PINT 7)',
        '$xorassign_selected_warning_right(S_first_return, pintegeroperation) = eps',
        '$xorassign_selected_warning_failure_operands(S_first_return, pintegeroperation) = eps',
        '$xorassign_selected_rhs_warning_snapshot(S_first_return, pintegeroperation) = (pintegerconversion)',
        'pintegerconversion.INPUT = pvalue_saved', 'pintegerconversion.VALUE = 5',
        'pintegerconversion.NOTICES = [(2, ' + warning + '), (8192, ' + precision + ')]',
        '$integer_conversion(pvalue_saved) = (pintegerconversion)',
        '$string_long($ptascii("5.5tail")) = STRINT 5 ([LEADINGNUMBER, STRINGPRECISIONLOSS])',
        '$xorassign_selected_rhs_warning_plan(S_first_return) = (' + marker(0) + ')',
        valid('S_first_return', 0),
        'pintegeroperation_current = pintegeroperation[.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))]',
        '~$xorassign_selected_warning_source(S_first_return, pintegeroperation_current)',
        '$xorassign_selected_rhs_warning_snapshot(S_first_return, pintegeroperation_current) = eps',
        '$heap_owners($heap_prune($heap_graph(S_first_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_first_return)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_return)), HCELL n_replacement_right) = 2',
        '$xorassign_selected_diagnostics(S_first_return.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_first_return)', '$heap_valid($heap_graph(S_first_return))',
        'PhpStep: S_first_return ~> S_capture_atomic',
        'S_capture_atomic = S_first_return[.TODO = (' + marker(0) + ') :: ptask_tail*]',
    ]
    step('S_capture', 'S_first_return')
    checks += [
        'S_capture = S_capture_atomic', '$xorassign_selected_rhs_frontier(S_capture, 5)',
        '$task_nodes(' + marker(0) + ') = eps',
        '$call_task_valid(S_capture, ' + marker(0) + ')',
    ]
    step('S_warning', 'S_capture')
    checks += [
        '$xorassign_selected_rhs_frontier(S_warning, 6)',
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_warning) :: ptask_tail*',
        'perrorcall_warning.RESUME = ' + marker(1), 'perrorcall_warning.TARGET = eps',
        'perrorcall_warning.LEVEL = 2', 'perrorcall_warning.LINE = 25',
        'perrorcall_warning.MESSAGE = ' + warning,
        '$error_call_valid(S_warning, perrorcall_warning)', '$call_descriptors_valid(S_warning)',
    ]
    seek('S_warning_entered', 'S_warning', 11)
    checks += [
        '$xorassign_selected_rhs_entered(S_warning_entered.FRAMES, 1)',
        'S_warning_entered.CURRENT =/= eps', '$call_descriptors_valid(S_warning_entered)',
    ]
    seek('S_warning_return', 'S_warning_entered', 7)
    checks += [
        'S_warning_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_warning_return.CURRENT = eps', 'S_warning_return.FRAMES = eps',
        'S_warning_return.STORE[n_target] = DEFINED (PINT 88)',
        'S_warning_return.STORE[n_old_right] = DEFINED (PINT 7)',
        'S_warning_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_warning_return.STORE[n_calls] = DEFINED (PINT 2)',
        '$lookup(S_warning_return.ENV, $ptascii("leftAlias")) = (n_target)',
        '$lookup(S_warning_return.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_warning_return.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_warning_return.ENV, $ptascii("rightAlias")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_warning_return)), HCELL n_old_right) = 0',
        '~((HCELL n_old_right) <- S_warning_return.ALLOCATIONS)',
        '$integer_pointer_value(S_warning_return, pintegeroperation.RIGHTPOINTER) = eps',
        '$xorassign_selected_rhs_warning_snapshot(S_warning_return, pintegeroperation) = eps',
        valid('S_warning_return', 1), '~' + valid('S_warning_return', 0),
        '$string_bytes(pintegerconversion.INPUT) = ($ptascii("5.5tail"))',
        '$string_carrier_valid(S_warning_return, pintegerconversion.INPUT)',
        '$heap_owners($heap_prune($heap_graph(S_warning_return)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_warning_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_warning_return)), HCELL n_replacement_right) = 2',
        '$xorassign_selected_diagnostics(S_warning_return.EVENTS, "Warning") = 0',
        'S_warning_return.STRINGDATA[0:|S_first_return.STRINGDATA|] = S_first_return.STRINGDATA',
        '$call_descriptors_valid(S_warning_return)', '$heap_valid($heap_graph(S_warning_return))',
    ]
    step('S_precision', 'S_warning_return')
    checks += [
        '$xorassign_selected_rhs_frontier(S_precision, 8)',
        'S_precision.TODO = (ERROR_HANDLER_INVOKE perrorcall_precision) :: ptask_tail*',
        'perrorcall_precision.RESUME = ' + marker(2), 'perrorcall_precision.TARGET = eps',
        'perrorcall_precision.LEVEL = 8192', 'perrorcall_precision.LINE = 25',
        'perrorcall_precision.MESSAGE = ' + precision,
        '$error_call_valid(S_precision, perrorcall_precision)', '$call_descriptors_valid(S_precision)',
    ]
    seek('S_precision_entered', 'S_precision', 12)
    checks += [
        '$xorassign_selected_rhs_entered(S_precision_entered.FRAMES, 2)',
        'S_precision_entered.CURRENT =/= eps', '$call_descriptors_valid(S_precision_entered)',
    ]
    seek('S_return', 'S_precision_entered', 9)
    checks += [
        'S_return.TODO = (' + marker(2) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_target] = DEFINED (PINT 66)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 3)',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_return.ENV, $ptascii("rightAlias")) = eps',
        '~((HCELL n_old_right) <- S_return.ALLOCATIONS)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = eps',
        valid('S_return', 2),
        '$xorassign_selected_warning_target(S_return, pintegeroperation)',
        '$integer_binary(BITXOR, i_left, pintegerconversion.VALUE) = IRESULT 9',
        '$integer_binary(BITXOR, i_left, 7) = IRESULT 11',
        '$xorassign_selected_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        '$xorassign_selected_diagnostics(S_return.EVENTS, "Warning") = 0',
        'S_return.STRINGDATA[0:|S_warning_return.STRINGDATA|] = S_warning_return.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 9)][.LOCATION = ROOT n_target][.STORE[n_target] = DEFINED (PINT 9)]',
    ]
    step('S_commit', 'S_return')
    checks += [
        '$xorassign_selected_rhs_frontier(S_commit, 10)',
        'S_commit.RESULT = KNOWN (PINT 9)', 'S_commit.LOCATION = ROOT n_target',
        'S_commit.STORE = S_atomic.STORE', 'S_commit.ENV = S_return.ENV',
        'S_commit.REFCELLS = S_return.REFCELLS', 'S_commit.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_commit.OBJECTS = S_return.OBJECTS', 'S_commit.ARRAYS = S_return.ARRAYS',
        'S_commit.STRINGDATA = S_return.STRINGDATA', 'S_commit.EVENTS = S_return.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_old_right) = 0',
        '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_done = $drive_steps(S_commit, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_target] = DEFINED (PINT 6)',
        'S_done.STORE[n_old_right] = DEFINED (PINT 7)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        'S_done.STORE[n_v] = DEFINED (PINT 9)', 'S_done.STORE[n_calls] = DEFINED (PINT 3)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_target)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_old_right) = 0',
        '~((HCELL n_old_right) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$xorassign_selected_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$xorassign_selected_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_first_return, 0) = S_first_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_warning_return, 0) = S_warning_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
