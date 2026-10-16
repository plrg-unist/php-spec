#!/usr/bin/env python3
"""Reached ordered numeric bitwise captures, two callback exits and quiet-RHS handoff."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import bitassign_both_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $bitassign_both_task(ptask) : bool
def $bitassign_both_task(BIT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left n_stage) = true
def $bitassign_both_task(BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right n_stage) = true
def $bitassign_both_task(BIT_ASSIGN_WARNING pintegeroperation n_target n_right n_bits_left i_left n_stage) = true
def $bitassign_both_task(ERROR_HANDLER_INVOKE perrorcall) = $bitassign_both_task(perrorcall.RESUME)
def $bitassign_both_task(ERROR_HANDLER_RESULT perrorcall) = $bitassign_both_task(perrorcall.RESUME)
def $bitassign_both_task(ERROR_HANDLER_CLEAN perrorcall) = $bitassign_both_task(perrorcall.RESUME)
def $bitassign_both_task(ptask) = false -- otherwise
dec $bitassign_both_tasks(ptask*) : bool
def $bitassign_both_tasks(eps) = false
def $bitassign_both_tasks(ptask :: ptask_tail*) = ($bitassign_both_task(ptask) \/ $bitassign_both_tasks(ptask_tail*))
dec $bitassign_both_frame(pframe, nat) : bool
def $bitassign_both_frame(pframe, 0) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BIT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left 1
  -- if perrorcall.TARGET =/= eps
def $bitassign_both_frame(pframe, 1) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right 1
  -- if perrorcall.TARGET =/= eps
def $bitassign_both_frame(pframe, n) = false -- otherwise
dec $bitassign_both_entered(pframe*, nat) : bool
def $bitassign_both_entered(eps, n) = false
def $bitassign_both_entered(pframe :: pframe_tail*, n) = ($bitassign_both_frame(pframe, n) \/ $bitassign_both_entered(pframe_tail*, n))
dec $bitassign_both_frontier(pstate, nat) : bool
def $bitassign_both_frontier(S, 0) = ($bitassign_both_warning_plan(S) =/= eps)
def $bitassign_both_frontier(S, 1) = true
  -- if S.TODO = (BIT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left 0) :: ptask_tail*
def $bitassign_both_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BIT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left 1
  -- if perrorcall.TARGET = eps
def $bitassign_both_frontier(S, 3) = (S.CURRENT =/= eps /\ $bitassign_both_entered(S.FRAMES, 0))
def $bitassign_both_frontier(S, 4) = true
  -- if S.TODO = (BIT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left 1) :: ptask_tail*
def $bitassign_both_frontier(S, 5) = true
  -- if S.TODO = (BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right 0) :: ptask_tail*
def $bitassign_both_frontier(S, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right 1
  -- if perrorcall.TARGET = eps
def $bitassign_both_frontier(S, 7) = (S.CURRENT =/= eps /\ $bitassign_both_entered(S.FRAMES, 1))
def $bitassign_both_frontier(S, 8) = true
  -- if S.TODO = (BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right 1) :: ptask_tail*
def $bitassign_both_frontier(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (expression)
  -- if $bitassign_warning_operator(expression) =/= eps
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$bitassign_both_tasks(S.TODO)
def $bitassign_both_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$bitassign_both_tasks(S.TODO)
def $bitassign_both_frontier(S, 11) = true
  -- if S.TODO = (BIT_ASSIGN_WARNING pintegeroperation n_target n_right n_bits_left i_left 1) :: ptask_tail*
def $bitassign_both_frontier(S, n) = false -- otherwise
dec $bitassign_both_seek(pstate, nat, nat) : pstate
def $bitassign_both_seek(S, n_stage, n) = S -- if $bitassign_both_frontier(S, n_stage)
def $bitassign_both_seek(S, n_stage, n) = S
  -- if ~$bitassign_both_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bitassign_both_seek(S, n_stage, n) = S
  -- if ~$bitassign_both_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $bitassign_both_seek(S, n_stage, n) = $bitassign_both_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bitassign_both_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $bitassign_both_deprecation(pevent) : nat
def $bitassign_both_deprecation(DIAGNOSTIC "Deprecated" n* z) = 1
def $bitassign_both_deprecation(pevent) = 0 -- otherwise
dec $bitassign_both_deprecations(pevent*) : nat
def $bitassign_both_deprecations(eps) = 0
def $bitassign_both_deprecations(pevent :: pevent_tail*) = $($bitassign_both_deprecation(pevent) + $bitassign_both_deprecations(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    first_throw = name.endswith('-first-throw')
    second_throw = name.endswith('-second-throw')
    quiet = name.endswith('-first-quiet')
    thrown = first_throw or second_throw
    operation = 'BITAND' if '-and-' in name else ('BITOR' if '-or-' in name else 'BITXOR')
    other_ops = [op for op in ('BITAND', 'BITOR', 'BITXOR') if op != operation]
    result = {'BITAND': '4', 'BITOR': '13', 'BITXOR': '9'}[operation]
    left = lambda stage, bits='n_bits_left', value='12', op='pintegeroperation', target='n_target': f'BIT_ASSIGN_BOTH_LEFT {op} {target} n_right {bits} {value} {stage}'
    right = lambda stage, bits='n_bits_right', value='5', op='pintegeroperation', leftbits='n_bits_left', leftvalue='12': f'BIT_ASSIGN_BOTH_RIGHT {op} n_target n_right {leftbits} {leftvalue} {bits} {value} {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $bitassign_both_seek(S_initial, 0, 3000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_entry, 0)',
        '$bitassign_both_warning_plan(S_entry) = (' + left(0) + ')',
        'n_bits_left = 4623226492472524800', 'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 24',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S_entry.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_target <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        '$modassign_both_snapshot(S_entry, pintegeroperation, n_target, n_right, n_bits_left)',
        '$bitassign_warning_plan(S_entry) = eps', '$bitassign_right_warning_plan(S_entry) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$bitassign_both_warning_plan(S_entry[.REFCELLS = S_entry.REFCELLS ++ [n_target]]) = eps',
        '$bitassign_both_warning_plan(S_entry[.REFCELLS = S_entry.REFCELLS ++ [n_right]]) = eps',
        '$bitassign_both_warning_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_capture, 1)',
        'S_capture.TODO = (' + left(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_capture.LOCATION = ROOT n_target', 'S_capture.STORE = S_entry.STORE',
        '$task_nodes(' + left(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        '~$bitassign_both_left_valid(S_capture, pintegeroperation[.OP = MODULO], n_target, n_right, n_bits_left, 12, 0)',
        '~$bitassign_both_left_valid(S_capture, pintegeroperation[.SWAPPED = true], n_target, n_right, n_bits_left, 12, 0)',
        '~$bitassign_both_left_valid(S_capture, pintegeroperation[.LEFT = pintegeroperation.RIGHT], n_target, n_right, n_bits_left, 12, 0)',
        '~$bitassign_both_left_valid(S_capture, pintegeroperation, n_target, n_right, n_bits_left, 13, 1)',
        '~$bitassign_both_left_valid(S_capture, pintegeroperation, n_target, n_right, 18446744073709551616, 12, 1)',
        '~$bitassign_both_left_valid(S_capture, pintegeroperation, n_target, n_right, n_bits_left, 12, 2)',
        'pintegeroperation_line = pintegeroperation[.LINE = 24]',
        'S_line_bad = S_capture[.TODO = (' + left(0, op='pintegeroperation_line') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        'S_target_bad = S_capture[.TODO = (' + left(0, target='n_v') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_target_bad))', '~$call_descriptors_valid(S_target_bad)',
        'S_old_left = S_capture[.TODO = (BIT_ASSIGN_WARNING pintegeroperation n_target n_right n_bits_left 12 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_old_left))', '~$call_descriptors_valid(S_old_left)',
        'S_old_right = S_capture[.TODO = (BIT_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right 12 4620974692658839552 8 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_old_right))', '~$call_descriptors_valid(S_old_right)',
        'S_mod_bad = S_capture[.TODO = (MOD_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left 12 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_mod_bad))', '~$call_descriptors_valid(S_mod_bad)',
        'S_shift_bad = S_capture[.TODO = (SHIFT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left 12 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_shift_bad))', '~$call_descriptors_valid(S_shift_bad)',
        '~$bitassign_both_left_valid(S_capture, pintegeroperation[.OP = ' + other_ops[0] + '], n_target, n_right, n_bits_left, 12, 0)',
        '~$bitassign_both_left_valid(S_capture, pintegeroperation[.OP = ' + other_ops[1] + '], n_target, n_right, n_bits_left, 12, 0)',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_dispatch, perrorcall_first)', '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        '~$error_call_valid(S_dispatch, perrorcall_first[.LINE = 24])',
        '~$error_call_valid(S_dispatch, perrorcall_first[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall_first[.LEVEL = 2])',
        'n_message_other* = $ptascii("Implicit conversion from float 13.5 to int loses precision")',
        'perrorcall_first_cache = perrorcall_first[.RESUME = ' + left(1, bits='4623789442425946112', value='13') + '][.MESSAGE = n_message_other*][.EVENT = DIAGNOSTIC "Deprecated" n_message_other* 25]',
        '$bitassign_both_left_valid(S_dispatch, pintegeroperation, n_target, n_right, 4623789442425946112, 13, 1)',
        '~$error_call_valid(S_dispatch, perrorcall_first_cache)',
        'S_first_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_first_cache) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_first_bad))', '~$call_descriptors_valid(S_first_bad)',
        'S_entered_found = $bitassign_both_seek(S_dispatch, 3, 3000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_entered, 3)',
        '$bitassign_both_entered(S_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if not first_throw:
        checks += [
            'S_return_found = $bitassign_both_seek(S_entered, 4, 3000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_return, 4)',
            'S_return.TODO = (' + left(1) + ') :: ptask_tail*',
            'S_return.STORE[n_target] = DEFINED (PINT 99)',
            'S_return.STORE[n_right] = DEFINED (' + ('PINT 5' if quiet else 'PFLOAT 4617878467915022336') + ')',
            'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
            '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_return.REFCELLS',
            '$bitassign_both_left_valid(S_return, pintegeroperation, n_target, n_right, n_bits_left, 12, 1)',
            '~$modassign_both_snapshot(S_return, pintegeroperation, n_target, n_right, n_bits_left)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        if quiet:
            checks += [
                '$modassign_warning_ready(S_return, pintegeroperation, n_target, n_right) = (5)',
                '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
                'S_quiet_budget = $drive_steps(S_return, 1)', 'S_quiet_budget.COMPLETION = BUDGET',
                'S_ready = S_quiet_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_ready, 11)',
                'S_ready.TODO = (BIT_ASSIGN_WARNING pintegeroperation n_target n_right n_bits_left 12 1) :: ptask_tail*',
                '$bitassign_warning_valid(S_ready, pintegeroperation, n_target, n_right, n_bits_left, 12, 1)',
                '~$bitassign_warning_valid(S_ready, pintegeroperation, n_target, n_right, n_bits_left, 12, 0)',
                'S_ready.STORE = S_return.STORE', 'S_ready.ENV = S_return.ENV',
                'S_ready.ALLOCATIONS = S_return.ALLOCATIONS', 'S_ready.REFCELLS = S_return.REFCELLS',
                'S_ready.EVENTS = S_return.EVENTS',
                '$heap_owners($heap_prune($heap_graph(S_ready)), HCELL n_target) = 2',
                '$bitassign_both_deprecations(S_ready.EVENTS) = 0',
                '$call_descriptors_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
            ]
        else:
            checks += [
                '$modassign_warning_ready(S_return, pintegeroperation, n_target, n_right) = eps',
                '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = ((4617878467915022336, 5))',
                'S_right_budget = $drive_steps(S_return, 1)', 'S_right_budget.COMPLETION = BUDGET',
                'S_right = S_right_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_right, 5)',
                'S_right.TODO = (' + right(0) + ') :: ptask_tail*', 'n_bits_right = 4617878467915022336',
                'S_right.STORE = S_return.STORE', 'S_right.ALLOCATIONS = S_return.ALLOCATIONS',
                '$task_nodes(' + right(0) + ') = eps',
                '$bitassign_both_right_valid(S_right, pintegeroperation, n_target, n_right, n_bits_left, 12, n_bits_right, 5, 0)',
                '~$bitassign_both_right_valid(S_right, pintegeroperation, n_target, n_right, n_bits_left, 12, n_bits_right, 6, 1)',
                '~$bitassign_both_right_valid(S_right, pintegeroperation, n_target, n_right, n_bits_left, 13, n_bits_right, 5, 1)',
                '~$bitassign_both_right_valid(S_right, pintegeroperation, n_target, n_right, n_bits_left, 12, 18446744073709551616, 5, 1)',
                '~$bitassign_both_right_valid(S_right, pintegeroperation, n_target, n_right, n_bits_left, 12, n_bits_right, 5, 2)',
                '$modassign_both_right_snapshot(S_right[.REFCELLS = S_right.REFCELLS ++ [n_right]], pintegeroperation, n_target, n_right) = eps',
                '$modassign_both_right_snapshot(S_right[.ALLOCATIONS = eps], pintegeroperation, n_target, n_right) = eps',
                '$modassign_both_right_snapshot(S_right, pintegeroperation, n_v, n_right) = eps',
                '$modassign_both_right_snapshot(S_right[.PROPREFS = [{CELL n_target, SOURCES eps}]], pintegeroperation, n_target, n_right) = eps',
                '$modassign_both_right_snapshot(S_right[.STORE[n_target] = DEFINED (POBJECT n_second)], pintegeroperation, n_target, n_right) = eps',
                '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
                'S_dispatch_right_budget = $drive_steps(S_right, 1)', 'S_dispatch_right_budget.COMPLETION = BUDGET',
                'S_dispatch_right = S_dispatch_right_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_dispatch_right, 6)',
                'S_dispatch_right.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
                'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps',
                'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
                'perrorcall_second.MESSAGE = $ptascii("Implicit conversion from float 5.5 to int loses precision")',
                '$error_call_valid(S_dispatch_right, perrorcall_second)',
                'n_message_right_other* = $ptascii("Implicit conversion from float 6.5 to int loses precision")',
                'perrorcall_second_cache = perrorcall_second[.RESUME = ' + right(1, bits='4619004367821864960', value='6') + '][.MESSAGE = n_message_right_other*][.EVENT = DIAGNOSTIC "Deprecated" n_message_right_other* 25]',
                '$bitassign_both_right_valid(S_dispatch_right, pintegeroperation, n_target, n_right, n_bits_left, 12, 4619004367821864960, 6, 1)',
                '~$error_call_valid(S_dispatch_right, perrorcall_second_cache)',
                '~$error_call_valid(S_dispatch_right, perrorcall_second[.RESUME = ' + left(1) + '])',
                'S_second_bad = S_dispatch_right[.TODO = (ERROR_HANDLER_INVOKE perrorcall_second_cache) :: ptask_tail*]',
                '$heap_valid($heap_graph(S_second_bad))', '~$call_descriptors_valid(S_second_bad)',
                '$call_descriptors_valid(S_dispatch_right)', '$heap_valid($heap_graph(S_dispatch_right))',
                'S_second_entered_found = $bitassign_both_seek(S_dispatch_right, 7, 3000)',
                r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
                'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_second_entered, 7)',
                '$bitassign_both_entered(S_second_entered.FRAMES, 1)',
                '$call_descriptors_valid(S_second_entered)', '$heap_valid($heap_graph(S_second_entered))',
            ]
            if not second_throw:
                checks += [
                    'S_second_return_found = $bitassign_both_seek(S_second_entered, 8, 3000)',
                    r'S_second_return_found.COMPLETION = NORMAL \/ S_second_return_found.COMPLETION = BUDGET',
                    'S_ready = S_second_return_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_ready, 8)',
                    'S_ready.TODO = (' + right(1) + ') :: ptask_tail*',
                    'S_ready.STORE[n_target] = DEFINED (PINT 88)', 'S_ready.STORE[n_right] = DEFINED (PINT 10)',
                    'S_ready.STORE[n_calls] = DEFINED (PINT 2)', 'S_ready.STORE[n_v] = DEFINED (PINT 100)',
                    '$bitassign_both_right_valid(S_ready, pintegeroperation, n_target, n_right, n_bits_left, 12, n_bits_right, 5, 1)',
                    '~$bitassign_both_right_valid(S_ready, pintegeroperation, n_target, n_right, n_bits_left, 12, n_bits_right, 5, 0)',
                    '$heap_owners($heap_prune($heap_graph(S_ready)), HCELL n_target) = 2',
                    '$call_descriptors_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
                ]
    if thrown:
        base = 'S_entered' if first_throw else 'S_second_entered'
        checks += [
            'S_throw_found = $bitassign_both_seek(' + base + ', 10, 3000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_throw, 10)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$bitassign_both_tasks(S_throw.TODO)',
            '$lookup(S_throw.ENV, $ptascii("left")) = (n_target)', '$lookup(S_throw.ENV, $ptascii("alias")) = (n_target)',
            'n_target <- S_throw.REFCELLS', 'S_throw.STORE[n_target] = DEFINED (PINT ' + ('99' if first_throw else '88') + ')',
            'S_throw.STORE[n_right] = DEFINED (' + ('PFLOAT 4617878467915022336' if first_throw else 'PINT 10') + ')',
            'S_throw.STORE[n_calls] = DEFINED (PINT ' + ('1' if first_throw else '2') + ')',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_target) = 2',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER',
            '$bitassign_both_deprecations(S_throw.EVENTS) = 0',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 3000)', '$drive_steps(' + base + ', 3000) = S_done',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)', '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            '$powerassign_warning_ready(S_ready, pintegeroperation, n_target)',
            '~$powerassign_warning_ready(S_ready[.ALLOCATIONS = eps], pintegeroperation, n_target)',
            '~$powerassign_warning_ready(S_ready, pintegeroperation, n_v)',
            '~$powerassign_warning_ready(S_ready[.ENV = eps][.GLOBALTABLE = eps], pintegeroperation, n_target)',
            '~$powerassign_warning_ready(S_ready[.PROPREFS = [{CELL n_target, SOURCES eps}]], pintegeroperation, n_target)',
            'S_commit_budget = $drive_steps(S_ready, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_commit, 9)',
            'S_commit.TODO = ptask_tail*', 'S_commit.RESULT = KNOWN (PINT ' + result + ')',
            '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_ready.STORE|',
            'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
            '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
            'S_commit.STORE = S_ready.STORE ++ [DEFINED (PINT ' + result + ')]',
            'S_commit.ALLOCATIONS = S_ready.ALLOCATIONS ++ [HCELL n_new]',
            'S_commit.STORE[n_target] = DEFINED (PINT ' + ('99' if quiet else '88') + ')',
            'S_commit.STORE[n_v] = DEFINED (PINT 100)',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
            'S_commit.EVENTS = S_ready.EVENTS',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 3000)', '$drive_steps(S_ready, 3000) = S_done',
            'S_done.STORE[n_new] = DEFINED (PINT 7)',
            'S_done.STORE[n_target] = DEFINED (PINT ' + ('99' if quiet else '88') + ')',
            'S_done.STORE[n_v] = DEFINED (PINT ' + result + ')',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_right] = DEFINED (' + ('PFLOAT 4617878467915022336' if first_throw else 'PINT ' + ('5' if quiet else '10')) + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('1' if first_throw or quiet else '2') + ')',
        '$bitassign_both_deprecations(S_done.EVENTS) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]', '$drive_steps(S_capture, 3000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['bitassign_both_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
