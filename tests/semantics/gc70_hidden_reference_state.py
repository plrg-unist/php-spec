#!/usr/bin/env python3
"""Real unpack/COW reference copies through a native-retained Parent edge."""
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc70_peer_unpack_reference.php').read_text()
STAGE = (
    'S.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail* '
    '-- if S.NATIVEEXCESS = [HOBJECT n_parent] '
    '-- if $object_name(S, n_parent) = $ptascii("GC70ParentPeer") '
    '-- if $lookup(S.ENV, $ptascii("array")) = (n_array_cell) '
    '-- if S.STORE[n_array_cell] = DEFINED (PARRAY n_source) '
    '-- if S.ARRAYS[n_source].ITEMS = [ENTRY (KINT 0) (ALIAS n_ref)]')

DECLARATIONS = r'''dec $gc70_write(pstate, nat) : bool
def $gc70_write(S, n_target) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 23)
  -- if $lookup(S.ENV, $ptascii("copy")) = (n_copy_cell)
  -- if S.STORE[n_copy_cell] = DEFINED (PARRAY n_target)
def $gc70_write(S, n_target) = false -- otherwise
dec $gc70_seek_write(pstate, nat, nat) : pstate
def $gc70_seek_write(S, n_target, n) = S
  -- if $gc70_write(S, n_target)
def $gc70_seek_write(S, n_target, n) = $gc70_seek_write($drive_steps(S[.COMPLETION = NORMAL], 1), n_target, $nabs($(n - 1)))
  -- if ~$gc70_write(S, n_target) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc70_seek_write(S, n_target, 0) = S
  -- if ~$gc70_write(S, n_target)
def $gc70_seek_write(S, n_target, n) = S
  -- if ~$gc70_write(S, n_target)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc70_output(pevent*) : preqbytes
def $gc70_output(eps) = eps
def $gc70_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc70_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$native_excess_valid({state})',
            f'$destruction_state_valid({state})',
            f'$call_descriptors_valid({state})']


def counts(state, cell):
    return [f'$heap_owners($heap_graph({state}), HOBJECT n_parent) = 0',
            f'$native_rc({state}, HOBJECT n_parent) = 1',
            f'$heap_owners($heap_graph({state}), HCELL n_ref) = {cell}',
            f'$native_rc({state}, HCELL n_ref) = {cell}',
            f'{state}.NATIVEEXCESS = [HOBJECT n_parent]']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


CHECKS = [
    'n_source =/= n_target', 'S.ARRAYS[n_target].ITEMS = eps',
    '$lookup(S.ENV, $ptascii("parent")) = eps',
    '$lookup(S.ENV, $ptascii("ref")) = eps',
    'n_ref <- S.REFCELLS', 'S.STORE[n_ref] = DEFINED (PINT 17)',
    '$objectprops_at(S.OBJECTPROPS, n_parent) = ([ppropertyslot_quiet])',
    'ppropertyslot_quiet.NAME = $ptascii("quiet")',
    'ppropertyslot_quiet.STATE = PROP_VALUE (ALIAS n_ref)',
    '$node_children(S, HOBJECT n_parent) = [HCELL n_ref]',
    '$node_children(S, HARRAY n_source) = [HCELL n_ref]',
    '$node_children(S, HCELL n_ref) = eps',
    *counts('S', 2), *valid('S'),
    '$gc70_output(S.EVENTS) = $ptascii("O|B|1|17|")',
    'H = $heap_graph(S)', 'H_old = $heap_prune(H)',
    'H_native = $heap_prune_native(H, S.NATIVEEXCESS)',
    '~((HOBJECT n_parent) <- H_old.NODES)',
    '(HOBJECT n_parent) <- H_native.NODES',
    '$heap_owners(H_old, HCELL n_ref) = 1',
    '$heap_owners(H_native, HCELL n_ref) = 2',
    'H_native.ROOTS = H.ROOTS', 'H_native.DEBTS = H.DEBTS',
    '$heap_count(HCELL n_ref, H_native.ROOTS) = $heap_count(HCELL n_ref, H.ROOTS)',
    '$heap_prune_native(H, eps) = H_old',
    '$merge_item(S, ALIAS n_ref) = ALIAS n_ref',
    '$duplicate_item(S, n_source, ALIAS n_ref) = ALIAS n_ref',
    # Empty excess restores the old physical-only view. A genuine singleton
    # remains a singleton even when an unrelated Parent unit is present.
    'S_unprotected = S[.NATIVEEXCESS = eps]',
    '$heap_graph(S_unprotected) = H',
    '$merge_item(S_unprotected, ALIAS n_ref) = DIRECT (PINT 17)',
    '$duplicate_item(S_unprotected, n_source, ALIAS n_ref) = DIRECT (PINT 17)',
    'S_single = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_parent, [ppropertyslot_quiet[.STATE = PROP_VALUE (DIRECT (PINT 17))]])]',
    '$heap_valid($heap_graph(S_single))', *counts('S_single', 1),
    '$merge_item(S_single, ALIAS n_ref) = DIRECT (PINT 17)',
    '$duplicate_item(S_single, n_source, ALIAS n_ref) = DIRECT (PINT 17)',
    # Only array duplication retains its established source-self exception.
    'S_self = S_single[.STORE = $set_cell(S_single.STORE, n_ref, DEFINED (PARRAY n_source))]',
    '$heap_valid($heap_graph(S_self))',
    '$heap_owners($heap_prune_native($heap_graph(S_self), S_self.NATIVEEXCESS), HCELL n_ref) = 1',
    '$duplicate_item(S_self, n_source, ALIAS n_ref) = ALIAS n_ref',
    '$merge_item(S_self, ALIAS n_ref) = DIRECT (PARRAY n_source)',
    # Both consumers add one physical ALIAS edge and no native excess.
    'n_dup = |S.ARRAYS|', 'S_dup = $duplicate_array(S, n_source)',
    'S_dup.RESULT = KNOWN (PARRAY n_dup)',
    'S_dup.ARRAYS[n_dup].ITEMS = S.ARRAYS[n_source].ITEMS',
    'S_dup.STORE = S.STORE', 'S_dup.OBJECTPROPS = S.OBJECTPROPS',
    *counts('S_dup', 3),
    'S_read = $resolve_at(S, S.RESULT, z)',
    'S_read.RESULT = KNOWN (PARRAY n_source)',
    'S_helper = $array_unpack(S_read, n_target, PARRAY n_source, z)',
    'S_helper.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (ALIAS n_ref)]',
    'S_helper.STORE = S.STORE', 'S_helper.OBJECTPROPS = S.OBJECTPROPS',
    *counts('S_helper', 3),
    'PhpStep: S ~> S_raw',
    'S_raw.TODO = (ARRAY_NEXT n_target phpType13*) :: ptask_tail*',
    'S_raw.RESULT = KNOWN PNULL',
    'S_raw.ARRAYS = S_helper.ARRAYS',
    'S_raw.STORE = S.STORE', 'S_raw.OBJECTPROPS = S.OBJECTPROPS',
    'S_raw.EVENTS = S.EVENTS', *counts('S_raw', 3),
    *budget('S'),
    'S_after = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_after.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (ALIAS n_ref)]',
    *counts('S_after', 3), *valid('S_after'),
    'S_write_paused = $gc70_seek_write(S_after, n_target, 4000)',
    'S_write_paused.COMPLETION = BUDGET',
    'S_write = S_write_paused[.COMPLETION = NORMAL]',
    'S_write.TODO = (ASSIGN_ARRAY pbase z_write false) :: ptask_write_tail*',
    '$gc70_write(S_write, n_target)',
    'S_write.STORE[n_ref] = DEFINED (PINT 17)',
    'S_write.ARRAYS[n_source].ITEMS = [ENTRY (KINT 0) (ALIAS n_ref)]',
    'S_write.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (ALIAS n_ref)]',
    *counts('S_write', 3), *valid('S_write'),
    'PhpStep: S_write ~> S_written',
    'S_written.STORE[n_ref] = DEFINED (PINT 23)',
    'S_written.ARRAYS = S_write.ARRAYS',
    'S_written.OBJECTPROPS = S_write.OBJECTPROPS',
    'S_written.NATIVEEXCESS = S_write.NATIVEEXCESS',
    '$entry_value(S_written, ALIAS n_ref) = PINT 23',
    *counts('S_written', 3), *budget('S_write'),
    'S_done = $drive_steps(S_write, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = [HOBJECT n_parent]',
    'S_done.STORE[n_ref] = DEFINED (PINT 23)',
    '$objectprops_at(S_done.OBJECTPROPS, n_parent) = ([ppropertyslot_quiet])',
    *counts('S_done', 1), *valid('S_done'),
    '~((HARRAY n_source) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_target) <- S_done.ALLOCATIONS)',
    '$gc70_output(S_done.EVENTS) = $ptascii("O|B|1|17|A|23|23|23|E|D|23|")',
]

review.CASES = {'native-retained-parent-reference-copy': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS,
}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
