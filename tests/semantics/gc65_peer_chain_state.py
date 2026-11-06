#!/usr/bin/env python3
"""Real second Previous handoff, finite chain owners and later normal read."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc65_finite_previous_later_read.php').read_text()
STAGE = (
    'S.TODO = (THROW_SEARCH n_c) :: (DESTRUCTOR_RESULT pdestructorcall_second) :: ptask_second_tail* '
    '-- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_parent] '
    '-- if pdestructionoperation_parent.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite '
    '-- if pdestructionoperation_parent.PENDING = (n_b) '
    '-- if pdestructionoperation_inner.SOURCE = THROW_SEARCH n_a '
    '-- if $throwable_field(S, n_b, "previous") = POBJECT n_a')
DECLARATIONS = r'''syntax pgc65stage = CHILD_PIN | LATER_ENTER | LATER_READ | RETIRED | PARENT_EXIT
dec $gc65_at(pstate, pgc65stage, nat, nat, nat) : bool
def $gc65_at(S, CHILD_PIN, n_old, n_second, n_later) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n_second
def $gc65_at(S, LATER_ENTER, n_old, n_second, n_later) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_later
def $gc65_at(S, LATER_READ, n_old, n_second, n_later) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_later
def $gc65_at(S, RETIRED, n_old, n_second, n_later) = true
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = THROW_SEARCH n
def $gc65_at(S, PARENT_EXIT, n_old, n_second, n_later) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME paccess) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old
def $gc65_at(S, pgc65stage, n_old, n_second, n_later) = false -- otherwise
dec $gc65_seek(pstate, pgc65stage, nat, nat, nat, nat) : pstate
def $gc65_seek(S, pgc65stage, n_old, n_second, n_later, n) = S
  -- if $gc65_at(S, pgc65stage, n_old, n_second, n_later)
def $gc65_seek(S, pgc65stage, n_old, n_second, n_later, n) = $gc65_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc65stage, n_old, n_second, n_later, $nabs($(n - 1)))
  -- if ~$gc65_at(S, pgc65stage, n_old, n_second, n_later) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc65_seek(S, pgc65stage, n_old, n_second, n_later, 0) = S
  -- if ~$gc65_at(S, pgc65stage, n_old, n_second, n_later)
def $gc65_seek(S, pgc65stage, n_old, n_second, n_later, n) = S
  -- if ~$gc65_at(S, pgc65stage, n_old, n_second, n_later)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$destruction_state_valid({state})', f'$call_descriptors_valid({state})']


def owners(state):
    return [f'$heap_owners($heap_graph({state}), HOBJECT {node}) = 1'
            for node in ['n_a', 'n_b', 'n_c']]


def seek(before, state, stage):
    return [f'{state}_paused = $gc65_seek({before}, {stage}, n_old, n_second, n_later, 4000)',
            f'{state}_paused.COMPLETION = BUDGET', f'{state} = {state}_paused[.COMPLETION = NORMAL]']


CHECKS = [
    'pweakmapwrite.OLD.VALUE = POBJECT n_old',
    'pweakmapwrite.ACCESS.OBJECT = (n_map)',
    'pweakmapwrite.ACCESS.OFFSET = POBJECT n_key',
    '$instance_storage_for(S, n_old) = (pinstancestorage_selected)',
    'pinstancestorage_selected.NEXT = 3',
    'pinstancestorage_selected.SLOTS = [ppropertyslot_before, ppropertyslot_first, ppropertyslot_second, ppropertyslot_later, ppropertyslot_after]',
    'ppropertyslot_second.STATE = PROP_VALUE (DIRECT (POBJECT n_second))',
    'ppropertyslot_later.STATE = PROP_VALUE (DIRECT (POBJECT n_later))',
    'pdestructorcall_second.OBJECT = n_second',
    'pdestructorcall_second.OPERATION = (pdestructionoperation_inner)',
    'pdestructorcall_second.PENDING = eps',
    'S.DESTRUCTION.CALLS = [pdestructorcall_second]',
    r'$(n_a < n_b) /\ $(n_b < n_c)',
    '$weakmap_write_previous_path(S, pweakmapwrite, n_a, n_b) = ([n_b, n_a])',
    '$weakmap_write_previous_owned(S, [n_b, n_a])',
    '$throwable_field(S, n_c, "previous") = PNULL',
    *owners('S'),
    '$heap_owners($heap_graph(S), HOBJECT n_second) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
    '$node_children(S, HOBJECT n_old) = [HOBJECT n_later]',
    '$lookup(S.ENV, $ptascii("incoming65")) = (n_incoming_cell)',
    'S.STORE[n_incoming_cell] = DEFINED (POBJECT n_incoming)',
    '$heap_owners($heap_graph(S), HOBJECT n_incoming) = 2',
    *valid('S'),
    'S_effect = S[.TODO = (THROW_SEARCH n_c) :: ptask_second_tail*]',
    '$destructor_pending_parent(S_effect, pdestructorcall_second) = (pdestructionoperation_parent)',
    '$destructor_pending_anchor(S_effect, pdestructionoperation_inner, pdestructionoperation_parent)',
    '~$weakmap_write_previous_throw_boundary(S_effect, pdestructorcall_second)',
    '$weakmap_write_previous_path(S_effect, pweakmapwrite, n_b, n_b) = eps',
    '$weakmap_write_previous_path(S_effect, pweakmapwrite[.FIRSTNEW = n_b], n_a, n_b) = eps',
    'S_extra_a = S_effect[.RESULT = KNOWN (POBJECT n_a)]',
    '$heap_valid($heap_graph(S_extra_a))',
    '$weakmap_write_previous_path(S_extra_a, pweakmapwrite, n_a, n_b) = ([n_b, n_a])',
    '~$weakmap_write_previous_owned(S_extra_a, [n_b, n_a])',
    '$destructor_pending_anchor(S_extra_a, pdestructionoperation_inner, pdestructionoperation_parent)',
    '$destructor_pending_parent(S_extra_a, pdestructorcall_second) = eps',
    '$weakmap_write_previous_throw_boundary(S_extra_a, pdestructorcall_second)',
    'S_prelinked = $throwable_set_previous_id(S_effect, n_c, (n_b))',
    '$heap_valid($heap_graph(S_prelinked))',
    '$weakmap_write_previous_path(S_prelinked, pweakmapwrite, n_a, n_b) = ([n_b, n_a])',
    '$destructor_pending_parent(S_prelinked, pdestructorcall_second) = eps',
    '$weakmap_write_previous_throw_boundary(S_prelinked, pdestructorcall_second)',
    'S_rethrow = S_effect[.TODO = (THROW_SEARCH n_b) :: ptask_second_tail*]',
    '$destructor_pending_parent(S_rethrow, pdestructorcall_second) = eps',
    '$weakmap_write_previous_throw_boundary(S_rethrow, pdestructorcall_second)',
    'S_cycle = $throwable_set_previous_id($throwable_set_previous_id(S_effect, n_b, (n_c)), n_c, (n_b))',
    '$heap_valid($heap_graph(S_cycle))',
    '$weakmap_write_previous_path(S_cycle, pweakmapwrite, n_a, n_b) = eps',
    'pdestructionoperation_new = pdestructionoperation_parent[.PENDING = (n_c)]',
    'S_handoff = $destructor_result_pending(S_effect, pdestructorcall_second, eps)',
    'S_handoff.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_new]',
    'S_handoff.DESTRUCTION.CALLS = eps',
    '$throwable_field(S_handoff, n_c, "previous") = POBJECT n_b',
    '$throwable_field(S_handoff, n_b, "previous") = POBJECT n_a',
    '$throwable_field(S_handoff, n_a, "previous") = PNULL',
    '$weakmap_write_previous_path(S_handoff, pweakmapwrite, n_a, n_c) = ([n_c, n_b, n_a])',
    '$weakmap_write_previous_owned(S_handoff, [n_c, n_b, n_a])',
    *owners('S_handoff'),
    'S_handoff.ALLOCATIONS = S.ALLOCATIONS',
    'S_handoff.OBJECTPROPS = $throwable_set_previous_id(S, n_c, (n_b)).OBJECTPROPS',
    'PhpStep: S ~> S_raw',
    'S_raw = S_handoff',
    '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
    'S_next_paused = $drive_steps(S, 1)',
    'S_next_paused.COMPLETION = BUDGET',
    'S_next = S_next_paused[.COMPLETION = NORMAL]',
    'S_next.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cleanup) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) :: ptask_cleanup_tail*',
    'pdestructionrelease_cleanup.JOBS = [DESTRUCTION_VALUE (HOBJECT n_second)]',
    'pdestructionoperation_cleanup.SOURCE = THROW_SEARCH n_c',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) = eps',
    'S_next.DESTRUCTION.OPERATIONS = [pdestructionoperation_cleanup, pdestructionoperation_inner, pdestructionoperation_new]',
    *owners('S_next'),
    *valid('S_next'),
    '$drive_steps(S, 2) = $drive_steps(S_next, 1)',
    *seek('S_next', 'S_child_pin', 'CHILD_PIN'),
    *owners('S_child_pin'), *valid('S_child_pin'),
    *seek('S_child_pin', 'S_later_enter', 'LATER_ENTER'),
    'S_later_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall_later) :: ptask_later_enter*',
    'pdestructorcall_later.OPERATION = (pdestructionoperation_inner)',
    'pdestructorcall_later.PENDING = eps',
    *owners('S_later_enter'), *valid('S_later_enter'),
    *seek('S_later_enter', 'S_later', 'LATER_READ'),
    '$instance_storage_for(S_later, n_old) = (pinstancestorage_later)',
    'pinstancestorage_later.NEXT = 4',
    'pinstancestorage_later.SLOTS = pinstancestorage_selected.SLOTS',
    '$weakmap_write_selected_child(pinstancestorage_later) = (n_later)',
    'S_later.DESTRUCTION.CALLS = [pdestructorcall_later]',
    'S_later.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_new]',
    '$weakmap_write_previous_path(S_later, pweakmapwrite, n_a, n_c) = ([n_c, n_b, n_a])',
    *owners('S_later'),
    '$heap_owners($heap_graph(S_later), HOBJECT n_incoming) = 2',
    '$heap_owners($heap_graph(S_later), HOBJECT n_later) = 2',
    '$heap_owners($heap_graph(S_later), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_later), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S_later), HOBJECT n_key) = 2',
    *valid('S_later'),
    'S_later.TODO = (KEY_READ_DIM poperand_key z KEY_R) :: ptask_read_tail*',
    'S_later.ORIGIN = (porigin_read)',
    'paccess_initial = $access_record(S_later, porigin_read, z, ACCESS_READ KEY_R, BASE_VALUE S_later.RESULT, poperand_key, KNOWN PNULL, KEY_READ_DIM poperand_key z KEY_R, (n_map), true)',
    'paccess_read = paccess_initial[.SELECTED = $rcontainer_selected(S_later, S_later.RESULT)][.OFFSET = POBJECT n_key]',
    '$weakmap_write_callback_read(S_later, paccess_read)',
    'S_later.FRAMES = [pframe_later]',
    'pdestructorcall_later.RELEASE = (pdestructionrelease_later_original)',
    'pdestructionrelease_later_empty = pdestructionrelease_later_original[.JOBS = eps]',
    'pframe_later.TODO = (DESTRUCTOR_RESULT pdestructorcall_later) :: (DESTRUCTOR_RELEASE pdestructionrelease_later_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_later) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_new) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_frame_tail*',
    'S_frame = $call_frame_scope(S_later, pframe_later, eps)',
    'S_tasks = $destructor_saved_frame_scope($api_saved_frame_scope($parameter_string_frame_scope(S_frame, pframe_later, eps), pframe_later, eps), pframe_later)',
    'S_after_result = $call_after_origin(S_tasks, DESTRUCTOR_RESULT pdestructorcall_later)',
    'S_after_child = $call_after_origin(S_after_result, DESTRUCTOR_RELEASE pdestructionrelease_later_empty)',
    'S_after_root = $call_after_origin(S_after_child, DESTRUCTOR_RELEASE pdestructionrelease_root_empty)',
    'S_after_inner = $call_after_origin(S_after_root, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner)',
    'S_future = $call_after_origin(S_after_inner, DESTRUCTOR_RELEASE pdestructionrelease_old_empty)',
    'S_future.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]',
    'S_future.DESTRUCTION.CALLS = eps',
    'S_future.DESTRUCTION.RELEASES = eps',
    '~$destructor_operation_valid(S_future, pdestructionoperation_new)',
    '$eager_operation_task_valid(S_future, pdestructionoperation_new)',
    'S_read_paused = $drive_steps(S_later, 1)',
    'S_read_paused.COMPLETION = BUDGET',
    'S_read = S_read_paused[.COMPLETION = NORMAL]',
    'S_read.RESULT = KNOWN (POBJECT n_incoming)',
    '$heap_owners($heap_graph(S_read), HOBJECT n_incoming) = 3',
    *owners('S_read'),
    'S_read.OBJECTPROPS = S_later.OBJECTPROPS',
    'S_read.ALLOCATIONS = S_later.ALLOCATIONS',
    *seek('S_read', 'S_retired', 'RETIRED'),
    *owners('S_retired'), *valid('S_retired'),
    *seek('S_retired', 'S_parent', 'PARENT_EXIT'),
    'S_parent.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]',
    *owners('S_parent'), *valid('S_parent'),
]

review.CASES = {'finite-previous-second-handoff-state': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
