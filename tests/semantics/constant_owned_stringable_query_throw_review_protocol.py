#!/usr/bin/env python3
"""A destructor's raw API trace survives replacement Error and final array release."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_stringable_query_throw_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_query_throw_peer_unset(pstate, preqbytes) : bool
def $test_query_throw_peer_unset(S,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = preqbytes
def $test_query_throw_peer_unset(S,preqbytes) = false -- otherwise
dec $test_query_throw_peer_front(pstate, nat) : bool
def $test_query_throw_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_owned_query_string_call(pconfigcall)
def $test_query_throw_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if $dynamic_owned_query_string_call(pconfigcall)
def $test_query_throw_peer_front(S,2) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_query_throw_peer_front(S,3) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
def $test_query_throw_peer_front(S,4) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pdestructionoperation.PENDING =/= eps
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
def $test_query_throw_peer_front(S,5) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps
def $test_query_throw_peer_front(S,6) = $test_query_throw_peer_unset(S,$ptascii("error"))
def $test_query_throw_peer_front(S,7) = $test_query_throw_peer_unset(S,$ptascii("rawPrior"))
def $test_query_throw_peer_front(S,8) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("V103_REVIEW_RECOVERY"))
def $test_query_throw_peer_front(S,n_phase) = false -- otherwise
dec $test_query_throw_peer_seek(pstate, nat, nat) : pstate
def $test_query_throw_peer_seek(S,n_phase,0) = S
def $test_query_throw_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_query_throw_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_throw_peer_seek(S,n_phase,n) = $test_query_throw_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_throw_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_query_throw_peer_settled(pstate) : bool
def $test_query_throw_peer_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_query_throw_peer_settle(pstate, nat) : pstate
def $test_query_throw_peer_settle(S,0) = S
def $test_query_throw_peer_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_query_throw_peer_settled(S) \/ $test_query_throw_peer_front(S,2) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_throw_peer_settle(S,n) = $test_query_throw_peer_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_throw_peer_settled(S) /\ ~$test_query_throw_peer_front(S,2)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_query_throw_peer_seek({start},{phase},3500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_query_throw_peer_front({state},{phase})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def settle(state, start, result):
    return [f'{state}_found = $test_query_throw_peer_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_query_throw_peer_settled({state})',
        f'{state}.RESULT = KNOWN ({result})',
        f'{state}.EVENTS = {start}.EVENTS', *common.public(state)]


def previous_trace(state):
    return [f'$throwable_field({state},n_exception,"trace") = PARRAY n_previous_trace',
        f'{state}.ARRAYS[n_previous_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_destructor_frame)),ENTRY (KINT 1) (DIRECT (PARRAY n_raw_api_frame))]',
        f'$trace_array_field({state},n_destructor_frame,$ptascii("function")) = PSTRING ($ptascii("__destruct"))',
        f'$trace_array_field({state},n_destructor_frame,$ptascii("class")) = PSTRING ($ptascii("V103ReviewName"))',
        f'$entry_lookup({state}.ARRAYS[n_destructor_frame].ITEMS,KSTRING ($ptascii("file"))) = eps',
        f'$entry_lookup({state}.ARRAYS[n_destructor_frame].ITEMS,KSTRING ($ptascii("line"))) = eps',
        f'$trace_array_field({state},n_destructor_frame,$ptascii("args")) = PARRAY n_destructor_args',
        f'{state}.ARRAYS[n_destructor_args].ITEMS = eps',
        f'$trace_array_field({state},n_raw_api_frame,$ptascii("function")) = PSTRING ($ptascii("constant"))',
        f'$trace_array_field({state},n_raw_api_frame,$ptascii("file")) = PSTRING ($call_sourcefile({state}.FILES,pconfigcall.SITE))',
        f'$trace_array_field({state},n_raw_api_frame,$ptascii("line")) = PINT 33',
        f'$trace_array_field({state},n_raw_api_frame,$ptascii("args")) = PARRAY n_raw_args',
        f'{state}.ARRAYS[n_raw_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name))]']


def controls():
    # Borrowed-history projections test guards only; none is driven.
    values = ['$dynamic_query_string_release_valid(S_pending,pdestructionoperation,pconfigcall_received)',
        '$dynamic_query_string_release_invoke(S_pending.TODO,pdestructionoperation) = (pconfigcall_received)',
        'S_retired_raw = S_pending[.ALLOCATIONS = $destruction_node_delete(S_pending.ALLOCATIONS,HOBJECT n_name)]',
        '$dynamic_query_string_release_valid(S_retired_raw,pdestructionoperation,pconfigcall_received)',
        'S_wrong_owner = S_pending[.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_DEFINED]',
        '~$dynamic_query_string_release_valid(S_wrong_owner,pdestructionoperation,pconfigcall_received)']
    for change in ['.CALLER = (pcallcontext_destructor)', '.ORIGIN = (porigin_child)',
            '.COMPLETION = UNSUPPORTED "peer phase"', '.VALUE = KNOWN (PINT 1)',
            '.BASE = BASE_VALUE (KNOWN (PINT 1))', '.SOURCE = UNSET_ARRAY']:
        values += [f'~$dynamic_query_string_release_valid(S_pending,pdestructionoperation[{change}],pconfigcall_received)']
    for label, obj in [('weak','n_weak_name'),('outside','(|S_pending.OBJECTS|)')]:
        values += [f'pconfigcall_bad_{label} = pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT {obj}))]]',
            f'pdestructionoperation_bad_{label} = pdestructionoperation[.SOURCE = CONFIG_STRING_RESULT pconfigcall_bad_{label} {obj} porigin_child z_child pconfigcall.LINE]',
            f'~$dynamic_query_string_release_valid(S_pending,pdestructionoperation_bad_{label},pconfigcall_received)']
    for value in ['PSTRING ' + text('A::B'),'PSTRING ([65,0,66])','PINT 0']:
        values += [f'~$dynamic_query_string_release_valid(S_pending,pdestructionoperation,pconfigcall_received[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += ['$dynamic_query_string_release_invoke([CONFIG_INVOKE pconfigcall_received],pdestructionoperation) = eps',
        '$dynamic_query_string_release_invoke([DESTRUCTOR_OPERATION_EXIT pdestructionoperation],pdestructionoperation) = eps',
        'S_boundary = S_pending[.COMPLETION = UNSUPPORTED "peer boundary"]',
        '$dynamic_query_string_pending(S_boundary,n_exception) = S_boundary']
    return values


def checks(initial, stdout):
    converted = b'B|S|calleeHeld|'
    destructed = converted + b'D|calleeHeld|'
    caught = destructed + (b'Error|Undefined constant "V103_REVIEW_MISSING"|33|constant|file|33|apiS|'
        b'noPrimarySecond|samePrevious|V103_REVIEW_STOP|18|none|__destruct|noFile|internal|'
        b'constant|file|33|rawO|sameObject|end|currentNull|97|1|1|calleeGone|traceHeld|')
    raw = caught + b'rawHeld|1|'
    released = raw + b'gone|1|'
    assert stdout == released + b'23|A|'
    values = [*initial, 'S_initial.COMPLETION = BUDGET', *reach('S','S_initial',0),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_call*',
        'pconfigcall.KIND = INTRINSIC_CONSTANT', 'pconfigcall.OWNER = (n_callee)',
        'pconfigcall.SELECTION = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        'pconfigcall.INDEX = 1', 'pconfigcall.LINE = 33',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name))]',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_query_string_valid(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,0) = eps',
        '~$config_strict(S,pconfigcall)', '~$config_method_receiver(S,pconfigcall)',
        'S.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$config_string_source(S,pconfigcall) = ((porigin_child,z_child))',
        *[f'$lookup(S.ENV,{text(name)}) = (n_{label}_cv)' for name,label in [
            ('call','call'),('name','name'),('weakCall','weak_call'),('weakName','weak_name'),
            ('casts','casts'),('drops','drops'),('made','made'),('result','result')]],
        'S.STORE[n_call_cv] = DEFINED (POBJECT n_callee)',
        'S.STORE[n_name_cv] = DEFINED (POBJECT n_name)',
        'S.STORE[n_weak_call_cv] = DEFINED (POBJECT n_weak_call)',
        'S.STORE[n_weak_name_cv] = DEFINED (POBJECT n_weak_name)',
        'S.STORE[n_casts_cv] = DEFINED (PINT 0)', 'S.STORE[n_drops_cv] = DEFINED (PINT 0)',
        'S.STORE[n_made_cv] = DEFINED PNULL', 'S.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_name) = 2',
        'S.USERCONSTANTS = eps', 'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '$test_outputs(S.EVENTS) = ' + term(b'B|'),
        *reach('S_returned','S',1),
        'S_returned.TODO = (CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child pconfigcall.LINE) :: ptask_call*',
        'S_returned.ORIGIN = (porigin_child)', 'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps',
        'S_returned.RESULT = KNOWN pvalue_received',
        '$string_bytes(pvalue_received) = (' + text('V103_REVIEW_MISSING') + ')',
        '$string_carrier_valid(S_returned,pvalue_received)',
        '$config_string_site_valid(S_returned,pconfigcall,n_name,porigin_child,z_child,pconfigcall.LINE)',
        'S_returned.STORE[n_call_cv] = DEFINED PNULL',
        'S_returned.STORE[n_name_cv] = DEFINED PNULL',
        'S_returned.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_returned.STORE[n_drops_cv] = DEFINED (PINT 0)',
        '$task_nodes(CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child pconfigcall.LINE) = [HOBJECT n_name,HOBJECT n_callee,HOBJECT n_name]',
        '$test_outputs(S_returned.EVENTS) = ' + term(converted), *budget('S_returned'),
        'pconfigcall_received = pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_received)]]',
        *reach('S_enter','S_returned',2),
        'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_enter*',
        'pdestructorcall.OBJECT = n_name', 'pdestructorcall.CALLER = eps',
        'pdestructorcall.OPERATION = (pdestructionoperation_before)',
        'pdestructionoperation_before.SOURCE = CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child pconfigcall.LINE',
        'pdestructionoperation_before.PENDING = eps', 'pdestructorcall.USER',
        '$dynamic_query_string_release_invoke(S_enter.TODO,pdestructionoperation_before) = (pconfigcall_received)',
        'pdestructorcall.SITE = eps', '$destructor_callsite(pdestructorcall) = eps',
        '$destructor_line(pdestructorcall) = $(-1)',
        '$destructor_call_valid(S_enter,pdestructorcall)',
        '$weakref_get(S_enter,n_weak_call) = POBJECT n_callee',
        '$weakref_get(S_enter,n_weak_name) = POBJECT n_name',
        'S_enter.STORE[n_drops_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_enter.EVENTS) = ' + term(converted),
        *reach('S_throw','S_enter',3),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
        'S_throw.CURRENT = (pcallcontext_destructor)',
        '$context_target(pcallcontext_destructor) = pdestructorcall.TARGET',
        '$destructor_context_valid(S_throw,pcallcontext_destructor)',
        'pcallcontext_destructor.CALLSITE = eps', 'pcallcontext_destructor.LINE = $(-1)',
        'S_throw.STORE[n_made_cv] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable_exception',
        'pthrowable_exception.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('V103_REVIEW_STOP') + ')',
        '$throwable_field(S_throw,n_exception,"line") = PINT 18',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_chain_valid(S_throw,n_exception)', *previous_trace('S_throw'),
        'S_throw.USERCONSTANTS = [puserconstant]',
        'puserconstant.NAME = $ptascii("V103_REVIEW_RECOVERY")',
        'puserconstant.VALUE = PINT 23', 'puserconstant.CLASS = PVSCALAR',
        '$dynamic_define_source(S_throw,puserconstant.ORIGIN)',
        'S_throw.STORE[n_drops_cv] = DEFINED (PINT 1)',
        'S_throw.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_throw.STORE[n_result_cv] = DEFINED (PINT 97)',
        'n_name <- S_throw.DESTRUCTION.CALLED',
        '$weakref_get(S_throw,n_weak_call) = POBJECT n_callee',
        '$test_outputs(S_throw.EVENTS) = ' + term(destructed),
        *reach('S_pending','S_throw',4),
        'S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (CONFIG_INVOKE pconfigcall_received) :: ptask_call*',
        'pdestructionoperation.SOURCE = pdestructionoperation_before.SOURCE',
        'pdestructionoperation.PENDING = (n_exception)',
        'pdestructionoperation.VALUE = KNOWN PNULL', 'pdestructionoperation.COMPLETION = NORMAL',
        'S_pending.CURRENT = eps', 'S_pending.FRAMES = eps',
        '$call_task_valid(S_pending,DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
        '$config_invoke_valid(S_pending,pconfigcall_received)',
        '$dynamic_owned_global_query_valid(S_pending,pconfigcall_received)',
        '$weakref_get(S_pending,n_weak_call) = POBJECT n_callee',
        '$weakref_get(S_pending,n_weak_name) = POBJECT n_name',
        'S_pending.USERCONSTANTS = S_throw.USERCONSTANTS',
        '$test_outputs(S_pending.EVENTS) = ' + term(destructed), *budget('S_pending'), *controls(),
        *reach('S_error','S_pending',5),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_call*', 'n_error =/= n_exception',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "Error"',
        'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('Undefined constant "V103_REVIEW_MISSING"') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT 33',
        '$throwable_field(S_error,n_error,"previous") = POBJECT n_exception',
        '$throwable_previous_id(S_error,n_exception) = eps',
        '$throwable_chain_valid(S_error,n_error)',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_error_trace',
        'S_error.ARRAYS[n_error_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_frame))]',
        '$trace_array_field(S_error,n_api_frame,$ptascii("function")) = PSTRING ($ptascii("constant"))',
        '$trace_array_field(S_error,n_api_frame,$ptascii("file")) = PSTRING ($call_sourcefile(S_error.FILES,pconfigcall.SITE))',
        '$trace_array_field(S_error,n_api_frame,$ptascii("line")) = PINT 33',
        '$trace_array_field(S_error,n_api_frame,$ptascii("args")) = PARRAY n_api_args',
        'S_error.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_received)]',
        *previous_trace('S_error'),
        '~(HOBJECT n_callee <- S_error.ALLOCATIONS)',
        '$weakref_get(S_error,n_weak_call) = PNULL',
        '$weakref_get(S_error,n_weak_name) = POBJECT n_name',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_error.STORE[n_drops_cv] = DEFINED (PINT 1)',
        'S_error.USERCONSTANTS = S_throw.USERCONSTANTS',
        '$test_outputs(S_error.EVENTS) = ' + term(destructed),
        *reach('S_caught','S_error',6),
        '$lookup(S_caught.ENV,$ptascii("rawPrior")) = (n_raw_cv)',
        'S_caught.STORE[n_raw_cv] = DEFINED (PARRAY n_raw_args)',
        '$weakref_get(S_caught,n_weak_name) = POBJECT n_name',
        '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        *reach('S_raw','S_caught',7),
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)',
        '~(HOBJECT n_exception <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_error_trace <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_previous_trace <- S_raw.ALLOCATIONS)',
        'S_raw.STORE[n_raw_cv] = DEFINED (PARRAY n_raw_args)',
        '$entry_lookup(S_raw.ARRAYS[n_raw_args].ITEMS,KINT 0) = (DIRECT (POBJECT n_name))',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_name) = 1',
        '$weakref_get(S_raw,n_weak_name) = POBJECT n_name',
        'n_name <- S_raw.DESTRUCTION.CALLED',
        'S_raw.STORE[n_drops_cv] = DEFINED (PINT 1)',
        '$test_outputs(S_raw.EVENTS) = ' + term(raw), *budget('S_raw'),
        *reach('S_read','S_raw',8),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_reader)', 'n_reader =/= n_callee',
        'pconfigcall_read.SELECTION = eps', 'pconfigcall_read.PACKS = eps',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '~(HOBJECT n_name <- S_read.ALLOCATIONS)',
        '~(HARRAY n_raw_args <- S_read.ALLOCATIONS)',
        '$weakref_get(S_read,n_weak_name) = PNULL',
        'S_read.STORE[n_drops_cv] = DEFINED (PINT 1)',
        'S_read.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_read.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_read.USERCONSTANTS = S_throw.USERCONSTANTS',
        '$test_outputs(S_read.EVENTS) = ' + term(released),
        *common.step('S_value_pending','S_read'),
        *settle('S_value','S_value_pending','PINT 23'),
        'S_value.TODO = ptask_read*',
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_callee','HOBJECT n_name','HOBJECT n_weak_call','HOBJECT n_weak_name',
            'HOBJECT n_exception','HOBJECT n_error','HOBJECT n_reader',
            'HARRAY n_error_trace','HARRAY n_previous_trace','HARRAY n_raw_args',
            'HARRAY n_api_args','HARRAY n_destructor_args']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == CASE:
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
