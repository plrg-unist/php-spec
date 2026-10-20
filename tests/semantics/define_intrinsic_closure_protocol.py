#!/usr/bin/env python3
"""Intrinsic VALUE identity survives publication, COW and query-derived writers."""
from pathlib import Path

import define_owned_closure_protocol as owned
import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_protocol as prior
import typed_static_invoke_set_protocol as process_base
import define_intrinsic_closure_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = sources.DIRECT
PREFIX = runtime.PREFIX + r'''
dec $test_intrinsic_named(pstate) : bool
def $test_intrinsic_named(S) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 1
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_HOLE
def $test_intrinsic_named(S) = false -- otherwise
dec $test_intrinsic_named_seek(pstate, nat) : pstate
def $test_intrinsic_named_seek(S,0) = S
def $test_intrinsic_named_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_intrinsic_named(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_intrinsic_named_seek(S,n) = $test_intrinsic_named_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_intrinsic_named(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def named(state, start):
    return [f'{state}_found = $test_intrinsic_named_seek({start},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_intrinsic_named({state})', *common.public(state)]


def intrinsic(state, obj, kind='INTRINSIC_DEFINE'):
    return [f'{state}.OBJECTS[{obj}] = INTRINSICCLOSURE {kind}',
        f'$typed_closure({state},{obj})', f'$closure_live_object_valid({state},{obj})',
        f'$closure_scope_at({state}.CLOSURESCOPES,{obj}) = eps',
        f'$closure_binding_at({state}.CLOSUREBINDINGS,{obj}) = eps',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = eps',
        f'$node_children({state},HOBJECT {obj}) = eps',
        f'$dynamic_runtime_object({state},{obj})',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVOBJECT)']


def controls():
    return [
        '~$global_constant_class_supported(PVOBJECT)',
        '$constant_value_class_valid(S,POBJECT n_left,PVOBJECT)',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_left) = eps',
        'pclosurescope_bad = {OBJECT n_left,LEXICAL pconfigcall.SITE,CALLED pconfigcall.SITE,RECEIVER eps,CREATION eps}',
        'S_scope = S[.CLOSURESCOPES = [pclosurescope_bad]]',
        '$typed_closure(S_scope,n_left)', '~$dynamic_runtime_object(S_scope,n_left)',
        'pclosurebinding_bad = {OBJECT n_left,SITE pconfigcall.SITE,SOURCE n_left,LEXICAL eps,CALLED eps,RECEIVER eps}',
        'S_binding = S[.CLOSUREBINDINGS = [pclosurebinding_bad]]',
        '$typed_closure(S_binding,n_left)', '~$dynamic_runtime_object(S_binding,n_left)',
        'pconstantclosure_bad = {OBJECT n_left,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '$dynamic_define_value_class(S_record,POBJECT n_left) = eps',
        'S_wrapped = S[.OBJECTS[n_left] = CONSTANTCLOSURE pconfigcall.SITE (INTRINSICCLOSURE INTRINSIC_DEFINE)]',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_left) = eps',
        'S_current = S[.OBJECTS[n_left] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT]',
        '$typed_closure(S_current,n_left)', '$dynamic_runtime_object(S_current,n_left)',
        '~$dynamic_owned_define_valid(S,pconfigcall[.OWNER = (n_left)])',
        '~$dynamic_owned_define_valid(S,pconfigcall[.SELECTION = eps])']


def direct(initial, stdout):
    before = b'B|N|held|'
    queried = before + b'T|gone|same|split|null|defined|'
    values = [*initial, *named('S_capture','S_initial'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        *owned.receipt('S_capture','pconfigcall_capture','publish',0,0),
        'S_capture.SELECTEDCALLS = [pselectedcall_publish]',
        'S_capture.USERCONSTANTS = eps',
        'pconfigcall_capture.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_left))]',
        '$lookup(S_capture.ENV,$ptascii("left")) = (n_left_cv)',
        '$lookup(S_capture.ENV,$ptascii("other")) = (n_other)',
        '$lookup(S_capture.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("pointer")) = (n_pointer_cv)',
        'S_capture.STORE[n_left_cv] = DEFINED (POBJECT n_left)',
        'S_capture.STORE[n_value] = DEFINED (POBJECT n_left)',
        'S_capture.STORE[n_other] = DEFINED (POBJECT n_right)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.STORE[n_pointer_cv] = DEFINED (POBJECT n_pointer)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_publish)',
        'S_capture.OBJECTS[n_pointer] = WEAKREFERENCE (n_left)',
        'n_left =/= n_right', 'n_left =/= n_publish', 'n_right =/= n_publish',
        *intrinsic('S_capture','n_left'), *intrinsic('S_capture','n_right'),
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_left,HOBJECT n_publish]',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_left) = 3',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_publish) = 2',
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'),
        *define.reach('S','S_capture',0,'V98_DEFINE'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_publish)', 'pconfigcall.SELECTION = (0)',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V98_DEFINE"),POBJECT n_left))',
        '$dynamic_owned_define_header(S,pconfigcall)', '$dynamic_owned_define_valid(S,pconfigcall)',
        'S.STORE[n_left_cv] = DEFINED PNULL',
        'S.STORE[n_value] = DEFINED (POBJECT n_right)',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_publish) = 1',
        '~$destructor_operational(S)', '$test_outputs(S.EVENTS) = ' + term(before),
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*',
        'S_row.USERCONSTANTS = [puserconstant_object]',
        'puserconstant_object.NAME = $ptascii("V98_DEFINE")',
        'puserconstant_object.ORIGIN = pconfigcall.SITE',
        'puserconstant_object.VALUE = POBJECT n_left', 'puserconstant_object.CLASS = PVOBJECT',
        'puserconstant_object.READS = eps', 'puserconstant_object.RECEIVES = eps',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 1',
        '~(HOBJECT n_publish <- S_row.ALLOCATIONS)',
        '$weakref_get(S_row,n_weak) = PNULL',
        'S_row.SELECTEDCALLS = S_capture.SELECTEDCALLS',
        *common.reach('S_query','S_row',0,'V98_DEFINE'), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,$ptascii("V98_DEFINE")) = (POBJECT n_left)',
        *common.step('S_value','S_query','POBJECT n_left'),
        *named('S_second','S_value'),
        'S_second.TODO = (CONFIG_ARGS pconfigcall_second) :: ptask_second*',
        *owned.receipt('S_second','pconfigcall_second','writer',1,0),
        'n_writer = n_left',
        'S_second.SELECTEDCALLS = [pselectedcall_publish,pselectedcall_writer]',
        'pconfigcall_second.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PINT 23))]',
        '$lookup(S_second.ENV,$ptascii("writer")) = (n_writer_cv)',
        'S_second.STORE[n_writer_cv] = DEFINED (POBJECT n_left)',
        '~(HOBJECT n_right <- S_second.ALLOCATIONS)',
        '~(HOBJECT n_publish <- S_second.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_second),HOBJECT n_left) = 3',
        '$test_outputs(S_second.EVENTS) = ' + term(queried),
        *define.reach('S_write','S_second',0,'V98_RESULT'),
        'S_write.TODO = (CONFIG_INVOKE pconfigcall_write) :: ptask_write*',
        'pconfigcall_write.OWNER = (n_left)', 'pconfigcall_write.SELECTION = (1)',
        '$dynamic_define_values(pconfigcall_write) = (($ptascii("V98_RESULT"),PINT 23))',
        '$dynamic_owned_define_valid(S_write,pconfigcall_write)',
        'S_write.STORE[n_writer_cv] = DEFINED pvalue_writer',
        '$string_bytes(pvalue_writer) = ($ptascii("defined"))',
        '$heap_owners($heap_graph(S_write),HOBJECT n_left) = 2',
        '$test_outputs(S_write.EVENTS) = ' + term(queried+b'W|'),
        *common.step('S_written','S_write','PBOOL true'),
        'S_written.TODO = ptask_write*',
        'S_written.USERCONSTANTS = [puserconstant_object,puserconstant_result]',
        'puserconstant_result.NAME = $ptascii("V98_RESULT")',
        'puserconstant_result.ORIGIN = pconfigcall_write.SITE',
        'puserconstant_result.VALUE = PINT 23', 'puserconstant_result.CLASS = PVSCALAR',
        'puserconstant_result.READS = eps', 'puserconstant_result.RECEIVES = eps',
        '$heap_owners($heap_graph(S_written),HOBJECT n_left) = 1',
        *common.reach('S_result','S_written',0,'V98_RESULT'), *common.public('S_result'),
        '$dynamic_global_constant_value(S_result,$ptascii("V98_RESULT")) = (PINT 23)',
        '$selected_entry_source_valid(S_result,pselectedcall_publish)',
        '$selected_entry_source_valid(S_result,pselectedcall_writer)',
        'S_missing = S_result[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$user_constants_valid(S_missing,S_missing.USERCONSTANTS)',
        '$heap_graph(S_missing) = $heap_graph(S_result)',
        '$dynamic_define_value_class(S_missing,POBJECT n_left) = (PVOBJECT)',
        '$dynamic_global_constant_value(S_missing,$ptascii("V98_DEFINE")) = eps',
        *define.finish('S_result',stdout),
        'S_final.USERCONSTANTS = S_written.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall_publish,pselectedcall_writer]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '~(HOBJECT n_publish <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_right <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_pointer <- S_final.ALLOCATIONS)']
    return values


def array(initial, stdout):
    write, has, read = map(text,('write','has','read'))
    raw_items = f'[ENTRY (KSTRING {write}) (ALIAS n_cell),ENTRY (KSTRING {has}) (DIRECT (POBJECT n_has)),ENTRY (KSTRING {read}) (DIRECT (POBJECT n_read))]'
    values = [*initial, *named('S_capture','S_initial'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        *owned.receipt('S_capture','pconfigcall_capture','publish',0,0),
        'S_capture.SELECTEDCALLS = [pselectedcall_publish]',
        'pconfigcall_capture.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_input))]',
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("replacement")) = (n_replacement)',
        '$lookup(S_capture.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S_capture.ENV,$ptascii("raw")) = (n_raw)',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("pointer")) = (n_pointer_cv)',
        '$lookup(S_capture.ENV,$ptascii("oldWeak")) = (n_old_weak_cv)',
        'S_capture.STORE[n_cell] = DEFINED (POBJECT n_old)', 'n_cell <- S_capture.REFCELLS',
        'S_capture.STORE[n_replacement] = DEFINED (POBJECT n_left)',
        'S_capture.STORE[n_input_cv] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_raw] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.STORE[n_pointer_cv] = DEFINED (POBJECT n_pointer)',
        'S_capture.STORE[n_old_weak_cv] = DEFINED (POBJECT n_old_weak)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_publish)',
        'S_capture.OBJECTS[n_pointer] = WEAKREFERENCE (n_left)',
        'S_capture.OBJECTS[n_old_weak] = WEAKREFERENCE (n_old)',
        f'S_capture.ARRAYS[n_input].ITEMS = {raw_items}',
        'S_capture.ARRAYS[n_input].NEXT = 91',
        *intrinsic('S_capture','n_old'), *intrinsic('S_capture','n_left'),
        *intrinsic('S_capture','n_has','INTRINSIC_DEFINED'),
        *intrinsic('S_capture','n_read','INTRINSIC_CONSTANT'),
        *define.reach('S','S_capture',0,'V98_ARRAY'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_publish)', 'pconfigcall.SELECTION = (0)',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V98_ARRAY"),PARRAY n_input))',
        '$dynamic_array_call_valid(S,pconfigcall)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_left)',
        'S.STORE[n_replacement] = DEFINED PNULL',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)',
        'S.ARRAYS[n_caller].ITEMS = [ENTRY (KINT 90) (DIRECT (PINT 31))]',
        'HARRAY n_caller <- $pools_nodes(S.POOLS)',
        'S.ARRAYS[n_input] = S_capture.ARRAYS[n_input]',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        '~(HOBJECT n_old <- S.ALLOCATIONS)', '$weakref_get(S,n_old_weak) = PNULL',
        '$config_nodes(pconfigcall) = [HARRAY n_input,HOBJECT n_publish]',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 1',
        '~$destructor_operational(S)',
        'n_root = |S.ARRAYS|',
        f'parray_root = $array_insert($array_insert($array_insert($array_empty(),KSTRING {write},DIRECT (POBJECT n_left)),KSTRING {has},DIRECT (POBJECT n_has)),KSTRING {read},DIRECT (POBJECT n_read))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {write},PVOBJECT),(KSTRING {has},PVOBJECT),(KSTRING {read},PVOBJECT)])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_copy,PARRAY n_root,pvalueclass_tree))',
        'S_copy.ARRAYS = S.ARRAYS ++ [parray_root]',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.ARRAYS = S_copy.ARRAYS',
        'S_row.USERCONSTANTS = [puserconstant_tree]',
        'puserconstant_tree.NAME = $ptascii("V98_ARRAY")',
        'puserconstant_tree.ORIGIN = pconfigcall.SITE',
        'puserconstant_tree.VALUE = PARRAY n_root', 'puserconstant_tree.CLASS = pvalueclass_tree',
        'puserconstant_tree.READS = eps', 'puserconstant_tree.RECEIVES = eps',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0',
        '$node_children(S_row,HARRAY n_root) = [HOBJECT n_left,HOBJECT n_has,HOBJECT n_read]',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 2',
        '~(HOBJECT n_publish <- S_row.ALLOCATIONS)',
        '$weakref_get(S_row,n_weak) = PNULL',
        *common.reach('S_query','S_row',0,'V98_ARRAY'), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,$ptascii("V98_ARRAY")) = (PARRAY n_root)',
        *common.step('S_value','S_query','PARRAY n_root'),
        *define.reach('S_write','S_value',0,'V98_ARRAY_RESULT'),
        'S_write.TODO = (CONFIG_INVOKE pconfigcall_write) :: ptask_write*',
        *owned.receipt('S_write','pconfigcall_write','writer',1,0),
        'n_writer = n_left',
        'S_write.SELECTEDCALLS = [pselectedcall_publish,pselectedcall_writer]',
        '$dynamic_define_values(pconfigcall_write) = (($ptascii("V98_ARRAY_RESULT"),PINT 17))',
        '$dynamic_owned_define_valid(S_write,pconfigcall_write)',
        '$lookup(S_write.ENV,$ptascii("stored")) = (n_stored)',
        '$lookup(S_write.ENV,$ptascii("again")) = (n_again)',
        'S_write.STORE[n_stored] = DEFINED (PARRAY n_local)', 'n_local =/= n_root',
        'S_write.STORE[n_again] = DEFINED (PARRAY n_root)',
        'S_write.STORE[n_cell] = DEFINED PNULL',
        f'$entry_lookup(S_write.ARRAYS[n_local].ITEMS,KSTRING {write}) = (DIRECT PNULL)',
        '$entry_lookup(S_write.ARRAYS[n_local].ITEMS,KINT 0) = (DIRECT pvalue_local)',
        '$string_bytes(pvalue_local) = ($ptascii("local"))',
        '$entry_lookup(S_write.ARRAYS[n_input].ITEMS,KINT 91) = (DIRECT pvalue_raw)',
        '$string_bytes(pvalue_raw) = ($ptascii("raw"))',
        'S_write.ARRAYS[n_input].NEXT = 92',
        'S_write.ARRAYS[n_root] = parray_root',
        '$heap_owners($heap_graph(S_write),HOBJECT n_left) = 3',
        *common.step('S_written','S_write','PBOOL true'),
        'S_written.TODO = ptask_write*',
        'S_written.USERCONSTANTS = [puserconstant_tree,puserconstant_result]',
        'puserconstant_result.NAME = $ptascii("V98_ARRAY_RESULT")',
        'puserconstant_result.ORIGIN = pconfigcall_write.SITE',
        'puserconstant_result.VALUE = PINT 17', 'puserconstant_result.CLASS = PVSCALAR',
        'puserconstant_result.READS = eps', 'puserconstant_result.RECEIVES = eps',
        *define.finish('S_written',stdout),
        'S_final.USERCONSTANTS = S_written.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall_publish,pselectedcall_writer]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        'S_final.ARRAYS[n_root] = parray_root',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_has) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_read) = 1',
        '~(HOBJECT n_old <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_publish <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_local <- S_final.ALLOCATIONS)',
        'HARRAY n_caller <- $pools_nodes(S_final.POOLS)',
        'HARRAY n_caller <- S_final.ALLOCATIONS',
        '$heap_owners($heap_graph(S_final),HARRAY n_caller) = 1']
    return values


def checks(initial, name, stdout):
    return (direct if name == DIRECT else array)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 420
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
