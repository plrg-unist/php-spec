#!/usr/bin/env python3
"""Actual copied-target visit, untouched siblings and ordinary VALUE release."""
from pathlib import Path

import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc74_peer_selected_child_cow.php').read_text()
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if S.RESULT = KNOWN (PINT 23) '
    '-- if S.NATIVEEXCESS = [HARRAY n_old] '
    '-- if $lookup(S.ENV, $ptascii("kept")) = (n_kept) '
    '-- if S.STORE[n_kept] = DEFINED (PARRAY n_old) '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_target)), '
    'ENTRY (KINT 1) (DIRECT (POBJECT n_sibling)), ENTRY (KINT 2) (ALIAS n_quiet)] '
    '-- if $object_name(S, n_target) = $ptascii("GC74TargetPeer") '
    '-- if $object_name(S, n_sibling) = $ptascii("GC74SiblingPeer")')

DECLARATIONS = r'''syntax pgc74stage = WRITE | TRACE | TARGET | SIBLING
dec $gc74_at(pstate, pgc74stage, nat, nat) : bool
def $gc74_at(S, WRITE, n_target, n_sibling) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 29)
def $gc74_at(S, TRACE, n_target, n_sibling) = true
  -- if S.TODO = (GC_TRACE pgccall) :: ptask_tail*
def $gc74_at(S, TARGET, n_target, n_sibling) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.STORE /\ pdestructorcall.OBJECT = n_target
def $gc74_at(S, SIBLING, n_target, n_sibling) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.STORE /\ pdestructorcall.OBJECT = n_sibling
def $gc74_at(S, pgc74stage, n_target, n_sibling) = false -- otherwise
dec $gc74_seek(pstate, pgc74stage, nat, nat, nat) : pstate
def $gc74_seek(S, pgc74stage, n_target, n_sibling, n) = S
  -- if $gc74_at(S, pgc74stage, n_target, n_sibling)
def $gc74_seek(S, pgc74stage, n_target, n_sibling, n) = $gc74_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc74stage, n_target, n_sibling, $nabs($(n - 1)))
  -- if ~$gc74_at(S, pgc74stage, n_target, n_sibling) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc74_seek(S, pgc74stage, n_target, n_sibling, 0) = S
  -- if ~$gc74_at(S, pgc74stage, n_target, n_sibling)
def $gc74_seek(S, pgc74stage, n_target, n_sibling, n) = S
  -- if ~$gc74_at(S, pgc74stage, n_target, n_sibling)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc74_output(pevent*) : preqbytes
def $gc74_output(eps) = eps
def $gc74_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc74_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def seek(before, after, stage):
    return [f'{after}_paused = $gc74_seek({before}, {stage}, n_target, n_sibling, 4000)',
            f'{after}_paused.COMPLETION = NORMAL \\/ {after}_paused.COMPLETION = BUDGET',
            f'{after} = {after}_paused[.COMPLETION = NORMAL]',
            f'$gc74_at({after}, {stage}, n_target, n_sibling)']


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$native_excess_valid({state})',
            f'$destruction_state_valid({state})',
            f'$call_descriptors_valid({state})']


def counts(state, physical, native, target, sibling, quiet):
    return [f'$heap_owners($heap_graph({state}), HARRAY n_old) = {physical}',
            f'$native_rc({state}, HARRAY n_old) = {native}',
            f'$heap_owners($heap_graph({state}), HOBJECT n_target) = {target}',
            f'$heap_owners($heap_graph({state}), HOBJECT n_sibling) = {sibling}',
            f'$heap_owners($heap_graph({state}), HCELL n_quiet) = {quiet}']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


CHECKS = [
    'n_new = |S.ARRAYS|', 'pentry_old* = S.ARRAYS[n_old].ITEMS',
    'S.STORE[n_quiet] = DEFINED (PINT 17)',
    '~((HOBJECT n_target) <- $gc_nodes(S.GC.BUFFER))',
    '~((HOBJECT n_sibling) <- $gc_nodes(S.GC.BUFFER))',
    '~((HCELL n_quiet) <- $gc_nodes(S.GC.BUFFER))',
    *counts('S', 1, 2, 1, 1, 2), *valid('S'),
    'PhpStep: S ~> S_raw',
    'S_raw.ARRAYS = S.ARRAYS ++ [$array_insert(S.ARRAYS[n_old], KINT 0, DIRECT (PINT 23))]',
    'S_raw.STORE = $set_cell(S.STORE, n_kept, DEFINED (PARRAY n_new))',
    'S_raw.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_new]',
    'S_raw.NATIVEEXCESS = [HARRAY n_old]',
    'S_raw.GC.BUFFER = S.GC.BUFFER',
    *counts('S_raw', 0, 1, 1, 2, 3),
    '$eager_slots(S, S_raw) = [HARRAY n_old]',
    '$gc_array_copy_decrements(S, S_raw) = [HOBJECT n_target]',
    '$gc_same_location(S, S_raw) = [HOBJECT n_target]',
    '$gc_array_copy_decrements(S[.ORIGIN = eps], S_raw) = eps',
    '$gc_array_copy_decrements(S[.TODO = DISCARD :: ptask_tail*], S_raw) = eps',
    '$gc_array_copy_decrements(S[.RESULT = KNOWN (POBJECT n_target)], S_raw) = eps',
    '$gc_array_copy_decrements(S[.NATIVEEXCESS = eps], S_raw[.NATIVEEXCESS = eps]) = eps',
    '$gc_array_copy_decrements(S, S_raw[.NATIVEEXCESS = [HARRAY n_old, HARRAY n_new]]) = eps',
    'S_target_unit = S[.NATIVEEXCESS = [HARRAY n_old, HOBJECT n_target]]',
    '$gc_array_copy_decrements(S_target_unit, S_raw[.NATIVEEXCESS = S_target_unit.NATIVEEXCESS]) = eps',
    '$gc_array_copy_decrements(S, S_raw[.ORIGIN = eps]) = eps',
    '$gc_array_copy_decrements(S, S_raw[.REFCELLS = eps]) = eps',
    '$gc_array_copy_decrements(S, S_raw[.KEY = KINT 1]) = eps',
    '$gc_array_copy_decrements(S, S_raw[.CELL = n_quiet]) = eps',
    '$gc_array_copy_decrements(S, S_raw[.LOCATION = ELEMENT n_old (KINT 0)]) = eps',
    'S_bad_row = S_raw[.ARRAYS = $array_replace(S_raw.ARRAYS, n_new, $array_insert(S_raw.ARRAYS[n_new], KINT 0, DIRECT (PINT 24)))]',
    '$heap_graph(S_bad_row) = $heap_graph(S_raw)',
    '$gc_array_copy_decrements(S, S_bad_row) = eps',
    'S_bad_store = S_raw[.STORE = $set_cell(S_raw.STORE, n_kept, DEFINED (PARRAY n_old))]',
    '$gc_array_copy_decrements(S, S_bad_store) = eps',
    # The actual observer adds only the copied target's visit, with no Child job
    # or invented physical owner. The old header retains its genuine TEMP.
    'S_drop = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: ptask_drop_tail*',
    'pdestructionrelease_drop.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    'S_drop.DESTRUCTION.OPERATIONS = [pdestructionoperation_drop]',
    '$gc_operation_metadata_valid(S_drop, pdestructionoperation_drop)',
    '$gc_release_metadata_valid(S_drop, pdestructionrelease_drop)',
    *valid('S_drop'), *counts('S_drop', 1, 2, 1, 2, 3),
    '$gc_array_copy_decrements(S, S_drop) = [HOBJECT n_target]',
    '$gc_same_location(S, S_drop) = [HOBJECT n_target]',
    'pgc_target = $gc_buffer_add(S.GC, HOBJECT n_target)',
    'S_drop.GC.BUFFER = pgc_target.BUFFER',
    'S_drop.GC.FREE = pgc_target.FREE',
    '$heap_count(HOBJECT n_target, $gc_nodes(S_drop.GC.BUFFER)) = 1',
    '~((HOBJECT n_sibling) <- $gc_nodes(S_drop.GC.BUFFER))',
    '~((HCELL n_quiet) <- $gc_nodes(S_drop.GC.BUFFER))',
    'PhpStep: S_drop ~> S_popped',
    'S_popped.ARRAYS = S_drop.ARRAYS', 'S_popped.STORE = S_drop.STORE',
    '$heap_owners($heap_graph(S_popped), HOBJECT n_target) = 1',
    'S_after = $drive_steps(S_drop, 1)[.COMPLETION = NORMAL]',
    'S_after.GC.BUFFER = S_drop.GC.BUFFER',
    *counts('S_after', 0, 1, 1, 2, 3), *valid('S_after'),
    *budget('S'), *budget('S_drop'),
    # Pure borrowed counterstate protects the preexisting nonempty property
    # branch from overlap with the fresh-index forwarding rule.
    'ppropertyslot_keep = {DECL eps, NAME $ptascii("keep"), STATE PROP_VALUE (DIRECT (POBJECT n_sibling))}',
    'S_property = S[.TODO = (ASSIGN_ARRAY (BASE_PROPERTY (POBJECT n_target) $ptascii("keep")) z false) :: ptask_tail*][.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_target, [ppropertyslot_keep])]',
    'S_property_next = S_raw[.OBJECTPROPS = S_property.OBJECTPROPS]',
    '$heap_valid($heap_graph(S_property))', '$heap_valid($heap_graph(S_property_next))',
    '$gc_array_copy_decrements(S_property, S_property_next) = eps',
    '$gc_same_location(S_property, S_property_next) = [HOBJECT n_sibling]',
    *seek('S_after', 'S_write', 'WRITE'),
    'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write false) :: ptask_write_tail*',
    'S_write.STORE[n_kept] = DEFINED (PARRAY n_new)',
    '~((HOBJECT n_sibling) <- $gc_nodes(S_write.GC.BUFFER))',
    'PhpStep: S_write ~> S_written',
    'S_written.ARRAYS[n_old].ITEMS = pentry_old*',
    'S_written.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23)), ENTRY (KINT 1) (DIRECT (PINT 29)), ENTRY (KINT 2) (ALIAS n_quiet)]',
    *counts('S_written', 0, 1, 1, 1, 3),
    '$gc_array_copy_decrements(S_write, S_written) = eps',
    '$gc_same_location(S_write, S_written) = eps',
    '$eager_slots(S_write, S_written) = [HOBJECT n_sibling]',
    'S_value = $drive_steps(S_write, 1)[.COMPLETION = NORMAL]',
    'S_value.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: ptask_value_tail*',
    'pdestructionrelease_value.JOBS = [DESTRUCTION_VALUE (HOBJECT n_sibling)]',
    '$gc_release_metadata_valid(S_value, pdestructionrelease_value)',
    *valid('S_value'), *counts('S_value', 0, 1, 1, 2, 3),
    # Preserve the actual raw-to-driver boundary. A separate existing raw
    # root-writeback header visit is not a native-correctness claim here.
    'S_value.GC.BUFFER = S_written.GC.BUFFER',
    '~((HOBJECT n_sibling) <- $gc_nodes(S_value.GC.BUFFER))',
    '~((HCELL n_quiet) <- $gc_nodes(S_value.GC.BUFFER))',
    'PhpStep: S_value ~> S_released',
    *counts('S_released', 0, 1, 1, 1, 3),
    'S_released.GC.BUFFER = S_value.GC.BUFFER',
    'S_value_next = $drive_steps(S_value, 1)[.COMPLETION = NORMAL]',
    *counts('S_value_next', 0, 1, 1, 1, 3), *valid('S_value_next'),
    'pgc_sibling = $gc_buffer_add(S_value.GC, HOBJECT n_sibling)',
    'S_value_next.GC.BUFFER = pgc_sibling.BUFFER',
    '$heap_count(HOBJECT n_sibling, $gc_nodes(S_value_next.GC.BUFFER)) = 1',
    '$heap_count(HOBJECT n_target, $gc_nodes(S_value_next.GC.BUFFER)) = 1',
    '~((HCELL n_quiet) <- $gc_nodes(S_value_next.GC.BUFFER))',
    *budget('S_write'), *budget('S_value'),
    *seek('S_value_next', 'S_trace', 'TRACE'),
    'S_trace.TODO = (GC_TRACE pgccall) :: ptask_trace_tail*',
    'S_trace.NATIVEEXCESS = [HARRAY n_old]',
    '~((HARRAY n_new) <- S_trace.ALLOCATIONS)',
    *counts('S_trace', 0, 1, 1, 1, 1), *valid('S_trace'),
    'H_trace = $gc_graph(S_trace)',
    '$heap_count(HARRAY n_old, H_trace.ROOTS) = 0',
    '$gc_native_white(H_trace, S_trace.NATIVEEXCESS, $gc_eligible_nodes(S_trace.GC.BUFFER)) = eps',
    'pgcplan = $gc_plan(S_trace, pgccall)', 'pgcplan.DTORS = eps', 'pgcplan.FREESET = eps',
    'PhpStep: S_trace ~> S_plan', '$gc_plan_valid(S_plan, pgcplan)',
    *seek('S_plan', 'S_target', 'TARGET'),
    'n_target <- S_target.DESTRUCTION.CALLED',
    '~(n_sibling <- S_target.DESTRUCTION.CALLED)',
    *counts('S_target', 0, 1, 3, 1, 1), *valid('S_target'),
    *seek('S_target', 'S_sibling', 'SIBLING'),
    'n_target <- S_sibling.DESTRUCTION.CALLED',
    'n_sibling <- S_sibling.DESTRUCTION.CALLED',
    *counts('S_sibling', 0, 1, 1, 3, 1), *valid('S_sibling'),
    'S_done = $drive_steps(S_sibling, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = [HARRAY n_old]',
    'S_done.ARRAYS[n_old].ITEMS = pentry_old*',
    *counts('S_done', 0, 1, 1, 1, 1), *valid('S_done'),
    '$gc74_output(S_done.EVENTS) = $ptascii("O|B|1|gc74AvailablePeer|W|23|17|R|29|U|G|0|E|S|T|L|")',
]

review.CASES = {'copied-target-visit-and-ordinary-sibling-decrement': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS,
}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
