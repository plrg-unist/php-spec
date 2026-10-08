#!/usr/bin/env python3
"""Reached ordinary INSTANCE storage pins and ordered property transfers."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources

ROOT = sources.ROOT
cross = sources.cross
CASES = {
    'typed': 'review-instance-storage-typed-throws19',
    'generator': 'review-instance-storage-generator-return19',
    'fiber': 'review-instance-storage-fiber19',
}
PREFIX = r'''
dec $instance_test_output(pevent*) : ptbytes
dec $instance_test_is_output(pevent) : bool
def $instance_test_output(eps) = eps
def $instance_test_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $instance_test_output(pevent*)
def $instance_test_output(pevent :: pevent_tail*) = $instance_test_output(pevent_tail*) -- if ~$instance_test_is_output(pevent)
def $instance_test_is_output(OUTPUT ptbytes) = true
def $instance_test_is_output(pevent) = false -- otherwise
dec $instance_test_without(ptask*) : ptask*
dec $instance_test_without_frames(pframe*) : pframe*
def $instance_test_without(eps) = eps
def $instance_test_without(ptask :: ptask_tail*) = $instance_test_without(ptask_tail*)
  -- if $instance_storage_task(ptask) =/= eps
def $instance_test_without(ptask :: ptask_tail*) = ptask :: $instance_test_without(ptask_tail*)
  -- if $instance_storage_task(ptask) = eps
def $instance_test_without_frames(eps) = eps
def $instance_test_without_frames(pframe :: pframe_tail*) = pframe[.TODO = $instance_test_without(pframe.TODO)] :: $instance_test_without_frames(pframe_tail*)
dec $instance_test_phase(pstate, nat) : bool
def $instance_test_phase(S, 0) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if $object_name(S, n) = $ptascii("InstanceStorageParent359")
  -- if $destructor_method(S, n) = eps
  -- if $destructor_operation_for(S) = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
  -- if pforeachbind.VALUE = POBJECT n
  -- if $heap_owners($heap_graph(S), HOBJECT n) = 1
def $instance_test_phase(S, 1) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if $object_name(S, pinstancestorage.OBJECT) = $ptascii("InstanceStorageParent359")
  -- if pinstancestorage.NEXT = 0
def $instance_test_phase(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("InstanceStorageFirst359")
  -- if $instance_test_output(S.EVENTS) = $ptascii("A|InstanceStorageParent359/1|type|")
def $instance_test_phase(S, 3) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if $object_name(S, pinstancestorage.OBJECT) = $ptascii("InstanceStorageParent359")
  -- if pinstancestorage.NEXT = 1
def $instance_test_phase(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("InstanceStorageSecond359")
  -- if $instance_test_output(S.EVENTS) = $ptascii("A|InstanceStorageParent359/1|type|B|InstanceStorageParent359/1|free|")
def $instance_test_phase(S, 5) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if $object_name(S, pinstancestorage.OBJECT) = $ptascii("InstanceStorageParent359")
  -- if pinstancestorage.NEXT = 3
def $instance_test_phase(S, 6) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask*
  -- if pforeachbind.VALUE = POBJECT n
  -- if $object_name(S, n) = $ptascii("InstanceStorageParent359")
def $instance_test_phase(S, 10) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if $object_name(S, n) = $ptascii("ReturnParent355")
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|")
  -- if $trace_slot(S, S.ENV, $ptascii("wg")) = POBJECT n_weak
  -- if $weakref_get(S, n_weak) = POBJECT n_generator
  -- if $generator_storage_for(S, n_generator) = (pgenstorage)
  -- if pgenstorage.NEXT = 4
  -- if S.OBJECTS[n_generator] = GENERATOR pgenerator
  -- if pgenerator.RETURN = (POBJECT n)
def $instance_test_phase(S, 11) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if $object_name(S, pinstancestorage.OBJECT) = $ptascii("ReturnParent355")
  -- if pinstancestorage.NEXT = 0
def $instance_test_phase(S, 12) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("ReturnLeaf355")
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|L")
def $instance_test_phase(S, 20) = true
  -- if S.ACTIVEFIBER = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|paused|1|type|")
  -- if $trace_slot(S, S.ENV, $ptascii("fiber")) = POBJECT n_fiber
  -- if $fiber_at(S, n_fiber) = (pfiber)
  -- if pfiber.STATUS = FIBER_SUSPENDED
def $instance_test_phase(S, 21) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if S.ACTIVEFIBER =/= eps
  -- if pinstancestorage.NEXT = 1
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|paused|1|type|resume|")
def $instance_test_phase(S, n) = false -- otherwise
dec $instance_test_seek(pstate, nat, nat) : pstate
def $instance_test_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $instance_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $instance_test_phase(S, n_phase)
def $instance_test_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$instance_test_phase(S, n_phase)
def $instance_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$instance_test_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $instance_test_seek(S, n_phase, n) = $instance_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$instance_test_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $instance_test_seek({parent}, {phase}, 2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$instance_test_phase({state}, {phase})', *valid(state)]


def finish(state, expected):
    return [f'S_done = $drive({state}, 2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
            '$instance_test_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')',
            *valid('S_done')]


def typed_assertions(initial, expected):
    checks = ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 0),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_release_tail*',
        'pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionjob_tail*',
        '$trace_slot(S_release, S_release.ENV, $ptascii("wp")) = POBJECT n_weak',
        '$weakref_get(S_release, n_weak) = POBJECT n_parent',
        *seek('S_release', 'S_pinned', 1),
        'S_pinned = $drive_steps(S_release, 1)[.COMPLETION = NORMAL]',
        'S_pinned.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_pin_tail*',
        'pinstancestorage.OBJECT = n_parent',
        'pinstancestorage.SLOTS = [ppropertyslot_first, ppropertyslot_number, ppropertyslot_second]',
        'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_first))',
        'ppropertyslot_number.STATE = PROP_VALUE (ALIAS n_cell)',
        'ppropertyslot_number.DECL = (ppropertyid)',
        'ppropertyslot_second.STATE = PROP_VALUE (DIRECT (POBJECT n_second))',
        'pproptypesource = OBJECT_PROP_SOURCE n_parent ppropertyslot_number.NAME ppropertyid',
        '$instance_storage_valid(S_pinned, pinstancestorage)',
        '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_parent]',
        '$heap_owners($heap_graph(S_pinned), HOBJECT n_parent) = 1',
        '$node_children(S_pinned, HOBJECT n_parent) = [HOBJECT n_first, HCELL n_cell, HOBJECT n_second]',
        '$weakref_get(S_pinned, n_weak) = PNULL',
        '$destructor_handle(S_pinned, pinstancestorage.HANDLE, 0) = eps',
        '~(pinstancestorage.HANDLE <- S_pinned.DESTRUCTION.FREE)',
        '$gc_retired_valid(S_pinned, n_parent)',
        '$propref_source_valid(S_pinned, n_cell, pproptypesource)',
        '~$instance_storage_basic(S_pinned, pinstancestorage[.NEXT = 4])',
        '~$instance_storage_basic(S_pinned, pinstancestorage[.OBJECT = |S_pinned.OBJECTS|])',
        '~$instance_storage_basic(S_pinned, pinstancestorage[.HANDLE = $(pinstancestorage.HANDLE + 1)])',
        'S_pinned.OBJECTS[n_weak] = WEAKREFERENCE (n_parent)',
        '$node_children(S_pinned, HOBJECT n_weak) = eps',
        'S_weak_bad = S_pinned[.OBJECTS[n_weak] = WEAKREFERENCE eps]',
        '~$weakref_state_valid(S_weak_bad)',
        '~$call_descriptors_valid(S_weak_bad)',
        'S_duplicate = S_pinned[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: S_pinned.TODO]',
        '~$instance_storage_state_valid(S_duplicate)',
        '~$call_descriptors_valid(S_duplicate)',
        'S_absent = S_pinned[.TODO = ptask_pin_tail*]',
        '$instance_storage_for(S_absent, n_parent) = eps',
        '~$instance_storage_valid(S_absent, pinstancestorage)',
        'S_zero = $drive_steps(S_pinned, 0)',
        'S_zero = S_pinned[.COMPLETION = BUDGET]',
        *seek('S_pinned', 'S_first', 2),
        '$instance_storage_for(S_first, n_parent) = (pinstancestorage[.NEXT = 1])',
        '(HOBJECT n_parent) <- S_first.ALLOCATIONS',
        '$heap_owners($heap_graph(S_first), HOBJECT n_parent) = 1',
        '$node_children(S_first, HOBJECT n_parent) = [HCELL n_cell, HOBJECT n_second]',
        '$propref_source_valid(S_first, n_cell, pproptypesource)',
        '$gc_retired_find(S_first.GC.BUFFER, n_parent, 0) = (n_buffer)',
        '$gc_slot_find(S_first.GC.BUFFER, HOBJECT n_parent, 0) = eps',
        '$gc_buffer_add(S_first.GC, HOBJECT n_parent) = S_first.GC',
        'S_gc_duplicate = S_first[.GC.BUFFER = S_first.GC.BUFFER ++ [GC_ROOT (HOBJECT n_parent)]]',
        '~$gc_buffer_valid(S_gc_duplicate, S_gc_duplicate.GC)',
        'S_replay = S_first[.OBJECTPROPS = $objectprops_set(S_first.OBJECTPROPS, n_parent, pinstancestorage.SLOTS)]',
        '~$instance_storage_basic(S_replay, pinstancestorage[.NEXT = 1])',
        'S_future_read = $property_read(S_first, POBJECT n_parent, ppropertyslot_number.NAME, 1)',
        'S_future_read.COMPLETION = NORMAL',
        'S_future_read.RESULT = KNOWN (PINT 7)']
    for call in [
        '$property_store_value(S_first, n_parent, ppropertyslot_number.NAME, PINT 4, 1)',
        '$property_unset(S_first, POBJECT n_parent, ppropertyslot_number.NAME, 1)',
        '$base_find(S_first, BASE_PROPERTY (POBJECT n_parent) ppropertyslot_number.NAME, 1)',
        '$property_reference_fetch_unshared(S_first, n_parent, ppropertyslot_number.NAME, 1)',
        '$clone_value(S_first, POBJECT n_parent, 1)',
        '$cast_value(S_first, CASTARRAY, POBJECT n_parent, 1)',
        '$object_foreach_reset(S_first, n_parent)',
        '$weakref_create(S_first, n_parent)',
    ]:
        checks.append(call+'.COMPLETION = UNSUPPORTED '+json.dumps(
            'freeing instance clone' if 'clone_' in call else
            'freeing instance array cast' if 'cast_' in call else
            'freeing instance foreach' if 'foreach_' in call else
            'freeing instance new weak reference' if 'weakref_' in call else
            'freeing instance property access'))
    checks += [
        'S_clone = $allocate_array(S_first, $array_empty())',
        'S_clone.RESULT = KNOWN (PARRAY n_array)',
        'S_first.ORIGIN = (porigin_clone)',
        'pclonecall = {SITE porigin_clone, INDEX 2, SENT ([NAMED_SENT (KNOWN (POBJECT n_parent)), NAMED_SENT (KNOWN (PARRAY n_array))]), NAMED false, OWNER eps, NAME eps, LINE $property_current_line(S_first)}',
        'S_clone_refused = $clone_receive(S_clone, pclonecall)',
        'S_clone_refused.COMPLETION = UNSUPPORTED "freeing instance clone"',
        'S_clone_refused.ALLOCATIONS = S_clone.ALLOCATIONS',
        '$value_order(S_first, POBJECT n_parent, POBJECT n_parent, eps) = ORDER 0',
        '$value_order(S_first, POBJECT n_parent, POBJECT n_second, eps) = ORDERUNSUPPORTED "freeing instance structural comparison"',
        *seek('S_first', 'S_number', 3),
        'S_number.DESTRUCTION.OPERATIONS = pdestructionoperation_number :: pdestructionoperation_tail*',
        'pdestructionoperation_number.PENDING = (n_pending)',
        '$throwable_field(S_number, n_pending, "message") = PSTRING ($ptascii("A"))',
        'S_detached_found = $drive_steps(S_number, 1)',
        'S_detached_found.COMPLETION = BUDGET',
        'S_detached = S_detached_found[.COMPLETION = NORMAL]', *valid('S_detached'),
        'S_detached.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_number) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 2]) :: ptask_number_tail*',
        'pdestructionrelease_number.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
        '$node_children(S_detached, HOBJECT n_parent) = [HOBJECT n_second]',
        '$heap_owners($heap_graph(S_detached), HCELL n_cell) = 2',
        '~$propref_source_valid(S_detached, n_cell, pproptypesource)',
        'S_detached.PROPREFS = eps',
        *seek('S_detached', 'S_second', 4),
        '$instance_storage_for(S_second, n_parent) = (pinstancestorage[.NEXT = 3])',
        '$node_children(S_second, HOBJECT n_parent) = eps',
        '$heap_owners($heap_graph(S_second), HOBJECT n_parent) = 1',
        'S_second.DESTRUCTION.CALLS = pdestructorcall_second :: pdestructorcall_tail*',
        'pdestructorcall_second.OBJECT = n_second',
        'pdestructorcall_second.PENDING = (n_pending)',
        '$weakref_get(S_second, n_weak) = PNULL',
        *seek('S_second', 'S_finish', 5),
        'S_finish.DESTRUCTION.OPERATIONS = pdestructionoperation_finish :: pdestructionoperation_tail*',
        'pdestructionoperation_finish.PENDING = (n_final)',
        '$throwable_previous_id(S_finish, n_final) = (n_pending)',
        'S_escaped = S_finish[.HELD = (HOBJECT n_parent) :: S_finish.HELD]',
        '$heap_valid($heap_graph(S_escaped))',
        '$heap_owners($heap_graph(S_escaped), HOBJECT n_parent) = 2',
        '$drive_steps(S_escaped, 1).COMPLETION = UNSUPPORTED "freeing instance escaped reacquisition"',
        'S_retired_found = $drive_steps(S_finish, 1)',
        'S_retired_found.COMPLETION = BUDGET',
        'S_retired = S_retired_found[.COMPLETION = NORMAL]', *valid('S_retired'),
        '~((HOBJECT n_parent) <- S_retired.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_retired), HOBJECT n_parent) = 0',
        '$instance_storage_for(S_retired, n_parent) = eps',
        *seek('S_retired', 'S_commit', 6),
        'S_commit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_commit) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_commit_tail*',
        'pdestructionoperation_commit.PENDING = (n_final)',
        'S_bound_found = $drive_steps(S_commit, 1)',
        'S_bound_found.COMPLETION = BUDGET',
        'S_bound = S_bound_found[.COMPLETION = NORMAL]', *valid('S_bound'),
        '$lookup(S_bound.ENV, pforeachbind.NAME) = (pforeachbind.NEW)',
        'S_bound.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        'S_bound.TODO = (THROW_SEARCH n_final) :: ptask_commit_tail*',
        *finish('S_bound', expected)]
    return checks


def generator_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 10),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_release_tail*',
        'pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionjob_tail*',
        '$trace_slot(S_release, S_release.ENV, $ptascii("wg")) = POBJECT n_weak',
        '$weakref_get(S_release, n_weak) = POBJECT n_generator',
        '$generator_storage_for(S_release, n_generator) = (pgenstorage)',
        'pgenstorage.NEXT = 4',
        'S_release.OBJECTS[n_generator] = GENERATOR pgenerator',
        'pgenerator.RETURN = (POBJECT n_parent)',
        '$node_children(S_release, HOBJECT n_generator) = eps',
        '$heap_owners($heap_graph(S_release), HOBJECT n_parent) = 1',
        *seek('S_release', 'S_pinned', 11),
        'S_pinned.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_pin_tail*',
        'pinstancestorage.OBJECT = n_parent',
        'pinstancestorage.SLOTS = [ppropertyslot]',
        'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        '$heap_owners($heap_graph(S_pinned), HOBJECT n_generator) = 1',
        '$heap_owners($heap_graph(S_pinned), HOBJECT n_parent) = 1',
        '$heap_owners($heap_graph(S_pinned), HOBJECT n_leaf) = 1',
        '$node_children(S_pinned, HOBJECT n_parent) = [HOBJECT n_leaf]',
        *seek('S_pinned', 'S_leaf', 12),
        '$instance_storage_for(S_leaf, n_parent) = (pinstancestorage[.NEXT = 1])',
        '$generator_storage_for(S_leaf, n_generator) = (pgenstorage)',
        '(HOBJECT n_parent) <- S_leaf.ALLOCATIONS',
        '$node_children(S_leaf, HOBJECT n_parent) = eps',
        '$node_children(S_leaf, HOBJECT n_generator) = eps',
        '$heap_owners($heap_graph(S_leaf), HOBJECT n_parent) = 1',
        '$heap_owners($heap_graph(S_leaf), HOBJECT n_generator) = 1',
        '$weakref_get(S_leaf, n_weak) = POBJECT n_generator',
        '$generator_record_valid(S_leaf, pgenerator)',
        '$object_name(S_leaf, n_parent) = $ptascii("ReturnParent355")',
        *finish('S_leaf', expected),
        '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_generator) <- S_done.ALLOCATIONS)',
        '$weakref_get(S_done, n_weak) = PNULL']


def fiber_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_parked', 20),
        '$trace_slot(S_parked, S_parked.ENV, $ptascii("fiber")) = POBJECT n_fiber',
        '$fiber_at(S_parked, n_fiber) = (pfiber)',
        'pfiber.VM = (pfibervm)',
        '$instance_storage_all(S_parked) = [pinstancestorage]',
        'n_parent = pinstancestorage.OBJECT',
        'pinstancestorage.NEXT = 1',
        '$instance_storage_tasks(S_parked.TODO) ++ $instance_storage_frames(S_parked.FRAMES) = eps',
        '$instance_storage_tasks(pfibervm.TODO) ++ $instance_storage_frames(pfibervm.FRAMES) = [pinstancestorage]',
        'pinstancestorage.SLOTS = [ppropertyslot_leaf, ppropertyslot_number]',
        'ppropertyslot_number.STATE = PROP_VALUE (ALIAS n_cell)',
        'ppropertyslot_number.DECL = (ppropertyid)',
        'pproptypesource = OBJECT_PROP_SOURCE n_parent ppropertyslot_number.NAME ppropertyid',
        '$propref_source_valid(S_parked, n_cell, pproptypesource)',
        '$node_children(S_parked, HOBJECT n_parent) = [HCELL n_cell]',
        '$heap_owners($heap_graph(S_parked), HOBJECT n_parent) = 1',
        '$trace_slot(S_parked, S_parked.ENV, $ptascii("wp")) = POBJECT n_weak',
        '$weakref_get(S_parked, n_weak) = PNULL',
        '$destructor_handle(S_parked, pinstancestorage.HANDLE, 0) = eps',
        'S_vm = $fiber_vm_restore(S_parked, pfibervm)[.ACTIVEFIBER = (n_fiber)]',
        '$instance_storage_all(S_vm) = [pinstancestorage]',
        '$instance_storage_state_valid(S_vm)',
        '$heap_valid($heap_graph(S_vm))',
        'pfibervm_absent = pfibervm[.TODO = $instance_test_without(pfibervm.TODO)][.FRAMES = $instance_test_without_frames(pfibervm.FRAMES)]',
        'S_absent = $fiber_put(S_parked, n_fiber, pfiber[.VM = (pfibervm_absent)])',
        '$instance_storage_for(S_absent, n_parent) = eps',
        '$heap_owners($heap_graph(S_absent), HOBJECT n_parent) = 0',
        '~$gc_retired_valid(S_absent, n_parent)',
        'pfibervm_duplicate = pfibervm[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: pfibervm.TODO]',
        'S_duplicate = $fiber_put(S_parked, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
        '~$instance_storage_state_valid(S_duplicate)',
        'S_two_vms = S_parked[.OBJECTS = S_parked.OBJECTS ++ [FIBER pfiber]][.ALLOCATIONS = S_parked.ALLOCATIONS ++ [HOBJECT (|S_parked.OBJECTS|)]]',
        '$instance_storage_all(S_two_vms) = [pinstancestorage, pinstancestorage]',
        '~$instance_storage_state_valid(S_two_vms)',
        'S_zero = $drive_steps(S_parked, 0)',
        'S_zero = S_parked[.COMPLETION = BUDGET]',
        *seek('S_parked', 'S_slot', 21),
        '$instance_storage_for(S_slot, n_parent) = (pinstancestorage)',
        '$propref_source_valid(S_slot, n_cell, pproptypesource)',
        'S_detached_found = $drive_steps(S_slot, 1)',
        'S_detached_found.COMPLETION = BUDGET',
        'S_detached = S_detached_found[.COMPLETION = NORMAL]', *valid('S_detached'),
        '$instance_storage_for(S_detached, n_parent) = (pinstancestorage[.NEXT = 2])',
        '$node_children(S_detached, HOBJECT n_parent) = eps',
        '~$propref_source_valid(S_detached, n_cell, pproptypesource)',
        *finish('S_detached', expected),
        '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
        '$weakref_get(S_done, n_weak) = PNULL']


def prepare(directory, group):
    source = directory/'source.php'
    case = CASES[group]
    original = sources.CASES[case]
    source.write_bytes(original)
    sources.prepare(directory, source)
    initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
    body = {'typed': typed_assertions, 'generator': generator_assertions,
            'fiber': fiber_assertions}[group](initial, sources.EXPECTED[case])
    clauses = ['program_source = '+(directory/'program.watsup').read_text().strip(), *body]
    fixture = directory/'protocol.watsup'
    fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
                      ''.join('  -- if '+clause+'\n' for clause in clauses)+
                      '\ndec $main() : bool\ndef $main() = $body()\n')
    (directory/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
    assert source.read_bytes() == original
    return source, original, fixture, clauses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='instance-storage-pin-', dir=ROOT/'.tools'))
    report = {'before':before, 'profile':cross.invoke.types.PROFILE, 'passed':False,
              'native_evaluations':0, 'model_evaluations':0, 'state_assertions_evaluated':0,
              'runner_mode':'SL', 'numeric_cap_seconds':120, 'case':CASES[args.group], 'jobs':1}
    print(out, flush=True)
    try:
        source, original, fixture, clauses = prepare(out, args.group)
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture),
                      assertions=len(clauses))
        if not args.prepare_only:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type':type(error).__name__, 'message':str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
