#!/usr/bin/env python3
"""Reached returned-cell owners, readonly cleanup seals and scalar unwrap."""
import os
from pathlib import Path

import output_deprecation_warning_review_state as runner
import output_reference_return_sources as sources

ROOT = sources.common.ROOT
CASES = {name: sources.CASES[name] for name in
         ('local-cell-true', 'warning-rebinds-alias', 'cleanup-throw-defined', 'notice-throw-defined')}
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true -- if S.TODO = (OB_USER_REF_UNWRAP pobrefreturn) :: ptask_tail*
def $dp_phase(S, 1) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OB_USER_NORMAL_RESULT pobinvoke pdestructionframe_success) :: ptask_tail*
  -- if pdestructionframe.VALUE = REFERENCE n_cell
  -- if pdestructionframe.PENDING = (n)
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_reference_return_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_sources.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.common.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    phase = 1 if name == 'cleanup-throw-defined' else 0
    checks = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $dp_seek(S_initial, ' + str(phase) + ', 1536)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_reached = S_found[.COMPLETION = NORMAL]', '$dp_phase(S_reached, ' + str(phase) + ')',
        *runner.valid('S_reached'), '$ob_user_running(S_reached)',
        'S_reached.RESULT = KNOWN PNULL', 'S_reached.BASE = BASE_VALUE (KNOWN PNULL)',
    ]
    if phase == 1:
        checks += [
            'S_reached.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OB_USER_NORMAL_RESULT pobinvoke pdestructionframe_success) :: ptask_native*',
            'pdestructionframe.VALUE = REFERENCE n_cell', 'pdestructionframe.PENDING = (n)',
            'pdestructionframe_success = pdestructionframe[.PENDING = eps]',
            'S_reached.STORE[n_cell] = DEFINED (PBOOL true)',
            '$heap_count(HCELL n_cell, $task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe)) = 1',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_NORMAL_RESULT pobinvoke pdestructionframe_success)) = 0',
            '$call_task_valid(S_reached, OB_USER_NORMAL_RESULT pobinvoke pdestructionframe_success)',
            'S_unowned = S_reached[.TODO = (OB_USER_NORMAL_RESULT pobinvoke pdestructionframe_success) :: ptask_native*][.DESTRUCTION.FRAMES = eps]',
            '~$call_task_valid(S_unowned, OB_USER_NORMAL_RESULT pobinvoke pdestructionframe_success)',
            '~$call_task_valid(S_reached, OB_USER_NORMAL_RESULT pobinvoke pdestructionframe_success[.VALUE = REFERENCE 999999])',
            'S_pending_found = $drive_steps(S_reached, 1)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]',
            'S_pending.TODO = (OB_USER_NORMAL_PENDING pobinvoke pdestructionframe) :: ptask_native*',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_NORMAL_PENDING pobinvoke pdestructionframe)) = 1',
            '$heap_count(HOBJECT n, $task_nodes(OB_USER_NORMAL_PENDING pobinvoke pdestructionframe)) = 1',
            *runner.valid('S_pending'),
        ]
    else:
        checks += [
            'S_reached.TODO = (OB_USER_REF_UNWRAP pobrefreturn) :: ptask_native*',
            'pobrefreturn.TAIL = ptask_native*', 'pobrefreturn.CALLER = S_reached.CURRENT',
            'pobinvoke = pobrefreturn.INVOKE', '$ob_user_fci_arguments(pobinvoke)',
            'n_cell = pobrefreturn.CELL', 'S_reached.STORE[n_cell] = DEFINED (PBOOL true)',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_REF_UNWRAP pobrefreturn)) = 1',
            '$call_task_valid(S_reached, OB_USER_REF_UNWRAP pobrefreturn)',
            '~$call_task_valid(S_reached, OB_USER_REF_UNWRAP pobrefreturn[.CELL = 999999])',
            '~$call_task_valid(S_reached[.ORIGIN = eps], OB_USER_REF_UNWRAP pobrefreturn)',
            'S_bad_tail = S_reached[.TODO = (OB_USER_REF_UNWRAP pobrefreturn[.TAIL = eps]) :: ptask_native*]',
            '~$call_task_valid(S_bad_tail, OB_USER_REF_UNWRAP pobrefreturn[.TAIL = eps])',
            'pobinvoke_bad = pobinvoke[.PHASE = 999]',
            'pobrefreturn_bad = pobrefreturn[.INVOKE = pobinvoke_bad]',
            'S_bad_phase = S_reached[.TODO = (OB_USER_REF_UNWRAP pobrefreturn_bad) :: ptask_native*]',
            '~$call_task_valid(S_bad_phase, OB_USER_REF_UNWRAP pobrefreturn_bad)',
        ]
        if name != 'notice-throw-defined':
            checks += [
                'pobrefreturn.PENDING = eps', '$heap_owners($heap_graph(S_reached), HCELL n_cell) = 1',
                '$heap_count(HCELL n_cell, $machine_roots(S_reached)) = 1',
            ]
        else:
            checks += [
                'pobrefreturn.PENDING = (n)', '$throwable_live(S_reached, n)',
                '$heap_count(HOBJECT n, $task_nodes(OB_USER_REF_UNWRAP pobrefreturn)) = 1',
                '~$call_task_valid(S_reached, OB_USER_REF_UNWRAP pobrefreturn[.PENDING = (999999)])',
            ]
        if name == 'warning-rebinds-alias':
            checks += [
                '$lookup(S_reached.ENV, ([114])) = (n_global)', 'n_global =/= n_cell',
                'S_reached.STORE[n_global] = DEFINED (PBOOL false)',
                '$string_bytes(pobinvoke.VALUE) = ([65])', '$string_bytes(pobinvoke.INPUT) = ([65])',
                'pobinvoke.INPUT =/= pobinvoke.VALUE',
            ]
        checks += [
            'S_unwrapped_found = $drive_steps(S_reached, 1)',
            r'S_unwrapped_found.COMPLETION = NORMAL \/ S_unwrapped_found.COMPLETION = BUDGET',
            'S_unwrapped = S_unwrapped_found[.COMPLETION = NORMAL]',
            'S_unwrapped.TODO = (OB_USER_REF_COMMIT pobrefreturn poboutput) :: ptask_native*',
            'poboutput.VALUE = PSTRING ([49])', 'poboutput.BYTES = ([49])', '~poboutput.FAILED',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_REF_COMMIT pobrefreturn poboutput)) = 0',
            '~((HCELL n_cell) <- S_unwrapped.ALLOCATIONS)', *runner.valid('S_unwrapped'),
            '~$call_task_valid(S_unwrapped, OB_USER_REF_COMMIT pobrefreturn poboutput[.FAILED = true])',
            '~$call_task_valid(S_unwrapped, OB_USER_REF_COMMIT pobrefreturn poboutput[.VALUE = PBOOL true])',
        ]
    checks += [
        'S_budget = $drive_steps(S_reached, 0)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.TODO = S_reached.TODO', 'S_budget.STORE = S_reached.STORE',
        'S_budget.ALLOCATIONS = S_reached.ALLOCATIONS', 'S_budget.DESTRUCTION = S_reached.DESTRUCTION',
        'S_budget.OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS', *runner.valid('S_budget'),
        'S_done = $drive_steps(S_budget[.COMPLETION = NORMAL], 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.OUTPUTBUFFERS = eps', '$dp_output(S_done.EVENTS) = ' + runner.bytes_expr(CASES[name][1]),
        *runner.valid('S_done'),
    ]
    return checks


if __name__ == '__main__':
    runner.ROOT = ROOT
    runner.CASES = CASES
    runner.PREFIX = PREFIX
    runner.assertions = assertions
    runner.fingerprint = fingerprint
    runner.main()
