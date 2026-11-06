#!/usr/bin/env python3
"""Actual shared-Child exception handoff, later cleanup, owners and budgets."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc64_peer_shared_throw_slots.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_first) :: '
    '(INSTANCE_STORAGE_STEP pinstancestorage_first) :: ptask_first_tail* '
    '-- if pinstancestorage_first.NEXT = 2 '
    '-- if pinstancestorage_first.SLOTS = [ppropertyslot_lead, ppropertyslot_first, ppropertyslot_last, ppropertyslot_later, ppropertyslot_tail] '
    '-- if ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_shared)) '
    '-- if ppropertyslot_last.STATE = ppropertyslot_first.STATE '
    '-- if pdestructionrelease_first.JOBS = [DESTRUCTION_VALUE (HOBJECT n_shared)] '
    '-- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_outer] '
    '-- if pdestructionoperation_outer.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite '
    '-- if pweakmapwrite.OLD.VALUE = POBJECT n_old '
    '-- if pinstancestorage_first.OBJECT = n_old '
    '-- if pweakmapwrite.ACCESS.VALUE = PNULL')
DECLARATIONS = r'''syntax pgc64stage = SHARED_READ | SHARED_RESULT | SHARED_PIN | TAIL_ENTER | TAIL_READ | ROOT_DONE | RETIRED | OUTER_EXIT | CLAIM_DISCARD
dec $gc64_call_object(pstate) : nat?
def $gc64_call_object(S) = (pdestructorcall.OBJECT)
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $gc64_call_object(S) = eps -- otherwise
dec $gc64_at(pstate, pgc64stage, nat, nat, nat) : bool
def $gc64_at(S, SHARED_READ, n_old, n_shared, n_tail) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if $gc64_call_object(S) = (n_shared)
def $gc64_at(S, SHARED_RESULT, n_old, n_shared, n_tail) = true
  -- if S.TODO = (THROW_SEARCH n) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_shared
def $gc64_at(S, SHARED_PIN, n_old, n_shared, n_tail) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n_shared
def $gc64_at(S, TAIL_ENTER, n_old, n_shared, n_tail) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_tail
def $gc64_at(S, TAIL_READ, n_old, n_shared, n_tail) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if $gc64_call_object(S) = (n_tail)
def $gc64_at(S, ROOT_DONE, n_old, n_shared, n_tail) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n_old /\ pinstancestorage.NEXT = 5
def $gc64_at(S, RETIRED, n_old, n_shared, n_tail) = true
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: ptask_tail*
  -- if pdestructionoperation_inner.SOURCE = THROW_SEARCH n
def $gc64_at(S, OUTER_EXIT, n_old, n_shared, n_tail) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_outer) :: (ACCESS_RESUME paccess) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pdestructionoperation_outer.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old /\ paccess = pweakmapwrite.ACCESS
def $gc64_at(S, CLAIM_DISCARD, n_old, n_shared, n_tail) = true
  -- if S.TODO = (THROW_SEARCH n) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
def $gc64_at(S, pgc64stage, n_old, n_shared, n_tail) = false -- otherwise
dec $gc64_seek(pstate, pgc64stage, nat, nat, nat, nat) : pstate
def $gc64_seek(S, pgc64stage, n_old, n_shared, n_tail, n) = S
  -- if $gc64_at(S, pgc64stage, n_old, n_shared, n_tail)
def $gc64_seek(S, pgc64stage, n_old, n_shared, n_tail, n) = $gc64_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc64stage, n_old, n_shared, n_tail, $nabs($(n - 1)))
  -- if ~$gc64_at(S, pgc64stage, n_old, n_shared, n_tail) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc64_seek(S, pgc64stage, n_old, n_shared, n_tail, 0) = S
  -- if ~$gc64_at(S, pgc64stage, n_old, n_shared, n_tail)
def $gc64_seek(S, pgc64stage, n_old, n_shared, n_tail, n) = S
  -- if ~$gc64_at(S, pgc64stage, n_old, n_shared, n_tail)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def seek(before, state, stage):
    return [f'{state}_reached = $gc64_seek({before}, {stage}, n_old, n_shared, n_tail, 4000)',
            f'{state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]']


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$destruction_state_valid({state})', f'$call_descriptors_valid({state})']


SETUP = [
    'pweakmapwrite.ACCESS.OBJECT = (n_map)',
    'pweakmapwrite.ACCESS.OFFSET = POBJECT n_key',
    'ppropertyslot_lead.STATE = PROP_VALUE (DIRECT (PINT 17))',
    'ppropertyslot_later.STATE = PROP_VALUE (DIRECT (POBJECT n_tail))',
    'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (PINT 23))',
    'n_shared =/= n_tail',
    'ppropertyslot_original* = pinstancestorage_first.SLOTS',
    'pdestructionoperation_outer.PENDING = (n_a)',
    'pdestructionoperation_inner.SOURCE = THROW_SEARCH n_a',
    'pdestructionoperation_inner.PENDING = eps',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) = eps',
    '$throwable_field(S, n_a, "previous") = PNULL',
    '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_shared) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_tail) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_a) = 1',
    '$node_children(S, HOBJECT n_old) = [HOBJECT n_shared, HOBJECT n_tail]',
    '$lookup(S.ENV, $ptascii("oldWatch64Peer")) = (n_old_watch_cell)',
    'S.STORE[n_old_watch_cell] = DEFINED (POBJECT n_old_watch)',
    '$lookup(S.ENV, $ptascii("sharedWatch64Peer")) = (n_shared_watch_cell)',
    'S.STORE[n_shared_watch_cell] = DEFINED (POBJECT n_shared_watch)',
    '$lookup(S.ENV, $ptascii("tailWatch64Peer")) = (n_tail_watch_cell)',
    'S.STORE[n_tail_watch_cell] = DEFINED (POBJECT n_tail_watch)',
    '$weakref_get(S, n_old_watch) = PNULL',
    *valid('S'),
    'S_drop_paused = $drive_steps(S, 1)',
    'S_drop_paused.COMPLETION = BUDGET',
    'S_drop = S_drop_paused[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_drop), HOBJECT n_shared) = 1',
    'S_drop.DESTRUCTION.CALLS = eps',
    '~(n_shared <- S_drop.DESTRUCTION.CALLED)',
    '$drive_steps(S, 2) = $drive_steps(S_drop, 1)',
    *seek('S_drop', 'S_shared_read', 'SHARED_READ'),
    '$instance_storage_for(S_shared_read, n_old) = (pinstancestorage_selected)',
    'pinstancestorage_selected.SLOTS = ppropertyslot_original*',
    'pinstancestorage_selected.NEXT = 3',
    '$weakmap_write_selected_child(pinstancestorage_selected) = (n_shared)',
    '$heap_owners($heap_graph(S_shared_read), HOBJECT n_shared) = 2',
    '$heap_owners($heap_graph(S_shared_read), HOBJECT n_a) = 1',
    '$node_children(S_shared_read, HOBJECT n_old) = [HOBJECT n_tail]',
    *valid('S_shared_read'),
]

HANDOFF = [
    *seek('S_shared_read', 'S_result', 'SHARED_RESULT'),
    'S_result.TODO = (THROW_SEARCH n_b) :: (DESTRUCTOR_RESULT pdestructorcall_shared) :: ptask_result_tail*',
    'pdestructorcall_shared.OPERATION = (pdestructionoperation_inner)',
    'pdestructorcall_shared.PENDING = eps',
    'S_result.DESTRUCTION.CALLS = [pdestructorcall_shared]',
    'S_result.DESTRUCTION.CALLED = [n_old, n_shared]',
    'S_result.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_outer]',
    'pdestructorcall_shared.OBJECT = n_shared',
    '$(n_a < n_b)',
    '$weakmap_write_fresh_pending(S_result, pweakmapwrite, (n_a))',
    '$weakmap_write_fresh_pending(S_result, pweakmapwrite, (n_b))',
    '$throwable_field(S_result, n_a, "previous") = PNULL',
    '$throwable_field(S_result, n_b, "previous") = PNULL',
    '$heap_owners($heap_graph(S_result), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_result), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_result), HOBJECT n_shared) = 1',
    *valid('S_result'),
    'S_effect = S_result[.TODO = (THROW_SEARCH n_b) :: ptask_result_tail*]',
    '$destructor_pending_parent(S_effect, pdestructorcall_shared) = (pdestructionoperation_outer)',
    'S_no_called = S_effect[.DESTRUCTION.CALLED = [n_old]]',
    '$heap_graph(S_no_called) = $heap_graph(S_effect)',
    '$instance_storage_basic(S_no_called, pinstancestorage_selected)',
    '$destructor_pending_parent(S_no_called, pdestructorcall_shared) = eps',
    'S_default = $destructor_result_pending(S_no_called, pdestructorcall_shared, eps)',
    'S_default = $destructor_resume_pending($destructor_chain_pending(S_no_called[.DESTRUCTION.CALLS = eps], pdestructorcall_shared), pdestructorcall_shared)',
    'S_default.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner[.PENDING = (n_b)], pdestructionoperation_outer]',
    '$throwable_field(S_default, n_b, "previous") = PNULL',
    'S_two_a = S_effect[.RESULT = KNOWN (POBJECT n_a)]',
    '$heap_owners($heap_graph(S_two_a), HOBJECT n_a) = 2',
    '$heap_valid($heap_graph(S_two_a))',
    '$destructor_pending_parent(S_two_a, pdestructorcall_shared) = eps',
    'pdestructorcall_wrong = pdestructorcall_shared[.OBJECT = n_tail]',
    '$destructor_pending_parent(S_effect[.DESTRUCTION.CALLS = [pdestructorcall_wrong]], pdestructorcall_wrong) = eps',
    'pdestructorcall_line = pdestructorcall_shared[.LINE = 999]',
    '$destructor_pending_parent(S_effect[.DESTRUCTION.CALLS = [pdestructorcall_line]], pdestructorcall_line) = eps',
    'pdestructionoperation_new = pdestructionoperation_outer[.PENDING = (n_b)]',
    'S_handoff = $destructor_result_pending(S_effect, pdestructorcall_shared, eps)',
    'S_handoff.DESTRUCTION.CALLS = eps',
    'S_handoff.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_new]',
    '$throwable_field(S_handoff, n_b, "previous") = POBJECT n_a',
    '$throwable_field(S_handoff, n_a, "previous") = PNULL',
    '$heap_owners($heap_graph(S_handoff), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_handoff), HOBJECT n_b) = 1',
    'S_handoff.ALLOCATIONS = S_result.ALLOCATIONS',
    'S_handoff.OBJECTPROPS = $throwable_set_previous_id(S_result, n_b, (n_a)).OBJECTPROPS',
    '$destructor_pending_parent(S_handoff, pdestructorcall_shared) = eps',
    'S_zero = $drive_steps(S_result, 0)',
    'S_zero = S_result[.COMPLETION = BUDGET]',
    'PhpStep: S_result ~> S_raw',
    'S_raw = S_handoff',
    'S_next_paused = $drive_steps(S_result, 1)',
    'S_next_paused.COMPLETION = BUDGET',
    'S_next = S_next_paused[.COMPLETION = NORMAL]',
    'S_next.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cleanup) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) :: ptask_cleanup_tail*',
    'pdestructionrelease_cleanup.JOBS = [DESTRUCTION_VALUE (HOBJECT n_shared)]',
    'pdestructionoperation_cleanup.SOURCE = THROW_SEARCH n_b',
    'pdestructionoperation_cleanup.PENDING = eps',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) = eps',
    'S_next.DESTRUCTION.OPERATIONS = [pdestructionoperation_cleanup, pdestructionoperation_inner, pdestructionoperation_new]',
    '$throwable_field(S_next, n_b, "previous") = POBJECT n_a',
    '$heap_owners($heap_graph(S_next), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_next), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_next), HOBJECT n_shared) = 1',
    '$drive_steps(S_result, 2) = $drive_steps(S_next, 1)',
    *valid('S_next'),
    '$weakmap_write_previous_chain(S_next, pdestructionoperation_inner, pdestructionoperation_new, pweakmapwrite, S_next.DESTRUCTION.OPERATIONS)',
    'pdestructionoperation_wrong_source = pdestructionoperation_cleanup[.SOURCE = THROW_SEARCH n_a]',
    '~$weakmap_write_previous_chain(S_next[.DESTRUCTION.OPERATIONS = [pdestructionoperation_wrong_source, pdestructionoperation_inner, pdestructionoperation_new]], pdestructionoperation_inner, pdestructionoperation_new, pweakmapwrite, [pdestructionoperation_wrong_source, pdestructionoperation_inner, pdestructionoperation_new])',
    'S_cleanup_no_called = S_next[.DESTRUCTION.CALLED = [n_old]]',
    '$heap_graph(S_cleanup_no_called) = $heap_graph(S_next)',
    '$instance_storage_basic(S_cleanup_no_called, pinstancestorage_selected)',
    '~$weakmap_write_previous_chain(S_cleanup_no_called, pdestructionoperation_inner, pdestructionoperation_new, pweakmapwrite, S_cleanup_no_called.DESTRUCTION.OPERATIONS)',
    'ptask_cleanup_tail* = (DESTRUCTOR_RELEASE pdestructionrelease_child_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_selected) :: ptask_after_root_pin*',
    'pinstancestorage_rewind = pinstancestorage_selected[.NEXT = 2]',
    'S_rewind = S_next[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cleanup) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) :: (DESTRUCTOR_RELEASE pdestructionrelease_child_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_rewind) :: ptask_after_root_pin*][.OBJECTPROPS = $objectprops_set(S_next.OBJECTPROPS, n_old, [ppropertyslot_lead[.STATE = PROP_UNSET], ppropertyslot_first[.STATE = PROP_UNSET], ppropertyslot_last, ppropertyslot_later, ppropertyslot_tail])]',
    '$instance_storage_basic(S_rewind, pinstancestorage_rewind)',
    '$instance_storage_state_valid(S_rewind)',
    '$heap_valid($heap_graph(S_rewind))',
    '$heap_owners($heap_graph(S_rewind), HOBJECT n_shared) = 2',
    '$heap_count(HOBJECT n_shared, $node_children(S_rewind, HOBJECT n_old)) = 1',
    '~$weakmap_write_previous_chain(S_rewind, pdestructionoperation_inner, pdestructionoperation_new, pweakmapwrite, S_rewind.DESTRUCTION.OPERATIONS)',
    *seek('S_next', 'S_shared_pin', 'SHARED_PIN'),
    '$weakref_get(S_shared_pin, n_shared_watch) = PNULL',
    '$heap_owners($heap_graph(S_shared_pin), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_shared_pin), HOBJECT n_b) = 1',
    *valid('S_shared_pin'),
    *seek('S_shared_pin', 'S_tail_enter', 'TAIL_ENTER'),
    'S_tail_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall_tail) :: ptask_tail_enter*',
    'pdestructorcall_tail.OPERATION = (pdestructionoperation_inner)',
    'pdestructorcall_tail.PENDING = eps',
    'S_tail_enter.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_new]',
    '~((HOBJECT n_shared) <- S_tail_enter.ALLOCATIONS)',
    *valid('S_tail_enter'),
    *seek('S_tail_enter', 'S_tail', 'TAIL_READ'),
    '$instance_storage_for(S_tail, n_old) = (pinstancestorage_tail)',
    'pinstancestorage_tail.SLOTS = ppropertyslot_original*',
    'pinstancestorage_tail.NEXT = 4',
    '$weakmap_write_selected_child(pinstancestorage_tail) = (n_tail)',
    'S_tail.DESTRUCTION.CALLS = [pdestructorcall_tail]',
    'S_tail.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_new]',
    '$throwable_field(S_tail, n_b, "previous") = POBJECT n_a',
    '$heap_owners($heap_graph(S_tail), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_tail), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_tail), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_tail), HOBJECT n_tail) = 2',
    '$heap_owners($heap_graph(S_tail), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S_tail), HOBJECT n_key) = 2',
    '$weakref_get(S_tail, n_old_watch) = PNULL',
    '$node_children(S_tail, HOBJECT n_old) = eps',
    '$weakmap_write_declared_ancestry(S_tail, pdestructorcall_tail) = eps',
    '$weakmap_write_previous_ancestry(S_tail, pdestructorcall_tail) = (pweakmapwrite)',
    '$weakmap_write_previous_child_call(S_tail, pweakmapwrite, pinstancestorage_tail, pdestructorcall_tail)',
    *valid('S_tail'),
]

READ = [
    'S_tail.CURRENT = (pcallcontext_tail)',
    'S_tail.FRAMES = [pframe_tail]',
    'pdestructorcall_tail.RELEASE = (pdestructionrelease_tail_original)',
    'pdestructionrelease_tail_empty = pdestructionrelease_tail_original[.JOBS = eps]',
    'pframe_tail.TODO = (DESTRUCTOR_RESULT pdestructorcall_tail) :: (DESTRUCTOR_RELEASE pdestructionrelease_tail_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_tail) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_new) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_frame_tail*',
    'S_tail.TODO = (KEY_READ_DIM poperand_key z KEY_R) :: ptask_read_tail*',
    'S_tail.ORIGIN = (porigin_read)',
    'paccess_initial = $access_record(S_tail, porigin_read, z, ACCESS_READ KEY_R, BASE_VALUE S_tail.RESULT, poperand_key, KNOWN PNULL, KEY_READ_DIM poperand_key z KEY_R, (n_map), true)',
    'paccess_read = paccess_initial[.SELECTED = $rcontainer_selected(S_tail, S_tail.RESULT)][.OFFSET = POBJECT n_key]',
    '$weakmap_write_callback_read(S_tail, paccess_read)',
    '~$weakmap_write_callback_read(S_tail, paccess_read[.SELECTED = KNOWN (POBJECT n_map)])',
    'S_no_previous = $throwable_set_previous_id(S_tail, n_b, eps)[.RESULT = KNOWN (POBJECT n_a)]',
    '$heap_valid($heap_graph(S_no_previous))',
    '$heap_owners($heap_graph(S_no_previous), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_no_previous), HOBJECT n_b) = 1',
    '$instance_storage_basic(S_no_previous, pinstancestorage_tail)',
    '$weakmap_write_previous_ancestry(S_no_previous, pdestructorcall_tail) = eps',
    'pdestructionoperation_retag = pdestructionoperation_inner[.SOURCE = THROW_SEARCH n_b]',
    'pdestructorcall_retag = pdestructorcall_tail[.OPERATION = (pdestructionoperation_retag)]',
    'pframe_retag = pframe_tail[.TODO = (DESTRUCTOR_RESULT pdestructorcall_retag) :: (DESTRUCTOR_RELEASE pdestructionrelease_tail_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_tail) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_retag) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_new) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_frame_tail*]',
    'S_retag = S_tail[.DESTRUCTION.CALLS = [pdestructorcall_retag]][.FRAMES = [pframe_retag]][.DESTRUCTION.OPERATIONS = [pdestructionoperation_retag, pdestructionoperation_new]]',
    '$heap_graph(S_retag) = $heap_graph(S_tail)',
    '$weakmap_write_previous_ancestry(S_retag, pdestructorcall_retag) = eps',
    'pweakmapwrite_cells = pweakmapwrite[.KEYCELL = pweakmapwrite.MAPCELL]',
    'pdestructionoperation_cells = pdestructionoperation_new[.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite_cells]',
    'pframe_cells = pframe_tail[.TODO = (DESTRUCTOR_RESULT pdestructorcall_tail) :: (DESTRUCTOR_RELEASE pdestructionrelease_tail_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_tail) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cells) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite_cells) :: ptask_frame_tail*]',
    'S_cells = S_tail[.FRAMES = [pframe_cells]][.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_cells]]',
    '$heap_graph(S_cells) = $heap_graph(S_tail)',
    '~$weakmap_write_callback_read(S_cells, paccess_read)',
    'S_frame = $call_frame_scope(S_tail, pframe_tail, eps)',
    'S_tasks = $destructor_saved_frame_scope($api_saved_frame_scope($parameter_string_frame_scope(S_frame, pframe_tail, eps), pframe_tail, eps), pframe_tail)',
    'S_after_result = $call_after_origin(S_tasks, DESTRUCTOR_RESULT pdestructorcall_tail)',
    'S_after_child = $call_after_origin(S_after_result, DESTRUCTOR_RELEASE pdestructionrelease_tail_empty)',
    'S_after_root = $call_after_origin(S_after_child, DESTRUCTOR_RELEASE pdestructionrelease_root_empty)',
    'S_after_inner = $call_after_origin(S_after_root, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner)',
    'S_future = $call_after_origin(S_after_inner, DESTRUCTOR_RELEASE pdestructionrelease_old_empty)',
    'S_future.DESTRUCTION.RELEASES = eps',
    'S_future.DESTRUCTION.CALLS = eps',
    'S_future.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]',
    '~$destructor_operation_valid(S_future, pdestructionoperation_new)',
    '$eager_operation_task_valid(S_future, pdestructionoperation_new)',
    'pdestructorcall_bad_future = pdestructorcall_tail[.RELEASE = (pdestructionrelease_tail_original[.JOBS = [DESTRUCTION_TEMP (HOBJECT n_tail)]])]',
    'S_future_bad = S_future[.TODO = (DESTRUCTOR_RESULT pdestructorcall_bad_future) :: (DESTRUCTOR_RELEASE pdestructionrelease_tail_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_tail) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_new) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_frame_tail*]',
    '~$eager_operation_task_valid(S_future_bad, pdestructionoperation_new)',
    'S_read_paused = $drive_steps(S_tail, 1)',
    'S_read_paused.COMPLETION = BUDGET',
    'S_read = S_read_paused[.COMPLETION = NORMAL]',
    'S_read.RESULT = KNOWN PNULL',
    'S_read.ALLOCATIONS = S_tail.ALLOCATIONS',
    'S_read.OBJECTPROPS = S_tail.OBJECTPROPS',
    '$heap_owners($heap_graph(S_read), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_read), HOBJECT n_tail) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S_read), HOBJECT n_key) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_read), HOBJECT n_b) = 1',
]


def ending():
    chunks = ['B|', 's|', '1', '|', 'O|', '1', '|', 'U|'] + ['1', '|'] * 2
    chunks += ['C|', '1', '|', 'I|'] + ['1', '|'] * 2
    chunks += ['L|', '1', '|', 'J|'] + ['1', '|'] * 2
    chunks += ['T|', 'peer-child-64', '|', '10', '|', '__destruct', '|', '66', '|', '1', '|', '0', '|']
    chunks += ['P|', 'peer-own-64', '|', '34', '|', '1', '|', 'R|', '1', '|', '0', '|'] + ['1', '|'] * 5
    chunks += ['m|', '1', '|', 'K|', '1', '|']
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(x) + ')' for x in chunks) + ']'


FINISH = [
    *seek('S_read', 'S_root_done', 'ROOT_DONE'),
    '$weakref_get(S_root_done, n_tail_watch) = PNULL',
    '$heap_owners($heap_graph(S_root_done), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_root_done), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_root_done), HOBJECT n_b) = 1',
    *valid('S_root_done'),
    *seek('S_root_done', 'S_retired', 'RETIRED'),
    '$weakref_get(S_retired, n_old_watch) = PNULL',
    '$heap_owners($heap_graph(S_retired), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_retired), HOBJECT n_b) = 1',
    *valid('S_retired'),
    *seek('S_retired', 'S_outer', 'OUTER_EXIT'),
    'S_outer.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]',
    '$heap_owners($heap_graph(S_outer), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_outer), HOBJECT n_b) = 1',
    *valid('S_outer'),
    *seek('S_outer', 'S_claim', 'CLAIM_DISCARD'),
    'S_claim.TODO = (THROW_SEARCH n_b) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    '$task_nodes(WEAKMAP_WRITE_CLAIM pweakmapwrite) = eps',
    *valid('S_claim'),
    'S_claim_paused = $drive_steps(S_claim, 1)',
    'S_claim_paused.COMPLETION = BUDGET',
    'S_after_claim = S_claim_paused[.COMPLETION = NORMAL]',
    'S_after_claim.TODO = (THROW_SEARCH n_b) :: ptask_claim_tail*',
    'S_after_claim.OBJECTPROPS = S_claim.OBJECTPROPS',
    'S_after_claim.ALLOCATIONS = S_claim.ALLOCATIONS',
    '$heap_owners($heap_graph(S_after_claim), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_after_claim), HOBJECT n_b) = 1',
    'S_done = $drive_steps(S_after_claim, 4000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
    r'S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
    'S_done.DESTRUCTION.CALLS = eps', 'S_done.ITERATORS = eps',
    '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_shared) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_tail) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_a) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_b) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))', ending(),
]

SOURCE_BOUNDARY = SOURCE.replace(
    "             (int) ($result64Peer === 31), '|';\n    }\n}\nclass GC64OldPeer",
    "             (int) ($result64Peer === 31), '|';\n"
    "        throw new Exception('peer-later-64');\n    }\n}\nclass GC64OldPeer")
assert SOURCE_BOUNDARY != SOURCE
SOURCE_BOUNDARY = SOURCE_BOUNDARY.replace(
    "}\necho 'R|'",
    "    echo 'Q|', $error64Peer->getPrevious()->getPrevious()->getMessage(), '|',\n"
    "         $error64Peer->getPrevious()->getPrevious()->getLine(), '|',\n"
    "         (int) ($error64Peer->getPrevious()->getPrevious()->getPrevious() === null), '|';\n"
    "}\necho 'R|'")
BOUNDARY_STAGE = (
    'S.TODO = (THROW_SEARCH n_c) :: (DESTRUCTOR_RESULT pdestructorcall_tail) :: '
    '(DESTRUCTOR_RELEASE pdestructionrelease_tail_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_tail) :: ptask_boundary_rest* '
    '-- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_parent] '
    '-- if pdestructionoperation_parent.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite '
    '-- if pdestructionoperation_parent.PENDING = (n_b) '
    '-- if pdestructionoperation_inner.SOURCE = THROW_SEARCH n_a '
    '-- if $throwable_field(S, n_b, "previous") = POBJECT n_a '
    '-- if pweakmapwrite.OLD.VALUE = POBJECT n_old '
    '-- if pweakmapwrite.ACCESS.VALUE = PNULL '
    r'-- if pinstancestorage_tail.OBJECT = n_old /\ pinstancestorage_tail.NEXT = 4 '
    '-- if pdestructorcall_tail.OBJECT = n_tail')
BOUNDARY = [
    'S.CURRENT = eps', 'S.FRAMES = eps',
    'S.DESTRUCTION.CALLS = [pdestructorcall_tail]',
    'S.DESTRUCTION.CALLED = [n_old, n_shared, n_tail]',
    'pinstancestorage_tail.SLOTS = [ppropertyslot_lead, ppropertyslot_first, ppropertyslot_last, ppropertyslot_later, ppropertyslot_tail]',
    'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_shared))',
    'ppropertyslot_last.STATE = ppropertyslot_first.STATE',
    'ppropertyslot_later.STATE = PROP_VALUE (DIRECT (POBJECT n_tail))',
    'pdestructorcall_tail.OPERATION = (pdestructionoperation_inner)',
    'pdestructorcall_tail.PENDING = eps',
    'pdestructionoperation_inner.PENDING = eps',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) = eps',
    r'$(n_a < n_b) /\ $(n_b < n_c)',
    '$weakmap_write_fresh_pending(S, pweakmapwrite, (n_c))',
    '$throwable_field(S, n_a, "previous") = PNULL',
    '$throwable_field(S, n_c, "previous") = PNULL',
    '$heap_owners($heap_graph(S), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_c) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_tail) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
    '~((HOBJECT n_shared) <- S.ALLOCATIONS)',
    '$node_children(S, HOBJECT n_old) = eps',
    '$weakmap_write_claim_valid(S, pweakmapwrite)',
    '$weakmap_write_declared_pin(S, pweakmapwrite, pinstancestorage_tail)',
    '$weakmap_write_previous_ancestry(S, pdestructorcall_tail) = (pweakmapwrite)',
    '$weakmap_write_previous_child_call(S, pweakmapwrite, pinstancestorage_tail, pdestructorcall_tail)',
    '$destructor_result_valid(S, pdestructorcall_tail)',
    '$heap_valid($heap_graph(S))',
    '$destruction_state_valid(S)',
    'S_effect = S[.TODO = (THROW_SEARCH n_c) :: (DESTRUCTOR_RELEASE pdestructionrelease_tail_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_tail) :: ptask_boundary_rest*]',
    '$destructor_pending_parent(S_effect, pdestructorcall_tail) = eps',
    '$weakmap_write_previous_throw_boundary(S_effect, pdestructorcall_tail)',
    'S_no_called = S_effect[.DESTRUCTION.CALLED = [n_old, n_shared]]',
    '$heap_graph(S_no_called) = $heap_graph(S_effect)',
    '~$weakmap_write_previous_throw_boundary(S_no_called, pdestructorcall_tail)',
    '~$weakmap_write_previous_throw_boundary(S_effect[.DESTRUCTION.CALLS = eps], pdestructorcall_tail)',
    'pdestructorcall_bad = pdestructorcall_tail[.LINE = 999]',
    '~$weakmap_write_previous_throw_boundary(S_effect[.DESTRUCTION.CALLS = [pdestructorcall_bad]], pdestructorcall_bad)',
    'ptask_boundary_rest* = (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_parent) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_after_claim*',
    'pdestructionoperation_old_history = pdestructionoperation_parent[.PENDING = (n_a)]',
    'S_old_history = $throwable_set_previous_id(S_effect, n_b, eps)[.RESULT = KNOWN (POBJECT n_b)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_old_history]][.TODO = (THROW_SEARCH n_c) :: (DESTRUCTOR_RELEASE pdestructionrelease_tail_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_tail) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_old_history) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_after_claim*]',
    '$heap_valid($heap_graph(S_old_history))',
    '$heap_owners($heap_graph(S_old_history), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_old_history), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_old_history), HOBJECT n_c) = 1',
    '$weakmap_write_declared_ancestry(S_old_history, pdestructorcall_tail) = (pweakmapwrite)',
    '~$weakmap_write_previous_throw_boundary(S_old_history, pdestructorcall_tail)',
    '$destructor_pending_parent(S_old_history, pdestructorcall_tail) = (pdestructionoperation_old_history)',
    'S_raw_expected = S[.COMPLETION = UNSUPPORTED "further Child throw during WeakMap current-row cleanup"]',
    '$return_discard(S_effect, DESTRUCTOR_RESULT pdestructorcall_tail) = S_raw_expected',
    'PhpStep: S ~> S_raw',
    'S_raw = S_raw_expected',
    '$heap_graph(S_raw) = $heap_graph(S)',
    '$throwable_field(S_raw, n_c, "previous") = PNULL',
    '$throwable_field(S_raw, n_b, "previous") = POBJECT n_a',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_stopped = $drive_steps(S, 1)',
    'S_stopped.COMPLETION = UNSUPPORTED "further Child throw during WeakMap current-row cleanup"',
    'S_stopped.EVENTS = S.EVENTS',
    '$throwable_field(S_stopped, n_c, "previous") = PNULL',
    '$throwable_field(S_stopped, n_b, "previous") = POBJECT n_a',
    '$heap_owners($heap_graph(S_stopped), HOBJECT n_a) = 1',
    '$heap_owners($heap_graph(S_stopped), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_stopped), HOBJECT n_c) = 1',
    '$heap_owners($heap_graph(S_stopped), HOBJECT n_tail) = 1',
]

review.CASES = {'shared-child-pending-owner-state': {
    'source': SOURCE, 'stage': STAGE,
    'checks': [*SETUP, *HANDOFF, *READ, *FINISH]},
    'shared-child-further-throw-refusal-state': {
        'source': SOURCE_BOUNDARY, 'stage': BOUNDARY_STAGE, 'checks': BOUNDARY}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
