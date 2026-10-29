#!/usr/bin/env python3
"""Reach child-only CONFIG storage release with the saved key Exception."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_aggregate_fresh_iterator_protocol as prior
import config_aggregate_iterator_child_only_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = prior.PREFIX + r"""
dec $test_child_only_front(pstate, nat) : bool
def $test_child_only_front(S, 0) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
def $test_child_only_front(S, 1) = true
  -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
  -- if pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_child porigin
  -- if n_child =/= pconfigiterator.OBJECT
  -- if $instance_storage_for(S, pconfigiterator.OBJECT) = (pinstancestorage)
  -- if $test_outputs(S.EVENTS) = $ptascii("B|G|R|V0|U0|K0|PD|IL|FL|N0|V1|U1|K1|C|")
def $test_child_only_front(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"
  -- if ~((HOBJECT pconfigiterator.OBJECT) <- S.ALLOCATIONS)
def $test_child_only_front(S, n_stage) = false -- otherwise
dec $test_child_only_seek(pstate, nat, nat) : pstate
def $test_child_only_seek(S, n_stage, 0) = S
def $test_child_only_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_child_only_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_child_only_seek(S, n_stage, n) = $test_child_only_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_child_only_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
"""


def reach(state, start, stage):
    return [state + '_found = $test_child_only_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_child_only_front(' + state + ',' + str(stage) + ')']


def checks(program, path, name):
    assert name == 'child-only-throw'
    prefix = 'B|G|R|V0|U0|K0|PD|IL|FL|N0|V1|U1|K1|'
    final = prefix + 'C|E|S|saved|99|14|W|D|D|D|C1|'
    return ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        *prior.reach('S_return', 'S_initial', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_return*',
        'S_return.RESULT = KNOWN (POBJECT n_parent)',
        '(HOBJECT n_parent) <- S_return.ALLOCATIONS',
        '$heap_owners($heap_graph(S_return),HOBJECT n_parent) = 1',
        '$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        '$destructor_method(S_return,n_parent) = eps',
        '$lookup(S_return.ENV,' + text('childWatch') + ') = (n_child_watch_cell)',
        'S_return.STORE[n_child_watch_cell] = DEFINED (POBJECT n_child_watch)',
        'S_return.OBJECTS[n_child_watch] = WEAKREFERENCE (n_child)',
        '$weakref_get(S_return,n_child_watch) = POBJECT n_child',
        '$objectprops_at(S_return.OBJECTPROPS,n_parent) = (ppropertyslot_parent*)',
        '$property_slot_at(ppropertyslot_parent*,' + text('child') + ') = (ppropertyslot_child)',
        'ppropertyslot_child.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
        '$node_children(S_return,HOBJECT n_parent) = [HOBJECT n_child]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1',
        '$config_iterator_owned_child(S_return,n_parent)',
        '$config_iterator_finalizer(S_return,n_parent)',
        'S_extra_owner = S_return[.HELD = S_return.HELD ++ [HOBJECT n_child]]',
        '$heap_owners($heap_graph(S_extra_owner),HOBJECT n_child) = 2',
        '$config_iterator_owned_child(S_extra_owner,n_parent)',
        '$config_aggregate_return_allowed(S_extra_owner,pconfigaggregate)',
        'S_extra_edge = S_return[.OBJECTPROPS = $objectprops_set(S_return.OBJECTPROPS,n_parent,$property_slot_set(ppropertyslot_parent*,' + text('i') + ',PROP_VALUE (DIRECT (POBJECT n_child))))]',
        '~$config_iterator_owned_child(S_extra_edge,n_parent)',
        '~$config_aggregate_return_allowed(S_extra_edge,pconfigaggregate)',
        *driver.common.public('S_return'),
        *reach('S_throw', 'S_return', 0),
        'S_throw.TODO = (THROW_SEARCH n_saved) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask_throw*',
        'pconfigiterator.OBJECT = n_parent',
        'pconfigiterator.PRODUCER = (n_producer)',
        '$lookup(S_throw.ENV,' + text('saved') + ') = (n_saved_cell)',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        '$lookup(S_throw.ENV,' + text('result') + ') = (n_result_cell)',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$lookup(S_throw.ENV,' + text('childDeaths') + ') = (n_deaths_cell)',
        'S_throw.STORE[n_deaths_cell] = DEFINED (PINT 0)',
        '$lookup(S_throw.ENV,' + text('iterWatch') + ') = (n_parent_watch_cell)',
        'S_throw.STORE[n_parent_watch_cell] = DEFINED (POBJECT n_parent_watch)',
        'S_throw.OBJECTS[n_parent_watch] = WEAKREFERENCE (n_parent)',
        '~((HOBJECT n_producer) <- S_throw.ALLOCATIONS)',
        '(HOBJECT n_parent) <- S_throw.ALLOCATIONS',
        '(HOBJECT n_child) <- S_throw.ALLOCATIONS',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_parent) = 1',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1',
        '$destructor_method(S_throw,n_parent) = eps',
        '$config_iterator_finalizable_aggregate_data(S_throw,pconfigiterator)',
        '~$config_iterator_quiet_aggregate_data(S_throw,pconfigiterator)',
        '$weakref_get(S_throw,n_parent_watch) = POBJECT n_parent',
        '$weakref_get(S_throw,n_child_watch) = POBJECT n_child',
        '$throwable_live(S_throw,n_saved)',
        '$test_outputs(S_throw.EVENTS) = ' + text(prefix),
        *driver.common.public('S_throw'),
        *reach('S_child', 'S_throw', 1),
        'S_child.CURRENT = (pcallcontext_child)',
        'pcallcontext_child.TARGET = METHOD_TARGET n_child porigin_child_dtor',
        'S_child.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"',
        'pdestructionoperation.PENDING = (n_saved)',
        'pdestructionoperation.COMPLETION = NORMAL',
        '$instance_storage_for(S_child,n_parent) = (pinstancestorage)',
        'pinstancestorage.OBJECT = n_parent',
        '$instance_storage_basic(S_child,pinstancestorage)',
        '$instance_storage_state_valid(S_child)',
        '$property_slot_at(pinstancestorage.SLOTS,' + text('child') + ') = (ppropertyslot_child)',
        '$objectprops_at(S_child.OBJECTPROPS,n_parent) = (ppropertyslot_current*)',
        '$property_slot_at(ppropertyslot_current*,' + text('child') + ') = (ppropertyslot_unset)',
        'ppropertyslot_unset.STATE = PROP_UNSET',
        '(HOBJECT n_parent) <- S_child.ALLOCATIONS',
        '(HOBJECT n_child) <- S_child.ALLOCATIONS',
        'n_parent <- S_child.DESTRUCTION.CALLED',
        'n_child <- S_child.DESTRUCTION.CALLED',
        '$destructor_method(S_child,n_parent) = eps',
        '$instance_storage_freeing(S_child,n_parent)',
        '$heap_owners($heap_graph(S_child),HOBJECT n_parent) = 1',
        '$weakref_get(S_child,n_parent_watch) = PNULL',
        '$weakref_get(S_child,n_child_watch) = POBJECT n_child',
        '$throwable_live(S_child,n_saved)',
        'S_child.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_child.STORE[n_deaths_cell] = DEFINED (PINT 1)',
        'S_child.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_child.EVENTS) = ' + text(prefix + 'C|'),
        *prior.budget('S_child'), *driver.common.public('S_child'),
        *reach('S_exit', 'S_child', 2),
        'S_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_exit*',
        'pdestructionoperation.PENDING = (n_saved)',
        '~((HOBJECT n_parent) <- S_exit.ALLOCATIONS)',
        '~((HOBJECT n_child) <- S_exit.ALLOCATIONS)',
        'n_parent <- S_exit.DESTRUCTION.CALLED',
        'n_child <- S_exit.DESTRUCTION.CALLED',
        '$destructor_method(S_exit,n_parent) = eps',
        '$instance_storage_for(S_exit,n_parent) = eps',
        '$weakref_get(S_exit,n_parent_watch) = PNULL',
        '$weakref_get(S_exit,n_child_watch) = PNULL',
        '$config_iterator_quiet_aggregate_data(S_exit,pconfigiterator)',
        '~$config_iterator_finalizable_aggregate_data(S_exit,pconfigiterator)',
        '$config_iterator_aggregate_data(S_exit,pconfigiterator)',
        '$config_iterator_retired_scope(S_exit,pconfigiterator)',
        '$useriter_cursor_count(S_exit.ITERATORS,pconfigiterator.ITERATOR) = 0',
        '$eager_operation_source_valid(S_exit,pdestructionoperation)',
        '$destructor_operation_valid(S_exit,pdestructionoperation)',
        'S_no_marker = S_exit[.DESTRUCTION.CALLED = eps]',
        '$config_iterator_retired_scope(S_no_marker,pconfigiterator)',
        '~$eager_operation_source_valid(S_no_marker,pdestructionoperation)',
        '~$destructor_operation_valid(S_no_marker,pdestructionoperation)',
        'S_exit.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_exit.STORE[n_deaths_cell] = DEFINED (PINT 1)',
        'S_exit.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_exit.EVENTS) = ' + text(prefix + 'C|'),
        *prior.budget('S_exit'), *driver.common.public('S_exit'),
        'S_final = $drive_steps(S_exit,3000)',
        'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps',
        'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_final.STORE[n_deaths_cell] = DEFINED (PINT 1)',
        'S_final.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_final.EVENTS) = ' + text(final),
        *driver.common.public('S_final')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources.family.CASES = {'child-only-throw': sources.family.CASES['child-only-throw']}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    if args.phase == 'check':
        recorded = driver.recorder.recorded
        driver.recorder.recorded = lambda command, stem, cap: recorded(command, stem, 360)
    sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output)]
    driver.main()


if __name__ == '__main__':
    main()
