#!/usr/bin/env python3
"""Real shared-array retirement, selected descendant calls and refusal."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = (ROOT / 'tests/semantics/gc67_peer_shared_property_array.php').read_text()
FRESH = ORIGINAL.replace('$throwOwn67Peer = false;', '$throwOwn67Peer = true;')
BOUNDARY = FRESH.replace('$throwArray67Peer = false;', '$throwArray67Peer = true;')
OWN_STAGE = (
    'S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall_own) '
    '-- if pdestructorcall_own.OPERATION = (pdestructionoperation_own) '
    '-- if pdestructionoperation_own.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite '
    '-- if pweakmapwrite.OLD.VALUE = POBJECT pdestructorcall_own.OBJECT')
ENTER_STAGE = (
    'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_array) :: ptask_tail* '
    '-- if $object_name(S, pdestructorcall_array.OBJECT) = $ptascii("GC67ArrayChildPeer") '
    '-- if pdestructorcall_array.OPERATION = (pdestructionoperation_parent) '
    '-- if pdestructionoperation_parent.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite '
    '-- if pdestructionoperation_parent.PENDING = eps')
BOUNDARY_STAGE = (
    'S.TODO = (THROW_SEARCH n_new) :: (DESTRUCTOR_RESULT pdestructorcall_array) :: ptask_after_result* '
    '-- if $object_name(S, pdestructorcall_array.OBJECT) = $ptascii("GC67ArrayChildPeer") '
    '-- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_parent] '
    '-- if pdestructionoperation_parent.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite '
    '-- if pdestructionoperation_parent.PENDING = (n_pending)')
DECLARATIONS = r'''syntax pgc67stage = READ | SHARED | LAST | ENTER | RESULT | PIN | PARENT
dec $gc67_at(pstate, pgc67stage, nat, nat, nat) : bool
def $gc67_at(S, READ, n_old, n_box, n_callback) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_callback
def $gc67_at(S, SHARED, n_old, n_box, n_callback) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_box)]
  -- if $instance_storage_for(S, n_old) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 1
def $gc67_at(S, LAST, n_old, n_box, n_callback) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_box)]
  -- if $instance_storage_for(S, n_old) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 3
def $gc67_at(S, ENTER, n_old, n_box, n_callback) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_callback
def $gc67_at(S, RESULT, n_old, n_box, n_callback) = true
  -- if S.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_callback
def $gc67_at(S, PIN, n_old, n_box, n_callback) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if pinstancestorage.OBJECT = n_callback
def $gc67_at(S, PARENT, n_old, n_box, n_callback) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME paccess) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite
  -- if pweakmapwrite.OLD.VALUE = POBJECT n_old
  -- if ~((HOBJECT n_old) <- S.ALLOCATIONS)
def $gc67_at(S, pgc67stage, n_old, n_box, n_callback) = false -- otherwise
dec $gc67_seek(pstate, pgc67stage, nat, nat, nat, nat) : pstate
def $gc67_seek(S, pgc67stage, n_old, n_box, n_callback, n) = S
  -- if $gc67_at(S, pgc67stage, n_old, n_box, n_callback)
def $gc67_seek(S, pgc67stage, n_old, n_box, n_callback, n) = $gc67_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc67stage, n_old, n_box, n_callback, $nabs($(n - 1)))
  -- if ~$gc67_at(S, pgc67stage, n_old, n_box, n_callback) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc67_seek(S, pgc67stage, n_old, n_box, n_callback, 0) = S
  -- if ~$gc67_at(S, pgc67stage, n_old, n_box, n_callback)
def $gc67_seek(S, pgc67stage, n_old, n_box, n_callback, n) = S
  -- if ~$gc67_at(S, pgc67stage, n_old, n_box, n_callback)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def valid(state):
    return [f'$heap_valid($heap_graph({state}))', f'$destruction_state_valid({state})',
            f'$call_descriptors_valid({state})']


def seek(before, state, stage, callback='n_child'):
    return [f'{state}_paused = $gc67_seek({before}, {stage}, n_old, n_box, {callback}, 4000)',
            f'{state}_paused.COMPLETION = BUDGET', f'{state} = {state}_paused[.COMPLETION = NORMAL]']


def owner(state, kind, node, count):
    return f'$heap_owners($heap_graph({state}), {kind} {node}) = {count}'


def shared(state, count):
    return [owner(state, 'HARRAY', 'n_box', count), owner(state, 'HOBJECT', 'n_child', 2),
            f'$node_children({state}, HARRAY n_box) = [HOBJECT n_child, HOBJECT n_child]']


def budget(before, after):
    return [f'$drive_steps({before}, 0) = {before}[.COMPLETION = BUDGET]',
            f'{after}_paused = $drive_steps({before}, 1)',
            f'{after}_paused.COMPLETION = BUDGET', f'{after} = {after}_paused[.COMPLETION = NORMAL]',
            f'$drive_steps({before}, 2) = $drive_steps({after}, 1)']


def access(state):
    return [f'{state}.TODO = (KEY_READ_DIM poperand_{state} z_{state} KEY_R) :: ptask_{state}_tail*',
            f'{state}.ORIGIN = (porigin_{state})',
            f'paccess_{state}_initial = $access_record({state}, porigin_{state}, z_{state}, ACCESS_READ KEY_R, BASE_VALUE {state}.RESULT, poperand_{state}, KNOWN PNULL, KEY_READ_DIM poperand_{state} z_{state} KEY_R, (n_map), true)',
            f'paccess_{state} = paccess_{state}_initial[.SELECTED = $rcontainer_selected({state}, {state}.RESULT)][.OFFSET = POBJECT n_key]',
            f'$weakmap_write_callback_read({state}, paccess_{state})']


def bindings(state, pin=False):
    source = f'pinstancestorage_initial.SLOTS' if pin else 'ppropertyslot_initial*'
    result = ['pweakmapwrite.OLD.VALUE = POBJECT n_old',
              'pweakmapwrite.ACCESS.OBJECT = (n_map)', 'pweakmapwrite.ACCESS.OFFSET = POBJECT n_key',
              'pweakmapwrite.ACCESS.VALUE = PNULL']
    result += ([f'$instance_storage_for({state}, n_old) = (pinstancestorage_initial)'] if pin else
               [f'$objectprops_at({state}.OBJECTPROPS, n_old) = (ppropertyslot_initial*)'])
    result += [f'{source} = [ppropertyslot_first, ppropertyslot_middle, ppropertyslot_last, ppropertyslot_tail]',
               'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (PARRAY n_box))',
               'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
               'ppropertyslot_last.STATE = PROP_VALUE (DIRECT (PARRAY n_box))',
               'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_tail))',
               f'{state}.ARRAYS[n_box].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (POBJECT n_child)), ENTRY (KINT 2) (DIRECT (POBJECT n_child)), ENTRY (KINT 3) (DIRECT (PINT 23))]']
    return result


def virtual(state, fresh, suffix):
    inner = '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: ' if fresh else ''
    result = [
        f'{state}.FRAMES = [pframe_{suffix}]',
        f'pframe_{suffix}.TODO = (DESTRUCTOR_RESULT pdestructorcall_array) :: (DESTRUCTOR_RELEASE pdestructionrelease_array_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_array) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: {inner}(DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_parent) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_{suffix}_after_claim*',
        f'S_frame_{suffix} = $call_frame_scope({state}, pframe_{suffix}, eps)',
        f'S_tasks_{suffix} = $destructor_saved_frame_scope($api_saved_frame_scope($parameter_string_frame_scope(S_frame_{suffix}, pframe_{suffix}, eps), pframe_{suffix}, eps), pframe_{suffix})',
        f'S_result_{suffix} = $call_after_origin(S_tasks_{suffix}, DESTRUCTOR_RESULT pdestructorcall_array)',
        f'S_array_{suffix} = $call_after_origin(S_result_{suffix}, DESTRUCTOR_RELEASE pdestructionrelease_array_empty)',
        f'S_root_{suffix} = $call_after_origin(S_array_{suffix}, DESTRUCTOR_RELEASE pdestructionrelease_root_empty)',
    ]
    before = f'S_root_{suffix}'
    if fresh:
        result += [f'S_inner_{suffix} = $call_after_origin({before}, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner)']
        before = f'S_inner_{suffix}'
    result += [f'S_virtual_{suffix} = $call_after_origin({before}, DESTRUCTOR_RELEASE pdestructionrelease_old_empty)',
               f'S_virtual_{suffix}.DESTRUCTION.CALLS = eps',
               f'S_virtual_{suffix}.DESTRUCTION.RELEASES = eps',
               f'S_virtual_{suffix}.DESTRUCTION.OPERATIONS = [pdestructionoperation_parent]',
               f'~$destructor_operation_valid(S_virtual_{suffix}, pdestructionoperation_parent)',
               f'$eager_operation_task_valid(S_virtual_{suffix}, pdestructionoperation_parent)']
    return result


def frame_tasks(fresh, pin='pinstancestorage_array', call='pdestructorcall_array',
                release='pdestructionrelease_array_empty', suffix='fresh'):
    inner = '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_inner) :: ' if fresh else ''
    return (f'(DESTRUCTOR_RESULT {call}) :: (DESTRUCTOR_RELEASE {release}) :: '
            f'(INSTANCE_STORAGE_STEP {pin}) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: '
            f'{inner}(DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_parent) :: '
            '(ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: '
            f'ptask_{suffix}_after_claim*')


def retirement_tail(before):
    return [
        *seek(before, 'S_result', 'RESULT'),
        'S_result.TODO = (DESTRUCTOR_RESULT pdestructorcall_array) :: ptask_result_tail*',
        owner('S_result', 'HOBJECT', 'n_child', 1), *valid('S_result'),
        *seek('S_result', 'S_pin', 'PIN'),
        '$instance_storage_for(S_pin, n_child) = (pinstancestorage_child)',
        'pinstancestorage_child.SLOTS = eps', 'pinstancestorage_child.NEXT = 0',
        'pinstancestorage_child.OBJECT =/= n_old',
        owner('S_pin', 'HOBJECT', 'n_child', 1), owner('S_pin', 'HOBJECT', 'n_old', 1),
        '~((HARRAY n_box) <- S_pin.ALLOCATIONS)', *valid('S_pin'),
        *seek('S_pin', 'S_tail', 'READ', 'n_tail'),
        '~((HOBJECT n_child) <- S_tail.ALLOCATIONS)',
        '$instance_storage_for(S_tail, n_old) = (pinstancestorage_tail)',
        'pinstancestorage_tail.NEXT = 4',
        'pinstancestorage_tail.SLOTS = pinstancestorage_array.SLOTS',
        '$weakmap_write_array_pin(S_tail, pweakmapwrite, pinstancestorage_tail)',
        owner('S_tail', 'HOBJECT', 'n_tail', 2), owner('S_tail', 'HOBJECT', 'n_old', 1),
        *access('S_tail'), *valid('S_tail'),
        *seek('S_tail', 'S_parent', 'PARENT'),
        '~((HOBJECT n_old) <- S_parent.ALLOCATIONS)',
        '~((HOBJECT n_tail) <- S_parent.ALLOCATIONS)',
        '~((HARRAY n_box) <- S_parent.ALLOCATIONS)',
        'S_parent.DESTRUCTION.OPERATIONS = [pdestructionoperation_parent]',
        '$weakmap_write_claim_valid(S_parent, pweakmapwrite)', *valid('S_parent'),
        '$drive_steps(S_parent, 0) = S_parent[.COMPLETION = BUDGET]',
    ]


FRESH_CHECKS = [
    *bindings('S'),
    '$weakmap_write_array_value(S, n_old)',
    '~$weakmap_write_old_children(S, $node_children(S, HOBJECT n_old))',
    '$node_children(S, HOBJECT n_old) = [HARRAY n_box, HOBJECT n_middle, HARRAY n_box, HOBJECT n_tail]',
    owner('S', 'HOBJECT', 'n_old', 2), *shared('S', 2), *valid('S'),
    '$weakmap_write_scope(S, pweakmapwrite) = (S_scope)',
    '$lookup(S_scope.ENV, $ptascii("oldWatch67Peer")) = (n_old_watch_cell)',
    'S.STORE[n_old_watch_cell] = DEFINED (POBJECT n_old_watch)',
    '$lookup(S_scope.ENV, $ptascii("sharedWatch67Peer")) = (n_child_watch_cell)',
    'S.STORE[n_child_watch_cell] = DEFINED (POBJECT n_child_watch)',
    '$lookup(S.ENV, $ptascii("result67Peer")) = (n_result_cell)',
    'S.STORE[n_result_cell] = DEFINED (PINT 31)',
    '$weakref_get(S, n_old_watch) = POBJECT n_old',
    '$instance_storage_for(S, n_old) = eps', *access('S'),
    *seek('S', 'S_shared', 'SHARED'),
    'S_shared.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_shared) :: ptask_shared_tail*',
    '$instance_storage_for(S_shared, n_old) = (pinstancestorage_shared)',
    'pinstancestorage_shared.NEXT = 1',
    'pinstancestorage_shared.SLOTS = [ppropertyslot_first, ppropertyslot_middle, ppropertyslot_last, ppropertyslot_tail]',
    '$weakmap_write_array_selected(pinstancestorage_shared) = (n_box)',
    '$weakref_get(S_shared, n_old_watch) = PNULL',
    owner('S_shared', 'HOBJECT', 'n_old', 1), *shared('S_shared', 2), *valid('S_shared'),
    'PhpStep: S_shared ~> S_shared_raw',
    owner('S_shared_raw', 'HARRAY', 'n_box', 1),
    owner('S_shared_raw', 'HOBJECT', 'n_child', 2),
    'S_shared_raw.ARRAYS = S_shared.ARRAYS', 'S_shared_raw.ALLOCATIONS = S_shared.ALLOCATIONS',
    'S_shared_raw.DESTRUCTION.CALLED = S_shared.DESTRUCTION.CALLED',
    *budget('S_shared', 'S_shared_done'),
    *seek('S_shared_done', 'S_middle', 'READ', 'n_middle'),
    owner('S_middle', 'HARRAY', 'n_box', 1), owner('S_middle', 'HOBJECT', 'n_child', 2),
    owner('S_middle', 'HOBJECT', 'n_middle', 2), *access('S_middle'), *valid('S_middle'),
    *seek('S_middle', 'S_last', 'LAST'),
    'S_last.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_last) :: ptask_last_tail*',
    owner('S_last', 'HARRAY', 'n_box', 1), owner('S_last', 'HOBJECT', 'n_child', 2),
    '~((HOBJECT n_middle) <- S_last.ALLOCATIONS)',
    'S_last.DESTRUCTION.OPERATIONS = [pdestructionoperation_inner, pdestructionoperation_parent]',
    'pdestructionoperation_parent.SOURCE = WEAKMAP_WRITE_CLAIM pweakmapwrite',
    'pdestructionoperation_parent.PENDING = (n_pending)',
    'pdestructionoperation_inner.SOURCE = THROW_SEARCH n_pending',
    'pdestructionoperation_inner.PENDING = eps',
    owner('S_last', 'HOBJECT', 'n_pending', 1), *valid('S_last'),
    'PhpStep: S_last ~> S_retired_raw',
    '~((HARRAY n_box) <- S_retired_raw.ALLOCATIONS)',
    'S_retired_raw.ARRAYS = S_last.ARRAYS',
    'S_retired_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_children) :: ptask_last_tail*',
    'pdestructionrelease_children.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child), DESTRUCTION_VALUE (HOBJECT n_child)]',
    owner('S_retired_raw', 'HOBJECT', 'n_child', 2),
    '$heap_count(HARRAY n_box, $gc_nodes(S_retired_raw.GC.BUFFER)) = 0',
    *budget('S_last', 'S_jobs'),
    'S_jobs.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_children) :: ptask_last_tail*', *valid('S_jobs'),
    'PhpStep: S_jobs ~> S_first_raw',
    owner('S_first_raw', 'HOBJECT', 'n_child', 1),
    'S_first_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_children[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]]) :: ptask_last_tail*',
    'S_first_raw.DESTRUCTION.CALLED = S_jobs.DESTRUCTION.CALLED',
    'S_first_raw.ARRAYS = S_jobs.ARRAYS',
    *budget('S_jobs', 'S_first_done'),
    *seek('S_first_done', 'S_enter', 'ENTER'),
    'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall_array) :: ptask_enter_tail*',
    'pdestructorcall_array.RELEASE = (pdestructionrelease_array_original)',
    'pdestructionrelease_array_original.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    'pdestructorcall_array.OPERATION = (pdestructionoperation_inner)',
    '$task_nodes(DESTRUCTOR_ENTER pdestructorcall_array) = [HOBJECT n_child, HOBJECT n_child]',
    owner('S_enter', 'HOBJECT', 'n_child', 2), *valid('S_enter'),
    *seek('S_enter', 'S_array', 'READ'),
    '$instance_storage_for(S_array, n_old) = (pinstancestorage_array)',
    'pinstancestorage_array.NEXT = 3',
    '$weakmap_write_array_selected(pinstancestorage_array) = (n_box)',
    '~((HARRAY n_box) <- S_array.ALLOCATIONS)',
    '$weakmap_write_array_child_call(S_array, pweakmapwrite, pinstancestorage_array, pdestructorcall_array)',
    '$weakref_get(S_array, n_old_watch) = PNULL',
    '$weakref_get(S_array, n_child_watch) = POBJECT n_child',
    owner('S_array', 'HOBJECT', 'n_child', 2), owner('S_array', 'HOBJECT', 'n_old', 1),
    owner('S_array', 'HOBJECT', 'n_pending', 1),
    'S_array.STORE[n_result_cell] = DEFINED (PINT 31)', *access('S_array'), *valid('S_array'),
    *virtual('S_array', True, 'fresh'),
]
FRESH_CHECKS += [
    'n_wrong_array = |S_array.ARRAYS|',
    'parray_wrong = S_array.ARRAYS[n_box][.ITEMS = eps][.NEXT = 0][.POSITIONS = eps][.SERIAL = 0]',
    'pinstancestorage_wrong = pinstancestorage_array[.SLOTS = [ppropertyslot_first, ppropertyslot_middle, ppropertyslot_last[.STATE = PROP_VALUE (DIRECT (PARRAY n_wrong_array))], ppropertyslot_tail]]',
    f'pframe_wrong = pframe_fresh[.TODO = {frame_tasks(True, pin="pinstancestorage_wrong")}]',
    'S_wrong_slot = S_array[.ARRAYS = S_array.ARRAYS ++ [parray_wrong]][.FRAMES = [pframe_wrong]]',
    '$heap_graph(S_wrong_slot) = $heap_graph(S_array)',
    '$weakmap_write_array_pin(S_wrong_slot, pweakmapwrite, pinstancestorage_wrong)',
    '~$weakmap_write_array_child_call(S_wrong_slot, pweakmapwrite, pinstancestorage_wrong, pdestructorcall_array)',
    '~$weakmap_write_callback_read(S_wrong_slot, paccess_S_array)',
    'pdestructorcall_temp = pdestructorcall_array[.RELEASE = (pdestructionrelease_array_original[.JOBS = [DESTRUCTION_TEMP (HOBJECT n_child)]])]',
    f'pframe_temp = pframe_fresh[.TODO = {frame_tasks(True, call="pdestructorcall_temp")}]',
    'S_temp = S_array[.FRAMES = [pframe_temp]][.DESTRUCTION.CALLS = [pdestructorcall_temp]]',
    '$heap_graph(S_temp) = $heap_graph(S_array)',
    '~$weakmap_write_array_child_call(S_temp, pweakmapwrite, pinstancestorage_array, pdestructorcall_temp)',
    'pdestructionrelease_early_original = pdestructionrelease_array_original[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child), DESTRUCTION_VALUE (HOBJECT n_child)]]',
    'pdestructionrelease_early_remaining = pdestructionrelease_early_original[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]]',
    'pdestructorcall_early = pdestructorcall_array[.RELEASE = (pdestructionrelease_early_original)]',
    f'pframe_early = pframe_fresh[.TODO = {frame_tasks(True, call="pdestructorcall_early", release="pdestructionrelease_early_remaining")}]',
    'S_early = S_array[.FRAMES = [pframe_early]][.DESTRUCTION.CALLS = [pdestructorcall_early]][.DESTRUCTION.RELEASES = [pdestructionrelease_early_remaining, pdestructionrelease_root_empty, pdestructionrelease_old_empty]]',
    '$heap_valid($heap_graph(S_early))', owner('S_early', 'HOBJECT', 'n_child', 3),
    '$weakmap_write_array_pin(S_early, pweakmapwrite, pinstancestorage_array)',
    '~$weakmap_write_array_child_call(S_early, pweakmapwrite, pinstancestorage_array, pdestructorcall_early)',
    '~$weakmap_write_callback_read(S_early, paccess_S_array)',
    f'S_virtual_early = S_virtual_fresh[.TODO = {frame_tasks(True, call="pdestructorcall_early", release="pdestructionrelease_early_remaining")}]',
    '$heap_valid($heap_graph(S_virtual_early))', owner('S_virtual_early', 'HOBJECT', 'n_child', 2),
    '~$eager_operation_task_valid(S_virtual_early, pdestructionoperation_parent)',
    *retirement_tail('S_array'),
    'S_parent.STORE[n_result_cell] = DEFINED (PINT 31)',
    '$weakref_get(S_pin, n_child_watch) = PNULL',
    owner('S_parent', 'HOBJECT', 'n_pending', 1),
]

NORMAL_CHECKS = [
    *bindings('S', pin=True),
    'pdestructorcall_array.OBJECT = n_child',
    'pdestructorcall_array.PENDING = eps',
    '$task_nodes(DESTRUCTOR_ENTER pdestructorcall_array) = [HOBJECT n_child, HOBJECT n_child]',
    '~((HARRAY n_box) <- S.ALLOCATIONS)',
    owner('S', 'HOBJECT', 'n_child', 2), *valid('S'),
    *seek('S', 'S_array', 'READ'),
    '$instance_storage_for(S_array, n_old) = (pinstancestorage_array)',
    'S_array.DESTRUCTION.OPERATIONS = [pdestructionoperation_parent]',
    '$weakmap_write_array_child_call(S_array, pweakmapwrite, pinstancestorage_array, pdestructorcall_array)',
    owner('S_array', 'HOBJECT', 'n_child', 2), *access('S_array'), *valid('S_array'),
    *virtual('S_array', False, 'normal'),
    'pdestructionoperation_fake = pdestructionoperation_parent[.ORIGIN = eps]',
    'pdestructorcall_fake = pdestructorcall_array[.OPERATION = (pdestructionoperation_fake)]',
    'S_virtual_fake = S_virtual_normal[.TODO = (DESTRUCTOR_RESULT pdestructorcall_fake) :: (DESTRUCTOR_RELEASE pdestructionrelease_array_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_array) :: (DESTRUCTOR_RELEASE pdestructionrelease_root_empty) :: (DESTRUCTOR_RELEASE pdestructionrelease_old_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_parent) :: (ACCESS_RESUME pweakmapwrite.ACCESS) :: (WEAKMAP_WRITE_CLAIM pweakmapwrite) :: ptask_normal_after_claim*]',
    '$heap_graph(S_virtual_fake) = $heap_graph(S_virtual_normal)',
    '~$eager_operation_task_valid(S_virtual_fake, pdestructionoperation_parent)',
    *retirement_tail('S_array'),
]

BOUNDARY_CHECKS = [
    *bindings('S', pin=True),
    'pdestructorcall_array.OBJECT = n_child',
    'pdestructionoperation_inner.SOURCE = THROW_SEARCH n_pending',
    'pdestructionoperation_inner.PENDING = eps',
    '$throwable_field(S, n_new, "previous") = PNULL',
    owner('S', 'HOBJECT', 'n_pending', 1), owner('S', 'HOBJECT', 'n_new', 1),
    owner('S', 'HOBJECT', 'n_child', 1),
    '$heap_valid($heap_graph(S))', '$destruction_state_valid(S)',
    '$destructor_result_valid(S, pdestructorcall_array)',
    '$weakmap_write_array_pin(S, pweakmapwrite, pinstancestorage_initial)',
    '$weakmap_write_array_child_call(S, pweakmapwrite, pinstancestorage_initial, pdestructorcall_array)',
    'S_effect = S[.TODO = (THROW_SEARCH n_new) :: ptask_after_result*]',
    '$weakmap_write_array_throw_boundary(S_effect, pdestructorcall_array)',
    '$destructor_pending_parent(S_effect, pdestructorcall_array) = eps',
    'S_fence = $destructor_result_pending(S_effect, pdestructorcall_array, eps)',
    'S_fence = S[.COMPLETION = UNSUPPORTED "throwing Child during WeakMap array-slot cleanup"]',
    'PhpStep: S ~> S_raw', 'S_raw = S_fence',
    '$heap_graph(S_raw) = $heap_graph(S)',
    '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
    'S_terminal = $drive(S, 4000)',
    'S_terminal.COMPLETION = UNSUPPORTED "throwing Child during WeakMap array-slot cleanup"',
    'S_terminal.EVENTS = S.EVENTS', 'S_terminal.TODO = eps',
    'S_terminal.RESULT = KNOWN PNULL', 'S_terminal.HELD = eps',
    'S_terminal.ARRAYS = S.ARRAYS', 'S_terminal.OBJECTPROPS = S.OBJECTPROPS',
    'S_terminal.ALLOCATIONS = S.ALLOCATIONS',
]

review.CASES = {
    'fresh-shared-array-retirement': {'source': FRESH, 'stage': OWN_STAGE, 'checks': FRESH_CHECKS},
    'normal-array-call-prefix': {'source': ORIGINAL, 'stage': ENTER_STAGE, 'checks': NORMAL_CHECKS},
    'array-child-throw-boundary': {'source': BOUNDARY, 'stage': BOUNDARY_STAGE, 'checks': BOUNDARY_CHECKS},
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
