#!/usr/bin/env python3
"""Source-reached unique/shared reference unwrap and real Array GC release."""
import os
from pathlib import Path

import output_deprecation_warning_review_state as runner
import output_array_return_sources as sources

ROOT = sources.ROOT
CASES = {name: sources.CASES[name] for name in
         ('unique-ref-gc-transfer', 'shared-ref-gc-transfer')}
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true -- if S.TODO = (OB_USER_REF_ARRAY pobrefreturn n) :: ptask_tail*
def $dp_phase(S, 1) = true -- if S.TODO = (OB_USER_ARRAY_RESULT pobarrayreturn) :: ptask_tail*
def $dp_phase(S, 2) = true -- if S.TODO = (OB_USER_ARRAY_DONE pobarrayreturn) :: ptask_tail*
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_array_return_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_sources.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.runner.common.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    shared = name == 'shared-ref-gc-transfer'
    checks = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $dp_seek(S_initial, 0, 2048)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (OB_USER_REF_ARRAY pobrefreturn n_array) :: ptask_native*',
        'n_cell = pobrefreturn.CELL', 'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
        'pobrefreturn.PENDING = eps', '$ob_ref_current(S, pobrefreturn)',
        '$call_task_valid(S, OB_USER_REF_ARRAY pobrefreturn n_array)',
        '$heap_owners($heap_graph(S), HCELL n_cell) = ' + ('2' if shared else '1'),
        '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
        '$heap_count(HCELL n_cell, $task_nodes(OB_USER_REF_ARRAY pobrefreturn n_array)) = 1',
        '$heap_count(HARRAY n_array, $task_nodes(OB_USER_REF_ARRAY pobrefreturn n_array)) = 0',
        '~((HARRAY n_array) <- $gc_physical_nodes(S.GC.BUFFER))', *runner.valid('S'),
        'S_transfer_found = $drive_steps(S, 1)',
        r'S_transfer_found.COMPLETION = NORMAL \/ S_transfer_found.COMPLETION = BUDGET',
        'S_transfer = S_transfer_found[.COMPLETION = NORMAL]',
        '$ob_array_ref_transferred(S_transfer, pobrefreturn, n_array)', *runner.valid('S_transfer'),
        'pobarrayreturn = $ob_array_from_ref(pobrefreturn, n_array)',
        'pobarrayreturn.CELL = (n_cell)',
        'S_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cell) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cell) :: (OB_USER_ARRAY_WARN pobarrayreturn) :: ptask_native*',
        'pdestructionrelease_cell.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
        'pdestructionoperation_cell.SOURCE = OB_USER_REF_ARRAY pobrefreturn n_array',
        '$destructor_release_valid(S_transfer, pdestructionrelease_cell)',
        '$eager_operation_source_valid(S_transfer, pdestructionoperation_cell)',
        'S_cell_found = $drive_steps(S_transfer, 1)',
        r'S_cell_found.COMPLETION = NORMAL \/ S_cell_found.COMPLETION = BUDGET',
        'S_cell = S_cell_found[.COMPLETION = NORMAL]', *runner.valid('S_cell'),
        '$gc_consumed_decrements(S_transfer, S_cell, [HCELL n_cell, HARRAY n_array]) = [HARRAY n_array]',
        '~((HARRAY n_array) <- $gc_physical_nodes(S_cell.GC.BUFFER))',
        'pdestructionoperation_bad = pdestructionoperation_cell[.SOURCE = OB_USER_REF_ARRAY pobrefreturn[.CELL = 999999] n_array]',
        'S_source_bad = S_transfer[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cell) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (OB_USER_ARRAY_WARN pobarrayreturn) :: ptask_native*]',
        '~$eager_operation_source_valid(S_source_bad, pdestructionoperation_bad)',
        '$gc_consumed_decrements(S_source_bad, S_cell, [HCELL n_cell, HARRAY n_array]) = [HCELL n_cell, HARRAY n_array]',
        'S_no_operation = S_transfer[.DESTRUCTION.OPERATIONS = eps]',
        '$gc_consumed_decrements(S_no_operation, S_cell, [HCELL n_cell, HARRAY n_array]) = [HCELL n_cell, HARRAY n_array]',
        '$heap_count(HARRAY n_array, $task_nodes(OB_USER_ARRAY_WARN pobarrayreturn)) = 1',
        '$heap_count(HCELL n_cell, $task_nodes(OB_USER_ARRAY_WARN pobarrayreturn)) = 0',
        '$gc_consumed_decrements(S, S_transfer, [HCELL n_cell, HARRAY n_array]) = [HARRAY n_array]',
        '$gc_consumed_decrements(S[.ORIGIN = eps], S_transfer, [HCELL n_cell, HARRAY n_array]) = [HCELL n_cell, HARRAY n_array]',
        'S_missing = S_transfer[.TODO = ptask_native*]',
        '$gc_consumed_decrements(S, S_missing, [HCELL n_cell, HARRAY n_array]) = [HCELL n_cell, HARRAY n_array]',
        'S_warn_found = $dp_seek(S_transfer, 1, 1024)',
        r'S_warn_found.COMPLETION = NORMAL \/ S_warn_found.COMPLETION = BUDGET',
        'S_warn = S_warn_found[.COMPLETION = NORMAL]',
        'S_warn.TODO = (OB_USER_ARRAY_RESULT pobarrayreturn) :: ptask_native*',
        '$ob_array_current(S_warn, pobarrayreturn)', *runner.valid('S_warn'),
        '~((HARRAY n_array) <- $gc_physical_nodes(S_warn.GC.BUFFER))',
        '$heap_owners($heap_graph(S_warn), HARRAY n_array) = ' + ('2' if shared else '1'),
        '$heap_count(HARRAY n_array, $task_nodes(OB_USER_ARRAY_RESULT pobarrayreturn)) = 1',
        '$heap_count(HCELL n_cell, $task_nodes(OB_USER_ARRAY_RESULT pobarrayreturn)) = 0',
        'S_warn.RESULT = KNOWN PNULL', 'S_warn.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_warn.OUTPUTBUFFERS = [poutputbuffer]',
        r'poutputbuffer.FLAGS = 113 /\ poutputbuffer.BYTES = ([65,72])',
        '$string_bytes(pobarrayreturn.INVOKE.VALUE) = ([65])',
        '$string_bytes(pobarrayreturn.INVOKE.INPUT) = ([65])',
        'pobarrayreturn.INVOKE.VALUE =/= pobarrayreturn.INVOKE.INPUT',
        '~$call_task_valid(S_warn, OB_USER_ARRAY_WARN pobarrayreturn)',
        '~$call_task_valid(S_warn, OB_USER_ARRAY_RESULT pobarrayreturn[.CELL = (999999)])',
        '$gc_consumed_decrements(S_warn, S_warn, [HARRAY n_array]) = [HARRAY n_array]',
        'S_budget = $drive_steps(S_warn, 0)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.TODO = S_warn.TODO', 'S_budget.ALLOCATIONS = S_warn.ALLOCATIONS',
        'S_budget.STORE = S_warn.STORE', 'S_budget.GC = S_warn.GC',
        'S_budget.DESTRUCTION = S_warn.DESTRUCTION', *runner.valid('S_budget'),
        'S_done_found = $dp_seek(S_budget[.COMPLETION = NORMAL], 2, 1024)',
        r'S_done_found.COMPLETION = NORMAL \/ S_done_found.COMPLETION = BUDGET',
        'S_done = S_done_found[.COMPLETION = NORMAL]',
        'S_done.TODO = (OB_USER_ARRAY_DONE pobarrayreturn) :: ptask_native*',
        '$heap_count(HARRAY n_array, $task_nodes(OB_USER_ARRAY_DONE pobarrayreturn)) = 0',
        '$heap_count(HCELL n_cell, $task_nodes(OB_USER_ARRAY_DONE pobarrayreturn)) = 0',
        'S_done.DESTRUCTION.OPERATIONS = eps', *runner.valid('S_done'),
    ]
    if shared:
        checks += [
            '(HCELL n_cell) <- S_warn.ALLOCATIONS', 'S_warn.STORE[n_cell] = DEFINED (PARRAY n_array)',
            '(HARRAY n_array) <- S_done.ALLOCATIONS',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '(HARRAY n_array) <- $gc_physical_nodes(S_done.GC.BUFFER)',
        ]
    else:
        checks += [
            '~((HCELL n_cell) <- S_warn.ALLOCATIONS)',
            '$entry_lookup(S_warn.ARRAYS[n_array].ITEMS, KINT 0) = (DIRECT (POBJECT n_child))',
            '$heap_owners($heap_graph(S_warn), HOBJECT n_child) = 1',
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        ]
    checks += [
        'S_commit_found = $drive_steps(S_done, 1)',
        r'S_commit_found.COMPLETION = NORMAL \/ S_commit_found.COMPLETION = BUDGET',
        'S_commit = S_commit_found[.COMPLETION = NORMAL]',
        'S_commit.TODO = (OB_USER_ARRAY_COMMIT pobarrayreturn poboutput) :: ptask_native*',
        'poboutput.VALUE = PSTRING ([65,114,114,97,121])', '~poboutput.FAILED', *runner.valid('S_commit'),
        '~$call_task_valid(S_commit, OB_USER_ARRAY_RESULT pobarrayreturn)',
        'S_final = $drive_steps(S_commit, 2048)',
        r'S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps',
        'S_final.OUTPUTBUFFERS = eps', '$dp_output(S_final.EVENTS) = ' + runner.bytes_expr(CASES[name][1]),
        *runner.valid('S_final'),
    ]
    return checks


if __name__ == '__main__':
    runner.ROOT = ROOT
    runner.CASES = CASES
    runner.PREFIX = PREFIX
    runner.assertions = assertions
    runner.fingerprint = fingerprint
    runner.main()
