#!/usr/bin/env python3
"""Owned direct object publication, argument retirement and cached STD identity."""
import argparse
from pathlib import Path
import sys

import define_runtime_closure_protocol as real
import define_runtime_object_protocol as runtime
import define_runtime_stdclass_protocol as std
import define_owned_closure_protocol as owned
import define_owned_object_sources as sources

define, packet, common = owned.define, owned.packet, owned.common
prior, instance = owned.prior, runtime.instance
ROOT, text, term = owned.ROOT, owned.text, owned.term
DIRECT = sources.DIRECT
PREFIX = runtime.PREFIX + real.PREFIX[len(define.PREFIX):] + r'''
dec $test_owned_object_front(pstate, nat) : bool
def $test_owned_object_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0
def $test_owned_object_front(S,1) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_payload))]
def $test_owned_object_front(S,2) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if ~pdestructorcall.STORE
def $test_owned_object_front(S,n_phase) = false -- otherwise
dec $test_owned_object_seek(pstate, nat, nat) : pstate
def $test_owned_object_seek(S,n_phase,0) = S
def $test_owned_object_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_object_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_object_seek(S,n_phase,n) = $test_owned_object_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_object_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_object_seek({start},{phase},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_object_front({state},{phase})', *common.public(state)]


def controls():
    return [
        '~$global_constant_class_supported(PVOBJECT)',
        '~$constant_value_class_valid(S,POBJECT n_left,PVINSTANCE n_left pconfigcall.SITE)',
        '~$dynamic_owned_define_valid(S,pconfigcall[.OWNER = eps])',
        '~$dynamic_owned_define_valid(S,pconfigcall[.SELECTION = eps])',
        'S_missing = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$heap_graph(S_missing) = $heap_graph(S)',
        '~$dynamic_owned_define_valid(S_missing,pconfigcall)',
        '~$dynamic_define_source(S_missing,pconfigcall.SITE)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_left) = eps',
        '~$dynamic_owned_define_valid(S_dead,pconfigcall)',
        'pconstantobject_bad = {OBJECT n_left,SITE pconfigcall.SITE,DECL pconfigcall.SITE,CLASS porigin_left,PREFIX (|S.DECLARATIONS|),COMPLETE false}',
        'S_bad = S[.CONSTANTOBJECTS = [pconstantobject_bad]]',
        '$dynamic_define_value_class(S_bad,POBJECT n_left) = eps',
        '~$dynamic_owned_define_valid(S_bad,pconfigcall)',
        'pconfigcall_callee_value = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_first))]',
        '$dynamic_owned_define_header(S,pconfigcall_callee_value)',
        '$dynamic_define_value_class(S,POBJECT n_first) = (PVOBJECT)',
        '$dynamic_owned_define_valid(S,pconfigcall_callee_value)']


def direct(initial, stdout):
    target = 'V95_DIRECT_OWNED'
    values = [*initial, *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        *owned.receipt('S_capture','pconfigcall_capture','first',0,0),
        'S_capture.SELECTEDCALLS = [pselectedcall_first]',
        'S_capture.USERCONSTANTS = eps', 'pconfigcall_capture.SENT = eps',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("payload")) = (n_payload)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("pointerWeak")) = (n_pointer_cv)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("destroyed")) = (n_destroyed)',
        'S_capture.STORE[n_payload] = DEFINED (POBJECT n_left)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak_first)',
        'S_capture.OBJECTS[n_weak_first] = WEAKREFERENCE (n_first)',
        'S_capture.STORE[n_pointer_cv] = DEFINED (POBJECT n_pointer)',
        'S_capture.OBJECTS[n_pointer] = WEAKREFERENCE (n_left)',
        '$node_children(S_capture,HOBJECT n_pointer) = eps',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_first) = 2',
        *reach('S_args','S_capture',1),
        'S_args.TODO = (CONFIG_ARGS pconfigcall_args) :: ptask_capture*',
        'pconfigcall_args.OWNER = (n_first)', 'pconfigcall_args.SELECTION = (0)',
        'pconfigcall_args.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_left))]',
        'S_args.SELECTEDCALLS = S_capture.SELECTEDCALLS',
        *instance.property_value('S_args','n_left',7,'early'),
        '$heap_owners($heap_graph(S_args),HOBJECT n_left) = 2',
        *define.reach('S','S_args',0,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_first)', 'pconfigcall.SELECTION = (0)',
        'pconfigcall.NAMED', '|pconfigcall.SENT| = 2',
        '$dynamic_define_values(pconfigcall) = ((' + text(target) + ',POBJECT n_left))',
        '$dynamic_owned_define_header(S,pconfigcall)', '$dynamic_owned_define_valid(S,pconfigcall)',
        '~$dynamic_array_call_valid(S,pconfigcall)',
        *runtime.ordinary('S','n_left','left'),
        'S.STORE[n_payload] = DEFINED PNULL',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("constant"))',
        '$config_nodes(pconfigcall) = [HOBJECT n_left,HOBJECT n_first]',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_first) = 1',
        '$weakref_get(S,n_pointer) = POBJECT n_left',
        *instance.property_value('S','n_left',19,'captured'),
        '$test_outputs(S.EVENTS) = ' + term(b'B|N|1|held|'),
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_registered','S'), *common.public('S_registered'),
        '$drive_steps($test_running(S_pause),1) = S_registered_found',
        'S_registered.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_first) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_first) :: ptask_initial*',
        'pdestructionrelease_first.JOBS = [DESTRUCTION_VALUE (HOBJECT n_first)]',
        'pdestructionoperation_first.SOURCE = CONFIG_INVOKE pconfigcall',
        'pdestructionoperation_first.VALUE = KNOWN (PBOOL true)', 'pdestructionoperation_first.PENDING = eps',
        'S_registered.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = ' + text(target), 'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_left', 'puserconstant_row.CLASS = PVOBJECT',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        'S_row_found = $test_runtime_object_delivery_seek(S_registered,100)',
        r'S_row_found.COMPLETION = NORMAL \/ S_row_found.COMPLETION = BUDGET',
        'S_row = $test_running(S_row_found)', *common.public('S_row'),
        'S_row.TODO = ptask_initial*', 'S_row.RESULT = KNOWN (PBOOL true)',
        'S_row.USERCONSTANTS = S_registered.USERCONSTANTS',
        '~(HOBJECT n_first <- S_row.ALLOCATIONS)', '$weakref_get(S_row,n_weak_first) = PNULL',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 1',
        '$selected_entry_source_valid(S_row,pselectedcall_first)',
        'S_no_history = S_row[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$heap_graph(S_no_history) = $heap_graph(S_row)',
        '~$user_constants_valid(S_no_history,S_no_history.USERCONSTANTS)',
        *common.reach('S_query','S_row',0,target), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,' + text(target) + ') = (POBJECT n_left)',
        *common.step('S_value','S_query','POBJECT n_left'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_left) = 2',
        'S_value.USERCONSTANTS = S_row.USERCONSTANTS', 'S_value.ARRAYS = S_query.ARRAYS',
        *real.unset('S_observed','S_value','stored'),
        '$lookup(S_observed.ENV,$ptascii("stored")) = (n_stored)',
        '$lookup(S_observed.ENV,$ptascii("again")) = (n_again)',
        'S_observed.STORE[n_stored] = DEFINED (POBJECT n_left)',
        'S_observed.STORE[n_again] = DEFINED (POBJECT n_left)',
        '$heap_owners($heap_graph(S_observed),HOBJECT n_left) = 3',
        *instance.property_value('S_observed','n_left',23,'shared'),
        '$test_outputs(S_observed.EVENTS) = ' + term(b'B|N|1|held|T|gone|constant|null|same|19|same|23|'),
        *define.reach('S_dup','S_observed',1,target),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        'pconfigcall_dup.OWNER = (n_second)', 'pconfigcall_dup.SELECTION = (1)',
        'n_second =/= n_first', 'S_dup.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        'pselectedcall_second.OWNER = (n_second)', '$selected_entry_source_valid(S_dup,pselectedcall_second)',
        '$dynamic_define_values(pconfigcall_dup) = ((' + text(target) + ',POBJECT n_right))',
        '$dynamic_owned_define_valid(S_dup,pconfigcall_dup)',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.STORE[n_payload] = DEFINED PNULL',
        'S_dup.STORE[n_weak_cv] = DEFINED (POBJECT n_weak_second)',
        'S_dup.OBJECTS[n_weak_second] = WEAKREFERENCE (n_second)',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 1',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_second) = 1',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_left) = 1',
        *instance.property_value('S_dup','n_right',41,'duplicate'),
        *common.step('S_dispatch','S_dup'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        '$error_call_valid(S_dispatch,perrorcall)',
        *define.reach('S_marker','S_dispatch',4,target),
        'S_marker.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_dispatch*',
        'S_marker.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_marker.STORE[n_calls] = DEFINED (PINT 1)', 'S_marker.STORE[n_destroyed] = DEFINED (PINT 0)',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_right) = 1',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_second) = 1',
        '$test_outputs(S_marker.EVENTS) = ' + term(b'B|N|1|held|T|gone|constant|null|same|19|same|23|N|2|held|H|2|23|held|'),
        *common.step('S_release','S_marker'), *common.public('S_release'),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_dup) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_dup) :: ptask_dispatch*',
        'pdestructionrelease_dup.JOBS = [DESTRUCTION_VALUE (HOBJECT n_right),DESTRUCTION_VALUE (HOBJECT n_second)]',
        'pdestructionoperation_dup.SOURCE = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        'pdestructionoperation_dup.VALUE = KNOWN (PBOOL false)', 'pdestructionoperation_dup.PENDING = eps',
        *reach('S_free','S_release',2),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_free*',
        'pdestructorcall.OBJECT = n_right', '~pdestructorcall.STORE',
        'pdestructorcall.OPERATION = (pdestructionoperation_dup)', 'pdestructorcall.PENDING = eps',
        '$destructor_enter_valid(S_free,pdestructorcall)',
        '$heap_owners($heap_graph(S_free),HOBJECT n_right) = 2',
        '$heap_owners($heap_graph(S_free),HOBJECT n_second) = 1',
        '$weakref_get(S_free,n_weak_second) = POBJECT n_second',
        '$test_outputs(S_free.EVENTS) = $test_outputs(S_marker.EVENTS)',
        *common.reach('S_last_query','S_free',0,target), *common.public('S_last_query'),
        '~(HOBJECT n_right <- S_last_query.ALLOCATIONS)', '~(HOBJECT n_second <- S_last_query.ALLOCATIONS)',
        '$weakref_get(S_last_query,n_weak_second) = PNULL',
        'S_last_query.STORE[n_destroyed] = DEFINED (PINT 1)',
        'S_last_query.STORE[n_calls] = DEFINED (PINT 1)',
        'S_last_query.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_last_query.EVENTS) = ' + term(b'B|N|1|held|T|gone|constant|null|same|19|same|23|N|2|held|H|2|23|held|D|41|held|F|gone|'),
        *instance.store('S_store','S_last_query','n_left',1,stdout[:-5]),
        *define.finish('S_store_selected',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '~(HOBJECT n_first <- S_final.ALLOCATIONS)', '~(HOBJECT n_second <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_right <- S_final.ALLOCATIONS)',
        *instance.property_value('S_final','n_left',23,'final')]
    return values


def cached(initial, stdout):
    target = 'V95_STD_OWNED'
    values = [*initial, *define.reach('S','S_initial',0,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        *owned.receipt('S','pconfigcall','first',0,0),
        '$dynamic_define_values(pconfigcall) = ((' + text(target) + ',POBJECT n_box))',
        '$dynamic_owned_define_header(S,pconfigcall)', '$dynamic_owned_define_valid(S,pconfigcall)',
        '~$dynamic_array_call_valid(S,pconfigcall)',
        *std.ordinary('S','n_box','box'), *std.child('S','n_box','n_child','box_child'),
        'pitem_box_child = DIRECT (POBJECT n_child)',
        '$object_table_at(S.OBJECTTABLES,n_box) = (n_table)',
        'S.ARRAYS[n_table].ITEMS = [ENTRY (KSTRING ($ptascii("child"))) (DIRECT (POBJECT n_child))]',
        '$array_append_key(S.ARRAYS[n_table]) = KINT 0',
        '$node_children(S,HOBJECT n_box) = [HARRAY n_table]',
        '$node_children(S,HARRAY n_table) = [HOBJECT n_child]',
        '$lookup(S.ENV,$ptascii("payload")) = (n_payload)',
        '$lookup(S.ENV,$ptascii("child")) = (n_child_cv)',
        '$lookup(S.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S.ENV,$ptascii("weak")) = (n_weak_cv)',
        'S.STORE[n_payload] = DEFINED PNULL', 'S.STORE[n_child_cv] = DEFINED PNULL',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)', 'S.OBJECTS[n_weak] = WEAKREFERENCE (n_first)',
        '$config_nodes(pconfigcall) = [HOBJECT n_box,HOBJECT n_first]',
        '$heap_owners($heap_graph(S),HOBJECT n_box) = 1',
        '$heap_owners($heap_graph(S),HARRAY n_table) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_child) = 1',
        *instance.property_value('S','n_child',19,'child'),
        'S_dead_table = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_table)]',
        '~$dynamic_owned_define_valid(S_dead_table,pconfigcall)',
        'S_dead_child = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_child)]',
        '~$dynamic_owned_define_valid(S_dead_child,pconfigcall)',
        'S_bad_table = S[.ARRAYS[n_table].ITEMS = eps]',
        '~$dynamic_owned_define_valid(S_bad_table,pconfigcall)',
        '$test_outputs(S.EVENTS) = ' + term(b'B|N|held|'),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S',
        *common.step('S_registered','S'), *common.public('S_registered'),
        '$drive_steps($test_running(S_pause),1) = S_registered_found',
        'S_registered.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_initial*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_first)]',
        'pdestructionoperation.SOURCE = CONFIG_INVOKE pconfigcall',
        'pdestructionoperation.VALUE = KNOWN (PBOOL true)', 'pdestructionoperation.PENDING = eps',
        'S_registered.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = ' + text(target), 'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_box', 'puserconstant_row.CLASS = PVOBJECT',
        'S_row_found = $test_runtime_object_delivery_seek(S_registered,100)',
        r'S_row_found.COMPLETION = NORMAL \/ S_row_found.COMPLETION = BUDGET',
        'S_row = $test_running(S_row_found)', *common.public('S_row'),
        'S_row.TODO = ptask_initial*', 'S_row.RESULT = KNOWN (PBOOL true)',
        '~(HOBJECT n_first <- S_row.ALLOCATIONS)', '$weakref_get(S_row,n_weak) = PNULL',
        'S_row.USERCONSTANTS = S_registered.USERCONSTANTS',
        'S_row.ARRAYS = S.ARRAYS', 'S_row.OBJECTPROPS = S.OBJECTPROPS', 'S_row.OBJECTTABLES = S.OBJECTTABLES',
        '$selected_entry_source_valid(S_row,pselectedcall_first)',
        *common.reach('S_query','S_row',0,target), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,' + text(target) + ') = (POBJECT n_box)',
        *real.unset('S_observed','S_query','stored'),
        '$lookup(S_observed.ENV,$ptascii("stored")) = (n_stored)',
        '$lookup(S_observed.ENV,$ptascii("again")) = (n_again)',
        '$lookup(S_observed.ENV,$ptascii("leaf")) = (n_leaf)',
        '$lookup(S_observed.ENV,$ptascii("view")) = (n_view)',
        '$lookup(S_observed.ENV,$ptascii("againView")) = (n_again_view)',
        'S_observed.STORE[n_stored] = DEFINED (POBJECT n_box)',
        'S_observed.STORE[n_again] = DEFINED (POBJECT n_box)',
        'S_observed.STORE[n_leaf] = DEFINED (POBJECT n_child)',
        'S_observed.STORE[n_view] = DEFINED (PARRAY n_copy)',
        'S_observed.STORE[n_again_view] = DEFINED (PARRAY n_table)', 'n_copy =/= n_table',
        '$object_table_at(S_observed.OBJECTTABLES,n_box) = (n_table)',
        'S_observed.ARRAYS[n_table] = S.ARRAYS[n_table]',
        '$entry_lookup(S_observed.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("child"))) = (pitem_local)',
        '$entry_value(S_observed,pitem_local) = PNULL',
        '$array_append_key(S_observed.ARRAYS[n_copy]) = KINT 1',
        '$array_append_key(S_observed.ARRAYS[n_table]) = KINT 0',
        '$heap_owners($heap_graph(S_observed),HOBJECT n_box) = 3',
        '$heap_owners($heap_graph(S_observed),HOBJECT n_child) = 2',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S_observed).EDGES,[HARRAY n_table]) = 1',
        *instance.property_value('S_observed','n_child',41,'shared'),
        '$test_outputs(S_observed.EVENTS) = ' + term(stdout[:-7]),
        *instance.store('S_store','S_observed','n_child',1,stdout[:-5]),
        *define.finish('S_store_selected',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_box) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_table) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_child) = 1',
        '~(HOBJECT n_first <- S_final.ALLOCATIONS)', '~(HARRAY n_copy <- S_final.ALLOCATIONS)',
        'S_final.ARRAYS[n_table] = S.ARRAYS[n_table]',
        '$selected_entry_source_valid(S_final,pselectedcall_first)']
    return values


def checks(initial, name, stdout):
    return (direct if name == DIRECT else cached)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = real.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 420 if directory.parent.name == DIRECT else 240
    return packet_process(command, directory, timeout, cwd)


packet.process = process
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
