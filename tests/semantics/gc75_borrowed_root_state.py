#!/usr/bin/env python3
"""Borrowed root ARRAY writeback versus real zval and item decrements."""
from pathlib import Path

import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
AUTHOR = (ROOT / 'tests/semantics/gc75_borrowed_array_writeback.php').read_text()
PEER = (ROOT / 'tests/semantics/gc74_peer_selected_child_cow.php').read_text()
DECLARATIONS = r'''syntax pgc75stage = WRITE | SELF
 dec $gc75_at(pstate, pgc75stage) : bool
 def $gc75_at(S, WRITE) = true
   -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
   -- if S.RESULT = KNOWN (PINT 29)
 def $gc75_at(S, SELF) = true
   -- if S.TODO = (WRITE_NAME n_name* z) :: ptask_tail*
   -- if n_name* = $ptascii("a")
   -- if S.RESULT = VARIABLE n_name* z_read
 def $gc75_at(S, pgc75stage) = false -- otherwise
 dec $gc75_seek(pstate, pgc75stage, nat) : pstate
 def $gc75_seek(S, pgc75stage, n) = S
   -- if $gc75_at(S, pgc75stage)
 def $gc75_seek(S, pgc75stage, n) = $gc75_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc75stage, $nabs($(n - 1)))
   -- if ~$gc75_at(S, pgc75stage) /\ $(n > 0)
   -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
 def $gc75_seek(S, pgc75stage, 0) = S
   -- if ~$gc75_at(S, pgc75stage)
 def $gc75_seek(S, pgc75stage, n) = S
   -- if ~$gc75_at(S, pgc75stage)
   -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
 dec $gc75_output(pevent*) : preqbytes
 def $gc75_output(eps) = eps
 def $gc75_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc75_output(pevent_tail*)
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


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


def seek(before, after, stage):
    return [f'{after}_paused = $gc75_seek({before}, {stage}, 2000)',
            f'{after}_paused.COMPLETION = NORMAL \\/ {after}_paused.COMPLETION = BUDGET',
            f'{after} = {after}_paused[.COMPLETION = NORMAL]',
            f'$gc75_at({after}, {stage})']


AUTHOR_STAGE = (
    'S.TODO = (ACQUIRE_ARRAY z) :: ptask_tail* '
    '-- if S.BASE = BASE_DIM pbase_root (KNOWN (PINT 0)) z_dimension '
    '-- if $lookup(S.ENV, $ptascii("a")) = (n_root) '
    '-- if S.STORE[n_root] = DEFINED (PARRAY n_array) '
    '-- if S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), '
    'ENTRY (KINT 1) (DIRECT (POBJECT n_child))] '
    '-- if $object_name(S, n_child) = $ptascii("GC75ChildAuthor")')

AUTHOR_CHECKS = [
    *valid('S'), 'S.NATIVEEXCESS = eps',
    '~((HARRAY n_array) <- $gc_nodes(S.GC.BUFFER))',
    '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
    'S_inputs = $hold_task_inputs(S)',
    'S_inputs.TODO = ptask_tail*', 'S_inputs.RESULT = KNOWN PNULL',
    'S_base = $base_acquire(S_inputs, pbase_root, z_dimension)',
    'S_lookup = $separate_location_array(S_base, n_array)',
    'S_lookup.TODO = ptask_tail*', 'S_lookup.HELD = S_inputs.HELD',
    'S_lookup.RESULT = KNOWN (PARRAY n_array)',
    'S_lookup.STORE[n_root] = DEFINED (PARRAY n_array)',
    'S_lookup.LOCATION = ROOT n_root', 'S_lookup.CELL = n_root',
    '$native_rc(S_lookup, HARRAY n_array) = 2',
    '$native_rc(S_lookup[.RESULT = KNOWN PNULL], HARRAY n_array) = 1',
    '$gc_array_borrowed_source(S_lookup, n_root)',
    '$gc_array_borrowed_cell(S_lookup, n_root)',
    'S_stored = $location_array_store(S_lookup, ROOT n_root, PARRAY n_array)',
    'S_fetched = $fetch_location_array(S_base, ROOT n_root, z_dimension)',
    'S_fetched = S_stored', 'S_stored.STORE = S_lookup.STORE',
    'S_stored.ARRAYS = S_lookup.ARRAYS', 'S_stored.GC = S_lookup.GC',
    '$gc_same_cell(S_lookup, S_lookup, n_root) = S_lookup',
    # A real held zval is not erased by the borrowed count view.
    'S_held = S_lookup[.HELD = S_lookup.HELD ++ [HARRAY n_array]]',
    '$heap_valid($heap_graph(S_held))',
    '$native_rc(S_held[.RESULT = KNOWN PNULL], HARRAY n_array) = 2',
    '~$gc_array_borrowed_cell(S_held, n_root)',
    'S_held_next = $gc_same_cell(S_held, S_held, n_root)',
    '(HARRAY n_array) <- $gc_nodes(S_held_next.GC.BUFFER)',
    # Source, location, storage and retained-history counterstates.
    '~$gc_array_borrowed_cell(S_lookup[.ORIGIN = eps], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.CVS = eps], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.ENV = eps], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.CELL = |S_lookup.STORE|], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.LOCATION = ELEMENT n_array (KINT 0)], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.RESULT = KNOWN PNULL], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.STORE = $set_cell(S_lookup.STORE, n_root, DEFINED PNULL)], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.ALLOCATIONS = $native_remove_one(S_lookup.ALLOCATIONS, HARRAY n_array)], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.NATIVEEXCESS = [HARRAY n_array]], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.LITERALREFRETAINED = [n_root]], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.LITERALREFDEBTS = [n_root]], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.LITERALARRAYRETAINED = [n_array]], n_root)',
    '~$gc_array_borrowed_cell(S_lookup[.LITERALARRAYDEBTS = [n_array]], n_root)',
    # Real acquisition wraps the entry, not OP.VALUE or a second CELL owner.
    'PhpStep: S ~> S_raw',
    'S_raw.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_reference), ENTRY (KINT 1) (DIRECT (POBJECT n_child))]',
    'S_raw.STORE[n_reference] = DEFINED (PINT 17)',
    'n_reference <- S_raw.REFCELLS',
    'S_raw.RESULT = KNOWN PNULL',
    '$heap_owners($heap_graph(S_raw), HCELL n_reference) = 1',
    '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 1',
    'S_raw.GC.BUFFER = S.GC.BUFFER',
    'S_acquired = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    '~((HARRAY n_array) <- $gc_nodes(S_acquired.GC.BUFFER))',
    '$heap_owners($heap_graph(S_acquired), HCELL n_reference) = 1',
    *valid('S_acquired'), *budget('S'),
    *seek('S_acquired', 'S_write', 'WRITE'),
    'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write false) :: ptask_write_tail*',
    'pbase_write = BASE_DIM pbase_write_root (KNOWN (PINT 1)) z_write_dimension',
    'S_write.STORE[n_reference] = DEFINED (PINT 23)',
    '$heap_owners($heap_graph(S_write), HCELL n_reference) = 2',
    '~((HARRAY n_array) <- $gc_nodes(S_write.GC.BUFFER))',
    '~((HOBJECT n_child) <- $gc_nodes(S_write.GC.BUFFER))',
    'S_write_inputs = $hold_task_inputs(S_write)',
    'S_write_base = $base_acquire(S_write_inputs, pbase_write_root, z_write_dimension)',
    'S_write_lookup = $separate_location_array(S_write_base, n_array)',
    '$gc_array_borrowed_cell(S_write_lookup, n_root)',
    'PhpStep: S_write ~> S_written',
    '~((HARRAY n_array) <- $gc_nodes(S_written.GC.BUFFER))',
    'S_written.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_reference), ENTRY (KINT 1) (DIRECT (PINT 29))]',
    'S_value = $drive_steps(S_write, 1)[.COMPLETION = NORMAL]',
    'S_value.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_child) :: ptask_child_tail*',
    'pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    '$gc_release_metadata_valid(S_value, pdestructionrelease_child)',
    '$heap_owners($heap_graph(S_value), HOBJECT n_child) = 1',
    '~((HARRAY n_array) <- $gc_nodes(S_value.GC.BUFFER))',
    *valid('S_value'), *budget('S_write'),
    *seek('S_value', 'S_self', 'SELF'),
    'S_self.STORE[n_root] = DEFINED (PARRAY n_array)',
    'n_child <- S_self.DESTRUCTION.CALLED',
    '~((HOBJECT n_child) <- S_self.ALLOCATIONS)',
    '$gc75_output(S_self.EVENTS) = $ptascii("B|A|R|23|D|W|29|")',
    '~((HARRAY n_array) <- $gc_nodes(S_self.GC.BUFFER))',
    '~$gc_array_borrowed_source(S_self, n_root)',
    '~$gc_array_borrowed_cell(S_self, n_root)',
    'PhpStep: S_self ~> S_self_raw',
    '(HARRAY n_array) <- $gc_nodes(S_self_raw.GC.BUFFER)',
    'S_self_next = $drive_steps(S_self, 1)[.COMPLETION = NORMAL]',
    '(HARRAY n_array) <- $gc_nodes(S_self_next.GC.BUFFER)',
    *valid('S_self_next'), *budget('S_self'),
    'S_done = $drive_steps(S_self_next, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = eps',
    '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
    '~((HCELL n_reference) <- S_done.ALLOCATIONS)',
    '$gc75_output(S_done.EVENTS) = $ptascii("B|A|R|23|D|W|29|C|U|G|0|E|S|")',
    *valid('S_done'),
]

PEER_STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if S.RESULT = KNOWN (PINT 29) '
    '-- if pbase = BASE_DIM pbase_root (KNOWN (PINT 1)) z_dimension '
    '-- if $lookup(S.ENV, $ptascii("kept")) = (n_root) '
    '-- if S.STORE[n_root] = DEFINED (PARRAY n_visible) '
    '-- if S.NATIVEEXCESS = [HARRAY n_old] '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_target)), ENTRY (KINT 1) (DIRECT (POBJECT n_sibling)), ENTRY (KINT 2) (ALIAS n_quiet)] '
    '-- if S.ARRAYS[n_visible].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23)), ENTRY (KINT 1) (DIRECT (POBJECT n_sibling)), ENTRY (KINT 2) (ALIAS n_quiet)]')

PEER_CHECKS = [
    *valid('S'),
    '(HOBJECT n_target) <- $gc_nodes(S.GC.BUFFER)',
    '~((HARRAY n_visible) <- $gc_nodes(S.GC.BUFFER))',
    '~((HOBJECT n_sibling) <- $gc_nodes(S.GC.BUFFER))',
    '~((HCELL n_quiet) <- $gc_nodes(S.GC.BUFFER))',
    '$native_rc(S, HARRAY n_old) = 1',
    '$native_rc(S, HARRAY n_visible) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_sibling) = 2',
    '$heap_owners($heap_graph(S), HCELL n_quiet) = 3',
    'S_inputs = $hold_task_inputs(S)',
    'S_base = $base_acquire(S_inputs, pbase_root, z_dimension)',
    'S_lookup = $separate_location_array(S_base, n_visible)',
    '$gc_array_borrowed_source(S_lookup, n_root)',
    '$gc_array_borrowed_cell(S_lookup, n_root)',
    '$native_rc(S_lookup, HARRAY n_visible) = 2',
    '$native_rc(S_lookup[.RESULT = KNOWN PNULL], HARRAY n_visible) = 1',
    'S_stored = $location_array_store(S_lookup, ROOT n_root, PARRAY n_visible)',
    'S_stored.GC = S_lookup.GC',
    'S_stored.STORE = S_lookup.STORE',
    'S_stored.ARRAYS = S_lookup.ARRAYS',
    'PhpStep: S ~> S_raw',
    'S_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
    'S_raw.ARRAYS[n_visible].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23)), ENTRY (KINT 1) (DIRECT (PINT 29)), ENTRY (KINT 2) (ALIAS n_quiet)]',
    'S_raw.GC.BUFFER = S.GC.BUFFER',
    '$gc_array_copy_decrements(S, S_raw) = eps',
    '$gc_same_location(S, S_raw) = eps',
    '$eager_slots(S, S_raw) = [HOBJECT n_sibling]',
    'S_value = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_value.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_child) :: ptask_child_tail*',
    'pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_sibling)]',
    '$gc_release_metadata_valid(S_value, pdestructionrelease_child)',
    'S_value.GC.BUFFER = S.GC.BUFFER',
    '$heap_owners($heap_graph(S_value), HOBJECT n_sibling) = 2',
    *valid('S_value'),
    'PhpStep: S_value ~> S_popped',
    'S_popped.GC.BUFFER = S_value.GC.BUFFER',
    '$heap_owners($heap_graph(S_popped), HOBJECT n_sibling) = 1',
    'S_after = $drive_steps(S_value, 1)[.COMPLETION = NORMAL]',
    'pgc_expected = $gc_buffer_add(S.GC, HOBJECT n_sibling)',
    'S_after.GC.BUFFER = pgc_expected.BUFFER',
    '$heap_count(HOBJECT n_sibling, $gc_nodes(S_after.GC.BUFFER)) = 1',
    '$heap_count(HOBJECT n_target, $gc_nodes(S_after.GC.BUFFER)) = 1',
    '~((HARRAY n_visible) <- $gc_nodes(S_after.GC.BUFFER))',
    '~((HCELL n_quiet) <- $gc_nodes(S_after.GC.BUFFER))',
    '$heap_owners($heap_graph(S_after), HCELL n_quiet) = 3',
    'S_after.STORE[n_quiet] = DEFINED (PINT 17)',
    'S_after.NATIVEEXCESS = [HARRAY n_old]',
    *valid('S_after'), *budget('S'), *budget('S_value'),
]

review.CASES = {
    'borrowed-reference-lookup-and-real-cv-assignment': {
        'source': AUTHOR, 'stage': AUTHOR_STAGE, 'checks': AUTHOR_CHECKS},
    'same-table-writeback-retains-only-real-sibling-drop': {
        'source': PEER, 'stage': PEER_STAGE, 'checks': PEER_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
