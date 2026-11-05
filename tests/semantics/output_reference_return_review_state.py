#!/usr/bin/env python3
"""Reached returned-cell ownership inside diagnostic and callee destructors."""
import os

import output_deprecation_warning_review_state as runner
import output_reference_return_review_sources as sources

ROOT = sources.ROOT
CASES = {name: sources.CASES[name] for name in
         ('warning-retval-destructor-mutates-false-api', 'callee-cleanup-rebinds-global-and-throws')}
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.CLEANUP = (pdestructioncleanup)
  -- if pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall
  -- if perrorcall.RESUME = OB_USER_REF_DEPRECATED pobrefreturn
def $dp_phase(S, 1) = true -- if S.TODO = (OB_USER_REF_UNWRAP pobrefreturn) :: ptask_tail*
def $dp_phase(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = eps
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if pdestructionframe.VALUE = REFERENCE n_cell
def $dp_phase(S, 3) = true
  -- if S.TODO = (OB_USER_NORMAL_PENDING pobinvoke pdestructionframe) :: ptask_tail*
  -- if pdestructionframe.VALUE = REFERENCE n_cell
def $dp_phase(S, 4) = true -- if S.TODO = (OB_USER_REF_COMMIT pobrefreturn poboutput) :: ptask_tail*
def $dp_phase(S, 5) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = OB_USER_REF_UNWRAP pobrefreturn
def $dp_phase(S, n) = false -- otherwise
dec $rr_normal(ptask*) : pobinvoke?
dec $rr_normal_task(ptask) : bool
def $rr_normal_task(OB_USER_NORMAL_RESULT pobinvoke pdestructionframe) = true
def $rr_normal_task(ptask) = false -- otherwise
def $rr_normal(eps) = eps
def $rr_normal((OB_USER_NORMAL_RESULT pobinvoke pdestructionframe) :: ptask_tail*) = (pobinvoke)
def $rr_normal(ptask :: ptask_tail*) = $rr_normal(ptask_tail*) -- if ~$rr_normal_task(ptask)
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_reference_return_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_sources.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.common.sha(ROOT / name)
    return inputs


def release_checks(state, steps, negatives=False):
    checks = [
        'S_release_found = $drive_steps(' + state + ', ' + str(steps) + ')',
        r'S_release_found.COMPLETION = NORMAL \/ S_release_found.COMPLETION = BUDGET',
        'S_release = S_release_found[.COMPLETION = NORMAL]', *runner.valid('S_release'),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_unwrap) :: (OB_USER_REF_COMMIT pobrefreturn_pending poboutput) :: ptask_native*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
        'pdestructionoperation_unwrap.SOURCE = OB_USER_REF_UNWRAP pobrefreturn_pending',
        r'pdestructionoperation_unwrap.VALUE = KNOWN PNULL /\ pdestructionoperation_unwrap.BASE = BASE_VALUE (KNOWN PNULL) /\ pdestructionoperation_unwrap.PENDING = eps',
        '$eager_operation_source_guard(S_release, pdestructionoperation_unwrap)',
        '$heap_count(HCELL n_cell, $task_nodes(OB_USER_REF_COMMIT pobrefreturn_pending poboutput)) = 0',
        '$heap_count(HOBJECT n_pending, $task_nodes(OB_USER_REF_COMMIT pobrefreturn_pending poboutput)) = 1',
    ]
    if negatives:
        checks += ['S_release.DESTRUCTION.OPERATIONS = pdestructionoperation_unwrap :: pdestructionoperation_unwrap_tail*']
        for name, mutation in (('value', '[.VALUE = KNOWN (PINT 7)]'),
                               ('pending', '[.PENDING = (n_pending)]'),
                               ('origin', '[.ORIGIN = eps]')):
            checks += [
                'pdestructionoperation_unwrap_' + name + ' = pdestructionoperation_unwrap' + mutation,
                'S_bad_' + name + ' = S_release[.DESTRUCTION.OPERATIONS = pdestructionoperation_unwrap_' + name + ' :: pdestructionoperation_unwrap_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_unwrap_' + name + ') :: (OB_USER_REF_COMMIT pobrefreturn_pending poboutput) :: ptask_native*]',
                '~$eager_operation_source_guard(S_bad_' + name + ', pdestructionoperation_unwrap_' + name + ')',
            ]
        checks += [
            'ptask_native* =/= eps', 'pobrefreturn_bad = pobrefreturn_pending[.TAIL = eps]',
            'pdestructionoperation_unwrap_tail_bad = pdestructionoperation_unwrap[.SOURCE = OB_USER_REF_UNWRAP pobrefreturn_bad]',
            'S_bad_tail = S_release[.DESTRUCTION.OPERATIONS = pdestructionoperation_unwrap_tail_bad :: pdestructionoperation_unwrap_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_unwrap_tail_bad) :: (OB_USER_REF_COMMIT pobrefreturn_bad poboutput) :: ptask_native*]',
            '~$eager_operation_source_guard(S_bad_tail, pdestructionoperation_unwrap_tail_bad)',
        ]
    checks += [
        'S_exit_found = $dp_seek(S_release, 5, 16)',
        r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]', *runner.valid('S_exit'),
        '$eager_operation_source_guard(S_exit, pdestructionoperation_unwrap)',
        'S_converted_found = $drive_steps(S_exit, 1)',
        r'S_converted_found.COMPLETION = NORMAL \/ S_converted_found.COMPLETION = BUDGET',
        'S_converted = S_converted_found[.COMPLETION = NORMAL]', *runner.valid('S_converted'),
    ]
    return checks


def assertions(name, fixture, directory, path):
    diagnostic = name == 'warning-retval-destructor-mutates-false-api'
    phase = 0 if diagnostic else 2
    checks = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $dp_seek(S_initial, ' + str(phase) + ', 1536)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_reached = S_found[.COMPLETION = NORMAL]', '$dp_phase(S_reached, ' + str(phase) + ')',
        *runner.valid('S_reached'), 'S_reached.CURRENT = (pcallcontext)',
        '$destructor_context_call(pcallcontext, S_reached.CURRENT, S_reached.FRAMES) = (pdestructorcall)',
        '$dp_output(S_reached.EVENTS) = ([80])',
    ]
    if diagnostic:
        checks += [
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
            'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
            'perrorcall.RESUME = OB_USER_REF_DEPRECATED pobrefreturn',
            'pobrefreturn.INVOKE.CALL = OB_API pconfigcall',
            'pconfigcall.KIND = INTRINSIC_OB_GET_FLUSH', 'pconfigcall.LINE = 7',
            'n_cell = pobrefreturn.CELL', 'S_reached.STORE[n_cell] = DEFINED (PBOOL true)',
            '$ob_return_context(S_reached, OB_USER_REF_DEPRECATED pobrefreturn, pobrefreturn.CALLER, $ob_call_site(pobrefreturn.INVOKE.CALL), pobrefreturn.TAIL)', '~$ob_ref_current(S_reached, pobrefreturn)',
            '$call_task_valid(S_reached, OB_USER_REF_DEPRECATED pobrefreturn)',
            '$heap_count(HCELL n_cell, $machine_roots(S_reached)) = 2',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_REF_DEPRECATED pobrefreturn)) = 1',
            'S_reached.OUTPUTBUFFERS = [poutputbuffer]',
            r'poutputbuffer.FLAGS = 8305 /\ poutputbuffer.BYTES = ([65,72])',
            'S_pending_found = $dp_seek(S_reached, 1, 512)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]', *runner.valid('S_pending'),
            'S_pending.TODO = (OB_USER_REF_UNWRAP pobrefreturn_pending) :: ptask_native*',
            'pobrefreturn_pending.CELL = n_cell', 'pobrefreturn_pending.PENDING = (n_pending)',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_pending)) = 1',
            '$heap_count(HCELL n_cell, $machine_roots(S_pending)) = 2',
            'S_pending.STORE[n_cell] = DEFINED (PBOOL false)',
            '~((HOBJECT pdestructorcall.OBJECT) <- S_pending.ALLOCATIONS)',
            '$dp_output(S_pending.EVENTS) = ([80,68])',
            'S_budget = $drive_steps(S_pending, 0)', 'S_budget.COMPLETION = BUDGET',
            'S_budget.TODO = S_pending.TODO', 'S_budget.STORE = S_pending.STORE',
            'S_budget.DESTRUCTION = S_pending.DESTRUCTION', *runner.valid('S_budget'),
            *release_checks('S_budget[.COMPLETION = NORMAL]', 1),
            'S_converted.TODO = (OB_USER_REF_COMMIT pobrefreturn_pending poboutput) :: ptask_native*',
            r'poboutput.VALUE = PSTRING eps /\ poboutput.BYTES = eps /\ ~poboutput.FAILED',
            'S_converted.STORE[n_cell] = DEFINED (PBOOL false)',
            '$heap_count(HCELL n_cell, $machine_roots(S_converted)) = 1',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_converted)) = 1',
            '~$call_task_valid(S_converted, OB_USER_REF_COMMIT pobrefreturn_pending poboutput[.VALUE = PBOOL false][.FAILED = true])',
        ]
    else:
        checks += [
            'pdestructorcall.OPERATION = eps', 'pdestructorcall.FRAME = (pdestructionframe)',
            'pdestructionframe.VALUE = REFERENCE n_cell', 'pdestructionframe.PENDING = eps',
            'S_caller = $destructor_boundary_scope(S_reached, pdestructorcall, S_reached.FRAMES)',
            '$rr_normal(S_caller.TODO) = (pobinvoke)',
            '$ob_normal_result_prefix(S_caller.TODO, pdestructionframe)',
            '$call_task_valid(S_caller, OB_USER_NORMAL_RESULT pobinvoke pdestructionframe)',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_NORMAL_RESULT pobinvoke pdestructionframe)) = 0',
            '$heap_count(HCELL n_cell, $task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe)) = 1',
            '$heap_count(HCELL n_cell, $machine_roots(S_reached)) = 2',
            'S_caller.RESULT = KNOWN PNULL',
            'S_unowned = S_caller[.TODO = [OB_USER_NORMAL_RESULT pobinvoke pdestructionframe]]',
            '~$call_task_valid(S_unowned, OB_USER_NORMAL_RESULT pobinvoke pdestructionframe)',
            'S_pending_found = $dp_seek(S_reached, 3, 512)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]', *runner.valid('S_pending'),
            'S_pending.TODO = (OB_USER_NORMAL_PENDING pobinvoke pdestructionframe_pending) :: ptask_native*',
            'pdestructionframe_pending.VALUE = REFERENCE n_cell', 'pdestructionframe_pending.PENDING = (n_pending)',
            '$heap_count(HCELL n_cell, $machine_roots(S_pending)) = 1',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_pending)) = 1',
            '$lookup(S_pending.ENV, ([114])) = (n_global)', 'n_global =/= n_cell',
            'S_pending.STORE[n_global] = DEFINED (PBOOL false)',
            'S_pending.STORE[n_cell] = DEFINED (PBOOL true)',
            *release_checks('S_pending', 2, negatives=True),
            '~((HCELL n_cell) <- S_exit.ALLOCATIONS)',
            'S_converted.TODO = (OB_USER_REF_COMMIT pobrefreturn_pending poboutput) :: ptask_native*',
            r'poboutput.VALUE = PSTRING ([49]) /\ poboutput.BYTES = ([49]) /\ ~poboutput.FAILED',
            '~((HCELL n_cell) <- S_converted.ALLOCATIONS)',
            'S_converted.STORE[n_global] = DEFINED (PBOOL false)',
        ]
    checks += [
        'S_done = $drive_steps(S_converted, 2048)',
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
