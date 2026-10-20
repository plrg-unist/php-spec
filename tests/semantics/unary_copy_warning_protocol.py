#!/usr/bin/env python3
"""Reached by-value unary copy, source retirement and supplied throw."""
import base64
import json

import unary_copy_warning_cases as cases
import unary_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $unary_copy_frontier(pstate, nat) : bool
def $unary_copy_frontier(S, 0) = ($arithmetic_unary_copy_plan(S) =/= eps)
def $unary_copy_frontier(S, n) = $unary_frontier(S, n) -- if n =/= 0
dec $unary_copy_seek(pstate, nat, nat) : pstate
def $unary_copy_seek(S, n_stage, n) = S -- if $unary_copy_frontier(S, n_stage)
def $unary_copy_seek(S, n_stage, n) = S
  -- if ~$unary_copy_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $unary_copy_seek(S, n_stage, n) = S
  -- if ~$unary_copy_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $unary_copy_seek(S, n_stage, n) = $unary_copy_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$unary_copy_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']

    def seek(state, before, stage):
        checks.extend([f'{state}_found = $unary_copy_seek({before}, {stage}, 3000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]',
                       f'$unary_copy_frontier({state}, {stage})'])

    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)',
                       f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_unary_copy_plan(S_entry) = (punarywarning)',
        '$arithmetic_unary_plan(S_entry) = eps', '$arithmetic_unary_reference_plan(S_entry) = eps',
        '$arithmetic_unary_valid(S_entry, punarywarning)', '$arithmetic_unary_snapshot(S_entry, punarywarning)',
        'punarywarning.OP = POSITIVE', 'punarywarning.LINE = 25',
        'S_entry.RESULT = KNOWN punarywarning.VALUE', 'punarywarning.INPUT = KNOWN punarywarning.VALUE',
        '$string_bytes(punarywarning.VALUE) = ($ptascii("12.5tail"))',
        'punarywarning.NUMBER = NFLOAT 4623226492472524800',
        '$integer_operand_source(S_entry, punarywarning.SITE, [PCFIELD 0], punarywarning.INPUT)',
        '$lookup(S_entry.ENV, $ptascii("source")) = (n_source)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_source] = DEFINED punarywarning.VALUE',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_source <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_source) = 1',
        '$integer_outputs(S_entry.EVENTS) = ([80,59])',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$arithmetic_unary_copy_plan(S_entry[.ORIGIN = eps]) = eps',
        '$arithmetic_unary_copy_plan(S_entry[.CODE = eps]) = eps',
        '$arithmetic_unary_copy_plan(S_entry[.RESULT = KNOWN PNULL]) = eps',
        '$arithmetic_unary_copy_plan(S_entry[.RESULT = KNOWN (PINT 12)]) = eps',
        '$arithmetic_unary_copy_plan(S_entry[.RESULT = VARIABLE ($ptascii("source")) 25]) = eps',
        '$arithmetic_unary_copy_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$arithmetic_unary_copy_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.OP = NEGATIVE])',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.LINE = 24])',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.INPUT = VARIABLE ($ptascii("source")) 25])',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.INPUT = KNOWN PNULL])',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.NUMBER = NINT 12])',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_atomic_begin',
        'S_atomic_begin = S_entry[.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += ['S_capture = S_atomic_begin', '$unary_copy_frontier(S_capture, 1)',
               '$arithmetic_unary_warning_valid(S_capture, punarywarning, 0)',
               '$task_nodes(ARITHMETIC_UNARY_WARNING punarywarning 0) = eps',
               '~$arithmetic_unary_warning_valid(S_capture, punarywarning, 2)']
    step('S_dispatch', 'S_capture')
    checks += ['S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
               'perrorcall.RESUME = ARITHMETIC_UNARY_WARNING punarywarning 1', 'perrorcall.TARGET = eps',
               'perrorcall.LINE = 25', 'perrorcall.LEVEL = 2',
               'perrorcall.MESSAGE = $ptascii("A non-numeric value encountered")',
               'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25',
               '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)',
               '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
               '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])']
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$unary_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)']
    seek('S_throw', 'S_entered', 6)
    checks += ['S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
               'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$unary_tasks(S_throw.TODO)',
               '$lookup(S_throw.ENV, $ptascii("source")) = eps',
               'S_throw.STORE[n_source] = DEFINED (PINT 99)',
               'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
               '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_source) = 0',
               '~((HCELL n_source) <- S_throw.ALLOCATIONS)',
               '$integer_pointer_value(S_throw, INTEGER_CV ($ptascii("source"))) = eps',
               '$arithmetic_unary_snapshot(S_throw, punarywarning)',
               '$arithmetic_unary_warning_valid(S_throw, punarywarning, 1)',
               '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
               '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
               '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
               '$throwable_field(S_throw, n_second, "line") = PINT 20',
               'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
               '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
               'S_done = $drive_steps(S_throw, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
               'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
               'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
               'S_done.STORE[n_source] = DEFINED (PINT 99)',
               '$lookup(S_done.ENV, $ptascii("source")) = (n_fresh_source)',
               'n_fresh_source =/= n_source', 'S_done.STORE[n_fresh_source] = DEFINED (PINT 8)',
               '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_source) = 0',
               '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_fresh_source) = 1',
               '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]']
    assert len(checks) == len(set(checks))
    return checks
