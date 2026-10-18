#!/usr/bin/env python3
"""Reached raw string capture, pending fresh copy and real query-reference COW."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_array_byte_flag_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
TARGET = 'V78_REVIEW_PENDING'
PREFIX = define.PREFIX + r'''
dec $test_array_byte_peer_front(pstate, nat) : bool
def $test_array_byte_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 1
  -- if $named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PSTRING ($ptascii("false"))))
def $test_array_byte_peer_front(S,1) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V78_REVIEW_PENDING"),PARRAY n_input))
def $test_array_byte_peer_front(S,2) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_bucket) metadata_variable) :: expression_tail*
  -- if $base64(text_bucket) = $ptascii("bucket")
  -- if $lookup(S.ENV,$ptascii("bucket")) = (n_cell)
def $test_array_byte_peer_front(S,3) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_raw) metadata_variable) :: expression_tail*
  -- if $base64(text_raw) = $ptascii("raw")
def $test_array_byte_peer_front(S,n_phase) = false -- otherwise
dec $test_array_byte_peer_seek(pstate, nat, nat) : pstate
def $test_array_byte_peer_seek(S,n_phase,0) = S
def $test_array_byte_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_array_byte_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_byte_peer_seek(S,n_phase,n) = $test_array_byte_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_byte_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_array_byte_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_byte_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|1|2|E|V78_PENDING|none|define|raw|empty|saved|defined|kept|31|23|split|23|caller|41|23|53|23|zero|history|A|'
    edge, tag = text('edge'), text('tag')
    items = f'[ENTRY (KSTRING {edge}) (ALIAS n_cell)]'
    values = [*initial, *reach('S_capture', 'S_initial', 0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.INDEX = 1', 'pconfigcall_capture.SELECTION = (n_selection)',
        'S_capture.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$named_slot_at(pconfigcall_capture.SENT,0) = NAMED_HOLE',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_HOLE',
        '$named_slot_at(pconfigcall_capture.SENT,2) = NAMED_SENT (KNOWN pvalue_raw)',
        'pvalue_raw = PSTRING ($ptascii("false"))',
        '$dynamic_constant_class(pvalue_raw) = eps', '$value_nodes(pvalue_raw) = eps',
        '$lookup(S_capture.ENV,$ptascii("flags")) = (n_flags_cell)',
        '$lookup(S_capture.ENV,$ptascii("savedFlags")) = (n_saved_cell)',
        'S_capture.STORE[n_flags_cell] = DEFINED (PARRAY n_pool)',
        'S_capture.STORE[n_saved_cell] = DEFINED (PARRAY n_pool)',
        'parray_flags = S_capture.ARRAYS[n_pool]',
        '$entry_lookup(parray_flags.ITEMS,KINT 0) = (DIRECT (PSTRING ($ptascii("0"))))',
        '$entry_lookup(parray_flags.ITEMS,KINT 1) = (DIRECT pvalue_raw)',
        '$entry_lookup(parray_flags.ITEMS,KINT 2) = (DIRECT (PSTRING eps))',
        'HARRAY n_pool <- $pools_nodes(S_capture.POOLS)',
        *define.reach('S', 'S_capture', 0, TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = pconfigcall_capture.SITE',
        'pconfigcall.SELECTION = pconfigcall_capture.SELECTION',
        '$dynamic_scalar_define_flag_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input,pvalue_raw))',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall)',
        '$dynamic_scalar_define_flag_case_valid(S,pconfigcall)',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$call_task_valid(S,DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall)',
        '~$dynamic_constant_case_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$dynamic_array_quiet_flag(pvalue_raw)', '$truth(S,pvalue_raw)',
        '$dynamic_array_quiet_flag(PSTRING eps)',
        '$dynamic_array_quiet_flag(PSTRING ($ptascii("0")))',
        '~$dynamic_array_quiet_flag(PSTRING ([256]))',
        'S.STORE[n_flags_cell] = DEFINED (PARRAY n_flags)', 'n_flags =/= n_pool',
        '$entry_lookup(S.ARRAYS[n_flags].ITEMS,KINT 1) = (DIRECT pvalue_zero)',
        '$string_bytes(pvalue_zero) = ($ptascii("0"))',
        'S.STORE[n_saved_cell] = DEFINED (PARRAY n_pool)', 'S.ARRAYS[n_pool] = parray_flags',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S.ARRAYS[n_input].ITEMS = ' + items, 'S.ARRAYS[n_input].NEXT = 91',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 2',
        'S.USERCONSTANTS = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        # Malformed raw bytes remain outside the header; no projection is driven.
        'pconfigcall_bad = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PSTRING ([256])))]',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_bad)',
        '~$dynamic_array_call_valid(S,pconfigcall_bad)',
        '~$call_task_valid(S,DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_bad)',
        *common.step('S_dispatch', 'S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $dynamic_constant_case_message()',
        '$error_call_valid(S_dispatch,perrorcall)',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        *reach('S_throw', 'S_dispatch', 1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_after*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V78_PENDING"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT pvalue_raw)',
        'S_throw.STORE[n_flags_cell] = DEFINED (PARRAY n_flags)',
        '$entry_lookup(S_throw.ARRAYS[n_flags].ITEMS,KINT 1) = (DIRECT pvalue_empty)',
        '$string_bytes(pvalue_empty) = (eps)',
        'S_throw.STORE[n_saved_cell] = DEFINED (PARRAY n_pool)',
        'S_throw.ARRAYS[n_pool] = parray_flags',
        'S_throw.STORE[n_result] = DEFINED pvalue_sentinel',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_leaf23)',
        f'S_throw.ARRAYS[n_leaf23].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 23))]',
        'S_throw.STORE[n_input_cell] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '$entry_lookup(S_throw.ARRAYS[n_caller].ITEMS,KSTRING ' + edge + ') = (ALIAS n_cell)',
        '$entry_lookup(S_throw.ARRAYS[n_caller].ITEMS,KINT 90) = (DIRECT pvalue_caller)',
        '$string_bytes(pvalue_caller) = ($ptascii("caller"))',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V78_REVIEW_SIDE")) = (puserconstant_side)',
        'S_throw.USERCONSTANTS = [puserconstant_side]', 'puserconstant_side.VALUE = PINT 31',
        '$source_constant_lookup(S_throw,' + text(TARGET) + ') = eps',
        '$dynamic_scalar_define_flag_case_valid(S_throw,pconfigcall)',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 2',
        '~$destructor_operational(S_throw)',
        'n_child = |S_throw.ARRAYS|', 'n_root = $(n_child + 1)',
        f'parray_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 23))',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
        *common.step('S_after', 'S_throw'), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.RESULT = S_throw.RESULT', 'S_after.STORE = S_throw.STORE',
        'S_after.OBJECTS = S_throw.OBJECTS', 'S_after.EVENTS = S_throw.EVENTS',
        'S_after.ARRAYS = S_throw.ARRAYS ++ [parray_child,parray_root]',
        '$user_constant_at(S_after.USERCONSTANTS,' + text(TARGET) + ') = (puserconstant_target)',
        'S_after.USERCONSTANTS = S_throw.USERCONSTANTS ++ [puserconstant_target]',
        'puserconstant_target.VALUE = PARRAY n_root', 'puserconstant_target.ORIGIN = pconfigcall.SITE',
        f'puserconstant_target.CLASS = PVARRAY false ([(KSTRING {edge},PVARRAY false ([(KSTRING {tag},PVSCALAR)]))])',
        'puserconstant_target.READS = eps', 'puserconstant_target.RECEIVES = eps',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_throw.CALLBACK)',
        '$heap_owners($heap_graph(S_after),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_after),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 1',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_after).EDGES,[HARRAY n_input,HARRAY n_caller]) = 2',
        '$throwable_field(S_after,n_error,"previous") = PNULL',
        *common.reach('S_query', 'S_after', 0, TARGET), *common.public('S_query'),
        'n_query_owners = $heap_owners($heap_graph(S_query),HARRAY n_root)',
        *common.step('S_value', 'S_query', 'PARRAY n_root'), *common.public('S_value'),
        'S_value.ARRAYS = S_query.ARRAYS', 'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
        '$heap_owners($heap_graph(S_value),HARRAY n_root) = $(n_query_owners + 1)',
        *reach('S_bucket', 'S_value', 2),
        '$lookup(S_bucket.ENV,$ptascii("bucket")) = (n_bucket_cell)', 'n_bucket_cell =/= n_cell',
        '$lookup(S_bucket.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_bucket.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_root',
        f'S_bucket.ARRAYS[n_copy].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_bucket_cell)]',
        'S_bucket.ARRAYS[n_copy].NEXT = parray_root.NEXT',
        '$array_append_key(S_bucket.ARRAYS[n_copy]) = KINT 0',
        'S_bucket.STORE[n_bucket_cell] = DEFINED (PARRAY n_copy_child)', 'n_copy_child =/= n_child',
        f'S_bucket.ARRAYS[n_copy_child].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 53))]',
        'S_bucket.ARRAYS[n_root] = parray_root', 'S_bucket.ARRAYS[n_child] = parray_child',
        'S_bucket.STORE[n_cell] = DEFINED (PARRAY n_leaf41)',
        f'S_bucket.ARRAYS[n_leaf41].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 41))]',
        'S_bucket.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '$entry_lookup(S_bucket.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT pvalue_raw)',
        *reach('S_history', 'S_bucket', 3),
        '$entry_lookup(S_history.ARRAYS[n_copy].ITEMS,KINT 0) = (DIRECT pvalue_query)',
        '$string_bytes(pvalue_query) = ($ptascii("query"))',
        'S_history.ARRAYS[n_copy].NEXT = 1',
        '$lookup(S_history.ENV,$ptascii("view")) = (n_view_cell)',
        'S_history.STORE[n_view_cell] = DEFINED (PARRAY n_view)', 'n_view =/= n_input',
        '$entry_lookup(S_history.ARRAYS[n_view].ITEMS,KINT 91) = (DIRECT pvalue_history)',
        '$string_bytes(pvalue_history) = ($ptascii("trace"))', 'S_history.ARRAYS[n_view].NEXT = 92',
        '$entry_lookup(S_history.ARRAYS[n_view].ITEMS,KSTRING ' + edge + ') = (ALIAS n_cell)',
        'S_history.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_history.ARRAYS[n_root] = parray_root', 'S_history.ARRAYS[n_child] = parray_child',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_history).EDGES,[HARRAY n_input,HARRAY n_caller,HARRAY n_view]) = 3',
        *define.finish('S_history', stdout),
        'S_final.USERCONSTANTS = S_after.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        'S_final.ARRAYS[n_pool] = parray_flags',
        'HARRAY n_pool <- $pools_nodes(S_final.POOLS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_view <- S_final.ALLOCATIONS)', '~(HARRAY n_copy <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy_child <- S_final.ALLOCATIONS)', '~(HCELL n_bucket_cell <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)', '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)', '~(HARRAY n_args <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == 'raw-string-flag-capture-and-pending-fresh-snapshot':
        timeout = 150
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
