#!/usr/bin/env python3
"""Reach descriptor/DAG admission and real saved-Exception storage retirement."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_aggregate_fresh_iterator_protocol as prior
import config_aggregate_iterator_layout_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = prior.PREFIX + r"""
dec $test_layout_front(pstate, nat) : bool
def $test_layout_front(S, 0) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
def $test_layout_front(S, 1) = true
  -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
  -- if pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_branch porigin
  -- if n_branch =/= pconfigiterator.OBJECT
  -- if $instance_storage_for(S, pconfigiterator.OBJECT) = (pinstancestorage)
  -- if $test_outputs(S.EVENTS) = $ptascii("B|G|R|V0|U0|K0|PD|IL|F|BL|LL|7|2|N0|V1|U1|K1|J|PD|BL|LL|5|")
def $test_layout_front(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"
  -- if ~((HOBJECT pconfigiterator.OBJECT) <- S.ALLOCATIONS)
def $test_layout_front(S, 3) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("heldLeaf")
def $test_layout_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $test_outputs(S.EVENTS) = $ptascii("B|G|R|V0|U0|K0|PD|IL|F|BL|LL|7|2|N0|V1|U1|K1|J|PD|BL|LL|5|E|S|saved|99|14|W|PD|ID|BD|LL|J1|L0|X|L|PD|CL|")
def $test_layout_front(S, n_stage) = false -- otherwise
dec $test_layout_seek(pstate, nat, nat) : pstate
def $test_layout_seek(S, n_stage, 0) = S
def $test_layout_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_layout_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_layout_seek(S, n_stage, n) = $test_layout_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_layout_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
"""


def reach(state, start, stage):
    return [state + '_found = $test_layout_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_layout_front(' + state + ',' + str(stage) + ')']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *prior.reach('S_return', 'S_initial', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_return*',
        'S_return.RESULT = KNOWN (POBJECT n_parent)',
        '(HOBJECT n_parent) <- S_return.ALLOCATIONS',
        '$heap_owners($heap_graph(S_return),HOBJECT n_parent) = 1',
        '$destructor_method(S_return,n_parent) = eps',
        '$config_iterator_owned_fields(S_return,n_parent)',
        '$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        '$objectprops_at(S_return.OBJECTPROPS,n_parent) = (ppropertyslot_parent*)',
        '$property_slot_nodes(ppropertyslot_parent*) = $node_children(S_return,HOBJECT n_parent)',
        'ppropertyslot_private = ppropertyslot_parent*[1]',
        '$property_slot_descriptor(S_return,n_parent,ppropertyslot_private) = (ppropertydesc_private)',
        'ppropertydesc_private.VISIBILITY = PROPERTY_PRIVATE',
        'ppropertydesc_private.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
        'ppropertyslot_private.STATE = PROP_VALUE (DIRECT (PINT 7))',
        *driver.common.public('S_return')]
    if name == 'primitive-layout':
        return values + ['~$destructor_operational(S_return)',
            '$lookup(S_return.ENV,' + text('scalar') + ') = (n_scalar)',
            '$ordinary_reference_value(S_return,n_scalar) = (PINT 73)',
            '$property_slot_at(ppropertyslot_parent*,' + text('alias') + ') = (ppropertyslot_alias)',
            'ppropertyslot_alias.STATE = PROP_VALUE (ALIAS n_scalar)',
            '$heap_owners($heap_graph(S_return),HCELL n_scalar) = 2',
            '$property_slot_at(ppropertyslot_parent*,' + text('payload') + ') = (ppropertyslot_payload)',
            'ppropertyslot_payload.STATE = PROP_VALUE (DIRECT (PARRAY n_array))',
            '$property_slot_at(ppropertyslot_parent*,' + text('shadow') + ') = (ppropertyslot_shadow)',
            'ppropertyslot_shadow.STATE = PROP_VALUE (DIRECT (PARRAY n_array))',
            '$lookup(S_return.ENV,' + text('arrayHold') + ') = (n_array_cell)',
            'S_return.STORE[n_array_cell] = DEFINED (PARRAY n_array)',
            '$($heap_owners($heap_graph(S_return),HARRAY n_array) >= 3)',
            '$config_iterator_data_node(S_return,HARRAY n_array,eps)',
            '$test_outputs(S_return.EVENTS) = ' + text('B|G|')]
    assert name == 'graph-throw'
    prefix = 'B|G|R|V0|U0|K0|PD|IL|F|BL|LL|7|2|N0|V1|U1|K1|'
    branch_done = prefix + 'J|PD|BL|LL|5|'
    before = branch_done + 'E|S|saved|99|14|W|PD|ID|BD|LL|J1|L0|X|'
    return values + [
        '$lookup(S_return.ENV,' + text('heldLeaf') + ') = (n_held)',
        'S_return.STORE[n_held] = DEFINED (POBJECT n_leaf)',
        '$ordinary_reference_value(S_return,n_held) = (POBJECT n_leaf)',
        '$property_slot_at(ppropertyslot_parent*,' + text('alias') + ') = (ppropertyslot_alias)',
        'ppropertyslot_alias.STATE = PROP_VALUE (ALIAS n_held)',
        '$property_slot_at(ppropertyslot_parent*,' + text('shadow') + ') = (ppropertyslot_shadow)',
        'ppropertyslot_shadow.STATE = PROP_VALUE (DIRECT (POBJECT n_branch))',
        '$property_slot_at(ppropertyslot_parent*,' + text('payload') + ') = (ppropertyslot_payload)',
        'ppropertyslot_payload.STATE = PROP_VALUE (DIRECT (PARRAY n_payload))',
        '$property_slot_at(ppropertyslot_parent*,' + text('pool') + ') = (ppropertyslot_pool)',
        'ppropertyslot_pool.STATE = PROP_VALUE (DIRECT (PARRAY n_pool))',
        '$node_children(S_return,HOBJECT n_parent) = [HARRAY n_pool,HARRAY n_payload,HOBJECT n_branch,HCELL n_held]',
        'S_return.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner))]',
        'S_return.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_branch))]',
        '$objectprops_at(S_return.OBJECTPROPS,n_branch) = (ppropertyslot_branch*)',
        '$property_slot_at(ppropertyslot_branch*,' + text('bag') + ') = (ppropertyslot_bag)',
        'ppropertyslot_bag.STATE = PROP_VALUE (DIRECT (PARRAY n_bag))',
        'S_return.ARRAYS[n_bag].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf)),ENTRY (KINT 1) (DIRECT (POBJECT n_leaf))]',
        '$node_children(S_return,HARRAY n_bag) = [HOBJECT n_leaf,HOBJECT n_leaf]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_branch) = 2',
        '$heap_owners($heap_graph(S_return),HOBJECT n_leaf) = 3',
        '$heap_owners($heap_graph(S_return),HCELL n_held) = 2',
        'S_bad_type = S_return[.OBJECTPROPS = $objectprops_set(S_return.OBJECTPROPS,n_parent,$property_slot_set(ppropertyslot_parent*,ppropertyslot_private.NAME,PROP_VALUE (DIRECT (POBJECT n_leaf))))]',
        '~$config_iterator_owned_fields(S_bad_type,n_parent)',
        'ppropertyslot_parent* = ppropertyslot_head :: ppropertyslot_tail*',
        'S_missing = S_return[.OBJECTPROPS = $objectprops_set(S_return.OBJECTPROPS,n_parent,ppropertyslot_tail*)]',
        '~$config_iterator_owned_fields(S_missing,n_parent)',
        'S_bad_decl = S_return[.OBJECTPROPS = $objectprops_set(S_return.OBJECTPROPS,n_parent,[ppropertyslot_head[.DECL = eps]] ++ ppropertyslot_tail*)]',
        '~$config_iterator_owned_fields(S_bad_decl,n_parent)',
        'S_cycle_object = S_return[.OBJECTPROPS = $objectprops_set(S_return.OBJECTPROPS,n_parent,$property_slot_set(ppropertyslot_parent*,' + text('shadow') + ',PROP_VALUE (DIRECT (POBJECT n_parent))))]',
        '~$config_iterator_owned_fields(S_cycle_object,n_parent)',
        'S_cycle_array = S_return[.ARRAYS = $array_replace(S_return.ARRAYS,n_payload,S_return.ARRAYS[n_payload][.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload))]])]',
        '~$config_iterator_owned_fields(S_cycle_array,n_parent)',
        '$heap_owners($heap_graph(S_cycle_array),HOBJECT n_parent) = 1',
        '~$config_aggregate_return_allowed(S_cycle_array,pconfigaggregate)',
        'S_cycle_cell = S_return[.STORE = $set_cell(S_return.STORE,n_held,DEFINED (POBJECT n_parent))]',
        '~$config_iterator_owned_fields(S_cycle_cell,n_parent)',
        'S_cycle_mixed = S_return[.STORE = $set_cell(S_return.STORE,n_held,DEFINED (PARRAY n_payload))][.ARRAYS = $array_replace(S_return.ARRAYS,n_payload,S_return.ARRAYS[n_payload][.ITEMS = [ENTRY (KINT 0) (ALIAS n_held)]])]',
        '~$config_iterator_owned_fields(S_cycle_mixed,n_parent)',
        'S_array_debt = S_return[.LITERALARRAYDEBTS = n_payload :: S_return.LITERALARRAYDEBTS]',
        '~$config_iterator_owned_fields(S_array_debt,n_parent)',
        'S_special = S_return[.LITERALREFDEBTS = n_held :: S_return.LITERALREFDEBTS]',
        '$ordinary_reference_value(S_special,n_held) = eps',
        '~$config_iterator_owned_fields(S_special,n_parent)',
        '$lookup(S_return.ENV,' + text('saved') + ') = (n_saved_cell)',
        'S_return.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        'S_builtin = S_return[.OBJECTPROPS = $objectprops_set(S_return.OBJECTPROPS,n_parent,$property_slot_set(ppropertyslot_parent*,' + text('shadow') + ',PROP_VALUE (DIRECT (POBJECT n_saved))))]',
        '~$config_iterator_owned_fields(S_builtin,n_parent)',
        *reach('S_throw', 'S_return', 0),
        'S_throw.TODO = (THROW_SEARCH n_saved) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask_throw*',
        'pconfigiterator.OBJECT = n_parent',
        '$lookup(S_throw.ENV,' + text('result') + ') = (n_result_cell)',
        '$lookup(S_throw.ENV,' + text('branchDeaths') + ') = (n_branch_deaths)',
        '$lookup(S_throw.ENV,' + text('leafDeaths') + ') = (n_leaf_deaths)',
        '$lookup(S_throw.ENV,' + text('iterWatch') + ') = (n_parent_watch_cell)',
        'S_throw.STORE[n_parent_watch_cell] = DEFINED (POBJECT n_parent_watch)',
        '$lookup(S_throw.ENV,' + text('branchWatch') + ') = (n_branch_watch_cell)',
        'S_throw.STORE[n_branch_watch_cell] = DEFINED (POBJECT n_branch_watch)',
        '$lookup(S_throw.ENV,' + text('leafWatch') + ') = (n_leaf_watch_cell)',
        'S_throw.STORE[n_leaf_watch_cell] = DEFINED (POBJECT n_leaf_watch)',
        '$test_outputs(S_throw.EVENTS) = ' + text(prefix),
        *reach('S_branch', 'S_throw', 1),
        'S_branch.CURRENT = (pcallcontext_branch)',
        'pcallcontext_branch.TARGET = METHOD_TARGET n_branch porigin_branch_dtor',
        'S_branch.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator "key"',
        'pdestructionoperation.PENDING = (n_saved)',
        '$instance_storage_for(S_branch,n_parent) = (pinstancestorage)',
        '$instance_storage_basic(S_branch,pinstancestorage)',
        '$instance_storage_freeing(S_branch,n_parent)',
        '$instance_storage_state_valid(S_branch)',
        '(HOBJECT n_parent) <- S_branch.ALLOCATIONS',
        '$heap_owners($heap_graph(S_branch),HOBJECT n_parent) = 1',
        'n_parent <- S_branch.DESTRUCTION.CALLED',
        'n_branch <- S_branch.DESTRUCTION.CALLED',
        '~(n_leaf <- S_branch.DESTRUCTION.CALLED)',
        '$node_children(S_branch,HOBJECT n_parent) = [HCELL n_held]',
        '$config_iterator_owned_fields(S_branch,n_parent)',
        '$heap_owners($heap_graph(S_branch),HOBJECT n_leaf) = 3',
        '$weakref_get(S_branch,n_parent_watch) = PNULL',
        '$weakref_get(S_branch,n_branch_watch) = POBJECT n_branch',
        '$weakref_get(S_branch,n_leaf_watch) = POBJECT n_leaf',
        'S_branch.STORE[n_branch_deaths] = DEFINED (PINT 1)',
        'S_branch.STORE[n_leaf_deaths] = DEFINED (PINT 0)',
        *prior.budget('S_branch'), *driver.common.public('S_branch'),
        *reach('S_exit', 'S_branch', 2),
        'S_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_exit*',
        'S_exit.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        '~((HOBJECT n_parent) <- S_exit.ALLOCATIONS)',
        '~((HOBJECT n_branch) <- S_exit.ALLOCATIONS)',
        '(HOBJECT n_leaf) <- S_exit.ALLOCATIONS',
        '$heap_owners($heap_graph(S_exit),HOBJECT n_leaf) = 1',
        '$heap_owners($heap_graph(S_exit),HCELL n_held) = 1',
        '~(n_leaf <- S_exit.DESTRUCTION.CALLED)',
        '$weakref_get(S_exit,n_parent_watch) = PNULL',
        '$weakref_get(S_exit,n_branch_watch) = PNULL',
        '$weakref_get(S_exit,n_leaf_watch) = POBJECT n_leaf',
        '$instance_storage_for(S_exit,n_parent) = eps',
        '$config_iterator_quiet_aggregate_data(S_exit,pconfigiterator)',
        '$config_iterator_retired_scope(S_exit,pconfigiterator)',
        '$eager_operation_source_valid(S_exit,pdestructionoperation)',
        '$destructor_operation_valid(S_exit,pdestructionoperation)',
        'S_no_marker = S_exit[.DESTRUCTION.CALLED = eps]',
        '~$eager_operation_source_valid(S_no_marker,pdestructionoperation)',
        '$test_outputs(S_exit.EVENTS) = ' + text(branch_done),
        *prior.budget('S_exit'), *driver.common.public('S_exit'),
        *reach('S_before', 'S_exit', 3),
        '$lookup(S_before.ENV,' + text('heldLeaf') + ') = (n_held)',
        'S_before.STORE[n_held] = DEFINED (POBJECT n_leaf)',
        '$weakref_get(S_before,n_leaf_watch) = POBJECT n_leaf',
        'S_before.STORE[n_leaf_deaths] = DEFINED (PINT 0)',
        '$eager_operation_pending(S_before) = eps',
        '$test_outputs(S_before.EVENTS) = ' + text(before),
        *reach('S_leaf', 'S_before', 4),
        'S_leaf.CURRENT = (pcallcontext_leaf)',
        'pcallcontext_leaf.TARGET = METHOD_TARGET n_leaf porigin_leaf_dtor',
        'S_leaf.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
        'pdestructorcall.OBJECT = n_leaf', 'pdestructorcall.PENDING = eps',
        '~((HOBJECT n_parent) <- S_leaf.ALLOCATIONS)',
        '~((HOBJECT n_branch) <- S_leaf.ALLOCATIONS)',
        '$weakref_get(S_leaf,n_leaf_watch) = POBJECT n_leaf',
        'S_leaf.STORE[n_leaf_deaths] = DEFINED (PINT 1)',
        *driver.common.public('S_leaf'),
        'S_final = $drive_steps(S_leaf,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        '$lookup(S_final.ENV,' + text('heldLeaf') + ') = eps',
        '~((HOBJECT n_leaf) <- S_final.ALLOCATIONS)',
        '$weakref_get(S_final,n_leaf_watch) = PNULL',
        'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_final.STORE[n_branch_deaths] = DEFINED (PINT 1)',
        'S_final.STORE[n_leaf_deaths] = DEFINED (PINT 1)',
        'S_final.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_final.EVENTS) = ' + text(before + 'L|PD|CL|Z|LD|L1|'),
        *driver.common.public('S_final')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=['primitive-layout', 'graph-throw'])
    args = parser.parse_args()
    selected = (args.case,) if args.case else ('primitive-layout', 'graph-throw')
    sources.family.CASES = {name: sources.family.CASES[name] for name in selected}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    if args.phase == 'check':
        recorded = driver.recorder.recorded
        driver.recorder.recorded = lambda command, stem, cap: recorded(command, stem, 480 if Path(stem).parent.name == 'graph-throw' else 180)
    sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources), '--output', str(args.output)]
    driver.main()


if __name__ == '__main__':
    main()
