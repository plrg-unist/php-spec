#!/usr/bin/env python3
"""Actual outer-array copies and CV drops preserve shared descendant edges."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc66_peer_shared_array_read.php').read_text().replace(
    '$throw66Peer = false;', '$throw66Peer = true;')
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if S.CURRENT = eps '
    '-- if $weakmap_write_plan(S[.COMPLETION = NORMAL]) = (pweakmapwrite) '
    '-- if pweakmapwrite.ACCESS.VALUE = PARRAY n_outer '
    '-- if pweakmapwrite.OLD.VALUE = POBJECT n_old')
DECLARATIONS = r'''syntax pgc66stage = ARRAY_READ | ARRAY_RELEASE | PARENT_EXIT
dec $gc66_at(pstate, pgc66stage, nat, nat) : bool
def $gc66_at(S, ARRAY_READ, n_callback, n_outer) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_callback
def $gc66_at(S, ARRAY_RELEASE, n_callback, n_outer) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_outer)]
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_callback
def $gc66_at(S, PARENT_EXIT, n_callback, n_outer) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME paccess) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_callback
  -- if ~((HOBJECT n_callback) <- S.ALLOCATIONS)
def $gc66_at(S, pgc66stage, n_callback, n_outer) = false -- otherwise
dec $gc66_seek(pstate, pgc66stage, nat, nat, nat) : pstate
def $gc66_seek(S, pgc66stage, n_callback, n_outer, n) = S
  -- if $gc66_at(S, pgc66stage, n_callback, n_outer)
def $gc66_seek(S, pgc66stage, n_callback, n_outer, n) = $gc66_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc66stage, n_callback, n_outer, $nabs($(n - 1)))
  -- if ~$gc66_at(S, pgc66stage, n_callback, n_outer) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc66_seek(S, pgc66stage, n_callback, n_outer, 0) = S
  -- if ~$gc66_at(S, pgc66stage, n_callback, n_outer)
def $gc66_seek(S, pgc66stage, n_callback, n_outer, n) = S
  -- if ~$gc66_at(S, pgc66stage, n_callback, n_outer)
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


def graph(state, outer_owners):
    return [f'$heap_owners($heap_graph({state}), HARRAY n_outer) = {outer_owners}',
            f'$heap_owners($heap_graph({state}), HARRAY n_shared) = 2',
            f'$heap_owners($heap_graph({state}), HOBJECT n_leaf) = 3',
            f'$node_children({state}, HARRAY n_outer) = [HARRAY n_shared, HARRAY n_shared, HOBJECT n_leaf, HOBJECT n_leaf]',
            f'$node_children({state}, HARRAY n_shared) = [HOBJECT n_leaf]']


def seek(before, state, stage, callback):
    return [f'{state}_paused = $gc66_seek({before}, {stage}, {callback}, n_outer, 4000)',
            f'{state}_paused.COMPLETION = BUDGET', f'{state} = {state}_paused[.COMPLETION = NORMAL]']


def read_checks(state, next_state):
    return [
        f'{state}.TODO = (KEY_READ_DIM poperand_{state} z_{state} KEY_R) :: ptask_{state}_tail*',
        f'{state}.ORIGIN = (porigin_{state})',
        f'paccess_{state}_initial = $access_record({state}, porigin_{state}, z_{state}, ACCESS_READ KEY_R, BASE_VALUE {state}.RESULT, poperand_{state}, KNOWN PNULL, KEY_READ_DIM poperand_{state} z_{state} KEY_R, (n_map), true)',
        f'paccess_{state} = paccess_{state}_initial[.SELECTED = $rcontainer_selected({state}, {state}.RESULT)][.OFFSET = POBJECT n_key]',
        f'$weakmap_write_callback_read({state}, paccess_{state})',
        f'$weakmap_write_claim_valid({state}, pweakmapwrite)',
        f'$heap_owners($heap_graph({state}), HOBJECT n_map) = 3',
        f'$heap_owners($heap_graph({state}), HOBJECT n_key) = 2',
        *graph(state, 2), *valid(state),
        f'PhpStep: {state} ~> {next_state}_raw',
        f'{next_state}_raw.RESULT = KNOWN (PARRAY n_outer)',
        *graph(next_state + '_raw', 3),
        f'{next_state}_raw.ARRAYS = {state}.ARRAYS',
        f'{next_state}_raw.OBJECTPROPS = {state}.OBJECTPROPS',
        f'{next_state}_raw.ALLOCATIONS = {state}.ALLOCATIONS',
        f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
        f'{next_state}_paused = $drive_steps({state}, 1)',
        f'{next_state}_paused.COMPLETION = BUDGET',
        f'{next_state} = {next_state}_paused[.COMPLETION = NORMAL]',
        f'{next_state}.RESULT = KNOWN (PARRAY n_outer)',
        *graph(next_state, 3),
        f'$drive_steps({state}, 2) = $drive_steps({next_state}, 1)',
    ]


def release_checks(state, next_state, seen):
    return [
        f'{state}.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_{state}) :: ptask_{state}_tail*',
        f'pdestructionrelease_{state}.JOBS = [DESTRUCTION_VALUE (HARRAY n_outer)]',
        f'{state}.DESTRUCTION.OPERATIONS = pdestructionoperation_{state} :: pdestructionoperation_{state}_tail*',
        f'pdestructionoperation_{state}.SOURCE = UNSET expression_{state}',
        f'$weakmap_foreach_name(expression_{state}) = ($ptascii("{seen}"))',
        *graph(state, 3), *valid(state),
        f'$weakmap_write_claim_valid({state}, pweakmapwrite)',
        f'n_buffer_{state} = $heap_count(HARRAY n_outer, $gc_nodes({state}.GC.BUFFER))',
        f'$(n_buffer_{state} <= 1)',
        f'PhpStep: {state} ~> {next_state}_raw',
        *graph(next_state + '_raw', 2),
        f'{next_state}_raw.ARRAYS = {state}.ARRAYS',
        f'{next_state}_raw.OBJECTPROPS = {state}.OBJECTPROPS',
        f'{next_state}_raw.ALLOCATIONS = {state}.ALLOCATIONS',
        f'$heap_count(HARRAY n_outer, $gc_nodes({next_state}_raw.GC.BUFFER)) = 1',
        f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
        f'{next_state}_paused = $drive_steps({state}, 1)',
        f'{next_state}_paused.COMPLETION = BUDGET',
        f'{next_state} = {next_state}_paused[.COMPLETION = NORMAL]',
        *graph(next_state, 2),
        f'$drive_steps({state}, 2) = $drive_steps({next_state}, 1)',
    ]


CHECKS = [
    'pweakmapwrite.ACCESS.OBJECT = (n_map)',
    'pweakmapwrite.ACCESS.OFFSET = POBJECT n_key',
    'S.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (PARRAY n_shared)), ENTRY (KINT 2) (DIRECT (PARRAY n_shared)), ENTRY (KINT 3) (DIRECT (POBJECT n_leaf)), ENTRY (KINT 4) (DIRECT (POBJECT n_leaf))]',
    'S.ARRAYS[n_shared].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf)), ENTRY (KINT 1) (DIRECT (PINT 23))]',
    '$value_nodes(PARRAY n_outer) = [HARRAY n_outer]',
    *graph('S', 1),
    '$lookup(S.ENV, $ptascii("incoming66Peer")) = (n_rhs_cell)',
    'S.STORE[n_rhs_cell] = DEFINED (PARRAY n_outer)',
    '~(n_rhs_cell <- S.REFCELLS)',
    '$weakmap_write_incoming_before(S, PARRAY n_outer, |S.OBJECTS|)',
    'S_cycle = S[.ARRAYS[n_shared] = S.ARRAYS[n_shared][.ITEMS = S.ARRAYS[n_shared].ITEMS ++ [ENTRY (KINT 2) (DIRECT (PARRAY n_outer))]]]',
    '~$weakmap_write_incoming_before(S_cycle, PARRAY n_outer, |S.OBJECTS|)',
    'S_alias = S[.ARRAYS[n_shared] = S.ARRAYS[n_shared][.ITEMS = [ENTRY (KINT 0) (ALIAS n_rhs_cell)]]]',
    '~$weakmap_write_incoming_before(S_alias, PARRAY n_outer, |S.OBJECTS|)',
    'S_map_edge = S[.ARRAYS[n_shared] = S.ARRAYS[n_shared][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_map))]]]',
    '~$weakmap_write_incoming_before(S_map_edge, PARRAY n_outer, |S.OBJECTS|)',
    'S_key_edge = S[.ARRAYS[n_shared] = S.ARRAYS[n_shared][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_key))]]]',
    '~$weakmap_write_incoming_before(S_key_edge, PARRAY n_outer, |S.OBJECTS|)',
    '$node_children(S, HOBJECT n_old) = [HOBJECT n_child]',
    'S_callback_edge = S[.ARRAYS[n_shared] = S.ARRAYS[n_shared][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]]]',
    '~$weakmap_write_incoming_before(S_callback_edge, PARRAY n_outer, |S.OBJECTS|)',
    '$weakmap_write_plan(S[.STORE[n_rhs_cell] = UNDEFINED]) = eps',
    *seek('S', 'S_own', 'ARRAY_READ', 'n_old'),
    '$heap_owners($heap_graph(S_own), HOBJECT n_old) = 2',
    '$instance_storage_for(S_own, n_old) = eps',
    '$lookup(S_own.ENV, $ptascii("incoming66Peer")) = eps',
    *read_checks('S_own', 'S_own_copy'),
    *seek('S_own_copy', 'S_own_release', 'ARRAY_RELEASE', 'n_old'),
    *release_checks('S_own_release', 'S_own_dropped', 'seenOwn66Peer'),
    *seek('S_own_dropped', 'S_child', 'ARRAY_READ', 'n_child'),
    '$instance_storage_for(S_child, n_old) = (pinstancestorage)',
    'pinstancestorage.NEXT = 1',
    '$weakmap_write_selected_child(pinstancestorage) = (n_child)',
    '$node_children(S_child, HOBJECT n_old) = eps',
    '$heap_owners($heap_graph(S_child), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_child), HOBJECT n_child) = 2',
    'S_child.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_parent]',
    'pdestructionoperation_parent.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation_parent.PENDING = (n_pending)',
    'pdestructionoperation_inner.SOURCE = THROW_SEARCH n_pending',
    'pdestructionoperation_inner.PENDING = eps',
    '$heap_owners($heap_graph(S_child), HOBJECT n_pending) = 1',
    *read_checks('S_child', 'S_child_copy'),
    *seek('S_child_copy', 'S_child_release', 'ARRAY_RELEASE', 'n_child'),
    *release_checks('S_child_release', 'S_child_dropped', 'seenChild66Peer'),
    *seek('S_child_dropped', 'S_parent', 'PARENT_EXIT', 'n_old'),
    'S_parent.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_parent) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_parent_tail*',
    'S_parent.DESTRUCTION.OPERATIONS = [pdestructionoperation_parent]',
    '~((HOBJECT n_old) <- S_parent.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_parent.ALLOCATIONS)',
    '$weakmap_write_claim_valid(S_parent, pweakmapwrite)',
    '$heap_owners($heap_graph(S_parent), HOBJECT n_pending) = 1',
    *graph('S_parent', 2), *valid('S_parent'),
    '$drive_steps(S_parent, 0) = S_parent[.COMPLETION = BUDGET]',
]

review.CASES = {'retained-shared-array-copy-and-drop': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
