#!/usr/bin/env python3
"""Real output object wrapper handoff and pending cast-guard GC visits."""
import os
from pathlib import Path
import output_deprecation_warning_review_state as runner
import output_object_return_sources as sources

ROOT = sources.ROOT
CASES = {name: sources.CASES[name] for name in
         ('fresh-unique-ref-object-precast-gc', 'pending-deprecation-skips-cast',
          'method-reference-notice-framed', 'method-reference-notice-unframed')}
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true -- if S.TODO = (OB_USER_REF_OBJECT pobrefreturn n) :: ptask_tail*
def $dp_phase(S, 1) = true -- if S.TODO = (OB_USER_OBJECT_SKIP pobobjectreturn) :: ptask_tail*
def $dp_phase(S, 2) = true -- if S.TODO = (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_tail*
def $dp_phase(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = OB_USER_OBJECT_RELEASE pobobjectreturn poboutput
def $dp_phase(S, 4) = true -- if S.TODO = (OB_USER_OBJECT_RELEASE pobobjectreturn poboutput) :: ptask_tail*
def $dp_phase(S, 5) = true -- if S.TODO = (OB_USER_OBJECT_RETURN pobobjectreturn poperand) :: ptask_tail*
def $dp_phase(S, 6) = true -- if S.TODO = (OB_USER_OBJECT_COMMIT pobobjectreturn poboutput) :: ptask_tail*
def $dp_phase(S, 7) = true
  -- if S.TODO = (OB_USER_OBJECT_PENDING pobobjectreturn pdestructionframe) :: ptask_tail*
  -- if pdestructionframe.VALUE = REFERENCE n_cell
def $dp_phase(S, 8) = true
  -- if S.TODO = (THROW_SEARCH n_pending) :: (OB_USER_OBJECT_NOTICE pobobjectreturn n_cell n_pending) :: ptask_tail*
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_object_return_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.runner.common.sha(ROOT / name)
    return inputs


def seek(checks, source, name, phase):
    checks += [name + '_found = $dp_seek(' + source + ', ' + str(phase) + ', 2048)',
               name + r'_found.COMPLETION = NORMAL \/ ' + name + '_found.COMPLETION = BUDGET',
               name + ' = ' + name + '_found[.COMPLETION = NORMAL]', *runner.valid(name)]


def step(checks, source, name):
    checks += [name + '_found = $drive_steps(' + source + ', 1)',
               name + r'_found.COMPLETION = NORMAL \/ ' + name + '_found.COMPLETION = BUDGET',
               name + ' = ' + name + '_found[.COMPLETION = NORMAL]', *runner.valid(name)]


def assertions(name, fixture, directory, path):
    if name.startswith('method-reference-notice-'):
        return notice_assertions(name, fixture, directory, path)
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET']
    phase = 0 if name == 'fresh-unique-ref-object-precast-gc' else 1
    seek(checks, 'S_initial', 'S', phase)
    if phase == 0:
        checks += [
            'S.TODO = (OB_USER_REF_OBJECT pobrefreturn n_object) :: ptask_native*',
            'n_cell = pobrefreturn.CELL', 'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_object) = 1',
            '~((HOBJECT n_object) <- $gc_physical_nodes(S.GC.BUFFER))',
            '$call_task_valid(S, OB_USER_REF_OBJECT pobrefreturn n_object)',
            '$ob_ref_current(S, pobrefreturn)',
        ]
        step(checks, 'S', 'S_transfer')
        checks += [
            'pobobjectreturn = $ob_object_from_ref(pobrefreturn, n_object)',
            'pobobjectreturn.CELL = (n_cell)', 'pobobjectreturn.RETURNED = eps',
            'S_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cell) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_native*',
            'pdestructionrelease_cell.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
            'pdestructionoperation.SOURCE = OB_USER_REF_OBJECT pobrefreturn n_object',
            '$eager_operation_source_valid(S_transfer, pdestructionoperation)',
            '$destructor_release_valid(S_transfer, pdestructionrelease_cell)',
            '$gc_consumed_decrements(S, S_transfer, [HCELL n_cell, HOBJECT n_object]) = [HOBJECT n_object]',
            '$gc_consumed_decrements(S[.ORIGIN = eps], S_transfer, [HCELL n_cell]) = [HCELL n_cell]',
        ]
        step(checks, 'S_transfer', 'S_object_job')
        checks += [
            'S_object_job.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_object) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_native*',
            'pdestructionrelease_object.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
            '~((HCELL n_cell) <- S_object_job.ALLOCATIONS)',
            '~((HOBJECT n_object) <- $gc_physical_nodes(S_object_job.GC.BUFFER))',
            '$gc_consumed_decrements(S_transfer, S_object_job, [HCELL n_cell, HOBJECT n_object]) = [HOBJECT n_object]',
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = OB_USER_REF_OBJECT pobrefreturn[.CELL = 999999] n_object]',
            'S_bad = S_object_job[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_object) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_native*]',
            '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
        ]
        step(checks, 'S_object_job', 'S_after_object_job')
        checks += [
            '$gc_consumed_decrements(S_object_job, S_after_object_job, [HOBJECT n_object]) = eps',
            '$gc_consumed_decrements(S_bad, S_after_object_job, [HOBJECT n_object]) = [HOBJECT n_object]',
            '~((HOBJECT n_object) <- $gc_physical_nodes(S_after_object_job.GC.BUFFER))',
        ]
        seek(checks, 'S_after_object_job', 'S_cast', 2)
        checks += [
            'S_cast.TODO = (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_native*',
            'S_cast.DESTRUCTION.OPERATIONS = eps',
            '$heap_count(HOBJECT n_object, $task_nodes(OB_USER_OBJECT_CAST pobobjectreturn)) = 1',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_OBJECT_CAST pobobjectreturn)) = 0',
            '$heap_owners($heap_graph(S_cast), HOBJECT n_object) = 1',
            '~((HCELL n_cell) <- S_cast.ALLOCATIONS)',
            '~((HOBJECT n_object) <- $gc_physical_nodes(S_cast.GC.BUFFER))',
            '~$call_task_valid(S_cast, OB_USER_OBJECT_SKIP pobobjectreturn)',
        ]
        seek(checks, 'S_cast', 'S_return', 5)
        checks += [
            'S_return.TODO = (OB_USER_OBJECT_RETURN pobobjectreturn_return poperand_return) :: ptask_native*',
            'pobobjectreturn_return.OBJECT = n_object',
            'pobobjectreturn_return.CELL = (n_cell)',
            'pobobjectreturn_return.RETURNED = (poperand_return)',
            'pobobjectreturn_return.PENDING = eps',
            'poperand_return = KNOWN pvalue_return', '$string_bytes(pvalue_return) = ([72])',
            '$heap_owners($heap_graph(S_return), HOBJECT n_object) = 1',
            '(HOBJECT n_object) <- $gc_physical_nodes(S_return.GC.BUFFER)',
            '$gc_consumed_decrements(S_return, S_return, [HOBJECT n_object]) = [HOBJECT n_object]',
            'poperand_bad = KNOWN (PSTRING_CARRIER (REQUEST_STRING 999999) ([72]))',
            'pobobjectreturn_bad = pobobjectreturn_return[.RETURNED = (poperand_bad)]',
            'S_carrier_bad = S_return[.TODO = (OB_USER_OBJECT_RETURN pobobjectreturn_bad poperand_bad) :: ptask_native*]',
            '~$call_task_valid(S_carrier_bad, OB_USER_OBJECT_RETURN pobobjectreturn_bad poperand_bad)',
        ]
        seek(checks, 'S_return', 'S_destructor', 3)
    else:
        checks += [
            'S.TODO = (OB_USER_OBJECT_SKIP pobobjectreturn) :: ptask_native*',
            'n_object = pobobjectreturn.OBJECT', 'pobobjectreturn.PENDING = (n_pending)',
            'pobobjectreturn.CELL = eps', 'pobobjectreturn.RETURNED = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_object) = 2',
            '$heap_count(HOBJECT n_object, $task_nodes(OB_USER_OBJECT_SKIP pobobjectreturn)) = 2',
            '$heap_count(HOBJECT n_pending, $machine_roots(S)) = 1',
            '~((HOBJECT n_object) <- $gc_physical_nodes(S.GC.BUFFER))',
            '~$call_task_valid(S, OB_USER_OBJECT_CAST pobobjectreturn)',
            '~$call_task_valid(S, OB_USER_OBJECT_SKIP pobobjectreturn[.PENDING = eps])',
        ]
        step(checks, 'S', 'S_guard')
        checks += [
            'S_guard.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_guard) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_guard) :: (OB_USER_OBJECT_RELEASE pobobjectreturn poboutput_guard) :: ptask_native*',
            'pdestructionrelease_guard.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
            'pdestructionoperation_guard.SOURCE = OB_USER_OBJECT_SKIP pobobjectreturn',
            'pdestructionoperation_guard.PENDING = eps',
            '$eager_operation_source_valid(S_guard, pdestructionoperation_guard)',
            '$destructor_release_valid(S_guard, pdestructionrelease_guard)',
        ]
        step(checks, 'S_guard', 'S_after_guard')
        checks += [
            '$heap_owners($heap_graph(S_after_guard), HOBJECT n_object) = 1',
            '(HOBJECT n_object) <- $gc_physical_nodes(S_after_guard.GC.BUFFER)',
            '$gc_consumed_decrements(S_guard, S_after_guard, [HOBJECT n_object]) = [HOBJECT n_object]',
            'pdestructionoperation_bad = pdestructionoperation_guard[.SOURCE = OB_USER_OBJECT_SKIP pobobjectreturn[.PENDING = eps]]',
            'S_bad = S_guard[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_guard) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (OB_USER_OBJECT_RELEASE pobobjectreturn poboutput_guard) :: ptask_native*]',
            '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
        ]
        seek(checks, 'S_after_guard', 'S_release', 4)
        checks += [
            'S_release.TODO = (OB_USER_OBJECT_RELEASE pobobjectreturn poboutput_guard) :: ptask_native*',
            '$string_bytes(poboutput_guard.VALUE) = (eps)',
            '$heap_owners($heap_graph(S_release), HOBJECT n_object) = 1',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_release)) = 1',
            '(HOBJECT n_object) <- $gc_physical_nodes(S_release.GC.BUFFER)',
        ]
        seek(checks, 'S_release', 'S_destructor', 3)
    checks += [
        'S_destructor.CURRENT = (pcallcontext_destructor)',
        '$destructor_context_valid(S_destructor, pcallcontext_destructor)',
        '$destructor_context_call(pcallcontext_destructor, S_destructor.CURRENT, S_destructor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OPERATION = (pdestructionoperation_destructor)',
        'pdestructionoperation_destructor.SOURCE = OB_USER_OBJECT_RELEASE pobobjectreturn_destructor poboutput_destructor',
        'pobobjectreturn_destructor.OBJECT = n_object',
        '$eager_operation_source_valid(S_destructor, pdestructionoperation_destructor)',
        '(HOBJECT n_object) <- $gc_physical_nodes(S_destructor.GC.BUFFER)',
        '$heap_count(HOBJECT n_object, $task_nodes(OB_USER_OBJECT_DONE pobobjectreturn_destructor poboutput_destructor)) = 0',
        '$heap_count(HCELL n_cell, $task_nodes(OB_USER_OBJECT_DONE pobobjectreturn_destructor poboutput_destructor)) = 0' if phase == 0 else '$heap_count(HOBJECT n_pending, $task_nodes(OB_USER_OBJECT_DONE pobobjectreturn_destructor poboutput_destructor)) = 0',
        'S_budget = $drive_steps(S_destructor, 0)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.TODO = S_destructor.TODO', 'S_budget.GC = S_destructor.GC',
        'S_budget.ALLOCATIONS = S_destructor.ALLOCATIONS',
        'S_budget.DESTRUCTION = S_destructor.DESTRUCTION', *runner.valid('S_budget'),
    ]
    seek(checks, 'S_budget[.COMPLETION = NORMAL]', 'S_commit', 6)
    checks += [
        'S_commit.TODO = (OB_USER_OBJECT_COMMIT pobobjectreturn_commit poboutput_commit) :: ptask_native*',
        '~((HOBJECT n_object) <- S_commit.ALLOCATIONS)',
        '~((HOBJECT n_object) <- $gc_physical_nodes(S_commit.GC.BUFFER))',
        '$heap_count(HOBJECT n_object, $machine_roots(S_commit)) = 0',
        'S_commit.RESULT = KNOWN PNULL',
        'S_final = $drive_steps(S_commit, 4096)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps', 'S_final.OUTPUTBUFFERS = eps',
        '$dp_output(S_final.EVENTS) = ' + runner.bytes_expr(CASES[name][1]), *runner.valid('S_final'),
    ]
    return checks


def notice_assertions(name, fixture, directory, path):
    framed = name.endswith('-framed')
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET']
    seek(checks, 'S_initial', 'S', 7 if framed else 8)
    if framed:
        checks += [
            'S.TODO = (OB_USER_OBJECT_PENDING pobobjectreturn pdestructionframe) :: (STRINGIFY_RESULT n_object porigin z) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*',
            'pdestructionframe.VALUE = REFERENCE n_cell', 'pdestructionframe.PENDING = (n_pending)',
            '$call_task_valid(S, OB_USER_OBJECT_PENDING pobobjectreturn pdestructionframe)',
            '~$call_task_valid(S, OB_USER_OBJECT_PENDING pobobjectreturn pdestructionframe[.VALUE = KNOWN (PSTRING ([88]))])',
            '~$call_task_valid(S, OB_USER_OBJECT_PENDING pobobjectreturn pdestructionframe[.PENDING = eps])',
        ]
    else:
        checks += [
            'S.TODO = (THROW_SEARCH n_pending) :: (OB_USER_OBJECT_NOTICE pobobjectreturn n_cell n_pending) :: ptask_native*',
            'n_object = pobobjectreturn.OBJECT',
            '$call_task_valid(S, OB_USER_OBJECT_NOTICE pobobjectreturn n_cell n_pending)',
            '$heap_count(HOBJECT n_pending, $task_nodes(OB_USER_OBJECT_NOTICE pobobjectreturn n_cell n_pending)) = 0',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_OBJECT_NOTICE pobobjectreturn n_cell n_pending)) = 1',
            '~$call_task_valid(S, OB_USER_OBJECT_NOTICE pobobjectreturn n_cell 999999)',
            '~$call_task_valid(S, OB_USER_OBJECT_NOTICE pobobjectreturn 999999 n_pending)',
        ]
    checks += [
        'pobobjectreturn.OBJECT = n_object', 'pobobjectreturn.PENDING = eps',
        'S.STORE[n_cell] = DEFINED pvalue_return', '$string_bytes(pvalue_return) = ([72])',
        '$heap_owners($heap_graph(S), HOBJECT n_object) = 1',
        '$heap_count(HCELL n_cell, $machine_roots(S)) = 1',
        '$heap_count(HOBJECT n_pending, $machine_roots(S)) = 1',
        '$ob_object_current(S, pobobjectreturn)',
    ]
    step(checks, 'S', 'S_return')
    checks += [
        'S_return.TODO = (OB_USER_OBJECT_RETURN pobobjectreturn_return (REFERENCE n_cell)) :: ptask_native*',
        'pobobjectreturn_return.RETURNED = (REFERENCE n_cell)',
        'pobobjectreturn_return.PENDING = (n_pending)',
        '$heap_owners($heap_graph(S_return), HOBJECT n_object) = 1',
        '$heap_count(HCELL n_cell, $machine_roots(S_return)) = 1',
        '$heap_count(HOBJECT n_pending, $machine_roots(S_return)) = 1',
        '~$call_task_valid(S_return, OB_USER_OBJECT_RETURN pobobjectreturn_return (REFERENCE 999999))',
    ]
    step(checks, 'S_return', 'S_cell_job')
    if framed:
        checks += [
            'S_cell_job.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_OBJECT_RELEASE pobobjectreturn_return poboutput) :: ptask_native*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
            'pdestructionoperation.SOURCE = OB_USER_OBJECT_RETURN pobobjectreturn_return (REFERENCE n_cell)',
            'pdestructionoperation.COMPLETION = NORMAL', 'pdestructionoperation.PENDING = eps',
            '$eager_operation_source_valid(S_cell_job, pdestructionoperation)',
            '$destructor_release_valid(S_cell_job, pdestructionrelease)',
        ]
        step(checks, 'S_cell_job', 'S_after_cell')
        checks += [
            '~((HCELL n_cell) <- S_after_cell.ALLOCATIONS)',
            '$eager_operation_source_valid(S_after_cell, pdestructionoperation)',
            'pobobjectreturn_bad = pobobjectreturn_return[.RETURNED = (REFERENCE 999999)]',
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = OB_USER_OBJECT_RETURN pobobjectreturn_bad (REFERENCE 999999)]',
            'S_bad = S_after_cell[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]][.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (OB_USER_OBJECT_RELEASE pobobjectreturn_return poboutput) :: ptask_native*]',
            '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
        ]
        release_from = 'S_after_cell'
    else:
        checks += ['~((HCELL n_cell) <- S_cell_job.ALLOCATIONS)']
        release_from = 'S_cell_job'
    seek(checks, release_from, 'S_release', 4)
    checks += [
        'S_release.TODO = (OB_USER_OBJECT_RELEASE pobobjectreturn_return poboutput) :: ptask_native*',
        '$string_bytes(poboutput.VALUE) = ([72])', '~poboutput.FAILED',
        '$heap_count(HCELL n_cell, $task_nodes(OB_USER_OBJECT_RELEASE pobobjectreturn_return poboutput)) = 0',
        '$heap_count(HOBJECT n_pending, $machine_roots(S_release)) = 1',
        'S_budget = $drive_steps(S_release, 0)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.TODO = S_release.TODO', 'S_budget.ALLOCATIONS = S_release.ALLOCATIONS',
        'S_budget.DESTRUCTION = S_release.DESTRUCTION', *runner.valid('S_budget'),
    ]
    seek(checks, 'S_budget[.COMPLETION = NORMAL]', 'S_commit', 6)
    checks += [
        'S_commit.TODO = (OB_USER_OBJECT_COMMIT pobobjectreturn_return poboutput) :: ptask_native*',
        '~((HCELL n_cell) <- S_commit.ALLOCATIONS)', '~((HOBJECT n_object) <- S_commit.ALLOCATIONS)',
        '$heap_count(HCELL n_cell, $machine_roots(S_commit)) = 0',
        '$heap_count(HOBJECT n_object, $machine_roots(S_commit)) = 0',
        '$heap_count(HOBJECT n_pending, $machine_roots(S_commit)) = 1',
        'S_final = $drive_steps(S_commit, 4096)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
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
