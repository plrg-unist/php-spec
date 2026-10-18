#!/usr/bin/env python3
"""Independent byte-only copies, genuine carrier checks and abrupt retirement."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_literal_string_array_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V72_REVIEW_OLD'
PREFIX = define.PREFIX + r'''
dec $test_literal_string_peer_front(pstate, nat) : bool
def $test_literal_string_peer_front(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V72_REVIEW_OLD"),pvalue))
def $test_literal_string_peer_front(S,1) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V72_REVIEW_OLD"),pvalue))
def $test_literal_string_peer_front(S,2) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_bucket) metadata_variable) :: expression_tail*
  -- if $base64(text_bucket) = $ptascii("bucket")
  -- if $lookup(S.ENV,$ptascii("bucket")) = (n_bucket)
def $test_literal_string_peer_front(S,n_phase) = false -- otherwise
dec $test_literal_string_peer_seek(pstate, nat, nat) : pstate
def $test_literal_string_peer_seek(S,n_phase,0) = S
def $test_literal_string_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_literal_string_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_literal_string_peer_seek(S,n_phase,n) = $test_literal_string_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_literal_string_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_literal_string_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_literal_string_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|2|E|V72_STOP|define|false|old|bytes|request|changed|kept-cvs|17|31|kept|A|'
    key = {name: 'KSTRING ' + text(name) for name in
           ('head', 'again', 'request', 'word', 'binary', 'empty', 'one')}
    old_bytes, next_bytes = term(b'O\0\xff'), term(b'N\0\x80')
    old_items = f'[ENTRY ({key["word"]}) (DIRECT (PSTRING {text("old")})),ENTRY ({key["binary"]}) (DIRECT (PSTRING {old_bytes})),ENTRY ({key["empty"]}) (DIRECT (PSTRING eps))]'
    next_items = f'[ENTRY ({key["word"]}) (DIRECT (PSTRING {text("next")})),ENTRY ({key["binary"]}) (DIRECT (PSTRING {next_bytes})),ENTRY ({key["one"]}) (DIRECT (PSTRING {text("x")}))]'
    input_items = f'[ENTRY ({key["head"]}) (ALIAS n_cell),ENTRY ({key["again"]}) (ALIAS n_cell),ENTRY ({key["request"]}) (DIRECT pvalue_request)]'
    values = [*initial, *define.reach('S', 'S_initial', 1, TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL false))]',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        'S.USERCONSTANTS = [puserconstant_old]',
        'puserconstant_old.NAME = ' + text(TARGET),
        'puserconstant_old.VALUE = PINT 17', 'n_constants = 1',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        '$lookup(S.ENV,$ptascii("old")) = (n_old_cell)',
        'S.STORE[n_old_cell] = DEFINED (PARRAY n_old)',
        '$lookup(S.ENV,$ptascii("next")) = (n_next_cell)',
        'S.STORE[n_next_cell] = DEFINED (PARRAY n_next)',
        'n_old =/= n_next',
        'parray_old = S.ARRAYS[n_old]', 'parray_old.ITEMS = ' + old_items,
        'parray_next = S.ARRAYS[n_next]', 'parray_next.ITEMS = ' + next_items,
        'HARRAY n_old <- $pools_nodes(S.POOLS)',
        'HARRAY n_next <- $pools_nodes(S.POOLS)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        'n_cell <- S.REFCELLS', 'S.STORE[n_cell] = DEFINED (PARRAY n_next)',
        '$lookup(S.ENV,$ptascii("request")) = (n_request_cell)',
        'S.STORE[n_request_cell] = DEFINED pvalue_request',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("req-leaf"))',
        '$string_carrier_valid(S,pvalue_request)',
        'S.ARRAYS[n_input].ITEMS = ' + input_items,
        '$dynamic_array_value(S,PARRAY n_input,eps,false) = eps',
        # Raw leaves are byte-only values. No string identity is manufactured.
        f'$dynamic_array_value(S,PSTRING {next_bytes},eps,true) = ((S,PSTRING {next_bytes},PVSTRING false))',
        f'$dynamic_array_value(S,PSTRING {next_bytes},eps,false) = ((S,PSTRING {next_bytes},PVSTRING false))',
        f'$dynamic_constant_class(PSTRING {next_bytes}) = eps',
        f'$dynamic_define_value_class(S,PSTRING {next_bytes}) = eps',
        '$dynamic_array_value(S,PSTRING ([256]),eps,true) = eps',
        '$dynamic_array_value(S,PSTRING ([256]),eps,false) = eps',
        'n_before = |S.ARRAYS|',
        *common.step('S_dispatch', 'S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants',
        '$error_call_valid(S_dispatch,perrorcall)',
        'n_head_copy = n_before', 'n_again_copy = $(n_before + 1)',
        'n_candidate = $(n_before + 2)', 'n_head_copy =/= n_again_copy',
        f'parray_root = $array_insert($array_insert($array_insert($array_empty(),{key["head"]},DIRECT (PARRAY n_head_copy)),{key["again"]},DIRECT (PARRAY n_again_copy)),{key["request"]},DIRECT pvalue_request)',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_next,parray_next,parray_root]',
        f'pvalueclass_child = PVARRAY false ([({key["word"]},PVSTRING false),({key["binary"]},PVSTRING false),({key["one"]},PVSTRING false)])',
        f'pvalueclass = PVARRAY false ([({key["head"]},pvalueclass_child),({key["again"]},pvalueclass_child),({key["request"]},PVSTRING false)])',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,n_constants)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate,HARRAY n_input]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.STRINGDATA = S.STRINGDATA',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_head_copy) = 1',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_again_copy) = 1',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_input) = 2',
        # Pure changed states test validator rejection and are never driven.
        f'pvalueclass_bad_child = $pvclass_put(pvalueclass_child,{key["binary"]},PVSTRING true)',
        f'pvalueclass_bad = $pvclass_put(pvalueclass,{key["head"]},pvalueclass_bad_child)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass_bad,n_constants)',
        f'S_bad_byte = S_dispatch[.ARRAYS[n_head_copy].ITEMS = [ENTRY ({key["word"]}) (DIRECT (PSTRING {text("next")})),ENTRY ({key["binary"]}) (DIRECT (PSTRING ([256]))),ENTRY ({key["one"]}) (DIRECT (PSTRING {text("x")}))]]',
        '~$dynamic_array_duplicate_valid(S_bad_byte,pconfigcall,n_candidate,pvalueclass,n_constants)',
        'pvalue_bad_carrier = PSTRING_CARRIER (REQUEST_STRING (|S_dispatch.STRINGDATA|)) ($ptascii("req-leaf"))',
        '~$string_carrier_valid(S_dispatch,pvalue_bad_carrier)',
        '$dynamic_array_value(S_dispatch,pvalue_bad_carrier,eps,false) = eps',
        f'S_bad_carrier = S_dispatch[.ARRAYS[n_candidate].ITEMS = [ENTRY ({key["head"]}) (DIRECT (PARRAY n_head_copy)),ENTRY ({key["again"]}) (DIRECT (PARRAY n_again_copy)),ENTRY ({key["request"]}) (DIRECT pvalue_bad_carrier)]]',
        '~$dynamic_array_duplicate_valid(S_bad_carrier,pconfigcall,n_candidate,pvalueclass,n_constants)',
        *reach('S_entered', 'S_dispatch', 0), *reach('S_throw', 'S_entered', 1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_old)',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_throw.ARRAYS[n_head_copy] = parray_next',
        'S_throw.ARRAYS[n_again_copy] = parray_next',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_candidate,pvalueclass,n_constants)',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_trace_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_trace_args))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V72_REVIEW_SIDE")) = (puserconstant_side)',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_side]',
        'puserconstant_side.VALUE = PINT 31',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 3',
        *common.step('S_after', 'S_throw'), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 2',
        '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '~(HARRAY n_head_copy <- S_after.ALLOCATIONS)',
        '~(HARRAY n_again_copy <- S_after.ALLOCATIONS)',
        *reach('S_bucket', 'S_after', 2),
        '$lookup(S_bucket.ENV,$ptascii("bucket")) = (n_bucket)',
        'n_bucket =/= n_cell', 'n_bucket <- S_bucket.REFCELLS',
        'S_bucket.STORE[n_cell] = DEFINED (PARRAY n_written)',
        'n_written =/= n_old', 'n_written =/= n_next',
        f'$entry_lookup(S_bucket.ARRAYS[n_written].ITEMS,{key["binary"]}) = (ALIAS n_bucket)',
        'S_bucket.STORE[n_bucket] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        'S_bucket.ARRAYS[n_input].ITEMS = ' + input_items,
        'S_bucket.ARRAYS[n_old] = parray_old', 'S_bucket.ARRAYS[n_next] = parray_next',
        'S_bucket.STORE[n_old_cell] = DEFINED (PARRAY n_old)',
        'S_bucket.STORE[n_next_cell] = DEFINED (PARRAY n_next)',
        *define.finish('S_bucket', stdout), 'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_written <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HCELL n_bucket <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        'HARRAY n_old <- S_final.ALLOCATIONS', 'HARRAY n_next <- S_final.ALLOCATIONS',
        'HARRAY n_old <- $pools_nodes(S_final.POOLS)',
        'HARRAY n_next <- $pools_nodes(S_final.POOLS)',
        'S_final.ARRAYS[n_old] = parray_old', 'S_final.ARRAYS[n_next] = parray_next']
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
