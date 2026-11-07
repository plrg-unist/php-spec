#!/usr/bin/env python3
"""Real old-view owners, COW TEMP progress and genuine later VALUE drops."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = (ROOT / 'tests/semantics/gc78_shared_header_reference.php').read_text()
ASSIGNMENT = (ROOT / 'tests/semantics/gc78_shared_header_assignment.php').read_text()
# A state-only callback slice; this adds no native/source-agreement credit.
CALLBACK = (ROOT / 'tests/semantics/gc77_shared_owning_alias.php').read_text().replace(
    '$kept[0] = 23;', '$view = $kept;\n$kept[0] = 23;')

DECLARATIONS = r'''syntax pgc78phase = VIEW | VALUE | ACTIVE
dec $gc78_at(pstate, pgc78phase) : bool
def $gc78_at(S, VIEW) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("view")
def $gc78_at(S, VALUE) = true
  -- if S.NATIVEEXCESS = [HARRAY n_old]
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_old)]
def $gc78_at(S, ACTIVE) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.DESTRUCTION.CALLS = [pdestructorcall]
  -- if pcallcontext.TARGET = pdestructorcall.TARGET
def $gc78_at(S, pgc78phase) = false -- otherwise
dec $gc78_seek(pstate, pgc78phase, nat) : pstate
def $gc78_seek(S, pgc78phase, n) = S -- if $gc78_at(S, pgc78phase)
def $gc78_seek(S, pgc78phase, n) = $gc78_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc78phase, $nabs($(n - 1)))
  -- if ~$gc78_at(S, pgc78phase) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc78_seek(S, pgc78phase, 0) = S -- if ~$gc78_at(S, pgc78phase)
def $gc78_seek(S, pgc78phase, n) = S
  -- if ~$gc78_at(S, pgc78phase)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc78_op(pstate, pdestructionoperation) : pstate
def $gc78_op(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc78_output(pevent*) : preqbytes
def $gc78_output(eps) = eps
def $gc78_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc78_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$native_excess_valid({state})', f'$gc_state_valid({state})',
            f'$destruction_state_valid({state})', f'$call_descriptors_valid({state})']


def header(state, physical, native):
    return [f'$heap_owners($heap_graph({state}), HARRAY n_old) = {physical}',
            f'$native_rc({state}, HARRAY n_old) = {native}']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


def reject_op(name, patch):
    return [f'pdestructionoperation_bad_{name} = pdestructionoperation_live{patch}',
            f'S_bad_{name} = $gc78_op(S_live, pdestructionoperation_bad_{name})',
            f'$heap_graph(S_bad_{name}) = $heap_graph(S_live)',
            f'~$gc_operation_metadata_valid(S_bad_{name}, pdestructionoperation_bad_{name})']


COMMON = (
    '-- if $lookup(S.ENV, $ptascii("kept")) = (n_root) '
    '-- if $lookup(S.ENV, $ptascii("view")) = (n_view) '
    '-- if S.STORE[n_root] = DEFINED (PARRAY n_old) '
    '-- if S.STORE[n_view] = DEFINED (PARRAY n_old) '
    '-- if S.NATIVEEXCESS = [HARRAY n_old] ')
REF_STAGE = ('S.TODO = (ACQUIRE_ARRAY z) :: ptask_tail* ' + COMMON +
    '-- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_key '
    '-- if n_name* = $ptascii("kept") '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (POBJECT n_child))]')
ASG_STAGE = ('S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* ' + COMMON +
    '-- if S.RESULT = KNOWN (PINT 23) '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (POBJECT n_child))]')

REF_CHECKS = [
    *valid('S'), *header('S', 2, 3),
    '~((HARRAY n_old) <- $gc_nodes(S.GC.BUFFER))',
    'n_new = |S.ARRAYS|', 'n_ref = |S.STORE|',
    'PhpStep: S ~> S_raw',
    'S_raw.ARRAYS = S.ARRAYS ++ [$array_insert(S.ARRAYS[n_old], KINT 0, ALIAS n_ref)]',
    'S_raw.STORE = $set_cell(S.STORE, n_root, DEFINED (PARRAY n_new)) ++ [DEFINED (PINT 17)]',
    'S_raw.STORE[n_view] = DEFINED (PARRAY n_old)',
    'S_raw.REFCELLS = n_ref :: S.REFCELLS',
    'S_raw.RESULT = KNOWN PNULL', 'S_raw.CELL = n_ref',
    '$heap_owners($heap_graph(S_raw), HCELL n_ref) = 1',
    '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 2',
    *header('S_raw', 1, 2),
    'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
    'pgctemporary_done = pgctemporary_live[.PENDING = false]',
    '$gc_operation_temporary_extra(S, S_raw, ACQUIRE_ARRAY z, [HARRAY n_old]) = [pgctemporary_live]',
    # Coherent raw images with zero or two header losses cannot mint a receipt.
    'S_bad_no_loss = S_raw[.HELD = [HARRAY n_old]]',
    '$gc_operation_temporary_extra(S, S_bad_no_loss, ACQUIRE_ARRAY z, [HARRAY n_old]) = eps',
    'S_bad_two_losses = S[.HELD = [HARRAY n_old]]',
    '$gc_operation_temporary_extra(S_bad_two_losses, S_raw, ACQUIRE_ARRAY z, [HARRAY n_old]) = eps',
    'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: ptask_live_tail*',
    'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
    'pdestructionoperation_live.SOURCE = ACQUIRE_ARRAY z',
    'pdestructionoperation_live.NOGCEXTRA = [pgctemporary_live]',
    '$gc_array_header_progress(S_live, pgctemporary_live)',
    '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
    '$gc_release_metadata_valid(S_live, pdestructionrelease_live)',
    *valid('S_live'), *header('S_live', 2, 3),
    '$heap_owners($heap_graph(S_live), HCELL n_ref) = 1',
]
for name, patch in {
    'progress': '[.NOGCEXTRA = [pgctemporary_done]]',
    'tail': '[.NOGCEXTRA = [pgctemporary_live, pgctemporary_live]]',
    'source': '[.SOURCE = DISCARD]',
    'key': '[.KEY = KINT 1]',
    'cell': '[.CELL = n_root]',
}.items():
    REF_CHECKS += reject_op(name, patch)
REF_CHECKS += [
    '~$gc_array_header_progress(S_live[.NATIVEEXCESS = eps], pgctemporary_live)',
    '~$gc_array_header_progress(S_live[.NATIVEEXCESS = [HARRAY n_old, HARRAY n_old]], pgctemporary_live)',
    '~$gc_array_header_progress(S_live, pgctemporary_live[.OPERAND = KNOWN (PARRAY (|S_live.ARRAYS|))])',
    '~$gc_array_header_progress(S_live, pgctemporary_live[.OPERAND = REFERENCE n_ref])',
    # Count thresholds preserve debt adjustment; these are helper-only controls.
    'S_debt_one = S_live[.LITERALARRAYDEBTS = [n_old]]',
    '$native_rc(S_debt_one, HARRAY n_old) = 2',
    '$gc_array_header_progress(S_debt_one, pgctemporary_live)',
    'S_debt_two = S_live[.LITERALARRAYDEBTS = [n_old, n_old]]',
    '$native_rc(S_debt_two, HARRAY n_old) = 1',
    '~$gc_array_header_progress(S_debt_two, pgctemporary_live)',
    'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
    'pdestructionoperation_done = pdestructionoperation_live[.NOGCEXTRA = [pgctemporary_done]]',
    'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
    '$gc_array_header_progress(S_after, pgctemporary_done)',
    '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
    *header('S_after', 1, 2), *valid('S_after'),
    'S_after.GC.BUFFER = S_live.GC.BUFFER',
    '~((HARRAY n_old) <- $gc_nodes(S_after.GC.BUFFER))',
    # Native count permits pending here; exact TEMP suffix must reject it.
    '$gc_array_header_progress(S_after, pgctemporary_live)',
    'S_bad_late_pending = $gc78_op(S_after, pdestructionoperation_live)',
    '~$gc_operation_metadata_valid(S_bad_late_pending, pdestructionoperation_live)',
    *budget('S'), *budget('S_live'),
    'S_view_pause = $gc78_seek(S_after, VIEW, 3000)',
    'S_view = S_view_pause[.COMPLETION = NORMAL]',
    '$gc78_at(S_view, VIEW)',
    'S_view.STORE[n_view] = DEFINED (PARRAY n_old)',
    *header('S_view', 1, 2), *valid('S_view'),
    '~((HARRAY n_old) <- $gc_nodes(S_view.GC.BUFFER))',
    'PhpStep: S_view ~> S_view_raw',
    '$lookup(S_view_raw.ENV, $ptascii("view")) = eps',
    '$heap_owners($heap_graph(S_view_raw), HCELL n_view) = 0',
    *header('S_view_raw', 1, 2),
    'S_view_first = $drive_steps(S_view, 1)[.COMPLETION = NORMAL]',
    'S_view_live_pause = $gc78_seek(S_view_first, VALUE, 100)',
    'S_view_live = S_view_live_pause[.COMPLETION = NORMAL]',
    '$gc78_at(S_view_live, VALUE)',
    'S_view_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_view) :: ptask_view_tail*',
    'pdestructionrelease_view.JOBS = [DESTRUCTION_VALUE (HARRAY n_old)]',
    *header('S_view_live', 1, 2),
    'S_view_after = $drive_steps(S_view_live, 1)[.COMPLETION = NORMAL]',
    *header('S_view_after', 0, 1),
    '(HARRAY n_old) <- $gc_nodes(S_view_after.GC.BUFFER)',
    '$heap_owners($heap_graph(S_view_after), HOBJECT n_child) = 1',
    *valid('S_view_after'),
    'S_done = $drive_steps(S_view_after, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = [HARRAY n_old]',
    '(HARRAY n_old) <- S_done.ALLOCATIONS',
    'n_child <- S_done.DESTRUCTION.CALLED',
    '$gc78_output(S_done.EVENTS) = $ptascii("B|O|N|1|gc78AvailablePeer|Q|0|W|17|23|K|V|G|0|E|S|D|")',
    *valid('S_done'),
]

ASG_CHECKS = [
    *valid('S'), *header('S', 2, 3),
    '~((HARRAY n_old) <- $gc_nodes(S.GC.BUFFER))',
    'n_new = |S.ARRAYS|',
    'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
    'PhpStep: S ~> S_raw',
    'S_raw.STORE[n_view] = DEFINED (PARRAY n_old)',
    *header('S_raw', 1, 2),
    '$gc_operation_temporary_extra(S, S_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old]) = [pgctemporary_live]',
    'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: ptask_live_tail*',
    'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
    '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
    *header('S_live', 2, 3), *valid('S_live'),
    'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
    'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
    'pdestructionoperation_done.NOGCEXTRA = [pgctemporary_live[.PENDING = false]]',
    '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
    *header('S_after', 1, 2),
    '~((HARRAY n_old) <- $gc_nodes(S_after.GC.BUFFER))',
    # An exact constructed selected DIRECT Child tests the changed inference
    # at positive pre-count two, on both raw and eagered successor views.
    'parray_target = S.ARRAYS[n_old][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child)), ENTRY (KINT 1) (DIRECT (PINT 17))]]',
    'S_target = S[.ARRAYS = $array_replace(S.ARRAYS, n_old, parray_target)]',
    *valid('S_target'),
    'PhpStep: S_target ~> S_target_raw',
    '$gc_array_copy_decrements(S_target, S_target_raw) = [HOBJECT n_child]',
    'S_target_live = $drive_steps(S_target, 1)[.COMPLETION = NORMAL]',
    '$gc_array_copy_decrements(S_target, S_target_live) = [HOBJECT n_child]',
    '(HOBJECT n_child) <- $gc_nodes(S_target_live.GC.BUFFER)',
    '~((HARRAY n_old) <- $gc_nodes(S_target_live.GC.BUFFER))',
    '$heap_owners($heap_graph(S_target_live), HOBJECT n_child) = 1',
    *budget('S_live'),
]

MIXED_STAGE = ('S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* ' + COMMON +
    '-- if S.RESULT = KNOWN (PINT 23) '
    '-- if $lookup(S.ENV, $ptascii("slot")) = (n_leaf) '
    '-- if S.STORE[n_leaf] = DEFINED (POBJECT n_child) '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (ALIAS n_leaf)]')
MIXED_CHECKS = [
    *valid('S'), *header('S', 2, 3),
    'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
    'PhpStep: S ~> S_raw',
    *header('S_raw', 1, 2),
    '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 0',
    '$gc_operation_temporary_extra(S, S_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old, HOBJECT n_child]) = [pgctemporary_live]',
    # One copied DIRECT edge masks the shared payload drop. Test the pure
    # selector against both raw and eagered states, with two header owners.
    'S_masked = S[.ARRAYS = $array_replace(S.ARRAYS, n_old, $array_insert(S.ARRAYS[n_old], KINT 1, DIRECT (POBJECT n_child)))]',
    '$heap_valid($heap_graph(S_masked))',
    'PhpStep: S_masked ~> S_masked_raw',
    '$gc_array_copy_decrements(S_masked, S_masked_raw) = [HOBJECT n_child]',
    'S_masked_live = $drive_steps(S_masked, 1)[.COMPLETION = NORMAL]',
    '$gc_array_copy_decrements(S_masked, S_masked_live) = [HOBJECT n_child]',
    'S_masked_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_masked) :: ptask_masked_tail*',
    'pdestructionrelease_masked.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    '(HOBJECT n_child) <- $gc_nodes(S_masked_live.GC.BUFFER)',
    # The same exact alias row with a quiet payload exercises the sole-loss
    # alias mint and metadata arm; this is a constructed image only.
    '$lookup(S.ENV, $ptascii("name")) = (n_spare)',
    'S_quiet = S[.STORE = $set_cell($set_cell(S.STORE, n_leaf, DEFINED (PINT 17)), n_spare, DEFINED (POBJECT n_child))]',
    'S_quiet_raw = S_raw[.STORE = $set_cell(S_raw.STORE, n_spare, DEFINED (POBJECT n_child))]',
    '$heap_valid($heap_graph(S_quiet))',
    '$heap_owners($heap_graph(S_quiet), HOBJECT n_child) = 1',
    '$gc_operation_temporary_extra(S_quiet, S_quiet_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old]) = [pgctemporary_live]',
    'S_quiet_live = $drive_steps(S_quiet, 1)[.COMPLETION = NORMAL]',
    'S_quiet_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_quiet) :: ptask_quiet_tail*',
    'pdestructionrelease_quiet.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    'S_quiet_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_quiet]',
    '$gc_operation_metadata_valid(S_quiet_live, pdestructionoperation_quiet)',
    *header('S_quiet_live', 2, 3),
    'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: ptask_live_tail*',
    'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HARRAY n_old), DESTRUCTION_VALUE (HOBJECT n_child)]',
    'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
    '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
    *header('S_live', 2, 3), *valid('S_live'),
    'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
    'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
    'pdestructionoperation_done.NOGCEXTRA = [pgctemporary_live[.PENDING = false]]',
    '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
    *header('S_after', 1, 2),
    'S_active_pause = $gc78_seek(S_after, ACTIVE, 2000)',
    'S_active = S_active_pause[.COMPLETION = NORMAL]',
    '$gc78_at(S_active, ACTIVE)',
    'S_active.DESTRUCTION.CALLS = [pdestructorcall]',
    'pdestructorcall.OBJECT = n_child',
    'pdestructorcall.OPERATION = (pdestructionoperation_done)',
    '$gc_array_alias_callback_site(S_active, pdestructionoperation_done)',
    '$gc_operation_metadata_valid(S_active, pdestructionoperation_done)',
    '$gc_array_header_progress(S_active, pgctemporary_live[.PENDING = false])',
    *header('S_active', 1, 2), *valid('S_active'),
    *budget('S_after'),
]

review.CASES = {
    'reference-cow-real-view-and-later-value-drop': {'source': REFERENCE, 'stage': REF_STAGE, 'checks': REF_CHECKS},
    'assignment-view-and-selected-child-inference': {'source': ASSIGNMENT, 'stage': ASG_STAGE, 'checks': ASG_CHECKS},
    'shared-alias-view-and-consumed-callback-slice': {'source': CALLBACK, 'stage': MIXED_STAGE, 'checks': MIXED_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
