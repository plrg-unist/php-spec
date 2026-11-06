#!/usr/bin/env python3
"""Actual own-call fields, shared-slot transfer, ordered Child calls and ancestry."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc63_peer_shared_own_slots.php').read_text()
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if S.CURRENT = eps '
    '-- if $weakmap_write_plan(S[.COMPLETION = NORMAL]) = (pweakmapwrite) '
    '-- if pweakmapwrite.ACCESS.VALUE = PNULL '
    '-- if pweakmapwrite.OLD.VALUE = POBJECT n_old')
DECLARATIONS = r'''syntax pgc63stage = PRECALL | OWN_ENTER | OWN_GET | OWN_READ | ROOT_FREE | PIN_START | SHARED_JOB | MIDDLE_ENTER | MIDDLE_READ | SHARED_READ | PIN_DONE | RETIRED
dec $gc63_call_object(pstate) : nat?
def $gc63_call_object(S) = (pdestructorcall.OBJECT)
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $gc63_call_object(S) = eps -- otherwise
dec $gc63_at(pstate, pgc63stage, nat, nat, nat) : bool
def $gc63_at(S, PRECALL, n_old, n_shared, n_middle) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old /\ ~(n_old <- S.DESTRUCTION.CALLED)
def $gc63_at(S, OWN_ENTER, n_old, n_shared, n_middle) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_old
def $gc63_at(S, ROOT_FREE, n_old, n_shared, n_middle) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.CALLS = eps /\ n_old <- S.DESTRUCTION.CALLED
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]
  -- if $instance_storage_for(S, n_old) = eps
  -- if $heap_owners($heap_graph(S), HOBJECT n_old) = 1
def $gc63_at(S, MIDDLE_ENTER, n_old, n_shared, n_middle) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_middle
def $gc63_at(S, OWN_GET, n_old, n_shared, n_middle) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET /\ pconfigcall.SENT = eps
  -- if pconfigcall.OWNER = (n_wrapper)
  -- if $weakref_get(S, n_wrapper) = POBJECT n_old
  -- if $gc63_call_object(S) = (n_old)
def $gc63_at(S, OWN_READ, n_old, n_shared, n_middle) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if $gc63_call_object(S) = (n_old)
def $gc63_at(S, PIN_START, n_old, n_shared, n_middle) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n_old /\ pinstancestorage.NEXT = 0
def $gc63_at(S, SHARED_JOB, n_old, n_shared, n_middle) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_shared)]
  -- if pinstancestorage.OBJECT = n_old /\ pinstancestorage.NEXT = 2
def $gc63_at(S, MIDDLE_READ, n_old, n_shared, n_middle) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if $gc63_call_object(S) = (n_middle)
def $gc63_at(S, SHARED_READ, n_old, n_shared, n_middle) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if $gc63_call_object(S) = (n_shared)
def $gc63_at(S, PIN_DONE, n_old, n_shared, n_middle) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n_old /\ pinstancestorage.NEXT = 5
def $gc63_at(S, RETIRED, n_old, n_shared, n_middle) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME paccess) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old /\ pweakmapwrite.ACCESS = paccess
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
def $gc63_at(S, pgc63stage, n_old, n_shared, n_middle) = false -- otherwise
dec $gc63_seek(pstate, pgc63stage, nat, nat, nat, nat) : pstate
def $gc63_seek(S, pgc63stage, n_old, n_shared, n_middle, n) = S
  -- if $gc63_at(S, pgc63stage, n_old, n_shared, n_middle)
def $gc63_seek(S, pgc63stage, n_old, n_shared, n_middle, n) = $gc63_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc63stage, n_old, n_shared, n_middle, $nabs($(n - 1)))
  -- if ~$gc63_at(S, pgc63stage, n_old, n_shared, n_middle) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc63_seek(S, pgc63stage, n_old, n_shared, n_middle, 0) = S
  -- if ~$gc63_at(S, pgc63stage, n_old, n_shared, n_middle)
def $gc63_seek(S, pgc63stage, n_old, n_shared, n_middle, n) = S
  -- if ~$gc63_at(S, pgc63stage, n_old, n_shared, n_middle)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def seek(before, state, stage):
    return [f'{state}_reached = $gc63_seek({before}, {stage}, n_old, n_shared, n_middle, 4000)',
            f'{state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]']


SETUP = [
    'pweakmapwrite.ACCESS.OBJECT = (n_map)',
    'pweakmapwrite.ACCESS.OFFSET = POBJECT n_key',
    '$objectprops_at(S.OBJECTPROPS, n_old) = ([ppropertyslot_lead, ppropertyslot_first, ppropertyslot_middle, ppropertyslot_last, ppropertyslot_tail])',
    'ppropertyslot_lead.STATE = PROP_VALUE (DIRECT (PINT 17))',
    'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_shared))',
    'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
    'ppropertyslot_last.STATE = ppropertyslot_first.STATE',
    'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (PINT 23))',
    'n_shared =/= n_middle',
    'ppropertyslot_original* = [ppropertyslot_lead, ppropertyslot_first, ppropertyslot_middle, ppropertyslot_last, ppropertyslot_tail]',
    '$node_children(S, HOBJECT n_old) = [HOBJECT n_shared, HOBJECT n_middle, HOBJECT n_shared]',
    '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_shared) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
    '~$weakmap_write_old_value(S, n_old)',
    '~$weakmap_write_own_value(S, n_old)',
    '$weakmap_write_declared_value(S, n_old)',
    '$lookup(S.ENV, $ptascii("oldWatch63Peer")) = (n_old_watch_cell)',
    'S.STORE[n_old_watch_cell] = DEFINED (POBJECT n_old_watch)',
    '$lookup(S.ENV, $ptascii("sharedWatch63Peer")) = (n_shared_watch_cell)',
    'S.STORE[n_shared_watch_cell] = DEFINED (POBJECT n_shared_watch)',
    '$lookup(S.ENV, $ptascii("middleWatch63Peer")) = (n_middle_watch_cell)',
    'S.STORE[n_middle_watch_cell] = DEFINED (POBJECT n_middle_watch)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = $drive_steps(S, 1)',
]
OWN = [
    *seek('S', 'S_get', 'OWN_GET'),
    'S_get.CURRENT = (pcallcontext_own)',
    '$destructor_context_call(pcallcontext_own, S_get.CURRENT, S_get.FRAMES) = (pdestructorcall_own)',
    'pdestructorcall_own.OPERATION = (pdestructionoperation_outer)',
    'pdestructionoperation_outer.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation_outer.PENDING = eps',
    '$weakref_get(S_get, n_old_watch) = POBJECT n_old',
    '$instance_storage_for(S_get, n_old) = eps',
    '$heap_owners($heap_graph(S_get), HOBJECT n_old) = 2',
    '$heap_owners($heap_graph(S_get), HOBJECT n_shared) = 2',
    '$heap_owners($heap_graph(S_get), HOBJECT n_middle) = 1',
    '$node_children(S_get, HOBJECT n_old) = [HOBJECT n_shared, HOBJECT n_middle, HOBJECT n_shared]',
    '$destruction_state_valid(S_get)',
    '$call_descriptors_valid(S_get)',
    'PhpStep: S_get ~> S_get_raw',
    'S_get_raw.RESULT = KNOWN (POBJECT n_old)',
    '$heap_owners($heap_graph(S_get_raw), HOBJECT n_old) = 3',
    '$heap_owners($heap_graph(S_get_raw), HOBJECT n_shared) = 2',
    '$heap_owners($heap_graph(S_get_raw), HOBJECT n_middle) = 1',
    'S_get_raw.OBJECTPROPS = S_get.OBJECTPROPS',
    'S_get_paused = $drive_steps(S_get, 1)',
    'S_get_paused.COMPLETION = BUDGET',
    'S_get_one = S_get_paused[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_get_one), HOBJECT n_old) = 3',
    '$heap_owners($heap_graph(S_get_one), HOBJECT n_shared) = 2',
    '$heap_owners($heap_graph(S_get_one), HOBJECT n_middle) = 1',
    '$drive_steps(S_get, 2) = $drive_steps(S_get_one, 1)',
    *seek('S_get_paused', 'S_own_read', 'OWN_READ'),
    '$heap_owners($heap_graph(S_own_read), HOBJECT n_old) = 2',
    '$heap_owners($heap_graph(S_own_read), HOBJECT n_shared) = 2',
    '$heap_owners($heap_graph(S_own_read), HOBJECT n_middle) = 1',
    '$weakref_get(S_own_read, n_old_watch) = POBJECT n_old',
    '$instance_storage_for(S_own_read, n_old) = eps',
    '$eager_operation_source_valid(S_own_read, pdestructionoperation_outer)',
    '$destruction_state_valid(S_own_read)',
    '$call_descriptors_valid(S_own_read)',
]
SLOTS = [
    *seek('S_own_read', 'S_pin_start', 'PIN_START'),
    'S_pin_start.TODO = (INSTANCE_STORAGE_STEP pinstancestorage_start) :: ptask_start_tail*',
    'pinstancestorage_start.SLOTS = ppropertyslot_original*',
    'pinstancestorage_start.NEXT = 0',
    '$weakref_get(S_pin_start, n_old_watch) = PNULL',
    '$heap_owners($heap_graph(S_pin_start), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_pin_start), HOBJECT n_shared) = 2',
    '$heap_owners($heap_graph(S_pin_start), HOBJECT n_middle) = 1',
    '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage_start) = [HOBJECT n_old]',
    '$instance_storage_basic(S_pin_start, pinstancestorage_start)',
    '$destruction_state_valid(S_pin_start)',
    '$call_descriptors_valid(S_pin_start)',
    *seek('S_pin_start', 'S_shared_job', 'SHARED_JOB'),
    'S_shared_job.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_shared) :: (INSTANCE_STORAGE_STEP pinstancestorage_after_first) :: ptask_first_tail*',
    'pdestructionrelease_shared.JOBS = [DESTRUCTION_VALUE (HOBJECT n_shared)]',
    'pinstancestorage_after_first.SLOTS = ppropertyslot_original*',
    'pinstancestorage_after_first.NEXT = 2',
    '$objectprops_at(S_shared_job.OBJECTPROPS, n_old) = ([ppropertyslot_lead[.STATE = PROP_UNSET], ppropertyslot_first[.STATE = PROP_UNSET], ppropertyslot_middle, ppropertyslot_last, ppropertyslot_tail])',
    '$node_children(S_shared_job, HOBJECT n_old) = [HOBJECT n_middle, HOBJECT n_shared]',
    '$heap_owners($heap_graph(S_shared_job), HOBJECT n_shared) = 2',
    'S_shared_job.DESTRUCTION.CALLS = eps',
    '~(n_shared <- S_shared_job.DESTRUCTION.CALLED)',
    '$destruction_state_valid(S_shared_job)',
    '$call_descriptors_valid(S_shared_job)',
    'S_drop_paused = $drive_steps(S_shared_job, 1)',
    'S_drop_paused.COMPLETION = BUDGET',
    'S_drop = S_drop_paused[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_drop), HOBJECT n_shared) = 1',
    '$heap_owners($heap_graph(S_drop), HOBJECT n_middle) = 1',
    'S_drop.OBJECTPROPS = S_shared_job.OBJECTPROPS',
    'S_drop.DESTRUCTION.CALLS = eps',
    '~(n_shared <- S_drop.DESTRUCTION.CALLED)',
    '$weakref_get(S_drop, n_shared_watch) = POBJECT n_shared',
    '$drive_steps(S_shared_job, 2) = $drive_steps(S_drop, 1)',
    *seek('S_drop', 'S_middle_enter', 'MIDDLE_ENTER'),
    '$destruction_state_valid(S_middle_enter)',
    '$call_descriptors_valid(S_middle_enter)',
    *seek('S_middle_enter', 'S_middle', 'MIDDLE_READ'),
    '$instance_storage_for(S_middle, n_old) = (pinstancestorage_middle)',
    'pinstancestorage_middle.SLOTS = ppropertyslot_original*',
    'pinstancestorage_middle.NEXT = 3',
    '$weakref_get(S_middle, n_old_watch) = PNULL',
    '$instance_storage_for(S_middle, n_middle) = eps',
    '$heap_owners($heap_graph(S_middle), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_middle), HOBJECT n_middle) = 2',
    '$heap_owners($heap_graph(S_middle), HOBJECT n_shared) = 1',
    '$node_children(S_middle, HOBJECT n_old) = [HOBJECT n_shared]',
    '$weakmap_write_selected_child(pinstancestorage_middle) = (n_middle)',
    '~$weakmap_write_pin(S_middle, pweakmapwrite, pinstancestorage_middle)',
    '$destruction_state_valid(S_middle)',
    '$call_descriptors_valid(S_middle)',
    *seek('S_middle', 'S_shared', 'SHARED_READ'),
    '$instance_storage_for(S_shared, n_old) = (pinstancestorage_last)',
    'pinstancestorage_last.SLOTS = ppropertyslot_original*',
    'pinstancestorage_last.NEXT = 4',
    '$weakref_get(S_shared, n_old_watch) = PNULL',
    '$weakref_get(S_shared, n_middle_watch) = PNULL',
    '~((HOBJECT n_middle) <- S_shared.ALLOCATIONS)',
    '$instance_storage_for(S_shared, n_shared) = eps',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_shared) = 2',
    '$node_children(S_shared, HOBJECT n_old) = eps',
    '$weakmap_write_selected_child(pinstancestorage_last) = (n_shared)',
    '~$weakmap_write_pin(S_shared, pweakmapwrite, pinstancestorage_last)',
    '$destruction_state_valid(S_shared)',
    '$call_descriptors_valid(S_shared)',
]


def read_controls(state, child, pin, tag, fresh):
    call = 'pdestructorcall_' + tag
    context = 'pcallcontext_' + tag
    operation = 'pdestructionoperation_' + tag
    frame = 'pframe_' + tag
    original = 'pdestructionrelease_original_' + tag
    empty = 'pdestructionrelease_empty_' + tag
    tail = 'ptask_frame_' + tag + '*'
    result = [
        f'{state}.CURRENT = ({context})',
        f'$destructor_context_call({context}, {state}.CURRENT, {state}.FRAMES) = ({call})',
        f'{call}.OBJECT = {child}',
        f'{call}.OPERATION = ({operation})',
        f'{call}.PENDING = eps',
        f'{call}.RELEASE = ({original})',
        f'{original}.JOBS = [DESTRUCTION_VALUE (HOBJECT {child})]',
        f'{empty} = {original}[.JOBS = eps]',
        f'{state}.DESTRUCTION.CALLS = [{call}]',
        f'{state}.FRAMES = [{frame}]',
        f'{frame}.TODO = (DESTRUCTOR_RESULT {call}) :: {tail}',
        f'$weakmap_write_declared_pin({state}, pweakmapwrite, {pin})',
        f'$heap_owners($heap_graph({state}), HOBJECT n_map) = 3',
        f'$heap_owners($heap_graph({state}), HOBJECT n_key) = 2',
        f'{state}.TODO = (KEY_READ_DIM poperand_key_{tag} z_{tag} KEY_R) :: ptask_read_{tag}*',
        f'{state}.ORIGIN = (porigin_{tag})',
        f'paccess_initial_{tag} = $access_record({state}, porigin_{tag}, z_{tag}, ACCESS_READ KEY_R, BASE_VALUE {state}.RESULT, poperand_key_{tag}, KNOWN PNULL, KEY_READ_DIM poperand_key_{tag} z_{tag} KEY_R, (n_map), true)',
        f'paccess_{tag} = paccess_initial_{tag}[.SELECTED = $rcontainer_selected({state}, {state}.RESULT)][.OFFSET = POBJECT n_key]',
        f'$weakmap_write_callback_read({state}, paccess_{tag})',
        f'~$weakmap_write_callback_read({state}, paccess_{tag}[.SELECTED = KNOWN (POBJECT n_map)])',
    ]
    if fresh:
        result += [
            f'$weakmap_write_declared_ancestry({state}, {call}) = (pweakmapwrite)',
            f'{state}.DESTRUCTION.OPERATIONS = [{operation}, pdestructionoperation_pending]',
            'pdestructionoperation_pending.PENDING = (n_pending)',
            'n_pending = pweakmapwrite.FIRSTNEW',
            'pdestructionoperation_pending = pdestructionoperation_outer[.PENDING = (n_pending)]',
            f'{operation}.SOURCE = THROW_SEARCH n_pending',
            f'{operation}.PENDING = eps',
            f'$destructor_operation_live({state}, {operation})',
            f'$weakmap_write_declared_child_call({state}, pweakmapwrite, {pin}, {call})',
            f'~$weakmap_write_selected_call({state}, pweakmapwrite, {pin}, {call})',
            f'{tail} = (DESTRUCTOR_RELEASE {empty}) :: (INSTANCE_STORAGE_STEP {pin}) :: (DESTRUCTOR_RELEASE pdestructionrelease_free_{tag}) :: (DESTRUCTOR_OPERATION_EXIT {operation}) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_{tag}) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_{tag}*',
        ]
    else:
        result += [
            f'{operation} = pdestructionoperation_outer',
            f'{operation}.PENDING = eps',
            f'$weakmap_write_declared_ancestry({state}, {call}) = eps',
            f'$weakmap_write_selected_call({state}, pweakmapwrite, {pin}, {call})',
            f'{tail} = (DESTRUCTOR_RELEASE {empty}) :: (INSTANCE_STORAGE_STEP {pin}) :: (DESTRUCTOR_RELEASE pdestructionrelease_free_{tag}) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_{tag}) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_outer) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_{tag}*',
        ]
    guard = '$weakmap_write_declared_child_call' if fresh else '$weakmap_write_selected_call'
    result += [
        f'pdestructorcall_bad_{tag} = {call}[.RELEASE = ({original}[.JOBS = [DESTRUCTION_TEMP (HOBJECT {child})]])]',
        f'S_bad_{tag} = {state}[.DESTRUCTION.CALLS = [pdestructorcall_bad_{tag}]][.FRAMES = [{frame}[.TODO = (DESTRUCTOR_RESULT pdestructorcall_bad_{tag}) :: {tail}]]]',
        f'~{guard}(S_bad_{tag}, pweakmapwrite, {pin}, pdestructorcall_bad_{tag})',
        f'S_frame_{tag} = $call_frame_scope({state}, {frame}, eps)',
        f'S_tasks_{tag} = $destructor_saved_frame_scope($api_saved_frame_scope($parameter_string_frame_scope(S_frame_{tag}, {frame}, eps), {frame}, eps), {frame})',
        f'S_after_result_{tag} = $call_after_origin(S_tasks_{tag}, DESTRUCTOR_RESULT {call})',
        f'S_after_child_{tag} = $call_after_origin(S_after_result_{tag}, DESTRUCTOR_RELEASE {empty})',
        f'S_after_free_{tag} = $call_after_origin(S_after_child_{tag}, DESTRUCTOR_RELEASE pdestructionrelease_free_{tag})',
    ]
    if fresh:
        result += [
            f'S_after_inner_{tag} = $call_after_origin(S_after_free_{tag}, DESTRUCTOR_OPERATION_EXIT {operation})',
            f'S_future_{tag} = $call_after_origin(S_after_inner_{tag}, DESTRUCTOR_RELEASE pdestructionrelease_old_{tag})',
        ]
    else:
        result += [f'S_future_{tag} = $call_after_origin(S_after_free_{tag}, DESTRUCTOR_RELEASE pdestructionrelease_old_{tag})']
    outer = 'pdestructionoperation_pending' if fresh else 'pdestructionoperation_outer'
    result += [
        f'S_future_{tag}.DESTRUCTION.RELEASES = eps',
        f'S_future_{tag}.DESTRUCTION.CALLS = eps',
        f'S_future_{tag}.DESTRUCTION.OPERATIONS = [{outer}]',
        f'~$destructor_operation_valid(S_future_{tag}, {outer})',
        f'$eager_operation_task_valid(S_future_{tag}, {outer})',
        f'S_future_bad_{tag} = S_future_{tag}[.TODO = (DESTRUCTOR_RESULT pdestructorcall_bad_{tag}) :: {tail}]',
        f'~$eager_operation_task_valid(S_future_bad_{tag}, {outer})',
        f'~$eager_operation_task_valid(S_future_{tag}[.DESTRUCTION.CALLED = eps], {outer})',
        f'S_read_paused_{tag} = $drive_steps({state}, 1)',
        f'S_read_paused_{tag}.COMPLETION = BUDGET',
        f'S_read_after_{tag} = S_read_paused_{tag}[.COMPLETION = NORMAL]',
        f'S_read_after_{tag}.RESULT = KNOWN PNULL',
        f'S_read_after_{tag}.OBJECTPROPS = {state}.OBJECTPROPS',
        f'S_read_after_{tag}.ALLOCATIONS = {state}.ALLOCATIONS',
        f'$heap_owners($heap_graph(S_read_after_{tag}), HOBJECT {child}) = 2',
        f'$heap_owners($heap_graph(S_read_after_{tag}), HOBJECT n_old) = 1',
        f'$heap_owners($heap_graph(S_read_after_{tag}), HOBJECT n_map) = 3',
        f'$heap_owners($heap_graph(S_read_after_{tag}), HOBJECT n_key) = 2',
    ]
    return result


def coherent_controls(fresh):
    outer = 'pdestructionoperation_pending' if fresh else 'pdestructionoperation_outer'
    after_pin = '(DESTRUCTOR_RELEASE pdestructionrelease_free_shared) :: '
    if fresh:
        after_pin += '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_shared) :: '
    after_pin += ('(DESTRUCTOR_RELEASE pdestructionrelease_old_shared) :: '
                  f'(DESTRUCTOR_OPERATION_EXIT {outer}) :: '
                  '(ACCESS_RESUME pweakmapwrite.ACCESS) :: '
                  '(WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_claim_shared*')
    guard = '$weakmap_write_declared_child_call' if fresh else '$weakmap_write_selected_call'
    result = [
        # Rewind to the first Shared visit and restore its still-owning later edge.
        'pinstancestorage_earlier = pinstancestorage_last[.SLOTS = [ppropertyslot_lead, ppropertyslot_first, ppropertyslot_middle[.STATE = PROP_UNSET], ppropertyslot_last, ppropertyslot_tail]][.NEXT = 2]',
        'pframe_earlier = pframe_shared[.TODO = (DESTRUCTOR_RESULT pdestructorcall_shared) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty_shared) :: (INSTANCE_STORAGE_STEP pinstancestorage_earlier) :: ' + after_pin + ']',
        'S_earlier = S_shared[.FRAMES = [pframe_earlier]][.OBJECTPROPS = $objectprops_set(S_shared.OBJECTPROPS, n_old, [ppropertyslot_lead[.STATE = PROP_UNSET], ppropertyslot_first[.STATE = PROP_UNSET], ppropertyslot_middle[.STATE = PROP_UNSET], ppropertyslot_last, ppropertyslot_tail])]',
        '$instance_storage_basic(S_earlier, pinstancestorage_earlier)',
        '$weakmap_write_selected_child(pinstancestorage_earlier) = (n_shared)',
        '$heap_valid($heap_graph(S_earlier))',
        '$heap_owners($heap_graph(S_earlier), HOBJECT n_shared) = 3',
        f'~{guard}(S_earlier, pweakmapwrite, pinstancestorage_earlier, pdestructorcall_shared)',
        '~$weakmap_write_callback_read(S_earlier, paccess_shared)',
    ]
    if fresh:
        no_pending = after_pin.replace('(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending)',
                                       '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_outer)')
        result += [
            'pframe_no_pending = pframe_shared[.TODO = (DESTRUCTOR_RESULT pdestructorcall_shared) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty_shared) :: (INSTANCE_STORAGE_STEP pinstancestorage_last) :: ' + no_pending + ']',
            'S_no_pending = S_shared[.DESTRUCTION.OPERATIONS = [pdestructionoperation_shared, pdestructionoperation_outer]][.FRAMES = [pframe_no_pending]]',
            '$heap_valid($heap_graph(S_no_pending))',
            '$destructor_operation_live(S_no_pending, pdestructionoperation_shared)',
            '$weakmap_write_declared_ancestry(S_no_pending, pdestructorcall_shared) = eps',
            '~$weakmap_write_declared_child_call(S_no_pending, pweakmapwrite, pinstancestorage_last, pdestructorcall_shared)',
            '~$weakmap_write_callback_read(S_no_pending, paccess_shared)',
            'S_future_no_pending = S_future_shared[.DESTRUCTION.OPERATIONS = [pdestructionoperation_outer]][.TODO = pframe_no_pending.TODO]',
            '~$eager_operation_task_valid(S_future_no_pending, pdestructionoperation_outer)',
            'pdestructorcall_retagged = pdestructorcall_shared[.OPERATION = (pdestructionoperation_pending)]',
            'S_retagged = S_shared[.DESTRUCTION.CALLS = [pdestructorcall_retagged]][.FRAMES = [pframe_shared[.TODO = (DESTRUCTOR_RESULT pdestructorcall_retagged) :: ptask_frame_shared*]]]',
            '$heap_graph(S_retagged) = $heap_graph(S_shared)',
            '$weakmap_write_declared_ancestry(S_retagged, pdestructorcall_retagged) = eps',
            '~$weakmap_write_declared_child_call(S_retagged, pweakmapwrite, pinstancestorage_last, pdestructorcall_retagged)',
            '~$weakmap_write_callback_read(S_retagged, paccess_shared)',
        ]
    return result


def ending(fresh):
    chunks = ['B|', 's|', '1', '|', 'O|', '1', '|', 'U|'] + ['1', '|'] * 4
    if not fresh:
        chunks += ['o|']
    chunks += ['M|', '1', '|', 'I|'] + ['1', '|'] * 2
    chunks += ['C|', '1', '|', 'J|'] + ['1', '|'] * 2
    if fresh:
        chunks += ['T|', 'peer-fresh-63', '|', '36', '|', '__destruct', '|', '70', '|', '1', '|', '0', '|']
        chunks += ['R|', '1', '|', '0', '|', '0', '|'] + ['1', '|'] * 5
    else:
        chunks += ['A|', '1', '|', 'R|', '0', '|'] + ['1', '|'] * 7
    chunks += ['m|'] + ['1', '|'] * 2 + ['K|', '1', '|']
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(x) + ')' for x in chunks) + ']'


def finish(fresh):
    return [
        *seek('S_shared', 'S_pin_done', 'PIN_DONE'),
        '$weakref_get(S_pin_done, n_old_watch) = PNULL',
        '$weakref_get(S_pin_done, n_shared_watch) = PNULL',
        '~((HOBJECT n_shared) <- S_pin_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_pin_done), HOBJECT n_old) = 1',
        '$destruction_state_valid(S_pin_done)',
        '$call_descriptors_valid(S_pin_done)',
        *seek('S_pin_done', 'S_retired', 'RETIRED'),
        '$destruction_state_valid(S_retired)',
        '$call_descriptors_valid(S_retired)',
        'S_done = $drive_steps(S_retired, 4000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
        r'S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.DESTRUCTION.CALLS = eps', 'S_done.ITERATORS = eps',
        ending(fresh),
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
        '$heap_valid($heap_graph(S_done))',
    ]


NORMAL_PHASES = [
    *seek('S', 'S_precall', 'PRECALL'),
    'S_precall.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_precall) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_outer) :: ptask_precall_tail*',
    'pdestructionoperation_outer.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation_outer.PENDING = eps',
    '$destruction_state_valid(S_precall)',
    '$call_descriptors_valid(S_precall)',
    *seek('S_precall', 'S_enter', 'OWN_ENTER'),
    '$destruction_state_valid(S_enter)',
    '$call_descriptors_valid(S_enter)',
    '$weakref_get(S_enter, n_old_watch) = POBJECT n_old',
    *seek('S_enter', 'S_free', 'ROOT_FREE'),
    '$eager_operation_source_valid(S_free, pdestructionoperation_outer)',
    '$destruction_state_valid(S_free)',
    '$call_descriptors_valid(S_free)',
    '$weakref_get(S_free, n_old_watch) = POBJECT n_old',
    *seek('S_free', 'S_middle_enter', 'MIDDLE_ENTER'),
    '$destruction_state_valid(S_middle_enter)',
    '$call_descriptors_valid(S_middle_enter)',
    *seek('S_middle_enter', 'S_middle', 'MIDDLE_READ'),
    '$instance_storage_for(S_middle, n_old) = (pinstancestorage_middle)',
    'pinstancestorage_middle.SLOTS = ppropertyslot_original*',
    'pinstancestorage_middle.NEXT = 3',
    '$weakref_get(S_middle, n_old_watch) = PNULL',
    '$heap_owners($heap_graph(S_middle), HOBJECT n_middle) = 2',
    '$heap_owners($heap_graph(S_middle), HOBJECT n_shared) = 1',
    '$destruction_state_valid(S_middle)',
    '$call_descriptors_valid(S_middle)',
    *seek('S_middle', 'S_shared', 'SHARED_READ'),
    '$instance_storage_for(S_shared, n_old) = (pinstancestorage_last)',
    'pinstancestorage_last.SLOTS = ppropertyslot_original*',
    'pinstancestorage_last.NEXT = 4',
    '$weakref_get(S_shared, n_old_watch) = PNULL',
    '$weakref_get(S_shared, n_middle_watch) = PNULL',
    '~((HOBJECT n_middle) <- S_shared.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_shared) = 2',
    '$node_children(S_shared, HOBJECT n_old) = eps',
    '$destruction_state_valid(S_shared)',
    '$call_descriptors_valid(S_shared)',
]


review.CASES = {
    'shared-own-slots-fresh-state': {
        'source': SOURCE.replace('$throw63Peer = false;', '$throw63Peer = true;'),
        'stage': STAGE, 'checks': [*SETUP, *OWN, *SLOTS,
                                  *read_controls('S_middle', 'n_middle', 'pinstancestorage_middle', 'middle', True),
                                  *read_controls('S_shared', 'n_shared', 'pinstancestorage_last', 'shared', True),
                                  *coherent_controls(True),
                                  *finish(True)]},
    'shared-own-slots-normal-state': {
        'source': SOURCE, 'stage': STAGE,
        'checks': [*SETUP, *NORMAL_PHASES,
                   *read_controls('S_middle', 'n_middle', 'pinstancestorage_middle', 'middle', False),
                   *read_controls('S_shared', 'n_shared', 'pinstancestorage_last', 'shared', False),
                   *coherent_controls(False)]},
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
