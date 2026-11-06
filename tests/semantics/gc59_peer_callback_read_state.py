#!/usr/bin/env python3
"""A genuine shared-Child callback borrows write history and copies the new row."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc59_peer_shared_child_read.php').read_text().replace(
    '$throw59Peer = false;', '$throw59Peer = true;')
STAGE = (
    'S.TODO = (KEY_READ_DIM poperand_key z KEY_R) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if $lookup(S.ENV, $ptascii("map59Peer")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_scalar, pweakmapentry_new]) '
    '-- if S.ITERATORS = [WEAKMAPITER n n_map 2 n_keys*]')
CHUNKS = (['B|', 's|', '17', '|', 'C|'] + ['1', '|'] * 5
          + ['T|', 'peer-fresh-59', '|', '14', '|', '__destruct', '|', '44', '|', '1', '|', '0', '|', 'R|']
          + ['1', '|', '0', '|', '0', '|'] + ['1', '|'] * 4
          + ['M|'] + ['1', '|'] * 2 + ['V|', '1', '|', 'K|', '1', '|'])
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
    'pweakmapwrite.ACCESS.VALUE = POBJECT n_new',
    'pweakmapwrite.ACCESS.OBJECT = (n_map)',
    'pweakmapwrite.ACCESS.OFFSET = POBJECT n_key',
    'pweakmapwrite.CURSOR = WEAKMAPITER n n_map 2 n_keys*',
    'n_keys* = [n_scalar_key, n_key]',
    r'pweakmapentry_scalar.KEY = n_scalar_key /\ pweakmapentry_scalar.VALUE = PINT 17',
    'pweakmapentry_new = pweakmapwrite.OLD[.VALUE = POBJECT n_new]',
    'pweakmapwrite.MAPCELL = n_map_cell',
    '$lookup(S.ENV, $ptascii("loopKey59Peer")) = (n_key_cell)',
    'pweakmapwrite.KEYCELL = n_key_cell',
    r'n_map_cell <- S.REFCELLS /\ n_key_cell <- S.REFCELLS',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("map59Peer")) = (n_map_cell)',
    '$lookup(S_global.ENV, $ptascii("loopKey59Peer")) = (n_key_cell)',
    '$lookup(S_global.ENV, $ptascii("loopValue59Peer")) = (n_value_cell)',
    'pweakmapwrite.VALUECELL = n_value_cell',
    'S.STORE[n_value_cell] = DEFINED (PBOOL false)',
    '~(n_value_cell <- S.REFCELLS)',
    '$lookup(S_global.ENV, $ptascii("result59Peer")) = (n_result_cell)',
    '$lookup(S.ENV, $ptascii("result59Peer")) = (n_result_cell)',
    'n_result_cell <- S.REFCELLS',
    'S.STORE[n_result_cell] = DEFINED (PINT 31)',
    '$lookup(S_global.ENV, $ptascii("incoming59Peer")) = (n_incoming_cell)',
    'S.STORE[n_incoming_cell] = DEFINED (POBJECT n_new)',
    '~(n_incoming_cell <- S.REFCELLS)',
    '$lookup(S_global.ENV, $ptascii("oldWatch59Peer")) = (n_old_watch_cell)',
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
    '$node_children(S, HOBJECT n_new) = eps',
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
    '$heap_owners($heap_graph(S), HOBJECT n_new) = 2',
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
    '~$weakmap_write_callback_read(S, paccess[.OFFSET = POBJECT n_scalar_key])',
    '~$weakmap_write_callback_read(S, paccess[.MODE = ACCESS_READ KEY_IS])',
    '~$weakmap_write_callback_read(S, paccess[.TARGET = pweakmapwrite.LOOP])',
    '~$weakmap_write_callback_read(S, paccess[.OBJECT = (n_old)])',
    '~$weakmap_write_callback_read(S[.GC.WORKER = (n_map)], paccess)',
    '~$weakmap_write_callback_read(S[.ITERATORS = [WEAKMAPITER n n_map 1 n_keys*]], paccess)',
    '~$weakmap_write_callback_read(S[.ENV = (BIND $ptascii("map59Peer") n_key_cell) :: $unbind(S.ENV, $ptascii("map59Peer"))], paccess)',
    '~$weakmap_write_source_site(S_scope, pweakmapwrite[.MAPCELL = n_key_cell], ptask_loop)',
    '~$weakmap_write_source_site(S_scope, pweakmapwrite[.KEYCELL = n_value_cell], ptask_loop)',
    '~$weakmap_write_source_site(S_scope, pweakmapwrite[.LOOP = porigin_read], ptask_loop)',
    '~$weakmap_write_source_site(S_scope, pweakmapwrite[.CURSOR = WEAKMAPITER n n_map 1 n_keys*], ptask_loop)',
    '~$weakmap_write_source_site(S_scope, pweakmapwrite[.OLD = pweakmapwrite.OLD[.ORDER = $(pweakmapwrite.OLD.ORDER + 1)]], ptask_loop)',
    '~$weakmap_write_pin(S, pweakmapwrite[.OLD = pweakmapwrite.OLD[.VALUE = POBJECT n_new]], pinstancestorage)',
    'pinstancestorage_partial = pinstancestorage[.NEXT = 1]',
    'pframe_partial = pframe[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_partial) :: ptask_after_pin*]',
    'S_partial = S[.FRAMES = [pframe_partial]][.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_old, [ppropertyslot_first[.STATE = PROP_UNSET], ppropertyslot_second])]',
    '$instance_storage_basic(S_partial, pinstancestorage_partial)',
    '$heap_valid($heap_graph(S_partial))',
    '$heap_owners($heap_graph(S_partial), HOBJECT n_child) = 3',
    '~$weakmap_write_selected_call(S_partial, pweakmapwrite, pinstancestorage_partial, pdestructorcall)',
    '~$weakmap_write_callback_read(S_partial, paccess)',
    'pdestructorcall_bad = pdestructorcall[.RELEASE = (pdestructionrelease_child[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_new)]])]',
    'pframe_bad = pframe[.TODO = (DESTRUCTOR_RESULT pdestructorcall_bad) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_after_pin*]',
    'S_bad_job = S[.DESTRUCTION.CALLS = [pdestructorcall_bad]][.FRAMES = [pframe_bad]]',
    '$heap_valid($heap_graph(S_bad_job))',
    '~$weakmap_write_selected_call(S_bad_job, pweakmapwrite, pinstancestorage, pdestructorcall_bad)',
    '~$weakmap_write_callback_read(S_bad_job, paccess)',
    r'$destruction_state_valid(S) /\ $call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_read = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_read.RESULT = KNOWN (POBJECT n_new)',
    'S_read.TODO = ptask_tail*',
    '$heap_owners($heap_graph(S_read), HOBJECT n_new) = 3',
    '$heap_owners($heap_graph(S_read), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S_read), HOBJECT n_key) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_read), HOBJECT n_child) = 2',
    'S_read.STORE = S.STORE',
    'S_read.OBJECTS = S.OBJECTS',
    r'S_read.OBJECTPROPS = S.OBJECTPROPS /\ S_read.ITERATORS = S.ITERATORS',
    r'S_read.DESTRUCTION = S.DESTRUCTION /\ S_read.EVENTS = S.EVENTS',
    r'$call_descriptors_valid(S_read) /\ $heap_valid($heap_graph(S_read))',
    'S_paused = $drive_steps(S, 1)',
    'S_paused = S_read[.COMPLETION = BUDGET]',
    'S_done = $drive_steps(S_read, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
    'S_done.CURRENT = eps',
    r'S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps',
    'S_done.ITERATORS = eps',
    ENDING,
    '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_scalar_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'shared-child-callback-current-row-read': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
