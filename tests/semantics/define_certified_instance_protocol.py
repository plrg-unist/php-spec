#!/usr/bin/env python3
"""Reached instance capture, receipt guards, duplicate roots and store callbacks."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as runner
import define_certified_instance_sources as sources

define, packet, common = runner.define, runner.packet, runner.common
ROOT, text, term = runner.ROOT, runner.text, runner.term
PREFIX = define.PREFIX + r'''
dec $test_instance_define_store(pstate, nat) : bool
def $test_instance_define_store(S,n_object) = true
  -- if S.TODO = [DESTRUCTOR_STORE]
  -- if S.DESTRUCTION.PHASE = DESTRUCTION_STORE
  -- if $destructor_handle(S,S.DESTRUCTION.INDEX,0) = (n_object)
  -- if ~(n_object <- S.DESTRUCTION.CALLED)
  -- if $destructor_method(S,n_object) =/= eps
def $test_instance_define_store(S,n_object) = false -- otherwise
dec $test_instance_define_store_seek(pstate, nat, nat) : pstate
def $test_instance_define_store_seek(S,n_object,0) = S
def $test_instance_define_store_seek(S,n_object,n) = S
  -- if $(n > 0)
  -- if $test_instance_define_store(S,n_object) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_instance_define_store_seek(S,n_object,n) = $test_instance_define_store_seek($drive_steps($test_running(S),1),n_object,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_instance_define_store(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def property_value(state, obj, value, suffix):
    return [f'$objectprops_at({state}.OBJECTPROPS,{obj}) = (ppropertyslot_all_{suffix}*)',
        f'$property_slot_at(ppropertyslot_all_{suffix}*,$ptascii("value")) = (ppropertyslot_{suffix})',
        f'ppropertyslot_{suffix}.STATE = PROP_VALUE pitem_{suffix}',
        f'$entry_value({state},pitem_{suffix}) = PINT {value}']


def certified(state, obj, donor, suffix):
    record, row, site = 'pconstantobject_' + suffix, 'puserconstant_' + suffix, 'porigin_' + suffix
    return [f'$user_constant_at({state}.USERCONSTANTS,{text(donor)}) = ({row})',
        f'{row}.VALUE = POBJECT {obj}', f'{row}.CLASS = PVINSTANCE {obj} {site}',
        f'$global_new_record({state}.CONSTANTOBJECTS,{obj}) = ({record})',
        f'{record}.OBJECT = {obj}', f'{record}.SITE = {site}',
        f'$global_new_completed({state},{record})',
        f'{state}.OBJECTS[{obj}] = INSTANCE {record}.CLASS',
        f'$constant_value_class_valid({state},POBJECT {obj},PVINSTANCE {obj} {site})',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVINSTANCE {obj} {site})']


def controls(obj, record):
    values = []
    for suffix, change in [
        ('missing', '[.CONSTANTOBJECTS = eps]'),
        ('incomplete', f'[.CONSTANTOBJECTS = $global_new_record_put(S.CONSTANTOBJECTS,{record}[.COMPLETE = false])]'),
        ('site', f'[.CONSTANTOBJECTS = $global_new_record_put(S.CONSTANTOBJECTS,{record}[.SITE = PORIGIN 0 eps])]'),
        ('prefix', f'[.CONSTANTOBJECTS = $global_new_record_put(S.CONSTANTOBJECTS,{record}[.PREFIX = 0])]'),
        ('dead', f'[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT {obj})]')]:
        values += ['S_' + suffix + ' = S' + change,
            f'$dynamic_define_value_class(S_{suffix},POBJECT {obj}) = eps']
    return [*values, '$dynamic_define_value_class(S,POBJECT (|S.OBJECTS|)) = eps']


def store(state, start, obj, owners, before):
    return [f'{state}_found = $test_instance_define_store_seek({start},{obj},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_instance_define_store({state},{obj})', *common.public(state),
        f'$test_outputs({state}.EVENTS) = ' + term(before),
        f'$heap_owners($heap_graph({state}),HOBJECT {obj}) = {owners}',
        *common.step(state + '_selected', state),
        f'{state}_selected.TODO = (DESTRUCTOR_ENTER pdestructorcall_{state}) :: ptask_{state}*',
        f'pdestructorcall_{state}.OBJECT = {obj}', f'pdestructorcall_{state}.STORE',
        f'$destructor_enter_valid({state}_selected,pdestructorcall_{state})',
        f'$heap_owners($heap_graph({state}_selected),HOBJECT {obj}) = $({owners} + 2)']


def checks(initial, name, stdout):
    selected = name.startswith('selected-')
    target = 'V73_EVAL_ROW' if selected else 'V73_ROW'
    if selected:
        values = [*initial, *define.reach('S','S_initial',1,target),
            'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
            'pconfigcall.SITE = PORIGIN 1 pcpath_define', 'pconfigcall.SELECTION = (n_selection)',
            '$dynamic_define_values(pconfigcall) = ((' + text(target) + ',POBJECT n_candidate))',
            *certified('S','n_candidate','V73_EVAL_NEXT','candidate'),
            *certified('S','n_object','V73_EVAL_OLD','old'),
            '$user_constant_at(S.USERCONSTANTS,' + text(target) + ') = (puserconstant_row)',
            'puserconstant_row.VALUE = POBJECT n_object',
            'puserconstant_row.CLASS = PVINSTANCE n_object porigin_old',
            'n_object =/= n_candidate', 'n_constants = |S.USERCONSTANTS|', 'n_constants = 3',
            '$dynamic_constant_duplicate_valid(S,pconfigcall,n_constants)',
            *property_value('S','n_object',7,'before_old'),
            *property_value('S','n_candidate',23,'before_candidate'),
            *controls('n_candidate','pconstantobject_candidate'),
            'n_candidate_owners = $heap_owners($heap_graph(S),HOBJECT n_candidate)',
            *common.step('S_dispatch','S'), *common.public('S_dispatch'),
            'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*',
            'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants',
            'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
            'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_dispatch),HOBJECT n_candidate) = n_candidate_owners',
            *define.reach('S_done','S_dispatch',2,target),
            'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_done*',
            'perrorcall_done.RESUME = perrorcall.RESUME', 'S_done.RESULT = KNOWN (PBOOL true)',
            '$user_constant_at(S_done.USERCONSTANTS,$ptascii("V73_SIDE")) = (puserconstant_side)',
            'S_done.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_side]',
            'puserconstant_side.VALUE = PINT 19',
            '$dynamic_constant_duplicate_valid(S_done,pconfigcall,n_constants)',
            *property_value('S_done','n_object',13,'after_old'),
            *property_value('S_done','n_candidate',29,'after_candidate'),
            *common.step('S_cleanup','S_done'), *common.public('S_cleanup'),
            'S_cleanup.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cleanup) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) :: (ERROR_HANDLER_CLEAN perrorcall_done) :: ptask_done*',
            'pdestructionrelease_cleanup.JOBS = eps',
            'pdestructionoperation_cleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall_done',
            'pdestructionoperation_cleanup.VALUE = KNOWN PNULL',
            'pdestructionoperation_cleanup.PENDING = eps',
            *common.step('S_cleanup_exit','S_cleanup'),
            *common.step('S_clean','S_cleanup_exit'),
            'S_clean.TODO = (ERROR_HANDLER_CLEAN perrorcall_done) :: ptask_done*',
            '$error_cleanup_valid(S_clean,perrorcall_done)',
            *common.step('S_pending','S_clean'), *common.public('S_pending'),
            'S_pending.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants) :: ptask_done*',
            'S_pending.EVENTS = S_done.EVENTS',
            'S_pending.DESTRUCTION.CLEANUPS = S_done.DESTRUCTION.CLEANUPS',
            'n_pending_owners = $heap_owners($heap_graph(S_pending),HOBJECT n_candidate)',
            *common.step('S_release','S_pending'),
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_candidate) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_candidate) :: ptask_done*',
            'pdestructionrelease_candidate.JOBS = [DESTRUCTION_VALUE (HOBJECT n_candidate)]',
            'pdestructionoperation_candidate.SOURCE = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants',
            'pdestructionoperation_candidate.VALUE = KNOWN (PBOOL false)',
            'pdestructionoperation_candidate.PENDING = eps',
            '$heap_owners($heap_graph(S_release),HOBJECT n_candidate) = n_pending_owners',
            *common.step('S_released','S_release'),
            '$heap_owners($heap_graph(S_released),HOBJECT n_candidate) = $(n_pending_owners - 1)',
            '~(n_candidate <- S_released.DESTRUCTION.CALLED)',
            *common.step('S_release_exit','S_released'),
            *common.step('S_false','S_release_exit','PBOOL false'),
            '$heap_owners($heap_graph(S_false),HOBJECT n_candidate) = $(n_pending_owners - 1)',
            'S_false.USERCONSTANTS = S_done.USERCONSTANTS',
            *store('S_store_old','S_false','n_object',2,b'B|T|H|F|old|13|29|19|A|'),
            *store('S_store_next','S_store_old_selected','n_candidate',1,b'B|T|H|F|old|13|29|19|A|D|13|'),
            *define.finish('S_store_next_selected',stdout),
            'S_final.USERCONSTANTS = S_done.USERCONSTANTS',
            '$heap_owners($heap_graph(S_final),HOBJECT n_candidate) = 1',
            'n_candidate <- S_final.DESTRUCTION.CALLED',
            *property_value('S_final','n_candidate',29,'final_candidate')]
    else:
        values = [*initial, *define.reach('S','S_initial',0,target),
            'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
            '$dynamic_define_values(pconfigcall) = ((' + text(target) + ',POBJECT n_object))',
            *certified('S','n_object','V73_DONOR','donor'),
            *property_value('S','n_object',5,'initial'),
            '$source_constant_lookup(S,' + text(target) + ') = eps',
            '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
            'n_owners = $heap_owners($heap_graph(S),HOBJECT n_object)',
            *controls('n_object','pconstantobject_donor'),
            'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)', 'S_resume = S',
            *common.step('S_row','S_resume','PBOOL true'),
            '$user_constant_at(S_row.USERCONSTANTS,' + text(target) + ') = (puserconstant_row)',
            'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
            'puserconstant_row.VALUE = POBJECT n_object',
            'puserconstant_row.CLASS = PVINSTANCE n_object porigin_donor',
            'puserconstant_row.ORIGIN = pconfigcall.SITE',
            'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
            '$heap_graph(S_row).EDGES = $heap_graph(S).EDGES',
            '$heap_owners($heap_graph(S_row),HOBJECT n_object) = n_owners']
        values += [f'S_row.{field} = S.{field}' for field in ['ALLOCATIONS','OBJECTS','OBJECTPROPS','OBJECTTABLES','PROPREFS','STORE','ARRAYS','STRINGDATA','CONSTANTOBJECTS']]
        values += ['puserconstant_bad = puserconstant_row[.CLASS = PVOBJECT]',
            '~$user_constants_valid(S_row[.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_bad]],S.USERCONSTANTS ++ [puserconstant_bad])',
            *common.reach('S_query','S_row',0,target), *common.public('S_query'),
            'n_query_owners = $heap_owners($heap_graph(S_query),HOBJECT n_object)',
            *common.step('S_value','S_query','POBJECT n_object'),
            '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
            '$heap_owners($heap_graph(S_value),HOBJECT n_object) = $(n_query_owners + 1)',
            'S_value.ALLOCATIONS = S_query.ALLOCATIONS', 'S_value.OBJECTPROPS = S_query.OBJECTPROPS',
            *store('S_store','S_value','n_object',2,b'B|C|T|same|11|11|A|'),
            *property_value('S_store','n_object',11,'store'),
            *define.finish('S_store_selected',stdout),
            'S_final.USERCONSTANTS = S_row.USERCONSTANTS']
    values += ['S_final.DESTRUCTION.PHASE = DESTRUCTION_DONE',
        'n_object <- S_final.DESTRUCTION.CALLED',
        'S_final.CONSTANTOBJECTS = S.CONSTANTOBJECTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 2',
        *property_value('S_final','n_object',13 if selected else 11,'final')]
    return values


runner.sources, runner.checks, runner.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, runner.prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES)
    args, remaining = parser.parse_known_args()
    if args.case:
        sources.family.CASES = {args.case: sources.family.CASES[args.case]}
    sys.argv = [sys.argv[0], *remaining]
    raise SystemExit(0 if packet.main() else 1)
