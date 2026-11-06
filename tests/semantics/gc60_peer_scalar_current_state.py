#!/usr/bin/env python3
"""A present NULL read adds no payload owner during current-row old cleanup."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc60_peer_null_current_read.php').read_text().replace(
    '$throw60Peer = false;', '$throw60Peer = true;')
STAGE = (
    'S.TODO = (KEY_READ_DIM poperand_key z KEY_R) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if $lookup(S.ENV, $ptascii("map60Peer")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_scalar, pweakmapentry_new]) '
    '-- if S.ITERATORS = [WEAKMAPITER n n_map 2 n_keys*]')
DECLARATIONS = r'''dec $gc60_retired(pstate) : bool
def $gc60_retired(S) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME paccess) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pdestructionoperation.PENDING = (n_pending)
  -- if pweakmapwrite.ACCESS = paccess
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $gc60_retired(S) = false -- otherwise
dec $gc60_seek_retired(pstate, nat) : pstate
def $gc60_seek_retired(S, n) = S -- if $gc60_retired(S)
def $gc60_seek_retired(S, n) = $gc60_seek_retired($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$gc60_retired(S)
  -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc60_seek_retired(S, 0) = S -- if ~$gc60_retired(S)
def $gc60_seek_retired(S, n) = S
  -- if ~$gc60_retired(S)
  -- if $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture
CHUNKS = (['B|', 's|', '17', '|', 'C|'] + ['1', '|'] * 5
          + ['T|', 'peer-fresh-60', '|', '13', '|', '__destruct', '|', '42', '|', '1', '|', '0', '|', 'R|']
          + ['1', '|', '0', '|', '0', '|'] + ['1', '|'] * 4
          + ['M|'] + ['1', '|'] * 2 + ['K|', '1', '|'])
ENDING = 'S_done.EVENTS = [' + ', '.join(
    'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in CHUNKS) + ']'
CHECKS = [
    'S.ORIGIN = (porigin_read)',
    '$destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)',
    'S.DESTRUCTION.CALLS = [pdestructorcall]',
    'pdestructorcall.OPERATION = (pdestructionoperation)',
    'pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
    'pdestructionoperation.VALUE = KNOWN PNULL',
    'pdestructionoperation.PENDING = eps',
    'pweakmapwrite.OLD.VALUE = POBJECT n_old',
    'pweakmapwrite.ACCESS.VALUE = PNULL',
    'pweakmapwrite.ACCESS.OBJECT = (n_map)',
    'pweakmapwrite.ACCESS.OFFSET = POBJECT n_key',
    'pweakmapwrite.CURSOR = WEAKMAPITER n n_map 2 n_keys*',
    'n_keys* = [n_scalar_key, n_key]',
    'pweakmapentry_scalar.KEY = n_scalar_key /\\ pweakmapentry_scalar.VALUE = PINT 17',
    'pweakmapentry_new = pweakmapwrite.OLD[.VALUE = PNULL]',
    'pweakmapwrite.MAPCELL = n_map_cell',
    '$lookup(S.ENV, $ptascii("loopKey60Peer")) = (n_key_cell)',
    'pweakmapwrite.KEYCELL = n_key_cell',
    'n_map_cell <- S.REFCELLS /\\ n_key_cell <- S.REFCELLS',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("map60Peer")) = (n_map_cell)',
    '$lookup(S_global.ENV, $ptascii("loopKey60Peer")) = (n_key_cell)',
    '$lookup(S_global.ENV, $ptascii("loopValue60Peer")) = (n_value_cell)',
    'pweakmapwrite.VALUECELL = n_value_cell',
    'S.STORE[n_value_cell] = DEFINED (PBOOL false)',
    '~(n_value_cell <- S.REFCELLS)',
    '$lookup(S_global.ENV, $ptascii("result60Peer")) = (n_result_cell)',
    '$lookup(S.ENV, $ptascii("result60Peer")) = (n_result_cell)',
    'n_result_cell <- S.REFCELLS',
    'S.STORE[n_result_cell] = DEFINED (PINT 31)',
    '$lookup(S_global.ENV, $ptascii("incoming60Peer")) = (n_incoming_cell)',
    'S.STORE[n_incoming_cell] = DEFINED PNULL',
    '~(n_incoming_cell <- S.REFCELLS)',
    '$lookup(S_global.ENV, $ptascii("oldWatch60Peer")) = (n_old_watch_cell)',
    'S.STORE[n_old_watch_cell] = DEFINED (POBJECT n_old_watch)',
    '$weakref_get(S, n_old_watch) = PNULL',
    '$instance_storage_for(S, n_old) = (pinstancestorage)',
    'pinstancestorage.SLOTS = [ppropertyslot_first, ppropertyslot_second]',
    'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    'ppropertyslot_second.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    'pinstancestorage.NEXT = 2',
    'pdestructorcall.OBJECT = n_child',
    'pdestructorcall.RELEASE = (pdestructionrelease_child)',
    'pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    '$objectprops_at(S.OBJECTPROPS, n_old) = ([ppropertyslot_first[.STATE = PROP_UNSET], ppropertyslot_second[.STATE = PROP_UNSET]])',
    '$node_children(S, HOBJECT n_old) = eps',
    '$node_children(S, HOBJECT n_child) = eps',
    '$weakmap_write_selected_child(pinstancestorage) = (n_child)',
    '$weakmap_write_pin(S, pweakmapwrite, pinstancestorage)',
    '$weakmap_write_selected_call(S, pweakmapwrite, pinstancestorage, pdestructorcall)',
    'S.FRAMES = [pframe]',
    'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_after_pin*',
    'pdestructionrelease_empty = pdestructionrelease_child[.JOBS = eps]',
    '$call_context_roots(S.CURRENT) = [HOBJECT n_child]',
    '$task_nodes(DESTRUCTOR_RESULT pdestructorcall) = [HOBJECT n_child]',
    '$task_nodes(WEAKMAP_WRITE_CLAIM pweakmapwrite) = eps',
    '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S), HOBJECT n_key) = 2',
    '$heap_count(HOBJECT n_old, $frames_roots(S.FRAMES)) = 1',
    '$heap_count(HOBJECT n_map, $frames_roots(S.FRAMES)) = 2',
    '$weakmap_write_scope(S, pweakmapwrite) = (S_scope)',
    '$weakmap_write_claim_count(S_scope.TODO) = 1',
    '$weakmap_write_claim_tail(S_scope.TODO, pweakmapwrite) = (ptask_claim_tail*)',
    '$goto_saved(S_scope.TODO, pweakmapwrite.LOOP) = GOTOTASKS (ptask_loop :: ptask_loop_tail*)',
    '$weakmap_write_source_site(S_scope, pweakmapwrite, ptask_loop)',
    '$weakmap_write_claim_valid(S, pweakmapwrite)',
    '$weakmap_write_operation_source(S, pdestructionoperation, pweakmapwrite)',
    '$weakmap_write_operation(S, n_map)',
    '~$weakmap_foreach_write_operation(S, n_map)',
    '~$weakmap_entries_child_storage(S, n_map)',
    '~$weakmap_finite_foreach_storage(S, n_map)',
    'paccess_initial = $access_record(S, porigin_read, z, ACCESS_READ KEY_R, BASE_VALUE S.RESULT, poperand_key, KNOWN PNULL, KEY_READ_DIM poperand_key z KEY_R, (n_map), true)',
    'paccess = paccess_initial[.SELECTED = $rcontainer_selected(S, S.RESULT)][.OFFSET = POBJECT n_key]',
    'paccess.SELECTED = REFERENCE n_map_cell',
    '$weakmap_read_allowed(S, paccess)',
    '$weakmap_write_callback_read(S, paccess)',
    '$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetGet"))',
    '~$weakmap_write_callback_read(S, paccess[.SELECTED = KNOWN (POBJECT n_map)])',
    '~$weakmap_write_callback_read(S[.GC.WORKER = (n_map)], paccess)',
    '~$weakmap_write_callback_read(S[.ITERATORS = [WEAKMAPITER n n_map 1 n_keys*]], paccess)',
    '$lookup(S_scope.ENV, $ptascii("incoming60Peer")) = (n_rhs_cell)',
    'S_rhs_changed = S_scope[.STORE[n_rhs_cell] = DEFINED (PINT 1)]',
    '$heap_graph(S_rhs_changed) = $heap_graph(S_scope)',
    '~$weakmap_write_source_site(S_rhs_changed, pweakmapwrite, ptask_loop)',
    'S_rhs_reference = S_scope[.REFCELLS = n_rhs_cell :: S_scope.REFCELLS]',
    '~$weakmap_write_source_site(S_rhs_reference, pweakmapwrite, ptask_loop)',
    '$value_nodes(pweakmapwrite.ACCESS.VALUE) = eps',
    '$weakmap_write_quiet_scalar(S, PNULL)',
    '$weakmap_write_quiet_scalar(S, PBOOL true)',
    '$weakmap_write_quiet_scalar(S, PINT -7)',
    '$weakmap_write_quiet_scalar(S, PFLOAT 4608308318706860032)',
    '$weakmap_write_quiet_scalar(S, PSTRING_CARRIER INTERNED_STRING $ptascii("quiet"))',
    '~$weakmap_write_quiet_scalar(S, PFLOAT 9221120237041090560)',
    '~$weakmap_write_quiet_scalar(S, PFLOAT 18446744073709551616)',
    '~$weakmap_write_quiet_scalar(S, PSTRING $ptascii("quiet"))',
    'S_request_string = $string_request(S, $ptascii("quiet"))',
    'S_request_string.RESULT = KNOWN pvalue_request',
    '$weakmap_scalar_value(S_request_string, pvalue_request)',
    '$value_nodes(pvalue_request) = eps',
    '~$weakmap_write_quiet_scalar(S_request_string, pvalue_request)',
    '$weakmap_write_incoming_before(S, PNULL, 0)',
    '~$weakmap_write_source_site(S_scope, pweakmapwrite[.FIRSTNEW = 0], ptask_loop)',
    '$node_children(S, HOBJECT n_map) = eps',
    '$lookup(S.ENV, $ptascii("incoming60Peer")) = eps',
    '$destruction_state_valid(S) /\\ $call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET',
    'S_read = S_paused[.COMPLETION = NORMAL]',
    'S_read.RESULT = KNOWN PNULL',
    'S_read.TODO = ptask_tail*',
    '$heap_owners($heap_graph(S_read), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S_read), HOBJECT n_key) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_read), HOBJECT n_child) = 2',
    'S_read.STORE = S.STORE',
    'S_read.OBJECTS = S.OBJECTS',
    'S_read.ALLOCATIONS = S.ALLOCATIONS',
    '$value_nodes(PNULL) = eps',
    'S_read.OBJECTPROPS = S.OBJECTPROPS /\\ S_read.ITERATORS = S.ITERATORS',
    'S_read.DESTRUCTION = S.DESTRUCTION /\\ S_read.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_read) /\\ $heap_valid($heap_graph(S_read))',
    'S_retired_reached = $gc60_seek_retired(S_read, 4000)',
    'S_retired_reached.COMPLETION = BUDGET',
    'S_retired = S_retired_reached[.COMPLETION = NORMAL]',
    '$gc60_retired(S_retired)',
    'S_retired.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_retired) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'pdestructionoperation_retired.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation_retired.PENDING = (n_pending)',
    'n_pending = pweakmapwrite.FIRSTNEW',
    '$weakmap_write_fresh_pending(S_retired, pweakmapwrite, (n_pending))',
    '~$weakmap_write_fresh_pending(S_retired, pweakmapwrite[.FIRSTNEW = $(n_pending + 1)], (n_pending))',
    '~((HOBJECT n_old) <- S_retired.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_retired.ALLOCATIONS)',
    '$weakmap_write_operation_source(S_retired, pdestructionoperation_retired, pweakmapwrite)',
    'pdestructionoperation_wrong = pdestructionoperation_retired[.SOURCE = ACCESS_RESUME pweakmapwrite.ACCESS]',
    'S_wrong_source = S_retired[.DESTRUCTION.OPERATIONS = [pdestructionoperation_wrong]][.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_wrong) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*]',
    '~$weakmap_write_operation_source(S_wrong_source, pdestructionoperation_wrong, pweakmapwrite)',
    'S_after_old_paused = $drive_steps(S_retired, 1)',
    'S_after_old_paused.COMPLETION = BUDGET',
    'S_after_old = S_after_old_paused[.COMPLETION = NORMAL]',
    'S_after_old.TODO = (THROW_SEARCH n_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'S_after_old.DESTRUCTION.OPERATIONS = eps',
    'S_carrier_paused = $drive_steps(S_after_old, 1)',
    'S_carrier_paused.COMPLETION = BUDGET',
    'S_carrier = S_carrier_paused[.COMPLETION = NORMAL]',
    'S_carrier.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_carrier) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_carrier) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'pdestructionoperation_carrier.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation_carrier.PENDING = (n_pending)',
    'pdestructionoperation_carrier.VALUE = KNOWN PNULL',
    'pdestructionrelease_carrier.JOBS = [DESTRUCTION_VALUE (HOBJECT n_map)]',
    '$heap_owners($heap_graph(S_carrier), HOBJECT n_map) = 3',
    'S_carrier.STORE[n_result_cell] = DEFINED (PINT 31)',
    '$weakmap_write_operation_source(S_carrier, pdestructionoperation_carrier, pweakmapwrite)',
    '$weakmap_write_source_site(S_carrier, pweakmapwrite, ptask_loop)',
    '~$weakmap_write_source_site(S_carrier, pweakmapwrite[.MAPCELL = n_key_cell], ptask_loop)',
    'pweakmapwrite_wrong = pweakmapwrite[.ACCESS = pweakmapwrite.ACCESS[.VALUE = PINT 1]]',
    'S_wrong_claim = S_carrier[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_carrier) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_carrier) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite_wrong) :: ptask_claim_tail*]',
    '~$weakmap_write_operation_source(S_wrong_claim, pdestructionoperation_carrier, pweakmapwrite)',
    'S_carrier_drop_paused = $drive_steps(S_carrier, 1)',
    'S_carrier_drop_paused.COMPLETION = BUDGET',
    'S_carrier_drop = S_carrier_drop_paused[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_carrier_drop), HOBJECT n_map) = 2',
    'S_carrier_exit_paused = $drive_steps(S_carrier_drop, 1)',
    'S_carrier_exit_paused.COMPLETION = BUDGET',
    'S_carrier_exit = S_carrier_exit_paused[.COMPLETION = NORMAL]',
    'S_pending_claim_paused = $drive_steps(S_carrier_exit, 1)',
    'S_pending_claim_paused.COMPLETION = BUDGET',
    'S_pending_claim = S_pending_claim_paused[.COMPLETION = NORMAL]',
    'S_pending_claim.TODO = (THROW_SEARCH n_pending) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'S_pending_claim.DESTRUCTION.OPERATIONS = eps /\\ S_pending_claim.DESTRUCTION.RELEASES = eps',
    '$return_discard(S_pending_claim, WEAKMAP_WRITE_CLAIM pweakmapwrite) = S_pending_claim',
    'S_head_claim = S_pending_claim[.TODO = (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*][.RESULT = KNOWN (POBJECT n_pending)]',
    '$heap_owners($heap_graph(S_head_claim), HOBJECT n_pending) = 1',
    '$call_task_valid(S_head_claim, WEAKMAP_WRITE_CLAIM pweakmapwrite)',
    'PhpStep: S_head_claim ~> S_popped',
    'S_popped = S_head_claim[.TODO = ptask_claim_tail*]',
    '$heap_graph(S_popped) = $heap_graph(S_head_claim)',
    'S_bad_head = S_head_claim[.TODO = (WEAKMAP_WRITE_CLAIM pweakmapwrite_wrong) :: ptask_claim_tail*]',
    '~$call_task_valid(S_bad_head, WEAKMAP_WRITE_CLAIM pweakmapwrite_wrong)',
    'S_discarded_paused = $drive_steps(S_pending_claim, 1)',
    'S_discarded_paused.COMPLETION = BUDGET',
    'S_discarded = S_discarded_paused[.COMPLETION = NORMAL]',
    'S_discarded.TODO = (THROW_SEARCH n_pending) :: ptask_claim_tail*',
    '$heap_graph(S_discarded) = $heap_graph(S_pending_claim)',
    'S_discarded.STORE[n_result_cell] = DEFINED (PINT 31)',
    'S_done = $drive_steps(S_discarded, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    'S_done.CURRENT = eps',
    'S_done.DESTRUCTION.OPERATIONS = eps /\\ S_done.DESTRUCTION.CALLS = eps',
    'S_done.ITERATORS = eps',
    ENDING,
    '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_scalar_key) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'shared-child-present-null-current-read': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
