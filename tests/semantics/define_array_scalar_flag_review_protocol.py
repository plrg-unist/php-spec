#!/usr/bin/env python3
"""Raw flag identity, pending duplicate copies and real trace-bucket aliases."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_array_scalar_flag_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
TARGET = 'V76_REVIEW_ROW'
PREFIX = define.PREFIX + r'''
dec $test_array_scalar_peer_front(pstate, nat) : bool
def $test_array_scalar_peer_front(S,0) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V76_REVIEW_ROW"),pvalue))
def $test_array_scalar_peer_front(S,1) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_bucket) metadata_variable) :: expression_tail*
  -- if $base64(text_bucket) = $ptascii("bucket")
  -- if $lookup(S.ENV,$ptascii("bucket")) = (n_cell)
def $test_array_scalar_peer_front(S,2) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_raw) metadata_variable) :: expression_tail*
  -- if $base64(text_raw) = $ptascii("raw")
def $test_array_scalar_peer_front(S,n_phase) = false -- otherwise
dec $test_array_scalar_peer_seek(pstate, nat, nat) : pstate
def $test_array_scalar_peer_seek(S,n_phase,0) = S
def $test_array_scalar_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_array_scalar_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_scalar_peer_seek(S,n_phase,n) = $test_array_scalar_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_scalar_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_array_scalar_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_scalar_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|1|2|E|V76_PENDING|define|raw|zero|constant|23|split|caller|17|31|1|kept|41|41|history|A|'
    edge, tag = text('edge'), text('tag')
    items = f'[ENTRY (KSTRING {edge}) (ALIAS n_cell)]'
    values = [*initial, *define.reach('S', 'S_initial', 0, TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN pvalue_flag)',
        'pvalue_flag = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("false"))',
        '$string_carrier_valid(S,pvalue_flag)',
        '$dynamic_scalar_define_flag_call(pconfigcall)',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall)',
        '$dynamic_scalar_define_flag_case_valid(S,pconfigcall)',
        '~$dynamic_constant_case_valid(S,pconfigcall)',
        '$dynamic_array_call_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$truth(S,pvalue_flag)', '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (false)',
        'S.USERCONSTANTS = eps',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S.ARRAYS[n_input].ITEMS = ' + items, 'S.ARRAYS[n_input].NEXT = 91',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)', 'S.STORE[n_flag] = DEFINED pvalue_flag',
        '$lookup(S.ENV,$ptascii("stage")) = (n_stage)', 'S.STORE[n_stage] = DEFINED (PINT 0)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("define"))',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 2',
        # Pure header controls; none of these projections is driven.
        'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_flag = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("false"))',
        'pconfigcall_bad = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN pvalue_bad_flag)]',
        '$dynamic_scalar_define_flag_call(pconfigcall_bad)',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_bad)',
        '~$dynamic_array_call_valid(S,pconfigcall_bad)',
        'S_dead_input = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '~$dynamic_scalar_define_flag_valid(S_dead_input,pconfigcall)',
        *common.step('S_dispatch', 'S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $dynamic_constant_case_message()',
        'perrorcall.LINE = pconfigcall.LINE', '$error_call_valid(S_dispatch,perrorcall)',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS', 'S_dispatch.STORE = S.STORE',
        '$task_nodes(perrorcall.RESUME) = $config_nodes(pconfigcall)',
        *reach('S_throw', 'S_dispatch', 0),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_after*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V76_PENDING"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT pvalue_flag)',
        '$string_carrier_valid(S_throw,pvalue_flag)',
        'S_throw.STORE[n_flag] = DEFINED pvalue_live_flag',
        '$string_bytes(pvalue_live_flag) = ($ptascii("0"))', '~$truth(S_throw,pvalue_live_flag)',
        'S_throw.STORE[n_api] = DEFINED pvalue_api_after',
        '$string_bytes(pvalue_api_after) = ($ptascii("constant"))',
        'S_throw.STORE[n_stage] = DEFINED (PINT 1)',
        'S_throw.STORE[n_result] = DEFINED pvalue_sentinel',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_leaf23)',
        f'S_throw.ARRAYS[n_leaf23].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 23))]',
        'S_throw.STORE[n_input_cell] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '$entry_lookup(S_throw.ARRAYS[n_caller].ITEMS,KSTRING ' + edge + ') = (ALIAS n_cell)',
        '$entry_lookup(S_throw.ARRAYS[n_caller].ITEMS,KINT 90) = (DIRECT pvalue_caller)',
        '$string_bytes(pvalue_caller) = ($ptascii("caller"))',
        '$user_constant_at(S_throw.USERCONSTANTS,' + text(TARGET) + ') = (puserconstant_old)',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V76_REVIEW_SIDE")) = (puserconstant_side)',
        'S_throw.USERCONSTANTS = [puserconstant_old,puserconstant_side]',
        'puserconstant_old.VALUE = PINT 17', 'puserconstant_side.VALUE = PINT 31',
        '$dynamic_scalar_define_flag_case_valid(S_throw,pconfigcall)',
        '$dynamic_array_call_valid(S_throw,pconfigcall)',
        'n_constants = |S_throw.USERCONSTANTS|',
        '~$dynamic_scalar_define_flag_duplicate_valid(S_throw,pconfigcall,n_constants)',
        '$dynamic_array_duplicate_call_valid(S_throw,pconfigcall,n_constants)',
        # A pure copy/marker check also covers the shared normal duplicate route.
        '$dynamic_array_value(S_throw,PARRAY n_input,eps,true) = ((S_validation,PARRAY n_validation,pvalueclass_validation))',
        '$dynamic_array_duplicate_valid(S_validation,pconfigcall,n_validation,pvalueclass_validation,n_constants)',
        '$call_task_valid(S_validation,DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_validation pvalueclass_validation n_constants)',
        '$dynamic_array_recursive(S_throw,PARRAY n_input,eps) = (false)',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 2',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_throw).EDGES,[HARRAY n_input,HARRAY n_caller]) = 2',
        '~$destructor_operational(S_throw)',
        # Pending guards and cycle branch are pure projections, never driven.
        'S_no_pending = S_throw[.TODO = eps]',
        'S_no_pending_after = $dynamic_scalar_define_flag_pending(S_no_pending,pconfigcall)',
        'S_no_pending_after.COMPLETION = UNSUPPORTED "scalar define flag pending-exception registration"',
        'S_dead = S_throw[.ALLOCATIONS = $destruction_node_delete(S_throw.ALLOCATIONS,HOBJECT n_error)]',
        'S_dead_after = $dynamic_scalar_define_flag_pending(S_dead,pconfigcall)',
        'S_dead_after.COMPLETION = UNSUPPORTED "scalar define flag pending-exception registration"',
        'S_missing = S_throw[.STORE[n_cell] = UNDEFINED]',
        '$dynamic_array_recursive(S_missing,PARRAY n_input,eps) = eps',
        'S_missing_after = $dynamic_scalar_define_flag_pending(S_missing,pconfigcall)',
        'S_missing_after.COMPLETION = UNSUPPORTED "scalar define flag pending-exception registration"',
        'pconfigcall_zero = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PINT 0))]',
        '$dynamic_scalar_define_flag_valid(S_throw,pconfigcall_zero)',
        '~$dynamic_scalar_define_flag_case_valid(S_throw,pconfigcall_zero)',
        'S_zero_after = $dynamic_scalar_define_flag_pending(S_throw,pconfigcall_zero)',
        'S_zero_after.COMPLETION = UNSUPPORTED "scalar define flag pending-exception registration"',
        'S_cycle = S_throw[.STORE[n_cell] = DEFINED (PARRAY n_input)]',
        '$dynamic_array_recursive(S_cycle,PARRAY n_input,eps) = (true)',
        '$dynamic_scalar_define_flag_pending(S_cycle,pconfigcall) = S_cycle',
        'n_before = |S_throw.ARRAYS|',
        *common.step('S_after', 'S_throw'), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.RESULT = S_throw.RESULT', 'S_after.OBJECTS = S_throw.OBJECTS',
        'S_after.OBJECTTABLES = S_throw.OBJECTTABLES', 'S_after.OBJECTPROPS = S_throw.OBJECTPROPS',
        'S_after.STORE = S_throw.STORE', 'S_after.EVENTS = S_throw.EVENTS',
        'S_after.USERCONSTANTS = S_throw.USERCONSTANTS', 'S_after.ALLOCATIONS = S_throw.ALLOCATIONS',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_throw.CALLBACK)',
        '$throwable_field(S_after,n_error,"previous") = PNULL',
        'n_child = n_before', 'n_candidate = $(n_before + 1)',
        f'parray_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 23))',
        f'parray_candidate = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
        'S_after.ARRAYS = S_throw.ARRAYS ++ [parray_child,parray_candidate]',
        '~(HARRAY n_child <- S_after.ALLOCATIONS)', '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 1',
        '$error_handler_eligible(S_after,2)',
        *reach('S_bucket', 'S_after', 1),
        '$lookup(S_bucket.ENV,$ptascii("bucket")) = (n_cell)',
        '$lookup(S_bucket.ENV,$ptascii("raw")) = (n_raw_cell)',
        'S_bucket.STORE[n_raw_cell] = DEFINED (PARRAY n_raw)', 'n_raw =/= n_input',
        'S_bucket.ARRAYS[n_raw].ITEMS = ' + items, 'S_bucket.ARRAYS[n_raw].NEXT = 91',
        'S_bucket.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_bucket.STORE[n_input_cell] = DEFINED (PARRAY n_caller)',
        'S_bucket.STORE[n_cell] = DEFINED (PARRAY n_leaf41)',
        f'S_bucket.ARRAYS[n_leaf41].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 41))]',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_bucket).EDGES,[HARRAY n_input,HARRAY n_caller,HARRAY n_raw]) = 3',
        '$entry_lookup(S_bucket.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT pvalue_flag)',
        *reach('S_history', 'S_bucket', 2),
        'S_history.STORE[n_raw_cell] = DEFINED (PARRAY n_history)',
        '$entry_lookup(S_history.ARRAYS[n_history].ITEMS,KINT 91) = (DIRECT pvalue_history)',
        '$string_bytes(pvalue_history) = ($ptascii("trace"))',
        'S_history.ARRAYS[n_history].NEXT = 92',
        '$entry_lookup(S_history.ARRAYS[n_history].ITEMS,KSTRING ' + edge + ') = (ALIAS n_cell)',
        'S_history.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_history.USERCONSTANTS = S_throw.USERCONSTANTS',
        *define.finish('S_history', stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_history <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)', '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)', '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
        '~(HARRAY n_child <- S_final.ALLOCATIONS)', '~(HARRAY n_candidate <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
