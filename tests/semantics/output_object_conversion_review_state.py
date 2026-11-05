#!/usr/bin/env python3
"""Reached cast guards, late returned cells and output-specific release authority."""
import os

import output_deprecation_warning_review_state as runner
import output_object_conversion_review_sources as sources

ROOT = sources.ROOT
CASES = {name: sources.CASES[name] for name in
         ('raw-invokable-owner-after-route', 'reference-string-late-cleanup-throw',
          'unique-reference-object-gc-transfer')}
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ob_object_context(S, pcallcontext) = (pobobjectreturn)
def $dp_phase(S, 1) = true -- if S.TODO = (OB_USER_OBJECT_COMMIT pobobjectreturn poboutput) :: ptask_tail*
def $dp_phase(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = eps
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if pdestructionframe.VALUE = REFERENCE n
def $dp_phase(S, 3) = true -- if S.TODO = (OB_USER_OBJECT_PENDING pobobjectreturn pdestructionframe) :: ptask_tail*
def $dp_phase(S, 4) = true -- if S.TODO = (OB_USER_REF_OBJECT pobrefreturn n) :: ptask_tail*
def $dp_phase(S, 5) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = OB_USER_OBJECT_RETURN pobobjectreturn (REFERENCE n)
def $dp_phase(S, 6) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OB_USER_OBJECT_NORMAL pobobjectreturn pdestructionframe_success) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n)]
  -- if n = pobobjectreturn.OBJECT
def $dp_phase(S, n) = false -- otherwise
dec $or_normal(ptask*) : pobobjectreturn?
dec $or_normal_task(ptask) : bool
def $or_normal_task(OB_USER_OBJECT_NORMAL pobobjectreturn pdestructionframe) = true
def $or_normal_task(ptask) = false -- otherwise
def $or_normal((OB_USER_OBJECT_NORMAL pobobjectreturn pdestructionframe) :: ptask_tail*) = (pobobjectreturn)
def $or_normal(ptask :: ptask_tail*) = $or_normal(ptask_tail*) -- if ~$or_normal_task(ptask)
def $or_normal(eps) = eps
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_object_conversion_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_sources.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.common.sha(ROOT / name)
    return inputs


def seek(before, after, phase, fuel=1024):
    return [after + '_found = $dp_seek(' + before + ', ' + str(phase) + ', ' + str(fuel) + ')',
            after + r'_found.COMPLETION = NORMAL \/ ' + after + '_found.COMPLETION = BUDGET',
            after + ' = ' + after + '_found[.COMPLETION = NORMAL]', *runner.valid(after)]


def assertions(name, fixture, directory, path):
    phase = 0 if name == 'raw-invokable-owner-after-route' else 2 if name == 'reference-string-late-cleanup-throw' else 4
    checks = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_initial', 'S_reached', phase, 2048),
        '$dp_phase(S_reached, ' + str(phase) + ')',
    ]
    if phase == 0:
        checks += [
            'S_reached.CURRENT = (pcallcontext)',
            '$ob_object_context(S_reached, pcallcontext) = (pobobjectreturn)',
            'n_object = pobobjectreturn.OBJECT', 'pobobjectreturn.INVOKE.BUFFER.HANDLER = (poutputhandler)',
            'poutputhandler.ZOH = POBJECT n_object', 'pobobjectreturn.RETURNED = eps',
            '$heap_count(HOBJECT n_object, $machine_roots(S_reached)) = 3',
            '$heap_count(HOBJECT n_object, $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn)) = 0',
            '$reference_callback_used(S_reached, pcallcontext) = (true)',
            *seek('S_reached', 'S_commit', 1),
            'S_commit.TODO = (OB_USER_OBJECT_COMMIT pobobjectreturn_commit poboutput) :: ptask_native*',
            'pobobjectreturn_commit.OBJECT = n_object', 'pobobjectreturn_commit.PENDING = eps',
            'pobobjectreturn_commit[.RETURNED = eps] = pobobjectreturn',
            '$string_bytes(poboutput.VALUE) = ([72])',
            '$heap_count(HOBJECT n_object, $machine_roots(S_commit)) = 1',
            '$heap_count(HOBJECT n_object, $task_nodes(OB_USER_OBJECT_COMMIT pobobjectreturn_commit poboutput)) = 0',
            '$dp_output(S_commit.EVENTS) = ([80])',
            'poboutput_bad = $ob_user_output(S_commit, PSTRING ([90]))',
            '$ob_user_output_valid(S_commit, poboutput_bad)',
            '~$call_task_valid(S_commit, OB_USER_OBJECT_COMMIT pobobjectreturn_commit poboutput_bad)',
            'S_resume = S_commit',
        ]
    elif phase == 2:
        checks += [
            'S_reached.CURRENT = (pcallcontext)',
            '$destructor_context_call(pcallcontext, S_reached.CURRENT, S_reached.FRAMES) = (pdestructorcall)',
            'pdestructorcall.FRAME = (pdestructionframe)', 'pdestructionframe.VALUE = REFERENCE n_cell',
            'S_reached.STORE[n_cell] = DEFINED pvalue_before', '$string_bytes(pvalue_before) = ([72])',
            '$heap_count(HCELL n_cell, $machine_roots(S_reached)) = 2',
            'S_caller = $destructor_boundary_scope(S_reached, pdestructorcall, S_reached.FRAMES)',
            '$or_normal(S_caller.TODO) = (pobobjectreturn)',
            '$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_reached)) = 2',
            '$call_task_valid(S_caller, OB_USER_OBJECT_NORMAL pobobjectreturn pdestructionframe)',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_OBJECT_NORMAL pobobjectreturn pdestructionframe)) = 0',
            '$heap_count(HCELL n_cell, $task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe)) = 1',
            'S_caller.RESULT = KNOWN PNULL',
            'S_unowned = S_caller[.TODO = (OB_USER_OBJECT_NORMAL pobobjectreturn pdestructionframe) :: (STRINGIFY_RESULT pobobjectreturn.OBJECT $ob_call_site(pobobjectreturn.INVOKE.CALL) $ob_call_line(pobobjectreturn.INVOKE.CALL)) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: pobobjectreturn.TAIL]',
            '$ob_object_normal_certificate(S_unowned, pobobjectreturn, pdestructionframe)',
            '~$call_task_valid(S_unowned, OB_USER_OBJECT_NORMAL pobobjectreturn pdestructionframe)',
            *seek('S_reached', 'S_pending', 3),
            'S_pending.TODO = (OB_USER_OBJECT_PENDING pobobjectreturn pdestructionframe_pending) :: ptask_pending*',
            'pdestructionframe_pending.VALUE = REFERENCE n_cell', 'pdestructionframe_pending.PENDING = (n_pending)',
            '$throwable_field(S_pending, n_pending, "trace") = PARRAY n_trace',
            '$trace_graph_valid(S_pending, n_trace)',
            'S_pending.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame0)), ENTRY (KINT 1) (DIRECT (PARRAY n_frame1))]',
            '$string_bytes($trace_array_field(S_pending, n_frame0, $ptascii("function"))) = ($ptascii("__destruct"))',
            '$entry_lookup(S_pending.ARRAYS[n_frame0].ITEMS, KSTRING $ptascii("file")) = eps',
            '$entry_lookup(S_pending.ARRAYS[n_frame0].ITEMS, KSTRING $ptascii("line")) = eps',
            '$string_bytes($trace_array_field(S_pending, n_frame1, $ptascii("function"))) = ($ptascii("ob_get_flush"))',
            '$trace_array_field(S_pending, n_frame1, $ptascii("line")) = PINT 1',
            '$string_bytes($trace_array_field(S_pending, n_frame1, $ptascii("file"))) = (' + runner.bytes_expr(os.fsencode(path)) + ')',
            'S_pending.STORE[n_cell] = DEFINED pvalue_after', '$string_bytes(pvalue_after) = ([74])',
            '$heap_count(HCELL n_cell, $machine_roots(S_pending)) = 2',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_pending)) = 1',
            '$ob_object_normal_operand(S_pending, KNOWN (PSTRING ([90])))',
            '$string_bytes(PSTRING_CARRIER (REQUEST_STRING 999999) ([90])) = ([90])',
            '~$ob_object_normal_operand(S_pending, KNOWN (PSTRING_CARRIER (REQUEST_STRING 999999) ([90])))',
            '~$call_task_valid(S_pending, OB_USER_OBJECT_PENDING pobobjectreturn pdestructionframe_pending[.VALUE = KNOWN (PSTRING ([90]))])',
            'S_budget = $drive_steps(S_pending, 0)', 'S_budget.COMPLETION = BUDGET',
            'S_budget.TODO = S_pending.TODO', *runner.valid('S_budget'),
            *seek('S_budget', 'S_release', 5, 64),
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_OBJECT_RELEASE pobobjectreturn_returned poboutput) :: ptask_native*',
            'pdestructionoperation.SOURCE = OB_USER_OBJECT_RETURN pobobjectreturn_returned (REFERENCE n_cell)',
            'pobobjectreturn_returned = pobobjectreturn[.RETURNED = (REFERENCE n_cell)][.PENDING = (n_pending)]',
            'pobobjectreturn_returned.RETURNED = (REFERENCE n_cell)', 'pobobjectreturn_returned.PENDING = (n_pending)',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
            '$string_bytes(poboutput.VALUE) = ([74])',
            '$heap_count(HCELL n_cell, $task_nodes(OB_USER_OBJECT_RELEASE pobobjectreturn_returned poboutput)) = 0',
            '$eager_operation_source_guard(S_release, pdestructionoperation)',
            'S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pobobjectreturn_bad = pobobjectreturn_returned[.RETURNED = (REFERENCE 999999)]',
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = OB_USER_OBJECT_RETURN pobobjectreturn_bad (REFERENCE 999999)]',
            'S_bad = S_release[.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: pdestructionoperation_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (OB_USER_OBJECT_RELEASE pobobjectreturn_returned poboutput) :: ptask_native*]',
            '~$eager_operation_source_guard(S_bad, pdestructionoperation_bad)',
            *seek('S_release', 'S_commit', 1),
            'S_commit.TODO = (OB_USER_OBJECT_COMMIT pobobjectreturn_commit poboutput) :: ptask_native*',
            'pobobjectreturn_commit.RETURNED = (REFERENCE n_cell)', 'pobobjectreturn_commit.PENDING = (n_pending)',
            '$heap_count(HCELL n_cell, $machine_roots(S_commit)) = 1',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_commit)) = 1',
            '~((HOBJECT pobobjectreturn_returned.OBJECT) <- S_commit.ALLOCATIONS)',
            'S_resume = S_commit',
        ]
    else:
        checks += [
            'S_reached.TODO = (OB_USER_REF_OBJECT pobrefreturn n_object) :: ptask_native*',
            'n_cell = pobrefreturn.CELL', 'S_reached.STORE[n_cell] = DEFINED (POBJECT n_object)',
            '$heap_count(HCELL n_cell, $machine_roots(S_reached)) = 1',
            '$heap_owners($heap_graph(S_reached), HOBJECT n_object) = 1',
            'S_transfer_found = $drive_steps(S_reached, 1)',
            r'S_transfer_found.COMPLETION = NORMAL \/ S_transfer_found.COMPLETION = BUDGET',
            'S_transfer = S_transfer_found[.COMPLETION = NORMAL]', *runner.valid('S_transfer'),
            'S_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cell) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_ref) :: (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_native*',
            'pdestructionrelease_cell.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
            'pdestructionoperation_ref.SOURCE = OB_USER_REF_OBJECT pobrefreturn n_object',
            'pobobjectreturn = $ob_object_from_ref(pobrefreturn, n_object)',
            'pobobjectreturn.CELL = (n_cell)', 'pobobjectreturn.RETURNED = eps',
            '$eager_operation_source_guard(S_transfer, pdestructionoperation_ref)',
            'S_transfer.DESTRUCTION.OPERATIONS = pdestructionoperation_ref :: pdestructionoperation_tail*',
            'pobrefreturn_bad = pobrefreturn[.CELL = 999999]',
            'pdestructionoperation_bad = pdestructionoperation_ref[.SOURCE = OB_USER_REF_OBJECT pobrefreturn_bad n_object]',
            'S_bad = S_transfer[.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: pdestructionoperation_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cell) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_native*]',
            '~$eager_operation_source_guard(S_bad, pdestructionoperation_bad)',
            'S_cell_found = $drive_steps(S_transfer, 1)',
            r'S_cell_found.COMPLETION = NORMAL \/ S_cell_found.COMPLETION = BUDGET',
            'S_cell = S_cell_found[.COMPLETION = NORMAL]', *runner.valid('S_cell'),
            'S_cell.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_object) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_ref) :: (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_native*',
            'pdestructionrelease_object.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
            '~((HCELL n_cell) <- S_cell.ALLOCATIONS)',
            '$gc_consumed_decrements(S_transfer, S_cell, [HCELL n_cell, HOBJECT n_object]) = [HOBJECT n_object]',
            '$gc_consumed_decrements(S_bad, S_cell, [HCELL n_cell, HOBJECT n_object]) = [HCELL n_cell, HOBJECT n_object]',
            'S_cast_found = $drive_steps(S_cell, 1)',
            r'S_cast_found.COMPLETION = NORMAL \/ S_cast_found.COMPLETION = BUDGET',
            'S_cast = S_cast_found[.COMPLETION = NORMAL]', *runner.valid('S_cast'),
            '$gc_consumed_decrements(S_cell, S_cast, [HCELL n_cell, HOBJECT n_object]) = [HCELL n_cell]',
            'S_cast.GC.BUFFER = S_reached.GC.BUFFER',
            *seek('S_cast', 'S_guard', 6),
            'S_guard.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_guard) :: ptask_guard*',
            'pdestructionrelease_guard.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
            '~((HOBJECT n_object) <- $gc_physical_nodes(S_guard.GC.BUFFER))',
            '$heap_count(HOBJECT n_object, $machine_roots(S_guard)) = 2',
            'S_guard_drop_found = $drive_steps(S_guard, 1)',
            r'S_guard_drop_found.COMPLETION = NORMAL \/ S_guard_drop_found.COMPLETION = BUDGET',
            'S_guard_drop = S_guard_drop_found[.COMPLETION = NORMAL]', *runner.valid('S_guard_drop'),
            '$gc_consumed_decrements(S_guard, S_guard_drop, [HOBJECT n_object]) = [HOBJECT n_object]',
            '(HOBJECT n_object) <- $gc_physical_nodes(S_guard_drop.GC.BUFFER)',
            '$heap_count(HOBJECT n_object, $machine_roots(S_guard_drop)) = 1',
            'S_resume = S_guard_drop',
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
