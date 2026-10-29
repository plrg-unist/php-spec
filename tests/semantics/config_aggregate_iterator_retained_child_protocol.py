#!/usr/bin/env python3
"""Reach CONFIG parent retirement followed by actual outside Child release."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_aggregate_fresh_iterator_protocol as prior
import config_aggregate_iterator_retained_child_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = prior.PREFIX + r"""
dec $test_retained_child_front(pstate, nat) : bool
def $test_retained_child_front(S, 0) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
def $test_retained_child_front(S, 1) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.NEXT = 0
  -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
  -- if pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"
  -- if pinstancestorage.OBJECT = pconfigiterator.OBJECT
def $test_retained_child_front(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"
  -- if ~((HOBJECT pconfigiterator.OBJECT) <- S.ALLOCATIONS)
def $test_retained_child_front(S, 3) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("heldChild")
def $test_retained_child_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $test_outputs(S.EVENTS) = $ptascii("B|G|R|V0|U0|K0|PD|IL|FL|N0|V1|U1|K1|E|S|saved|99|14|W|D|D|L|C0|U|C|PD|CL|")
def $test_retained_child_front(S, n_stage) = false -- otherwise
dec $test_retained_child_seek(pstate, nat, nat) : pstate
def $test_retained_child_seek(S, n_stage, 0) = S
def $test_retained_child_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_retained_child_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_retained_child_seek(S, n_stage, n) = $test_retained_child_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_retained_child_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
"""


def reach(state, start, stage):
    return [state + '_found = $test_retained_child_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_retained_child_front(' + state + ',' + str(stage) + ')']


def checks(program, path, name):
    assert name == 'retained-child-throw'
    prefix = 'B|G|R|V0|U0|K0|PD|IL|FL|N0|V1|U1|K1|'
    before = prefix + 'E|S|saved|99|14|W|D|D|L|C0|U|'
    return ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        *prior.reach('S_return', 'S_initial', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_return*',
        'S_return.RESULT = KNOWN (POBJECT n_parent)',
        '(HOBJECT n_parent) <- S_return.ALLOCATIONS',
        '$heap_owners($heap_graph(S_return),HOBJECT n_parent) = 1',
        '$destructor_method(S_return,n_parent) = eps',
        '$lookup(S_return.ENV,' + text('heldChild') + ') = (n_held_cell)',
        'S_return.STORE[n_held_cell] = DEFINED (POBJECT n_child)',
        '$lookup(S_return.ENV,' + text('childWatch') + ') = (n_child_watch_cell)',
        'S_return.STORE[n_child_watch_cell] = DEFINED (POBJECT n_child_watch)',
        'S_return.OBJECTS[n_child_watch] = WEAKREFERENCE (n_child)',
        '$node_children(S_return,HOBJECT n_parent) = [HOBJECT n_child]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_child) = 2',
        '$config_iterator_owned_child(S_return,n_parent)',
        '$config_iterator_finalizer(S_return,n_parent)',
        '$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        *driver.common.public('S_return'),
        *reach('S_throw', 'S_return', 0),
        'S_throw.TODO = (THROW_SEARCH n_saved) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask_throw*',
        'pconfigiterator.OBJECT = n_parent',
        'pconfigiterator.PRODUCER = (n_producer)',
        '$lookup(S_throw.ENV,' + text('saved') + ') = (n_saved_cell)',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        '$lookup(S_throw.ENV,' + text('result') + ') = (n_result_cell)',
        '$lookup(S_throw.ENV,' + text('childDeaths') + ') = (n_deaths_cell)',
        '$lookup(S_throw.ENV,' + text('iterWatch') + ') = (n_parent_watch_cell)',
        'S_throw.STORE[n_parent_watch_cell] = DEFINED (POBJECT n_parent_watch)',
        'S_throw.OBJECTS[n_parent_watch] = WEAKREFERENCE (n_parent)',
        '~((HOBJECT n_producer) <- S_throw.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_parent) = 1',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 2',
        '$weakref_get(S_throw,n_parent_watch) = POBJECT n_parent',
        '$weakref_get(S_throw,n_child_watch) = POBJECT n_child',
        '$config_iterator_finalizable_aggregate_data(S_throw,pconfigiterator)',
        '$test_outputs(S_throw.EVENTS) = ' + text(prefix),
        *driver.common.public('S_throw'),
        *reach('S_storage', 'S_throw', 1),
        'S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_storage*',
        'pinstancestorage.OBJECT = n_parent',
        'S_storage.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"',
        'pdestructionoperation.PENDING = (n_saved)',
        '$instance_storage_valid(S_storage,pinstancestorage)',
        '(HOBJECT n_parent) <- S_storage.ALLOCATIONS',
        '(HOBJECT n_child) <- S_storage.ALLOCATIONS',
        'n_parent <- S_storage.DESTRUCTION.CALLED',
        '~(n_child <- S_storage.DESTRUCTION.CALLED)',
        '$node_children(S_storage,HOBJECT n_parent) = [HOBJECT n_child]',
        '$heap_owners($heap_graph(S_storage),HOBJECT n_child) = 2',
        '$weakref_get(S_storage,n_parent_watch) = PNULL',
        '$weakref_get(S_storage,n_child_watch) = POBJECT n_child',
        'S_storage.STORE[n_held_cell] = DEFINED (POBJECT n_child)',
        'S_storage.STORE[n_deaths_cell] = DEFINED (PINT 0)',
        '$test_outputs(S_storage.EVENTS) = ' + text(prefix),
        *prior.budget('S_storage'), *driver.common.public('S_storage'),
        *reach('S_exit', 'S_storage', 2),
        'S_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_exit*',
        'pdestructionoperation.PENDING = (n_saved)',
        '~((HOBJECT n_parent) <- S_exit.ALLOCATIONS)',
        '(HOBJECT n_child) <- S_exit.ALLOCATIONS',
        'n_parent <- S_exit.DESTRUCTION.CALLED',
        '~(n_child <- S_exit.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S_exit),HOBJECT n_child) = 1',
        '$instance_storage_for(S_exit,n_parent) = eps',
        '$weakref_get(S_exit,n_parent_watch) = PNULL',
        '$weakref_get(S_exit,n_child_watch) = POBJECT n_child',
        '$config_iterator_retired_scope(S_exit,pconfigiterator)',
        '$eager_operation_source_valid(S_exit,pdestructionoperation)',
        '$destructor_operation_valid(S_exit,pdestructionoperation)',
        'S_exit.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_exit.STORE[n_deaths_cell] = DEFINED (PINT 0)',
        'S_exit.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_exit.EVENTS) = ' + text(prefix),
        *prior.budget('S_exit'), *driver.common.public('S_exit'),
        *reach('S_before', 'S_exit', 3),
        '$lookup(S_before.ENV,' + text('heldChild') + ') = (n_held_cell)',
        'S_before.STORE[n_held_cell] = DEFINED (POBJECT n_child)',
        '(HOBJECT n_child) <- S_before.ALLOCATIONS',
        '~(n_child <- S_before.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S_before),HOBJECT n_child) = 1',
        '$weakref_get(S_before,n_parent_watch) = PNULL',
        '$weakref_get(S_before,n_child_watch) = POBJECT n_child',
        '$eager_operation_pending(S_before) = eps',
        'S_before.STORE[n_deaths_cell] = DEFINED (PINT 0)',
        '$test_outputs(S_before.EVENTS) = ' + text(before),
        *prior.budget('S_before'), *driver.common.public('S_before'),
        *reach('S_child', 'S_before', 4),
        'S_child.CURRENT = (pcallcontext_child)',
        'pcallcontext_child.TARGET = METHOD_TARGET n_child porigin_child_dtor',
        'S_child.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
        'pdestructorcall.OBJECT = n_child',
        'pdestructorcall.PENDING = eps',
        '(HOBJECT n_child) <- S_child.ALLOCATIONS',
        'n_child <- S_child.DESTRUCTION.CALLED',
        '$weakref_get(S_child,n_parent_watch) = PNULL',
        '$weakref_get(S_child,n_child_watch) = POBJECT n_child',
        'S_child.STORE[n_deaths_cell] = DEFINED (PINT 1)',
        '$test_outputs(S_child.EVENTS) = ' + text(before + 'C|PD|CL|'),
        *driver.common.public('S_child'),
        'S_final = $drive_steps(S_child,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        '$lookup(S_final.ENV,' + text('heldChild') + ') = eps',
        '~((HOBJECT n_child) <- S_final.ALLOCATIONS)',
        '$weakref_get(S_final,n_child_watch) = PNULL',
        'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_final.STORE[n_deaths_cell] = DEFINED (PINT 1)',
        'S_final.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_final.EVENTS) = ' + text(before + 'C|PD|CL|Z|D|C1|'),
        *driver.common.public('S_final')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources.family.CASES = {'retained-child-throw': sources.family.CASES['retained-child-throw']}
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
