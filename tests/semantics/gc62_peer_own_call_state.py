#!/usr/bin/env python3
"""Actual own-destructor weak-live copy, later storage, and claim ownership."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc62_peer_null_own_read.php').read_text().replace(
    '$throw62Peer = false;', '$throw62Peer = true;')
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if S.CURRENT = eps -- if $weakmap_write_plan(S[.COMPLETION = NORMAL]) = (pweakmapwrite) '
    '-- if pweakmapwrite.ACCESS.VALUE = PNULL '
    '-- if pweakmapwrite.OLD.VALUE = POBJECT n_old')
DECLARATIONS = r'''syntax pgc62stage = OWN_GET | OWN_READ | OWN_FREE | OWN_PIN | OWN_INNER_EXIT | OWN_RETIRED | OWN_PRECALL | OWN_ENTER | OWN_NORMAL_FREE | OWN_NORMAL_CLAIM
dec $gc62_at(pstate, pgc62stage, nat) : bool
def $gc62_at(S, OWN_GET, n_old) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET /\ pconfigcall.SENT = eps
  -- if pconfigcall.OWNER = (n_wrapper)
  -- if $weakref_get(S, n_wrapper) = POBJECT n_old
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_old
def $gc62_at(S, OWN_READ, n_old) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_old
def $gc62_at(S, OWN_FREE, n_old) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_free) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionrelease_free.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)] /\ pdestructionrelease_old.JOBS = eps
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old
  -- if pdestructionoperation.PENDING = (n_pending)
  -- if pdestructionoperation_inner.SOURCE = THROW_SEARCH n_pending
def $gc62_at(S, OWN_PIN, n_old) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n_old
def $gc62_at(S, OWN_INNER_EXIT, n_old) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.PENDING = (n_pending)
  -- if pdestructionoperation_inner.SOURCE = THROW_SEARCH n_pending
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
def $gc62_at(S, OWN_RETIRED, n_old) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME paccess) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old /\ pweakmapwrite.ACCESS = paccess
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
def $gc62_at(S, OWN_NORMAL_FREE, n_old) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_free) :: (DESTRUCTOR_RELEASE pdestructionrelease_old) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionrelease_free.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)] /\ pdestructionrelease_old.JOBS = eps
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old /\ pdestructionoperation.PENDING = eps
def $gc62_at(S, OWN_PRECALL, n_old) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old /\ ~(n_old <- S.DESTRUCTION.CALLED)
def $gc62_at(S, OWN_ENTER, n_old) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_old
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
def $gc62_at(S, OWN_NORMAL_CLAIM, n_old) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
def $gc62_at(S, pgc62stage, n_old) = false -- otherwise
dec $gc62_seek(pstate, pgc62stage, nat, nat) : pstate
def $gc62_seek(S, pgc62stage, n_old, n) = S -- if $gc62_at(S, pgc62stage, n_old)
def $gc62_seek(S, pgc62stage, n_old, n) = $gc62_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc62stage, n_old, $nabs($(n - 1)))
  -- if ~$gc62_at(S, pgc62stage, n_old) -- if $(n > 0) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc62_seek(S, pgc62stage, n_old, 0) = S -- if ~$gc62_at(S, pgc62stage, n_old)
def $gc62_seek(S, pgc62stage, n_old, n) = S -- if ~$gc62_at(S, pgc62stage, n_old) -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture
CHUNKS = (['B|', 's|', '1', '|', 'L|', '1', '|', 'C|'] + ['1', '|'] * 4
          + ['T|', 'peer-fresh-62', '|', '13', '|', '__destruct', '|', '39', '|', '1', '|', '0', '|', 'R|']
          + ['1', '|', '0', '|', '0', '|'] + ['1', '|'] * 3
          + ['M|'] + ['1', '|'] * 2 + ['K|', '1', '|'])
ENDING = 'S_done.EVENTS = [' + ', '.join(
    'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in CHUNKS) + ']'
CHECKS = [
    'pweakmapwrite.ACCESS.OBJECT = (n_map)',
    'pweakmapwrite.ACCESS.OFFSET = POBJECT n_key',
    'pweakmapwrite.CURSOR = WEAKMAPITER n n_map 2 n_keys*',
    'n_keys* = [n_spare_key, n_key]',
    '$weakmap_write_own_foreach_storage(S, n_map)',
    '$weakmap_write_own_value(S, n_old)',
    '~$weakmap_write_old_value(S, n_old)',
    '~(n_old <- S.DESTRUCTION.CALLED)',
    '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
    '$instance_storage_for(S, n_old) = eps',
    '$weakmap_write_plan(S[.DESTRUCTION.CALLED = n_old :: S.DESTRUCTION.CALLED]) = eps',
    '$lookup(S.ENV, $ptascii("oldWatch62Peer")) = (n_old_watch_cell)',
    'S.STORE[n_old_watch_cell] = DEFINED (POBJECT n_old_watch)',
    '$weakref_get(S, n_old_watch) = POBJECT n_old',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_get_reached = $gc62_seek(S, OWN_GET, n_old, 4000)',
    'S_get_reached.COMPLETION = BUDGET',
    'S_get = S_get_reached[.COMPLETION = NORMAL]',
    'S_get.TODO = (CONFIG_INVOKE pconfigcall_get) :: ptask_get_tail*',
    'pconfigcall_get.KIND = INTRINSIC_WEAKREF_GET',
    'pconfigcall_get.OWNER = (n_old_watch)',
    'pconfigcall_get.SENT = eps',
    'S_get.CURRENT = (pcallcontext)',
    '$destructor_context_call(pcallcontext, S_get.CURRENT, S_get.FRAMES) = (pdestructorcall)',
    'pdestructorcall.OBJECT = n_old',
    'pdestructorcall.OPERATION = (pdestructionoperation)',
    'pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructorcall.RELEASE = (pdestructionrelease_original)',
    'pdestructionrelease_original.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]',
    'pdestructionrelease_old_empty = pdestructionrelease_original[.JOBS = eps]',
    'pdestructionrelease_old_empty <- S_get.DESTRUCTION.RELEASES',
    'S_get.DESTRUCTION.CALLS = [pdestructorcall]',
    'n_old <- S_get.DESTRUCTION.CALLED',
    '$weakmap_write_own_call(S_get, pweakmapwrite, pdestructorcall)',
    '$weakmap_write_callback_owner(S_get, pweakmapwrite, pdestructorcall)',
    '$instance_storage_for(S_get, n_old) = eps',
    '$node_children(S_get, HOBJECT n_old) = eps',
    '$weakref_get(S_get, n_old_watch) = POBJECT n_old',
    '$heap_owners($heap_graph(S_get), HOBJECT n_old) = 2',
    '$heap_owners($heap_graph(S_get), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S_get), HOBJECT n_key) = 2',
    '$call_context_roots(S_get.CURRENT) = [HOBJECT n_old]',
    '$task_nodes(DESTRUCTOR_RESULT pdestructorcall) = [HOBJECT n_old]',
    '$task_nodes(WEAKMAP_WRITE_CLAIM pweakmapwrite) = eps',
    'n_old_gc_before = $heap_count(HOBJECT n_old, $gc_nodes(S_get.GC.BUFFER))',
    '$(n_old_gc_before <= 1)',
    'PhpStep: S_get ~> S_get_raw',
    'S_get_raw.RESULT = KNOWN (POBJECT n_old)',
    '$heap_owners($heap_graph(S_get_raw), HOBJECT n_old) = 3',
    'S_get_raw.OBJECTS = S_get.OBJECTS',
    'S_get_raw.OBJECTPROPS = S_get.OBJECTPROPS',
    'S_get_raw.ALLOCATIONS = S_get.ALLOCATIONS',
    '$instance_storage_for(S_get_raw, n_old) = eps',
    'S_get_paused = $drive_steps(S_get, 1)',
    'S_get_paused.COMPLETION = BUDGET',
    'S_get_one = S_get_paused[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_get_one), HOBJECT n_old) = 3',
    'S_read_reached = $gc62_seek(S_get_one, OWN_READ, n_old, 4000)',
    'S_read_reached.COMPLETION = BUDGET',
    'S_read = S_read_reached[.COMPLETION = NORMAL]',
    'S_read.TODO = (KEY_READ_DIM poperand_key z_read KEY_R) :: ptask_read_tail*',
    '$heap_owners($heap_graph(S_read), HOBJECT n_old) = 2',
    '$heap_count(HOBJECT n_old, $gc_nodes(S_read.GC.BUFFER)) = n_old_gc_before',
    '$weakref_get(S_read, n_old_watch) = POBJECT n_old',
    '$instance_storage_for(S_read, n_old) = eps',
    'S_read.FRAMES = [pframe]',
    'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    '$weakmap_write_own_call(S_read, pweakmapwrite, pdestructorcall)',
    '$weakmap_write_operation_source(S_read, pdestructionoperation, pweakmapwrite)',
    '$weakmap_write_operation(S_read, n_map)',
    '~$weakmap_foreach_write_operation(S_read, n_map)',
    '~$weakmap_entries_child_storage(S_read, n_map)',
    '$weakmap_write_scope(S_read, pweakmapwrite) = (S_scope)',
    '$goto_saved(S_scope.TODO, pweakmapwrite.LOOP) = GOTOTASKS (ptask_loop :: ptask_loop_tail*)',
    '$weakmap_write_source_site(S_scope, pweakmapwrite, ptask_loop)',
    '$lookup(S_read.ENV, $ptascii("map62Peer")) = (pweakmapwrite.MAPCELL)',
    '$lookup(S_read.ENV, $ptascii("loopKey62Peer")) = (pweakmapwrite.KEYCELL)',
    r'pweakmapwrite.MAPCELL <- S_read.REFCELLS /\ pweakmapwrite.KEYCELL <- S_read.REFCELLS',
    '~(pweakmapwrite.VALUECELL <- S_read.REFCELLS)',
    'S_read.STORE[pweakmapwrite.VALUECELL] = DEFINED (PBOOL false)',
    '$lookup(S_scope.ENV, $ptascii("incoming62Peer")) = (n_rhs_cell)',
    'S_read.STORE[n_rhs_cell] = DEFINED PNULL',
    '~(n_rhs_cell <- S_read.REFCELLS)',
    '$lookup(S_read.ENV, $ptascii("incoming62Peer")) = eps',
    '$lookup(S_read.ENV, $ptascii("result62Peer")) = (n_result_cell)',
    'S_read.STORE[n_result_cell] = DEFINED (PINT 31)',
    'S_read.ORIGIN = (porigin_read)',
    'paccess_initial = $access_record(S_read, porigin_read, z_read, ACCESS_READ KEY_R, BASE_VALUE S_read.RESULT, poperand_key, KNOWN PNULL, KEY_READ_DIM poperand_key z_read KEY_R, (n_map), true)',
    'paccess = paccess_initial[.SELECTED = $rcontainer_selected(S_read, S_read.RESULT)][.OFFSET = POBJECT n_key]',
    '$weakmap_write_callback_read(S_read, paccess)',
    '~$weakmap_write_callback_read(S_read, paccess[.SELECTED = KNOWN (POBJECT n_map)])',
    'pdestructorcall_wrong_job = pdestructorcall[.RELEASE = (pdestructionrelease_original[.JOBS = [DESTRUCTION_TEMP (HOBJECT n_old)]])]',
    'S_wrong_job = S_read[.DESTRUCTION.CALLS = [pdestructorcall_wrong_job]]',
    '~$weakmap_write_own_call(S_wrong_job, pweakmapwrite, pdestructorcall_wrong_job)',
    '~$weakmap_write_own_call(S_read, pweakmapwrite[.OLD = pweakmapwrite.OLD[.VALUE = POBJECT n_map]], pdestructorcall)',
    '~$weakmap_write_own_call(S_read[.DESTRUCTION.CALLED = eps], pweakmapwrite, pdestructorcall)',
    '~$weakmap_write_own_call(S_read, pweakmapwrite, pdestructorcall[.TARGET = METHOD_TARGET n_map pcallcontext.FUNCTION])',
    '$destruction_state_valid(S_read)',
    '$call_descriptors_valid(S_read)',
    'S_frame_scope = $call_frame_scope(S_read, pframe, eps)',
    'S_task_scope = $destructor_saved_frame_scope($api_saved_frame_scope($parameter_string_frame_scope(S_frame_scope, pframe, eps), pframe, eps), pframe)',
    'S_after_result = $call_after_origin(S_task_scope, DESTRUCTOR_RESULT pdestructorcall)',
    'S_future = $call_after_origin(S_after_result, DESTRUCTOR_RELEASE pdestructionrelease_old_empty)',
    r'S_future.DESTRUCTION.CALLS = eps /\ S_future.DESTRUCTION.RELEASES = eps',
    '~$destructor_operation_valid(S_future, pdestructionoperation)',
    '$eager_operation_task_valid(S_future, pdestructionoperation)',
    'S_future_bad = S_future[.TODO = (DESTRUCTOR_RESULT pdestructorcall_wrong_job) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*]',
    '~$eager_operation_task_valid(S_future_bad, pdestructionoperation)',
    '~$eager_operation_task_valid(S_future[.DESTRUCTION.CALLED = eps], pdestructionoperation)',
    'S_read_paused = $drive_steps(S_read, 1)',
    'S_read_paused.COMPLETION = BUDGET',
    'S_after_read = S_read_paused[.COMPLETION = NORMAL]',
    'S_after_read.RESULT = KNOWN PNULL',
    '$heap_owners($heap_graph(S_after_read), HOBJECT n_old) = 2',
    '$heap_owners($heap_graph(S_after_read), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S_after_read), HOBJECT n_key) = 2',
    'S_after_read.OBJECTS = S_read.OBJECTS',
    'S_after_read.OBJECTPROPS = S_read.OBJECTPROPS',
    'S_after_read.ALLOCATIONS = S_read.ALLOCATIONS',
    '$instance_storage_for(S_after_read, n_old) = eps',
    'S_free_reached = $gc62_seek(S_after_read, OWN_FREE, n_old, 4000)',
    'S_free_reached.COMPLETION = BUDGET',
    'S_free = S_free_reached[.COMPLETION = NORMAL]',
    'S_free.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_free) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'pdestructionrelease_free.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]',
    'pdestructionoperation_pending.PENDING = (n_pending)',
    'pdestructionoperation_pending = pdestructionoperation[.PENDING = (n_pending)]',
    'n_pending = pweakmapwrite.FIRSTNEW',
    'pdestructionoperation_inner.SOURCE = THROW_SEARCH n_pending',
    'pdestructionoperation_inner.PENDING = eps',
    'S_free.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_pending]',
    'S_free.DESTRUCTION.RELEASES = [pdestructionrelease_free, pdestructionrelease_old_empty]',
    '$destructor_operation_valid(S_free, pdestructionoperation_inner)',
    '$weakmap_write_fresh_pending(S_free, pweakmapwrite, (n_pending))',
    '$weakmap_write_operation_source(S_free, pdestructionoperation_pending, pweakmapwrite)',
    '$destruction_state_valid(S_free)',
    '$call_descriptors_valid(S_free)',
    'pdestructionoperation_no_pending = pdestructionoperation_pending[.PENDING = eps]',
    'S_free_no_pending = S_free[.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_no_pending]][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_free) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_no_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*]',
    '$destructor_operation_valid(S_free_no_pending, pdestructionoperation_inner)',
    '~$weakmap_write_operation_source(S_free_no_pending, pdestructionoperation_no_pending, pweakmapwrite)',
    'pdestructionrelease_temp = pdestructionrelease_free[.JOBS = [DESTRUCTION_TEMP (HOBJECT n_old)]]',
    'S_free_temp = S_free[.DESTRUCTION.RELEASES = [pdestructionrelease_temp, pdestructionrelease_old_empty]][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_temp) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*]',
    '~$weakmap_write_operation_source(S_free_temp, pdestructionoperation_pending, pweakmapwrite)',
    '$instance_storage_for(S_free, n_old) = eps',
    '$weakref_get(S_free, n_old_watch) = POBJECT n_old',
    '$heap_owners($heap_graph(S_free), HOBJECT n_old) = 1',
    'n_old_gc_before_pin = $heap_count(HOBJECT n_old, $gc_nodes(S_free.GC.BUFFER))',
    '$(n_old_gc_before_pin <= 1)',
    'S_pin_reached = $gc62_seek(S_free, OWN_PIN, n_old, 4000)',
    'S_pin_reached.COMPLETION = BUDGET',
    'S_pin = S_pin_reached[.COMPLETION = NORMAL]',
    'S_pin.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_pin_tail*',
    'ptask_pin_tail* = (DESTRUCTOR_RELEASE pdestructionrelease_free[.JOBS = eps]) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'pinstancestorage.OBJECT = n_old',
    r'pinstancestorage.SLOTS = eps /\ pinstancestorage.NEXT = 0',
    '$instance_storage_basic(S_pin, pinstancestorage)',
    '$weakmap_write_operation_source(S_pin, pdestructionoperation_pending, pweakmapwrite)',
    '$destruction_state_valid(S_pin)',
    '$call_descriptors_valid(S_pin)',
    '$weakref_get(S_pin, n_old_watch) = PNULL',
    '$heap_owners($heap_graph(S_pin), HOBJECT n_old) = 1',
    '$heap_count(HOBJECT n_old, $gc_nodes(S_pin.GC.BUFFER)) = 0',
    '$heap_count(HOBJECT n_old, $gc_physical_nodes(S_pin.GC.BUFFER)) = n_old_gc_before_pin',
    # Only a negative control transplants the genuinely reached later pin.
    'pframe_early_pin = pframe[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: pframe.TODO]',
    'S_early_pin = S_read[.FRAMES = [pframe_early_pin]]',
    '~$weakmap_write_own_call(S_early_pin, pweakmapwrite, pdestructorcall)',
    '~$weakmap_write_callback_read(S_early_pin, paccess)',
    'S_inner_exit_reached = $gc62_seek(S_pin, OWN_INNER_EXIT, n_old, 4000)',
    'S_inner_exit_reached.COMPLETION = BUDGET',
    'S_inner_exit = S_inner_exit_reached[.COMPLETION = NORMAL]',
    'S_inner_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    '$destructor_operation_valid(S_inner_exit, pdestructionoperation_inner)',
    '$weakmap_write_operation_source(S_inner_exit, pdestructionoperation_pending, pweakmapwrite)',
    '$destruction_state_valid(S_inner_exit)',
    '$call_descriptors_valid(S_inner_exit)',
    '$weakref_get(S_inner_exit, n_old_watch) = PNULL',
    '$heap_count(HOBJECT n_old, $gc_physical_nodes(S_inner_exit.GC.BUFFER)) = 0',
    'S_inner_no_pending = S_inner_exit[.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_no_pending]][.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_no_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*]',
    '$destructor_operation_valid(S_inner_no_pending, pdestructionoperation_inner)',
    '~$weakmap_write_operation_source(S_inner_no_pending, pdestructionoperation_no_pending, pweakmapwrite)',
    'S_retired_reached = $gc62_seek(S_inner_exit, OWN_RETIRED, n_old, 4000)',
    'S_retired_reached.COMPLETION = BUDGET',
    'S_retired = S_retired_reached[.COMPLETION = NORMAL]',
    'S_retired.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    '$heap_count(HOBJECT n_old, $gc_physical_nodes(S_retired.GC.BUFFER)) = 0',
    '$weakmap_write_operation_source(S_retired, pdestructionoperation_pending, pweakmapwrite)',
    'S_after_old_paused = $drive_steps(S_retired, 1)',
    'S_after_old_paused.COMPLETION = BUDGET',
    'S_after_old = S_after_old_paused[.COMPLETION = NORMAL]',
    'S_after_old.TODO = (THROW_SEARCH n_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'S_carrier_paused = $drive_steps(S_after_old, 1)',
    'S_carrier_paused.COMPLETION = BUDGET',
    'S_carrier = S_carrier_paused[.COMPLETION = NORMAL]',
    'S_carrier.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_carrier) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_carrier) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'pdestructionrelease_carrier.JOBS = [DESTRUCTION_VALUE (HOBJECT n_map)]',
    'pdestructionoperation_carrier.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation_carrier.PENDING = (n_pending)',
    '$heap_owners($heap_graph(S_carrier), HOBJECT n_map) = 3',
    '$weakmap_write_operation_source(S_carrier, pdestructionoperation_carrier, pweakmapwrite)',
    'pweakmapwrite_wrong = pweakmapwrite[.ACCESS = pweakmapwrite.ACCESS[.VALUE = PINT 1]]',
    'S_wrong_claim = S_carrier[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_carrier) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_carrier) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite_wrong) :: ptask_claim_tail*]',
    '~$weakmap_write_operation_source(S_wrong_claim, pdestructionoperation_carrier, pweakmapwrite)',
    'S_drop_paused = $drive_steps(S_carrier, 1)',
    'S_drop_paused.COMPLETION = BUDGET',
    'S_drop = S_drop_paused[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_drop), HOBJECT n_map) = 2',
    'S_exit_paused = $drive_steps(S_drop, 1)',
    'S_exit_paused.COMPLETION = BUDGET',
    'S_exit = S_exit_paused[.COMPLETION = NORMAL]',
    'S_claim_paused = $drive_steps(S_exit, 1)',
    'S_claim_paused.COMPLETION = BUDGET',
    'S_claim = S_claim_paused[.COMPLETION = NORMAL]',
    'S_claim.TODO = (THROW_SEARCH n_pending) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    '$return_discard(S_claim, WEAKMAP_WRITE_CLAIM pweakmapwrite) = S_claim',
    'S_discard_paused = $drive_steps(S_claim, 1)',
    'S_discard_paused.COMPLETION = BUDGET',
    'S_discard = S_discard_paused[.COMPLETION = NORMAL]',
    'S_discard.TODO = (THROW_SEARCH n_pending) :: ptask_claim_tail*',
    '$heap_graph(S_discard) = $heap_graph(S_claim)',
    'S_discard.STORE[n_result_cell] = DEFINED (PINT 31)',
    'S_done = $drive_steps(S_discard, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    '$drive_steps(S_get_paused[.COMPLETION = NORMAL], 4000) = S_done',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
    'S_done.CURRENT = eps',
    r'S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
    'S_done.DESTRUCTION.CALLS = eps',
    'S_done.ITERATORS = eps',
    ENDING,
    '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
NORMAL_CHUNKS = (['B|', 's|', '1', '|', 'L|', '1', '|', 'C|'] + ['1', '|'] * 4
                 + ['A|', '1', '|', 'R|', '0', '|'] + ['1', '|'] * 5
                 + ['M|'] + ['1', '|'] * 2 + ['K|', '1', '|'])
NORMAL_ENDING = 'S_done.EVENTS = [' + ', '.join(
    'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in NORMAL_CHUNKS) + ']'
NORMAL_CHECKS = [
    'pweakmapwrite.ACCESS.OBJECT = (n_map)',
    'pweakmapwrite.OLD.VALUE = POBJECT n_old',
    '$lookup(S.ENV, $ptascii("oldWatch62Peer")) = (n_old_watch_cell)',
    'S.STORE[n_old_watch_cell] = DEFINED (POBJECT n_old_watch)',
    'S_precall_reached = $gc62_seek(S, OWN_PRECALL, n_old, 4000)',
    'S_precall_reached.COMPLETION = BUDGET',
    'S_precall = S_precall_reached[.COMPLETION = NORMAL]',
    '$weakmap_write_operation(S_precall, n_map)',
    '$destruction_state_valid(S_precall)',
    '$call_descriptors_valid(S_precall)',
    '$weakref_get(S_precall, n_old_watch) = POBJECT n_old',
    '$instance_storage_for(S_precall, n_old) = eps',
    'S_enter_reached = $gc62_seek(S_precall, OWN_ENTER, n_old, 4000)',
    'S_enter_reached.COMPLETION = BUDGET',
    'S_enter = S_enter_reached[.COMPLETION = NORMAL]',
    '$weakmap_write_operation(S_enter, n_map)',
    '$destruction_state_valid(S_enter)',
    '$call_descriptors_valid(S_enter)',
    '$weakref_get(S_enter, n_old_watch) = POBJECT n_old',
    '$instance_storage_for(S_enter, n_old) = eps',
    'S_free_reached = $gc62_seek(S_enter, OWN_NORMAL_FREE, n_old, 4000)',
    'S_free_reached.COMPLETION = BUDGET',
    'S_free = S_free_reached[.COMPLETION = NORMAL]',
    'S_free.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_free) :: (DESTRUCTOR_RELEASE pdestructionrelease_old) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation.PENDING = eps',
    'pdestructionrelease_free.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]',
    'pdestructionrelease_old.JOBS = eps',
    'S_free.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
    'S_free.DESTRUCTION.RELEASES = [pdestructionrelease_free, pdestructionrelease_old]',
    'S_free.DESTRUCTION.CALLS = eps',
    'n_old <- S_free.DESTRUCTION.CALLED',
    '$heap_owners($heap_graph(S_free), HOBJECT n_old) = 1',
    '$weakref_get(S_free, n_old_watch) = POBJECT n_old',
    '$instance_storage_for(S_free, n_old) = eps',
    '$weakmap_write_operation_source(S_free, pdestructionoperation, pweakmapwrite)',
    '$destruction_state_valid(S_free)',
    '$call_descriptors_valid(S_free)',
    'S_after_free = $call_after_origin(S_free, DESTRUCTOR_RELEASE pdestructionrelease_free)',
    'S_future = $call_after_origin(S_after_free, DESTRUCTOR_RELEASE pdestructionrelease_old)',
    'S_future.DESTRUCTION.RELEASES = eps',
    '~$destructor_operation_valid(S_future, pdestructionoperation)',
    '$eager_operation_task_valid(S_future, pdestructionoperation)',
    'pdestructionrelease_temp = pdestructionrelease_free[.JOBS = [DESTRUCTION_TEMP (HOBJECT n_old)]]',
    'S_future_temp = S_future[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_temp) :: (DESTRUCTOR_RELEASE pdestructionrelease_old) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*]',
    '~$eager_operation_task_valid(S_future_temp, pdestructionoperation)',
    '~$eager_operation_task_valid(S_future[.DESTRUCTION.CALLED = eps], pdestructionoperation)',
    'S_pin_reached = $gc62_seek(S_free, OWN_PIN, n_old, 4000)',
    'S_pin_reached.COMPLETION = BUDGET',
    'S_pin = S_pin_reached[.COMPLETION = NORMAL]',
    'S_pin.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: (DESTRUCTOR_RELEASE pdestructionrelease_free[.JOBS = eps]) :: (DESTRUCTOR_RELEASE pdestructionrelease_old) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    r'pinstancestorage.OBJECT = n_old /\ pinstancestorage.SLOTS = eps /\ pinstancestorage.NEXT = 0',
    '$instance_storage_basic(S_pin, pinstancestorage)',
    '$weakref_get(S_pin, n_old_watch) = PNULL',
    '$heap_owners($heap_graph(S_pin), HOBJECT n_old) = 1',
    '$weakmap_write_operation_source(S_pin, pdestructionoperation, pweakmapwrite)',
    '$destruction_state_valid(S_pin)',
    '$call_descriptors_valid(S_pin)',
    'S_retired_reached = $gc62_seek(S_pin, OWN_RETIRED, n_old, 4000)',
    'S_retired_reached.COMPLETION = BUDGET',
    'S_retired = S_retired_reached[.COMPLETION = NORMAL]',
    '$weakmap_write_operation_source(S_retired, pdestructionoperation, pweakmapwrite)',
    '$destruction_state_valid(S_retired)',
    '$call_descriptors_valid(S_retired)',
    'S_claim_reached = $gc62_seek(S_retired, OWN_NORMAL_CLAIM, n_old, 4000)',
    'S_claim_reached.COMPLETION = BUDGET',
    'S_claim = S_claim_reached[.COMPLETION = NORMAL]',
    'S_claim.TODO = (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_tail*',
    'S_claim.RESULT = KNOWN PNULL',
    '$weakmap_write_claim_valid(S_claim, pweakmapwrite)',
    'PhpStep: S_claim ~> S_pop',
    'S_pop = S_claim[.TODO = ptask_claim_tail*]',
    'S_zero = $drive_steps(S_free, 0)',
    'S_zero = S_free[.COMPLETION = BUDGET]',
    'S_done = $drive_steps(S_pop, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
    'S_done.CURRENT = eps',
    r'S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
    'S_done.DESTRUCTION.CALLS = eps',
    'S_done.ITERATORS = eps',
    NORMAL_ENDING,
    '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {
    'own-call-weak-live-then-real-storage': {
        'source': SOURCE, 'stage': STAGE, 'checks': CHECKS},
    'own-normal-storage-certificate': {
        'source': (ROOT / 'tests/semantics/gc62_peer_null_own_read.php').read_text(),
        'stage': STAGE, 'checks': NORMAL_CHECKS},
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
