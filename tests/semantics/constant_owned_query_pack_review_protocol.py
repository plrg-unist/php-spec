#!/usr/bin/env python3
"""Named unpack delivers a scalar snapshot without rooting its retired ARRAY."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_query_pack_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_query_pack_peer_unset(pstate, preqbytes) : bool
def $test_query_pack_peer_unset(S,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = preqbytes
def $test_query_pack_peer_unset(S,preqbytes) = false -- otherwise
dec $test_query_pack_peer_front(pstate, nat) : bool
def $test_query_pack_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps /\ pconfigcall.INDEX = 0
  -- if $config_method_receiver(S,pconfigcall)
def $test_query_pack_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
def $test_query_pack_peer_front(S,2) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.PACKS =/= eps
def $test_query_pack_peer_front(S,3) = $test_query_pack_peer_unset(S,$ptascii("error"))
def $test_query_pack_peer_front(S,4) = $test_query_pack_peer_unset(S,$ptascii("rawApi"))
def $test_query_pack_peer_front(S,5) = $test_query_pack_peer_unset(S,$ptascii("rawInvoke"))
def $test_query_pack_peer_front(S,6) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps /\ pconfigcall.PACKS = eps
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("V106_REVIEW_RECOVERY"))
def $test_query_pack_peer_front(S,n_phase) = false -- otherwise
dec $test_query_pack_peer_seek(pstate, nat, nat) : pstate
def $test_query_pack_peer_seek(S,n_phase,0) = S
def $test_query_pack_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_query_pack_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_pack_peer_seek(S,n_phase,n) = $test_query_pack_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_pack_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_query_pack_peer_settled(pstate) : bool
def $test_query_pack_peer_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_query_pack_peer_user_entry(pstate) : bool
def $test_query_pack_peer_user_entry(S) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_query_pack_peer_user_entry(S) = false -- otherwise
dec $test_query_pack_peer_settle(pstate, nat) : pstate
def $test_query_pack_peer_settle(S,0) = S
def $test_query_pack_peer_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_query_pack_peer_settled(S) \/ $test_query_pack_peer_user_entry(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_pack_peer_settle(S,n) = $test_query_pack_peer_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_pack_peer_settled(S) /\ ~$test_query_pack_peer_user_entry(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_query_pack_peer_seek({start},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_query_pack_peer_front({state},{phase})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def settle(state, start):
    return [f'{state}_found = $test_query_pack_peer_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_query_pack_peer_settled({state})', *common.public(state)]


def replay(state):
    return [f'$config_source_replay({state},pconfigcall,pconfigcall[.INDEX = 0][.SENT = eps][.NAMED = false][.PACKS = eps],pconfigcall.PACKS) = ((pconfigcall[.PACKS = eps],eps))']


def controls():
    # These projections check authority/history, not additional source execution.
    values = ['S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_callee)]',
        '~$dynamic_owned_global_query_valid(S_dead,pconfigcall)',
        'S_wrong = S[.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_DEFINED]',
        '~$dynamic_owned_global_query_valid(S_wrong,pconfigcall)',
        'S_bad_string = S[.STRINGDATA[n_string] = $ptascii("wrong")]',
        '~$dynamic_owned_global_query_valid(S_bad_string,pconfigcall)']
    for change in ['.OWNER = eps','.OWNER = (|S.OBJECTS|)','.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE','.KIND = INTRINSIC_DEFINED','.INDEX = 0',
            '.SITE = PORIGIN 0 eps','.LINE = $(pconfigcall.LINE + 1)',
            '.NAMED = false','.PACKS = eps','.PACKS = pconfigcall.PACKS ++ pconfigcall.PACKS',
            '.SENT = eps','.SENT = pconfigcall.SENT ++ pconfigcall.SENT']:
        values += [f'~$dynamic_owned_global_query_valid(S,pconfigcall[{change}])']
    for change in ['.INDEX = 1','.ARRAY = (|S.ARRAYS|)','.SITE = PORIGIN 0 eps',
            '.LINE = $(pconfigpack.LINE + 1)','.ITEMS = eps',
            '.ITEMS = pconfigpack.ITEMS ++ pconfigpack.ITEMS',
            '.ITEMS = [ENTRY (KSTRING $ptascii("name")) (ALIAS n_cell)]',
            '.ITEMS = [ENTRY (KSTRING $ptascii("constant_name")) (DIRECT pvalue_name)]',
            '.ITEMS = [ENTRY (KINT 9) (DIRECT pvalue_name)]']:
        values += [f'~$dynamic_owned_global_query_valid(S,pconfigcall[.PACKS = [pconfigpack[{change}]]])']
    for index,value in enumerate(['PSTRING ($ptascii("A::B"))',
            'PSTRING ($ptascii("__COMPILER_HALT_OFFSET__"))','PSTRING ([65,0,66])','PINT 0']):
        values += [f'pconfigpack_bad_{index} = pconfigpack[.ITEMS = [ENTRY (KSTRING $ptascii("name")) (DIRECT ({value}))]]',
            f'~$dynamic_owned_global_query_valid(S,pconfigcall[.PACKS = [pconfigpack_bad_{index}]][.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += ['~$config_ini_pack_known(S,pconfigpack.ITEMS,(PINT 0))',
        'S_history = S[.ARRAYS[n_pack].ITEMS = [ENTRY (KSTRING $ptascii("name")) (DIRECT (PINT 88))]]',
        '$config_invoke_valid(S_history,pconfigcall)',
        '$dynamic_owned_global_query_valid(S_history,pconfigcall)']
    return values


def checks(initial, stdout):
    before = b'B|P|calleeHeld|'
    error_text = b'Undefined constant "V106_REVIEW_MISSING"'
    caught = before + b'E|' + error_text + (b'|25|none|constant|apiFile|25|api0|__invoke|Closure|->|'
        b'invokeFile|25|invoke0|end|currentNull|calleeGone|97|1|apiKept|invokeKept|changed-after-pack|')
    raw_api = caught + b'apiHeld|'
    raw_invoke = raw_api + b'invokeHeld|'
    assert stdout == raw_invoke + b'23|A|'
    values = [*initial,'S_initial.COMPLETION = BUDGET',*reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_callee)','pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.PACKS = eps','pconfigcall_capture.SENT = eps',
        'S_capture.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in ['call','pack','weakCall','result','effects']],
        '$lookup(S_capture.ENV,$ptascii("target")) = (n_cell)',
        'S_capture.STORE[n_pack_cv] = DEFINED (PARRAY n_pack)',
        'S_capture.STORE[n_weakCall_cv] = DEFINED (POBJECT n_weak_call)',
        'S_capture.STORE[n_cell] = DEFINED pvalue_name',
        'pvalue_name = PSTRING_CARRIER (REQUEST_STRING n_string) preqbytes_name',
        'preqbytes_name = $ptascii("V106_REVIEW_MISSING")',
        'n_cell <- S_capture.REFCELLS',
        'S_capture.ARRAYS[n_pack].ITEMS = [ENTRY (KSTRING $ptascii("name")) (ALIAS n_cell)]',
        '~$array_immutable(S_capture,n_pack)',
        '$heap_count(HARRAY n_pack,$pools_nodes(S_capture.POOLS)) = 0',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_callee) = 2',
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'),
        *reach('S_unpack','S_capture',1),
        'S_unpack.TODO = (CONFIG_UNPACK_NEXT pconfigcall_unpack (KNOWN (PARRAY n_pack)) 0) :: ptask_unpack*',
        'pconfigcall_unpack.OWNER = (n_callee)','pconfigcall_unpack.INDEX = 0',
        'pconfigcall_unpack.SENT = eps','~pconfigcall_unpack.NAMED',
        'pconfigcall_unpack.PACKS = [pconfigpack]',
        'pconfigpack.INDEX = 0','pconfigpack.ARRAY = n_pack',
        'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("name")) (DIRECT pvalue_name)]',
        '$config_pack_source_valid(S_unpack,pconfigcall_unpack,pconfigpack)',
        '$config_unpack_valid(S_unpack,pconfigcall_unpack,KNOWN (PARRAY n_pack),0)',
        '$config_pack_capture(S_unpack,S_unpack.ARRAYS[n_pack].ITEMS) = pconfigpack.ITEMS',
        '$intrinsic_argument(S_unpack,pconfigcall_unpack.SITE,0) = ((expression,true,eps,pconfigpack.SITE,pconfigpack.LINE))',
        '$compiled_read(S_unpack,pconfigpack.SITE) = eps',
        'S_unpack.ARRAYS[n_pack] = S_capture.ARRAYS[n_pack]',
        'HARRAY n_pack <- S_unpack.ALLOCATIONS','HCELL n_cell <- S_unpack.ALLOCATIONS',
        '$node_children(S_unpack,HARRAY n_pack) = [HCELL n_cell]',
        '$config_nodes(pconfigcall_unpack) = [HOBJECT n_callee]',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_unpack (KNOWN (PARRAY n_pack)) 0) = [HOBJECT n_callee,HARRAY n_pack]',
        'S_unpack.STORE[n_call_cv] = DEFINED PNULL','S_unpack.STORE[n_pack_cv] = DEFINED PNULL',
        'S_unpack.STORE[n_effects_cv] = DEFINED (PINT 1)',
        '$weakref_get(S_unpack,n_weak_call) = POBJECT n_callee',
        '$heap_owners($heap_graph(S_unpack),HOBJECT n_callee) = 1',
        '$test_outputs(S_unpack.EVENTS) = ' + term(before),*budget('S_unpack'),
        *common.step('S_sent','S_unpack'),*common.public('S_sent'),
        'S_sent.TODO = (CONFIG_UNPACK_NEXT pconfigcall_sent (KNOWN (PARRAY n_pack)) 1) :: ptask_unpack*',
        'pconfigcall_sent.PACKS = [pconfigpack]','pconfigcall_sent.INDEX = 0',
        'pconfigcall_sent.SENT = [NAMED_SENT (KNOWN pvalue_name)]','pconfigcall_sent.NAMED',
        '$config_unpack_valid(S_sent,pconfigcall_sent,KNOWN (PARRAY n_pack),1)',
        '$config_destination(INTRINSIC_CONSTANT,($ptascii("name")),0) = (0)',
        '$config_nodes(pconfigcall_sent) = [HOBJECT n_callee]',
        'HARRAY n_pack <- S_sent.ALLOCATIONS',
        'S_sent.STORE[n_cell] = DEFINED pvalue_name',
        *reach('S','S_sent',2),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_call*',
        'pconfigcall = pconfigcall_sent[.INDEX = 1]',
        'pconfigcall.PACKS = [pconfigpack]','pconfigcall.LINE = 25',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name)]','pconfigcall.NAMED',
        '$config_invoke_valid(S,pconfigcall)','$dynamic_owned_global_query_valid(S,pconfigcall)',
        '$dynamic_global_constant_call(pconfigcall)','$dynamic_global_constant_valid(S,pconfigcall)',
        '$config_ini_pack_known(S,pconfigpack.ITEMS,$compiled_read(S,pconfigpack.SITE))',
        '$exit_strict(S,pconfigcall.SITE)','~$config_strict(S,pconfigcall)',
        '$config_method_receiver(S,pconfigcall)',
        '~(HARRAY n_pack <- S.ALLOCATIONS)','HCELL n_cell <- S.ALLOCATIONS',
        'S.STORE[n_cell] = DEFINED pvalue_name',
        '$config_nodes(pconfigcall) = [HOBJECT n_callee]',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_callee]',
        '$string_carrier_valid(S,pvalue_name)',*replay('S'),
        'S.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S.EVENTS) = ' + term(before),*controls(),*budget('S'),
        *common.step('S_error_pending','S'),*settle('S_error','S_error_pending'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_call*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable','pthrowable.KIND = "Error"',
        'pthrowable.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + term(error_text) + ')',
        '$throwable_field(S_error,n_error,"line") = PINT 25',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_invoke))]',
        '$trace_array_field(S_error,n_api,$ptascii("function")) = PSTRING ($ptascii("constant"))',
        '$trace_array_field(S_error,n_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_error,n_invoke,$ptascii("class")) = PSTRING ($ptascii("Closure"))',
        '$trace_array_field(S_error,n_invoke,$ptascii("type")) = PSTRING ($ptascii("->"))',
        '$trace_array_field(S_error,n_api,$ptascii("args")) = PARRAY n_api_args',
        '$trace_array_field(S_error,n_invoke,$ptascii("args")) = PARRAY n_invoke_args',
        'n_api_args =/= n_invoke_args',
        'S_error.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]',
        'S_error.ARRAYS[n_invoke_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]',
        '$node_children(S_error,HARRAY n_api_args) = eps',
        '$node_children(S_error,HARRAY n_invoke_args) = eps',
        '~(HOBJECT n_callee <- S_error.ALLOCATIONS)',
        '$weakref_get(S_error,n_weak_call) = PNULL',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_error.EVENTS) = ' + term(before),
        *reach('S_caught','S_error',3),
        '$lookup(S_caught.ENV,$ptascii("rawApi")) = (n_api_cv)',
        '$lookup(S_caught.ENV,$ptascii("rawInvoke")) = (n_invoke_cv)',
        'S_caught.STORE[n_api_cv] = DEFINED (PARRAY n_api_args)',
        'S_caught.STORE[n_invoke_cv] = DEFINED (PARRAY n_invoke_args)',
        'S_caught.STORE[n_cell] = DEFINED pvalue_current',
        '$string_bytes(pvalue_current) = ($ptascii("changed-after-pack"))',
        'pvalue_current =/= pvalue_name',
        'S_caught.ARRAYS[n_pack].ITEMS = [ENTRY (KSTRING $ptascii("name")) (ALIAS n_cell)]',
        '$entry_value(S_caught,ALIAS n_cell) = pvalue_current',*replay('S_caught'),
        '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        *reach('S_api','S_caught',4),
        '~(HOBJECT n_error <- S_api.ALLOCATIONS)','~(HARRAY n_trace <- S_api.ALLOCATIONS)',
        '~(HARRAY n_api <- S_api.ALLOCATIONS)','~(HARRAY n_invoke <- S_api.ALLOCATIONS)',
        '~(HCELL n_cell <- S_api.ALLOCATIONS)','~(HARRAY n_pack <- S_api.ALLOCATIONS)',
        'S_api.STORE[n_api_cv] = DEFINED (PARRAY n_api_args)',
        'S_api.STORE[n_invoke_cv] = DEFINED (PARRAY n_invoke_args)',
        '$heap_owners($heap_graph(S_api),HARRAY n_api_args) = 1',
        '$heap_owners($heap_graph(S_api),HARRAY n_invoke_args) = 1',
        '$string_carrier_valid(S_api,pvalue_name)',*replay('S_api'),
        '$test_outputs(S_api.EVENTS) = ' + term(raw_api),*budget('S_api'),
        *reach('S_invoke','S_api',5),
        '~(HARRAY n_api_args <- S_invoke.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_invoke),HARRAY n_invoke_args) = 1',
        'S_invoke.ARRAYS[n_invoke_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]',
        '$test_outputs(S_invoke.EVENTS) = ' + term(raw_invoke),
        *reach('S_read','S_invoke',6),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_reader)','n_reader =/= n_callee',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '~(HARRAY n_invoke_args <- S_read.ALLOCATIONS)',
        'S_read.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_read.EVENTS) = ' + term(raw_invoke),
        *common.step('S_value_pending','S_read'),*settle('S_value','S_value_pending'),
        'S_value.TODO = ptask_read*','S_value.RESULT = KNOWN (PINT 23)',
        *define.finish('S_value',stdout),
        'S_final.STRINGDATA[n_string] = preqbytes_name',
        'S_final.SELECTEDCALLS = eps','S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_callee','HOBJECT n_weak_call','HOBJECT n_error','HOBJECT n_reader',
            'HARRAY n_pack','HCELL n_cell','HARRAY n_trace','HARRAY n_api','HARRAY n_invoke',
            'HARRAY n_api_args','HARRAY n_invoke_args']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == CASE:
        timeout = 420
    return packet_process(command,directory,timeout,cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
