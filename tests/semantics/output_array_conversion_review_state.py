#!/usr/bin/env python3
"""Reached CELL/array transfer, child exceptions and readonly return owners."""
import os

import output_deprecation_warning_review_state as runner
import output_array_conversion_review_sources as sources
import output_reference_return_review_sources as scalar

ROOT = sources.ROOT
CASES = {name: sources.CASES[name] for name in
         ('reference-array-capture-before-warning', 'callee-array-owner-then-child-replacement')}
CASES['scalar-return-marker-authority'] = scalar.CASES['warning-retval-destructor-mutates-false-api']
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true -- if S.TODO = (OB_USER_REF_ARRAY pobrefreturn n_array) :: ptask_tail*
def $dp_phase(S, 1) = true -- if S.TODO = (OB_USER_ARRAY_WARN pobarrayreturn) :: ptask_tail*
def $dp_phase(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = OB_USER_ARRAY_RESULT pobarrayreturn
def $dp_phase(S, 3) = true -- if S.TODO = (OB_USER_ARRAY_COMMIT pobarrayreturn poboutput) :: ptask_tail*
def $dp_phase(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = eps
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if pdestructionframe.VALUE = KNOWN (PARRAY n_array)
def $dp_phase(S, 5) = true -- if S.TODO = (OB_USER_REF_COMMIT pobrefreturn poboutput) :: ptask_tail*
def $dp_phase(S, n) = false -- otherwise
dec $ar_normal(ptask*) : pobinvoke?
dec $ar_normal_task(ptask) : bool
def $ar_normal_task(OB_USER_NORMAL_RESULT pobinvoke pdestructionframe) = true
def $ar_normal_task(ptask) = false -- otherwise
def $ar_normal(eps) = eps
def $ar_normal((OB_USER_NORMAL_RESULT pobinvoke pdestructionframe) :: ptask_tail*) = (pobinvoke)
def $ar_normal(ptask :: ptask_tail*) = $ar_normal(ptask_tail*) -- if ~$ar_normal_task(ptask)
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_array_conversion_review_state.py',
                 'tests/semantics/output_reference_return_review_sources.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_sources.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.common.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    phase = 0 if name == 'reference-array-capture-before-warning' else 4 if name == 'callee-array-owner-then-child-replacement' else 5
    checks = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $dp_seek(S_initial, ' + str(phase) + ', 2048)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_reached = S_found[.COMPLETION = NORMAL]', '$dp_phase(S_reached, ' + str(phase) + ')',
        *runner.valid('S_reached'),
    ]
    if phase == 0:
        checks += [
            'S_reached.TODO = (OB_USER_REF_ARRAY pobrefreturn n_array) :: ptask_native*',
            'n_cell = pobrefreturn.CELL', 'pobrefreturn.PENDING = eps',
            'S_reached.STORE[n_cell] = DEFINED (PARRAY n_array)',
            '$heap_count(HCELL n_cell, $machine_roots(S_reached)) = 2',
            '$heap_owners($heap_graph(S_reached), HARRAY n_array) = 1',
            '$heap_count(HARRAY n_array, $task_nodes(OB_USER_REF_ARRAY pobrefreturn n_array)) = 0',
            'S_budget = $drive_steps(S_reached, 0)', 'S_budget.COMPLETION = BUDGET',
            'S_budget.TODO = S_reached.TODO', 'S_budget.STORE = S_reached.STORE', *runner.valid('S_budget'),
            'S_transfer_found = $drive_steps(S_budget[.COMPLETION = NORMAL], 1)',
            r'S_transfer_found.COMPLETION = NORMAL \/ S_transfer_found.COMPLETION = BUDGET',
            'S_transfer = S_transfer_found[.COMPLETION = NORMAL]', *runner.valid('S_transfer'),
            'S_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_ref) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_ref) :: (OB_USER_ARRAY_WARN pobarrayreturn) :: ptask_native*',
            'pdestructionrelease_ref.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
            'pdestructionoperation_ref.SOURCE = OB_USER_REF_ARRAY pobrefreturn n_array',
            'pobarrayreturn = $ob_array_from_ref(pobrefreturn, n_array)',
            'pobarrayreturn.CELL = (n_cell)',
            '$heap_count(HARRAY n_array, $task_nodes(OB_USER_ARRAY_WARN pobarrayreturn)) = 1',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_ARRAY_WARN pobarrayreturn)) = 0',
            '$eager_operation_source_guard(S_transfer, pdestructionoperation_ref)',
            'S_transfer.DESTRUCTION.OPERATIONS = pdestructionoperation_ref :: pdestructionoperation_tail*',
            'pobrefreturn_bad = pobrefreturn[.CELL = 999999]',
            'pdestructionoperation_bad = pdestructionoperation_ref[.SOURCE = OB_USER_REF_ARRAY pobrefreturn_bad n_array]',
            'S_bad = S_transfer[.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: pdestructionoperation_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_ref) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (OB_USER_ARRAY_WARN pobarrayreturn) :: ptask_native*]',
            '~$eager_operation_source_guard(S_bad, pdestructionoperation_bad)',
            'S_drop_found = $drive_steps(S_transfer, 1)',
            r'S_drop_found.COMPLETION = NORMAL \/ S_drop_found.COMPLETION = BUDGET',
            'S_drop = S_drop_found[.COMPLETION = NORMAL]', *runner.valid('S_drop'),
            '$gc_consumed_decrements(S_transfer, S_drop, [HCELL n_cell, HARRAY n_array]) = [HARRAY n_array]',
            '$gc_consumed_decrements(S_bad, S_drop, [HCELL n_cell, HARRAY n_array]) = [HCELL n_cell, HARRAY n_array]',
            'S_warn_found = $dp_seek(S_drop, 1, 32)',
            r'S_warn_found.COMPLETION = NORMAL \/ S_warn_found.COMPLETION = BUDGET',
            'S_warn = S_warn_found[.COMPLETION = NORMAL]', *runner.valid('S_warn'),
            'S_warn.TODO = (OB_USER_ARRAY_WARN pobarrayreturn) :: ptask_native*',
            '$heap_count(HCELL n_cell, $machine_roots(S_warn)) = 1',
            '$heap_owners($heap_graph(S_warn), HARRAY n_array) = 2',
            'S_warn.GC.BUFFER = S_reached.GC.BUFFER',
            '~$call_task_valid(S_warn, OB_USER_ARRAY_RESULT pobarrayreturn)',
            'S_child_found = $dp_seek(S_warn, 2, 1024)',
            r'S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET',
            'S_child = S_child_found[.COMPLETION = NORMAL]', *runner.valid('S_child'),
            'S_child.CURRENT = (pcallcontext)',
            '$destructor_context_call(pcallcontext, S_child.CURRENT, S_child.FRAMES) = (pdestructorcall_child)',
            'pdestructorcall_child.OPERATION = (pdestructionoperation_child)',
            'pdestructionoperation_child.SOURCE = OB_USER_ARRAY_RESULT pobarrayreturn_retired',
            'pobarrayreturn_retired.ARRAY = n_array', 'pobarrayreturn_retired.CELL = (n_cell)',
            'pobarrayreturn_retired.PENDING = (n_original)',
            r'pdestructionoperation_child.COMPLETION = THROWING n_original /\ pdestructionoperation_child.PENDING = (n_original)',
            '~((HARRAY n_array) <- S_child.ALLOCATIONS)',
            '$heap_count(HARRAY n_array, $task_nodes(OB_USER_ARRAY_DONE pobarrayreturn_retired)) = 0',
            '$heap_count(HOBJECT n_original, $task_nodes(OB_USER_ARRAY_DONE pobarrayreturn_retired)) = 0',
            '$heap_count(HOBJECT n_original, $machine_roots(S_child)) = 1',
            '$heap_owners($heap_graph(S_child), HOBJECT pdestructorcall_child.OBJECT) = 2',
            'S_child.STORE[n_cell] = DEFINED (PBOOL false)',
            '$eager_operation_source_guard(S_child, pdestructionoperation_child)',
            'S_commit_found = $dp_seek(S_child, 3, 1024)',
            r'S_commit_found.COMPLETION = NORMAL \/ S_commit_found.COMPLETION = BUDGET',
            'S_commit = S_commit_found[.COMPLETION = NORMAL]', *runner.valid('S_commit'),
            'S_commit.TODO = (OB_USER_ARRAY_COMMIT pobarrayreturn_commit poboutput) :: ptask_native*',
            'pobarrayreturn_commit.PENDING = (n_pending)', 'n_pending =/= n_original',
            'pobarrayreturn_commit.CELL = (n_cell)',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_commit)) = 1',
            '$heap_count(HOBJECT n_original, $machine_roots(S_commit)) = 0',
            '$heap_owners($heap_graph(S_commit), HOBJECT n_original) = 1',
            '$throwable_field(S_commit, n_pending, "previous") = POBJECT n_original',
            '~((HOBJECT pdestructorcall_child.OBJECT) <- S_commit.ALLOCATIONS)',
            'S_resume = S_commit',
        ]
    elif phase == 4:
        checks += [
            'S_reached.CURRENT = (pcallcontext)',
            '$destructor_context_call(pcallcontext, S_reached.CURRENT, S_reached.FRAMES) = (pdestructorcall)',
            'pdestructorcall.FRAME = (pdestructionframe)',
            'pdestructionframe.VALUE = KNOWN (PARRAY n_array)', 'pdestructionframe.PENDING = eps',
            'S_caller = $destructor_boundary_scope(S_reached, pdestructorcall, S_reached.FRAMES)',
            '$ar_normal(S_caller.TODO) = (pobinvoke)',
            '$ob_normal_result_prefix(S_caller.TODO, pdestructionframe)',
            '$call_task_valid(S_caller, OB_USER_NORMAL_RESULT pobinvoke pdestructionframe)',
            '$heap_count(HARRAY n_array, $task_nodes(OB_USER_NORMAL_RESULT pobinvoke pdestructionframe)) = 0',
            '$heap_count(HARRAY n_array, $task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe)) = 1',
            '$heap_count(HARRAY n_array, $machine_roots(S_reached)) = 1',
            'S_caller.RESULT = KNOWN PNULL',
            'S_unowned = S_caller[.TODO = [OB_USER_NORMAL_RESULT pobinvoke pdestructionframe]]',
            '~$call_task_valid(S_unowned, OB_USER_NORMAL_RESULT pobinvoke pdestructionframe)',
            'S_resume = S_reached',
        ]
    else:
        checks += [
            'S_reached.TODO = (OB_USER_REF_COMMIT pobrefreturn poboutput) :: ptask_native*',
            'S_reached.STORE[pobrefreturn.CELL] = DEFINED (PBOOL false)',
            'poboutput.VALUE = PSTRING eps',
            '$call_task_valid(S_reached, OB_USER_REF_COMMIT pobrefreturn poboutput)',
            '~$call_task_valid(S_reached, OB_USER_REF_UNWRAP pobrefreturn)',
            'poboutput_other = $ob_user_output(S_reached, PSTRING ([90]))',
            '$ob_user_output_valid(S_reached, poboutput_other)',
            '~$call_task_valid(S_reached, OB_USER_REF_COMMIT pobrefreturn poboutput_other)',
            'S_resume = S_reached',
        ]
    checks += [
        'S_done = $drive_steps(S_resume, 4096)',
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
