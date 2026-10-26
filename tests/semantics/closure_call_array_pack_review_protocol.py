#!/usr/bin/env python3
"""An unpacked alias is copied before Closure::call creates a fresh formal cell."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import closure_call_array_pack_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_closure_pack_peer_front(pstate,nat) : bool
def $test_closure_pack_peer_front(S,0) = true
  -- if S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail*
  -- if pclosurecall.INDEX = 0
def $test_closure_pack_peer_front(S,1) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 0) :: ptask_tail*
def $test_closure_pack_peer_front(S,2) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 1) :: ptask_tail*
def $test_closure_pack_peer_front(S,3) = true
  -- if S.TODO = (CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs n_base) :: ptask_tail*
def $test_closure_pack_peer_front(S,4) = true
  -- if S.TODO = (CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base) :: ptask_tail*
def $test_closure_pack_peer_front(S,5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver
  -- if $lookup(S.ENV,$ptascii("value")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PINT 31)
def $test_closure_pack_peer_front(S,6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver
  -- if $lookup(S.ENV,$ptascii("value")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PINT 53)
def $test_closure_pack_peer_front(S,7) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("call")
def $test_closure_pack_peer_front(S,n_phase) = false -- otherwise
dec $test_closure_pack_peer_seek(pstate,nat,nat) : pstate
def $test_closure_pack_peer_seek(S,n_phase,0) = S
def $test_closure_pack_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_closure_pack_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_pack_peer_seek(S,n_phase,n) = $test_closure_pack_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_pack_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_closure_pack_peer_settled(pstate) : bool
def $test_closure_pack_peer_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_closure_pack_peer_user_entry(pstate) : bool
def $test_closure_pack_peer_user_entry(S) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_closure_pack_peer_user_entry(S) = false -- otherwise
dec $test_closure_pack_peer_settle(pstate,nat) : pstate
def $test_closure_pack_peer_settle(S,0) = S
def $test_closure_pack_peer_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_closure_pack_peer_settled(S) \/ $test_closure_pack_peer_user_entry(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_pack_peer_settle(S,n) = $test_closure_pack_peer_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_pack_peer_settled(S) /\ ~$test_closure_pack_peer_user_entry(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_closure_pack_peer_seek({start},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_pack_peer_front({state},{phase})', *common.public(state)]


def settle(state, start):
    return [f'{state}_found = $test_closure_pack_peer_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_pack_peer_settled({state})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def checks(initial, stdout):
    before_warning = b'B|P|calleeHeld|receiverHeld|'
    marker = b'|warningFile|52|31|calleeHeld|receiverHeld|'
    message, _ = stdout[len(before_warning + b'W|2|'):].split(marker, 1)
    assert stdout.startswith(before_warning + b'W|2|')
    assert message.startswith(b'V107ReviewReceiver::{closure:')
    assert message.endswith(b':33}(): Argument #1 ($value) must be passed by reference, value given')
    after_warning = before_warning + b'W|2|' + message + marker
    written = after_warning + b'BODY|31|47|bound|calleeHeld|receiverHeld|'
    assert stdout == written + b'47|53|47|1|1|1|currentNull|calleeGone|receiverGone||23|A|'
    values = [*initial, 'S_initial.COMPLETION = BUDGET',
        *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_capture) :: ptask_capture*',
        'n_source = pclosurecall_capture.SOURCE',
        'pclosurecall_capture.PACKS = eps', 'pclosurecall_capture.RAW = eps',
        '$closure_call_source(S_capture,n_source)',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in
            ['call','receiver','pack','weakCall','weakReceiver','cell','effects','warnings','bodyCount','result']],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_source)',
        'S_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_receiver)',
        'S_capture.STORE[n_pack_cv] = DEFINED (PARRAY n_pack)',
        'S_capture.STORE[n_weakCall_cv] = DEFINED (POBJECT n_weak_call)',
        'S_capture.STORE[n_weakReceiver_cv] = DEFINED (POBJECT n_weak_receiver)',
        'S_capture.STORE[n_cell_cv] = DEFINED (PINT 17)',
        'n_cell_cv <- S_capture.REFCELLS',
        'S_capture.ARRAYS[n_pack].ITEMS = [ENTRY (KSTRING $ptascii("value")) (ALIAS n_cell_cv)]',
        '(HOBJECT n_source) <- $task_nodes(CLOSURE_CALL_ARGS pclosurecall_capture)',
        *reach('S_unpack','S_capture',1),
        'S_unpack.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_unpack (KNOWN (PARRAY n_pack)) 0) :: ptask_unpack*',
        'pclosurecall_unpack.SOURCE = n_source',
        'pclosurecall_unpack.FIRST = (POBJECT n_receiver)',
        'pclosurecall_unpack.RECEIVER = (n_receiver)', 'pclosurecall_unpack.INDEX = 1',
        'pclosurecall_unpack.PACKS = [pconfigpack]',
        'pconfigpack.ARRAY = n_pack', 'pconfigpack.INDEX = 1',
        'pconfigpack.LINE = 52',
        'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (PINT 31))]',
        'pclosurecall_unpack.RAW = eps',
        'pclosurecall_unpack.SENT = {SLOTS eps, NAMED eps}',
        'S_unpack.ARRAYS[n_pack].ITEMS = [ENTRY (KSTRING $ptascii("value")) (ALIAS n_cell_cv)]',
        'S_unpack.STORE[n_cell_cv] = DEFINED (PINT 31)',
        'S_unpack.STORE[n_call_cv] = DEFINED (POBJECT n_recovery)', 'n_recovery =/= n_source',
        'S_unpack.STORE[n_receiver_cv] = DEFINED PNULL',
        'S_unpack.STORE[n_pack_cv] = DEFINED PNULL',
        '(HARRAY n_pack) <- $task_nodes(CLOSURE_CALL_UNPACK_NEXT pclosurecall_unpack (KNOWN (PARRAY n_pack)) 0)',
        '(HARRAY n_pack) <- S_unpack.ALLOCATIONS',
        '$test_outputs(S_unpack.EVENTS) = ' + term(before_warning),
        '~$call_task_valid(S_unpack,CLOSURE_CALL_UNPACK_NEXT pclosurecall_unpack (KNOWN (PARRAY n_pack)) 2)',
        'S_dead_pack = S_unpack[.ALLOCATIONS = $destruction_node_delete(S_unpack.ALLOCATIONS,HARRAY n_pack)]',
        '~$call_task_valid(S_dead_pack,CLOSURE_CALL_UNPACK_NEXT pclosurecall_unpack (KNOWN (PARRAY n_pack)) 0)',
        'S_live_change = S_unpack[.STORE[n_cell_cv] = DEFINED (PINT 47)]',
        '~$call_task_valid(S_live_change,CLOSURE_CALL_UNPACK_NEXT pclosurecall_unpack (KNOWN (PARRAY n_pack)) 0)',
        *budget('S_unpack'),
        *reach('S_sent','S_unpack',2),
        'S_sent.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_sent (KNOWN (PARRAY n_pack)) 1) :: ptask_sent*',
        'pclosurecall_sent.PACKS = [pconfigpack]',
        'pclosurecall_sent.RAW = [(KSTRING $ptascii("value"), KNOWN (PINT 31))]',
        'pclosurecall_sent.SENT = {SLOTS ([(NAMED_SENT (KNOWN (PINT 31)))]), NAMED eps}',
        'pclosurecall_sent.ERROR = eps',
        *reach('S_forward_pending','S_sent',3), *settle('S_forward','S_forward_pending'),
        'S_forward.TODO = (CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs_empty n_base) :: ptask_forward*',
        'pnamedargs_empty = {SLOTS eps, NAMED eps}',
        'pclosurecall.INDEX = 2', 'pclosurecall.PACKS = [pconfigpack]',
        'pclosurecall.SOURCE = n_source', 'pclosurecall.RECEIVER = (n_receiver)',
        'pclosurecall.RAW = [(KSTRING $ptascii("value"), KNOWN (PINT 31))]',
        '~(HARRAY n_pack <- S_forward.ALLOCATIONS)',
        '~((HARRAY n_pack) <- $task_nodes(CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs_empty n_base))',
        'n_base = |S_forward.STORE|',
        'S_forward.STORE[n_cell_cv] = DEFINED (PINT 31)',
        'S_forward.STORE[n_warnings_cv] = DEFINED (PINT 0)',
        'S_forward.STORE[n_bodyCount_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_forward.EVENTS) = ' + term(before_warning),
        *budget('S_forward')]
    # These are undriven authority projections, not extra source executions.
    for change in ['.PACKS = eps','.INDEX = 1','.LINE = $(pclosurecall.LINE + 1)',
            '.SOURCE = |S_forward.OBJECTS|','.RECEIVER = eps','.FIRST = eps',
            '.RAW = [(KSTRING $ptascii("other"), KNOWN (PINT 31))]',
            '.SENT = {SLOTS eps, NAMED eps}']:
        values += [f'~$call_task_valid(S_forward,CLOSURE_CALL_FORWARD pclosurecall[{change}] 0 pnamedargs_empty n_base)']
    for change in ['.INDEX = 0','.ARRAY = |S_forward.ARRAYS|','.LINE = $(pconfigpack.LINE + 1)',
            '.SITE = PORIGIN 0 eps','.ITEMS = eps',
            '.ITEMS = [ENTRY (KSTRING $ptascii("value")) (ALIAS n_cell_cv)]']:
        values += [f'~$call_task_valid(S_forward,CLOSURE_CALL_FORWARD pclosurecall[.PACKS = [pconfigpack[{change}]]] 0 pnamedargs_empty n_base)']
    values += [
        'S_history = S_forward[.ARRAYS[n_pack].ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (PINT 99))]]',
        '$call_task_valid(S_history,CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs_empty n_base)',
        *reach('S_prepared','S_forward',4),
        'S_prepared.TODO = (CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs_prepared n_base) :: ptask_prepared*',
        'pnamedargs_prepared.SLOTS = [NAMED_SENT (REFERENCE n_temp)]',
        'pnamedargs_prepared.NAMED = eps',
        'S_prepared.STORE[n_temp] = DEFINED (PINT 31)',
        'S_prepared.STORE[n_cell_cv] = DEFINED (PINT 47)',
        'S_prepared.GLOBALTABLE = eps',
        '$lookup(S_prepared.ENV,$ptascii("noise")) = (n_noise)',
        '$lookup(S_prepared.ENV,$ptascii("noiseAlias")) = (n_noise_alias)',
        'S_prepared.STORE[n_noise] = DEFINED (PINT 71)',
        'S_prepared.STORE[n_noise_alias] = DEFINED PNULL',
        '$(n_noise >= n_base)', '$(n_temp > n_noise)',
        'n_temp =/= n_cell_cv',
        '$call_reference_operand_valid(S_prepared,REFERENCE n_temp)',
        'S_prepared.STORE[n_warnings_cv] = DEFINED (PINT 1)',
        'S_prepared.STORE[n_bodyCount_cv] = DEFINED (PINT 0)',
        'S_prepared.STORE[n_result_cv] = DEFINED (PINT 97)',
        '(HOBJECT n_source) <- S_prepared.ALLOCATIONS',
        '(HOBJECT n_receiver) <- S_prepared.ALLOCATIONS',
        '$test_outputs(S_prepared.EVENTS) = ' + term(after_warning),
        'pnamedargs_bad = pnamedargs_prepared[.SLOTS = [NAMED_SENT (REFERENCE n_cell_cv)]]',
        '~$call_task_valid(S_prepared,CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs_bad n_base)',
        *budget('S_prepared'),
        *reach('S_body','S_prepared',5),
        'S_body.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver',
        'pcallcontext.RECEIVER = (n_receiver)', 'pcallcontext.ARGC = 1',
        'pcallcontext.WRAPPER = (pnamedargs_wrapper)',
        'pnamedargs_wrapper.SLOTS = eps',
        'pnamedargs_wrapper.NAMED = [($ptascii("value"), KNOWN (PINT 31))]',
        '$lookup(S_body.ENV,$ptascii("value")) = (n_temp)',
        'S_body.STORE[n_temp] = DEFINED (PINT 31)',
        'S_body.STORE[n_cell_cv] = DEFINED (PINT 47)',
        '$wrapper_context_valid(S_body,pcallcontext)',
        '~$wrapper_context_valid(S_body,pcallcontext[.WRAPPER = eps])',
        '~$wrapper_context_valid(S_body,pcallcontext[.WRAPPER = (pnamedargs_wrapper[.NAMED = [($ptascii("other"), KNOWN (PINT 31))]])])',
        '~$wrapper_context_valid(S_body,pcallcontext[.NAMED = [($ptascii("other"), KNOWN (PINT 31))]])',
        *reach('S_written','S_body',6),
        'S_written.CURRENT = (pcallcontext_written)',
        'pcallcontext_written.WRAPPER = (pnamedargs_wrapper)',
        'S_written.STORE[n_temp] = DEFINED (PINT 53)',
        'S_written.STORE[n_cell_cv] = DEFINED (PINT 47)',
        'S_written.STORE[n_bodyCount_cv] = DEFINED (PINT 1)',
        '$test_outputs(S_written.EVENTS) = ' + term(written),
        *reach('S_cleanup_pending','S_written',7), *settle('S_cleanup','S_cleanup_pending'),
        'S_cleanup.STORE[n_result_cv] = DEFINED (PINT 53)',
        'S_cleanup.STORE[n_cell_cv] = DEFINED (PINT 47)',
        'S_cleanup.STORE[n_noise] = DEFINED (PINT 71)',
        'S_cleanup.STORE[n_noise_alias] = DEFINED PNULL',
        'S_cleanup.STORE[n_effects_cv] = DEFINED (PINT 1)',
        'S_cleanup.STORE[n_warnings_cv] = DEFINED (PINT 1)',
        'S_cleanup.STORE[n_bodyCount_cv] = DEFINED (PINT 1)',
        *[f'~({node} <- S_cleanup.ALLOCATIONS)' for node in
            ['HOBJECT n_source','HOBJECT n_receiver','HARRAY n_pack','HCELL n_temp']],
        '$test_outputs(S_cleanup.EVENTS) = ' + term(stdout[:-2]),
        *define.finish('S_cleanup',stdout)]
    for node in ['HOBJECT n_source','HOBJECT n_receiver','HOBJECT n_recovery',
            'HOBJECT n_weak_call','HOBJECT n_weak_receiver','HARRAY n_pack',
            'HCELL n_cell_cv','HCELL n_noise','HCELL n_noise_alias','HCELL n_temp']:
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
