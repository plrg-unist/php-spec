#!/usr/bin/env python3
"""Actual raw array credit, COW headers, repeated Child edges and GC/STORE."""
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc71_peer_repeated_array_cow.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
    '(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output* '
    '-- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput '
    '-- if S.STORE[penumqueryoutput.CELL] = DEFINED (PARRAY n_original) '
    '-- if S.ARRAYS[n_original].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child)), '
    'ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (DIRECT (POBJECT n_child))] '
    '-- if $object_name(S, n_child) = $ptascii("GC71ChildPeer")')

DECLARATIONS = r'''syntax pgc71stage = COW | WRITE29 | WRITE31 | TRACE | CHILD
dec $gc71_at(pstate, pgc71stage, nat, nat) : bool
def $gc71_at(S, COW, n_original, n_child) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 23)
def $gc71_at(S, WRITE29, n_original, n_child) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 29)
def $gc71_at(S, WRITE31, n_original, n_child) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 31)
def $gc71_at(S, TRACE, n_original, n_child) = true
  -- if S.TODO = (GC_TRACE pgccall) :: ptask_tail*
def $gc71_at(S, CHILD, n_original, n_child) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.STORE /\ pdestructorcall.OBJECT = n_child
def $gc71_at(S, pgc71stage, n_original, n_child) = false -- otherwise
dec $gc71_seek(pstate, pgc71stage, nat, nat, nat) : pstate
def $gc71_seek(S, pgc71stage, n_original, n_child, n) = S
  -- if $gc71_at(S, pgc71stage, n_original, n_child)
def $gc71_seek(S, pgc71stage, n_original, n_child, n) = $gc71_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc71stage, n_original, n_child, $nabs($(n - 1)))
  -- if ~$gc71_at(S, pgc71stage, n_original, n_child) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc71_seek(S, pgc71stage, n_original, n_child, 0) = S
  -- if ~$gc71_at(S, pgc71stage, n_original, n_child)
def $gc71_seek(S, pgc71stage, n_original, n_child, n) = S
  -- if ~$gc71_at(S, pgc71stage, n_original, n_child)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc71_op_view(pstate, pdestructionoperation) : pstate
def $gc71_op_view(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc71_output(pevent*) : preqbytes
def $gc71_output(eps) = eps
def $gc71_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc71_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def seek(before, after, stage):
    return [f'{after}_paused = $gc71_seek({before}, {stage}, n_original, n_child, 4000)',
            f'{after}_paused.COMPLETION = BUDGET',
            f'{after} = {after}_paused[.COMPLETION = NORMAL]']


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$native_excess_valid({state})',
            f'$destruction_state_valid({state})',
            f'$call_descriptors_valid({state})']


def counts(state, physical, native, child):
    return [f'$heap_owners($heap_graph({state}), HARRAY n_original) = {physical}',
            f'$native_rc({state}, HARRAY n_original) = {native}',
            f'$heap_owners($heap_graph({state}), HOBJECT n_child) = {child}',
            f'$native_rc({state}, HOBJECT n_child) = {child}',
            f'$heap_count(HOBJECT n_child, {state}.NATIVEEXCESS) = 0']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


def reject_op(name, patch):
    operation = f'pdestructionoperation_{name}'
    state = f'S_{name}'
    return [f'{operation} = pdestructionoperation_drop{patch}',
            f'{state} = $gc71_op_view(S_drop, {operation})',
            f'$heap_graph({state}) = $heap_graph(S_drop)',
            f'~$gc_operation_metadata_valid({state}, {operation})']


CHECKS = [
    'S.NATIVEEXCESS = eps', '$destructor_operation_valid(S, pdestructionoperation)',
    '$lookup(S.ENV, $ptascii("kept")) = (n_kept)',
    'n_kept =/= penumqueryoutput.CELL', '(HCELL n_kept) <- S.ALLOCATIONS',
    'S.STORE[n_kept] = DEFINED (PARRAY n_original)',
    '$lookup(S.ENV, $ptascii("watch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    'pentry_original* = S.ARRAYS[n_original].ITEMS',
    '$node_children(S, HARRAY n_original) = [HOBJECT n_child, HOBJECT n_child]',
    '$node_children(S, HOBJECT n_child) = eps',
    '~$array_immutable(S, n_original)', '~$gc_proxy(S, n_original)',
    *counts('S', 2, 2, 2), *valid('S'),
    'PhpStep: S ~> S_raw',
    'S_raw.NATIVEEXCESS = [HARRAY n_original]',
    'S_raw.TODO = ptask_after_output*',
    'S_raw.DESTRUCTION.OPERATIONS = eps', 'S_raw.DESTRUCTION.RELEASES = eps',
    'S_raw.ARRAYS = S.ARRAYS', 'S_raw.OBJECTPROPS = S.OBJECTPROPS',
    'S_raw.ALLOCATIONS = S.ALLOCATIONS', 'S_raw.EVENTS = S.EVENTS',
    'S_raw.STORE[penumqueryoutput.CELL] = DEFINED (PSTRING penumqueryoutput.NAME)',
    *counts('S_raw', 1, 2, 2), *valid('S_raw'),
    '$native_decrements(S, S_raw, [HARRAY n_original]) = eps',
    '$heap_count(HARRAY n_original, $eager_slots(S, S_raw)) = 0',
    '$weakref_get(S_raw, n_watch) = POBJECT n_child',
    # Reuse the genuine sent-CELL receipt to challenge only new array admission.
    'S_emit = S_raw[.STORE = S.STORE][.NATIVEEXCESS = eps][.TODO = (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output*]',
    '$enum_is_callable_array_excess_ready(S_emit, penumqueryoutput)',
    '~$enum_is_callable_output_excess_ready(S_emit, penumqueryoutput)',
    '~$enum_is_callable_output_ready(S_emit, penumqueryoutput)',
    '$enum_is_callable_output_commit(S_emit, penumqueryoutput) = S_raw',
    '$enum_is_callable_array_excess_cv(S_emit, n_original, penumqueryoutput.CELL, $ptascii("kept"))',
    '~$enum_is_callable_array_excess_cv(S_emit, n_original, penumqueryoutput.CELL, $ptascii("name"))',
    'S_no_cv = S_emit[.CVS = eps]',
    '$heap_graph(S_no_cv) = $heap_graph(S_emit)',
    '~$enum_is_callable_array_excess_ready(S_no_cv, penumqueryoutput)',
    'S_old_unit = S_emit[.NATIVEEXCESS = [HARRAY n_original]]',
    '$heap_graph(S_old_unit) = $heap_graph(S_emit)',
    '~$enum_is_callable_array_excess_ready(S_old_unit, penumqueryoutput)',
    'S_child_unit = S_emit[.NATIVEEXCESS = [HOBJECT n_child]]',
    '$heap_graph(S_child_unit) = $heap_graph(S_emit)',
    '~$enum_is_callable_array_excess_ready(S_child_unit, penumqueryoutput)',
    'S_called = S_emit[.DESTRUCTION.CALLED = n_child :: S_emit.DESTRUCTION.CALLED]',
    '~$enum_is_callable_array_excess_ready(S_called, penumqueryoutput)',
    '~$enum_is_callable_array_excess_entries(S_emit, [ENTRY (KINT 0) (DIRECT (PARRAY n_original))])',
    '~$enum_is_callable_array_excess_entries(S_emit, [ENTRY (KINT 0) (ALIAS n_kept)])',
    '~$enum_is_callable_array_excess_entries(S_emit, [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 0) (DIRECT (PINT 23))])',
    *budget('S'),
    'S_after = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    *seek('S_after', 'S_cow', 'COW'),
    'S_cow.STORE[n_kept] = DEFINED (PARRAY n_original)',
    'S_cow.ARRAYS[n_original].ITEMS = pentry_original*',
    'S_cow.TODO = (ASSIGN_ARRAY pbase_cow z_cow false) :: ptask_cow_tail*',
    *counts('S_cow', 1, 2, 2), *valid('S_cow'),
    'n_copy = |S_cow.ARRAYS|',
    'S_probe = $separate_location_array(S_cow, n_original)',
    'S_probe.RESULT = KNOWN (PARRAY n_copy)',
    'S_probe.ARRAYS[n_copy].ITEMS = pentry_original*',
    'S_probe.ARRAYS[n_original] = S_cow.ARRAYS[n_original]',
    'S_probe.NATIVEEXCESS = [HARRAY n_original]',
    '$heap_count(HARRAY n_copy, S_probe.NATIVEEXCESS) = 0',
    *counts('S_probe', 1, 2, 4),
    'PhpStep: S_cow ~> S_copied',
    'S_copied.STORE[n_kept] = DEFINED (PARRAY n_copy)',
    'S_copied.ARRAYS[n_original] = S_cow.ARRAYS[n_original]',
    'S_copied.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child)), ENTRY (KINT 1) (DIRECT (PINT 23)), ENTRY (KINT 2) (DIRECT (POBJECT n_child))]',
    'S_copied.NATIVEEXCESS = [HARRAY n_original]',
    '$heap_count(HARRAY n_copy, S_copied.NATIVEEXCESS) = 0',
    '$heap_owners($heap_graph(S_copied), HARRAY n_copy) = 1',
    *counts('S_copied', 0, 1, 4), *budget('S_cow'),
    '$gc_operation_temporary_extra(S_cow, S_copied, ASSIGN_ARRAY pbase_cow z_cow false, [HARRAY n_original]) = [{OPERAND KNOWN (PARRAY n_original), PENDING true}]',
    '$gc_operation_temporary_extra(S_cow, S_copied, ASSIGN_ARRAY pbase_cow z_cow false, [HOBJECT n_child]) = eps',
    '$gc_operation_temporary_extra(S_cow, S_copied, ASSIGN_ARRAY pbase_cow z_cow false, [HARRAY n_original, HOBJECT n_child]) = eps',
    'S_cow_no_unit = S_cow[.NATIVEEXCESS = eps]',
    'S_copied_no_unit = S_copied[.NATIVEEXCESS = eps]',
    '$gc_operation_temporary_extra(S_cow_no_unit, S_copied_no_unit, ASSIGN_ARRAY pbase_cow z_cow false, [HARRAY n_original]) = eps',
    # Driver observation retains the real old-header decrement until release.
    'S_copy_next = $drive_steps(S_cow, 1)[.COMPLETION = NORMAL]',
    'S_drop = S_copy_next',
    'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: ptask_drop_tail*',
    '$destruction_job_nodes(pdestructionrelease_drop.JOBS) = [HARRAY n_original]',
    *counts('S_drop', 1, 2, 4), *valid('S_drop'),
    'pdestructionrelease_drop.JOBS = [DESTRUCTION_TEMP (HARRAY n_original)]',
    'S_drop.DESTRUCTION.OPERATIONS = [pdestructionoperation_drop]',
    'pdestructionoperation_drop.NOGC = eps',
    'pdestructionoperation_drop.NOGCEXTRA = [pgctemporary_drop]',
    'pgctemporary_drop.OPERAND = KNOWN (PARRAY n_original)',
    'pgctemporary_drop.PENDING',
    '$gc_operation_metadata_valid(S_drop, pdestructionoperation_drop)',
    '$gc_release_metadata_valid(S_drop, pdestructionrelease_drop)',
    '$gc_operation_jobs(pdestructionoperation_drop, [HARRAY n_original, HOBJECT n_child]) = [DESTRUCTION_TEMP (HARRAY n_original), DESTRUCTION_VALUE (HOBJECT n_child)]',
    *reject_op('bad_source', '[.SOURCE = DISCARD]'),
    *reject_op('bad_origin', '[.ORIGIN = eps]'),
    *reject_op('bad_cell', '[.CELL = penumqueryoutput.CELL]'),
    *reject_op('bad_key', '[.KEY = KINT 0]'),
    *reject_op('bad_location', '[.LOCATION = ELEMENT n_original (KINT 1)]'),
    *reject_op('bad_target', '[.NOGCEXTRA = [pgctemporary_drop[.OPERAND = KNOWN (PARRAY n_copy)]]]'),
    *reject_op('early_consumed', '[.NOGCEXTRA = [pgctemporary_drop[.PENDING = false]]]'),
    *reject_op('duplicate_receipt', '[.NOGCEXTRA = [pgctemporary_drop, pgctemporary_drop]]'),
    'S_no_old_unit = S_drop[.NATIVEEXCESS = eps]',
    '$heap_graph(S_no_old_unit) = $heap_graph(S_drop)',
    '~$gc_operation_metadata_valid(S_no_old_unit, pdestructionoperation_drop)',
    'S_new_unit = S_drop[.NATIVEEXCESS = [HARRAY n_original, HARRAY n_copy]]',
    '$heap_graph(S_new_unit) = $heap_graph(S_drop)',
    '~$gc_operation_metadata_valid(S_new_unit, pdestructionoperation_drop)',
    'S_wrong_row = S_drop[.ARRAYS = $array_replace(S_drop.ARRAYS, n_copy, $array_insert(S_drop.ARRAYS[n_copy], KINT 1, DIRECT (PINT 24)))]',
    '$heap_graph(S_wrong_row) = $heap_graph(S_drop)',
    '~$gc_operation_metadata_valid(S_wrong_row, pdestructionoperation_drop)',
    'pdestructionrelease_value = pdestructionrelease_drop[.JOBS = [DESTRUCTION_VALUE (HARRAY n_original)]]',
    'S_value = S_drop[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: ptask_drop_tail*][.DESTRUCTION.RELEASES = [pdestructionrelease_value]]',
    '$heap_graph(S_value) = $heap_graph(S_drop)',
    '~$gc_operation_metadata_valid(S_value, pdestructionoperation_drop)',
    '~$gc_release_metadata_valid(S_value, pdestructionrelease_value)',
    'PhpStep: S_drop ~> S_dropped',
    'S_dropped.ARRAYS = S_drop.ARRAYS',
    'S_dropped.NATIVEEXCESS = [HARRAY n_original]',
    *counts('S_dropped', 0, 1, 4),
    'S_dropped.DESTRUCTION.OPERATIONS = [pdestructionoperation_consumed]',
    'pdestructionoperation_consumed = pdestructionoperation_drop[.NOGCEXTRA = [pgctemporary_drop[.PENDING = false]]]',
    '$gc_operation_metadata_valid(S_dropped, pdestructionoperation_consumed)',
    # Raw PhpStep precedes the driver's count/GC observer.
    'S_dropped.GC.BUFFER = S_drop.GC.BUFFER',
    'S_drop_next = $drive_steps(S_drop, 1)[.COMPLETION = NORMAL]',
    *counts('S_drop_next', 0, 1, 4), *valid('S_drop_next'),
    'S_drop_next.DESTRUCTION.OPERATIONS = [pdestructionoperation_consumed]',
    *budget('S_drop'),
    # SEPARATE_ARRAY uses GC_TRY_DELREF, without a possible-root visit. Also
    # remove any existing membership through the canonical buffer helper so a
    # duplicate visit cannot be hidden by a previously buffered old header.
    'S_drop_next.GC.BUFFER = S_drop.GC.BUFFER',
    'S_drop_clear = S_drop[.GC = $gc_buffer_remove(S_drop.GC, HARRAY n_original)]',
    '$heap_graph(S_drop_clear) = $heap_graph(S_drop)',
    '$gc_state_valid(S_drop_clear)',
    '~((HARRAY n_original) <- $gc_nodes(S_drop_clear.GC.BUFFER))',
    'S_drop_clear_next = $drive_steps(S_drop_clear, 1)[.COMPLETION = NORMAL]',
    'S_drop_clear_next.GC.BUFFER = S_drop_clear.GC.BUFFER',
    *seek('S_drop_next', 'S_write29', 'WRITE29'),
    *counts('S_write29', 0, 1, 4),
    'PhpStep: S_write29 ~> S_written29',
    'S_written29.ARRAYS[n_original].ITEMS = pentry_original*',
    'S_written29.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 29)), ENTRY (KINT 1) (DIRECT (PINT 23)), ENTRY (KINT 2) (DIRECT (POBJECT n_child))]',
    *counts('S_written29', 0, 1, 3),
    'S_write29_next = $drive_steps(S_write29, 1)[.COMPLETION = NORMAL]',
    *seek('S_write29_next', 'S_write31', 'WRITE31'),
    *counts('S_write31', 0, 1, 3),
    'PhpStep: S_write31 ~> S_written31',
    'S_written31.ARRAYS[n_original].ITEMS = pentry_original*',
    'S_written31.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 29)), ENTRY (KINT 1) (DIRECT (PINT 23)), ENTRY (KINT 2) (DIRECT (PINT 31))]',
    *counts('S_written31', 0, 1, 2),
    'S_write31_next = $drive_steps(S_write31, 1)[.COMPLETION = NORMAL]',
    *seek('S_write31_next', 'S_trace', 'TRACE'),
    'S_trace.TODO = (GC_TRACE pgccall) :: ptask_trace_tail*',
    'S_trace.NATIVEEXCESS = [HARRAY n_original]',
    'S_trace.ARRAYS[n_original].ITEMS = pentry_original*',
    '~((HARRAY n_copy) <- S_trace.ALLOCATIONS)',
    *counts('S_trace', 0, 1, 2), *valid('S_trace'),
    'H_trace = $gc_graph(S_trace)',
    '$heap_count(HARRAY n_original, H_trace.ROOTS) = 0',
    '$heap_count(HOBJECT n_child, H_trace.ROOTS) = 0',
    '$gc_native_white(H_trace, S_trace.NATIVEEXCESS, $gc_eligible_nodes(S_trace.GC.BUFFER)) = eps',
    'pgcplan = $gc_plan(S_trace, pgccall)',
    'pgcplan.EXCESS = [HARRAY n_original]', 'pgcplan.GRAPH = H_trace',
    'pgcplan.DTORS = eps', 'pgcplan.FREESET = eps',
    'PhpStep: S_trace ~> S_plan',
    'S_plan.TODO = (GC_DTORS pgcplan) :: ptask_trace_tail*',
    '$gc_plan_valid(S_plan, pgcplan)', *budget('S_trace'),
    *seek('S_plan', 'S_child', 'CHILD'),
    'S_child.TODO = (DESTRUCTOR_ENTER pdestructorcall_child) :: ptask_child_tail*',
    'pdestructorcall_child.STORE', 'pdestructorcall_child.OBJECT = n_child',
    'n_child <- S_child.DESTRUCTION.CALLED',
    'S_child.ARRAYS[n_original].ITEMS = pentry_original*',
    'S_child.NATIVEEXCESS = [HARRAY n_original]',
    *counts('S_child', 0, 1, 4), *valid('S_child'),
    '$instance_storage_for(S_child, n_child) = eps',
    '$weakref_get(S_child, n_watch) = POBJECT n_child',
    'S_done = $drive_steps(S_child, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = [HARRAY n_original]',
    'S_done.ARRAYS[n_original].ITEMS = pentry_original*',
    '(HARRAY n_original) <- S_done.ALLOCATIONS',
    '(HOBJECT n_child) <- S_done.ALLOCATIONS',
    *counts('S_done', 0, 1, 2), *valid('S_done'),
    '$gc71_output(S_done.EVENTS) = $ptascii("O|B|1|gc71TargetPeer|17|1|W|23|1|R|1|U|1|G|0|1|E|S|1|D|")',
]

review.CASES = {'retained-array-credit-cow-and-physical-child-edges': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS,
}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
