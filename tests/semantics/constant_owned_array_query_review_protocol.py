#!/usr/bin/env python3
"""A captured ARRAY TypeError separates DIRECT COW from one shared scalar cell."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_array_query_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_owned_array_peer_unset(pstate, preqbytes) : bool
def $test_owned_array_peer_unset(S,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = preqbytes
def $test_owned_array_peer_unset(S,preqbytes) = false -- otherwise
dec $test_owned_array_peer_front(pstate, nat) : bool
def $test_owned_array_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.OWNER =/= eps /\ pconfigcall.INDEX = 0
def $test_owned_array_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED /\ $dynamic_owned_query_array_call(pconfigcall)
def $test_owned_array_peer_front(S,2) = $test_owned_array_peer_unset(S,$ptascii("error"))
def $test_owned_array_peer_front(S,3) = $test_owned_array_peer_unset(S,$ptascii("rawArgs"))
def $test_owned_array_peer_front(S,4) = $test_owned_array_peer_unset(S,$ptascii("error"))
def $test_owned_array_peer_front(S,5) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("V105_REVIEW_RECOVERY"))
def $test_owned_array_peer_front(S,n_phase) = false -- otherwise
dec $test_owned_array_peer_seek(pstate, nat, nat) : pstate
def $test_owned_array_peer_seek(S,n_phase,0) = S
def $test_owned_array_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_array_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_array_peer_seek(S,n_phase,n) = $test_owned_array_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_array_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_owned_array_peer_settled(pstate) : bool
def $test_owned_array_peer_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_owned_array_peer_user_entry(pstate) : bool
def $test_owned_array_peer_user_entry(S) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_owned_array_peer_user_entry(S) = false -- otherwise
dec $test_owned_array_peer_settle(pstate, nat) : pstate
def $test_owned_array_peer_settle(S,0) = S
def $test_owned_array_peer_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_owned_array_peer_settled(S) \/ $test_owned_array_peer_user_entry(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_array_peer_settle(S,n) = $test_owned_array_peer_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_array_peer_settled(S) /\ ~$test_owned_array_peer_user_entry(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_array_peer_seek({start},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_array_peer_front({state},{phase})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def settle(state, start):
    return [f'{state}_found = $test_owned_array_peer_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_array_peer_settled({state})', *common.public(state)]


def items(plain):
    return '[ENTRY (KSTRING $ptascii("plain")) (DIRECT (PINT ' + str(plain) + ')),ENTRY (KSTRING $ptascii("alias")) (ALIAS n_cell)]'


def arrays(state, copied=False):
    values = [f'{state}.ARRAYS[n_input].ITEMS = ' + items(17),
        f'{state}.ARRAYS[n_live].ITEMS = ' + items(29),
        f'$node_children({state},HARRAY n_input) = [HCELL n_cell]',
        f'$node_children({state},HARRAY n_live) = [HCELL n_cell]',
        'n_live =/= n_input']
    if copied:
        values += [f'{state}.ARRAYS[n_copy].ITEMS = ' + items(47),
            f'$node_children({state},HARRAY n_copy) = [HCELL n_cell]',
            'n_copy =/= n_input', 'n_copy =/= n_live']
    return values


def controls():
    # Refusal projections are never driven as additional source histories.
    values = ['~$dynamic_query_array_call(pconfigcall)',
        'S_dead_callee = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_callee)]',
        '~$dynamic_query_array_valid(S_dead_callee,pconfigcall)',
        'S_dead_array = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '~$dynamic_query_array_valid(S_dead_array,pconfigcall)',
        'S_dead_cell = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HCELL n_cell)]',
        '~$dynamic_query_array_valid(S_dead_cell,pconfigcall)',
        'S_wrong_callee = S[.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_CONSTANT]',
        '~$dynamic_query_array_valid(S_wrong_callee,pconfigcall)']
    for change in ['.OWNER = eps', '.OWNER = (|S.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.KIND = INTRINSIC_CONSTANT', '.INDEX = 0',
            '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)', '.NAMED = true',
            '.SENT = eps', '.SENT = pconfigcall.SENT ++ pconfigcall.SENT']:
        values += [f'~$dynamic_query_array_valid(S,pconfigcall[{change}])']
    for value in ['PNULL','PBOOL false','PINT 0','PFLOAT 0',
            'PSTRING ($ptascii(""))','POBJECT n_weak_call','PARRAY (|S.ARRAYS|)']:
        values += [f'~$dynamic_query_array_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += ['pconfigpack_bad = {INDEX 0,SITE pconfigcall.SITE,LINE pconfigcall.LINE,ARRAY n_input,ITEMS eps}',
        '~$dynamic_query_array_valid(S,pconfigcall[.PACKS = [pconfigpack_bad]])']
    for label,value in [('nested','PARRAY n_live'),('object','POBJECT n_weak_call'),
            ('legacy','PSTRING ($ptascii("legacy"))')]:
        values += [f'S_bad_{label} = S[.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING $ptascii("plain")) (DIRECT ({value}))]]',
            f'~$dynamic_query_array_valid(S_bad_{label},pconfigcall)']
    values += ['S_bad_alias = S[.STORE[n_cell] = DEFINED (PARRAY n_live)]',
        '~$dynamic_query_array_valid(S_bad_alias,pconfigcall)']
    return values


def checks(initial, stdout):
    before = b'B|N|calleeHeld|'
    message = 'defined(): Argument #1 ($constant_name) must be of type string, array given'
    caught = before + b'T|' + message.encode() + (b'|23|none|defined|file|23|end|'
        b'17|31|29|31|31|constant|97|1|calleeGone|')
    cow = caught + b'17|53|47|53|29|53|53|'
    raw = cow + b'17|53|'
    released = raw + b'47|59|29|59|59|'
    assert stdout == released + b'23|A|'
    values = [*initial, 'S_initial.COMPLETION = BUDGET', *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_callee)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.SENT = eps', '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_callee]',
        'S_capture.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_DEFINED',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in ['call','name','weakCall','result','effects']],
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        'S_capture.STORE[n_name_cv] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_weakCall_cv] = DEFINED (POBJECT n_weak_call)',
        'S_capture.STORE[n_cell] = DEFINED (PINT 19)', 'n_cell <- S_capture.REFCELLS',
        'S_capture.ARRAYS[n_input].ITEMS = ' + items(17),
        '~$array_immutable(S_capture,n_input)',
        '$heap_count(HARRAY n_input,$pools_nodes(S_capture.POOLS)) = 0',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_callee) = 2',
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_call*',
        'pconfigcall.KIND = INTRINSIC_DEFINED', 'pconfigcall.OWNER = (n_callee)',
        'pconfigcall.SELECTION = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        'pconfigcall.INDEX = 1', 'pconfigcall.LINE = 23',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_input))]',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_owned_query_array_call(pconfigcall)',
        '$dynamic_query_array_valid(S,pconfigcall)',
        '$dynamic_query_array_entries(S,S.ARRAYS[n_input].ITEMS)',
        '$config_nodes(pconfigcall) = [HOBJECT n_callee,HARRAY n_input]',
        '~$config_strict(S,pconfigcall)', '~$config_method_receiver(S,pconfigcall)',
        '~$pipe_site(S,pconfigcall.SITE)', '$dynamic_define_known(S,pconfigcall.SITE,0) = eps',
        'S.STORE[n_name_cv] = DEFINED (PARRAY n_live)', *arrays('S'),
        'S.STORE[n_cell] = DEFINED (PINT 31)', 'n_cell <- S.REFCELLS',
        '$call_reference_operand_valid(S,REFERENCE n_cell)',
        'S.STORE[n_call_cv] = DEFINED pvalue_current',
        '$string_bytes(pvalue_current) = ($ptascii("constant"))',
        'S.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S.STORE[n_effects_cv] = DEFINED (PINT 1)',
        '$weakref_get(S,n_weak_call) = POBJECT n_callee',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 1',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 1',
        'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '$test_outputs(S.EVENTS) = ' + term(before), *controls(), *budget('S'),
        *common.step('S_error_pending','S'), *settle('S_error','S_error_pending'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_call*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text(message) + ')',
        '$throwable_field(S_error,n_error,"line") = PINT 23',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api))]',
        '$trace_array_field(S_error,n_api,$ptascii("function")) = PSTRING ($ptascii("defined"))',
        '$trace_array_field(S_error,n_api,$ptascii("line")) = PINT 23',
        '$trace_array_field(S_error,n_api,$ptascii("file")) = PSTRING ($call_sourcefile(S_error.FILES,pconfigcall.SITE))',
        '$trace_array_field(S_error,n_api,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_input))]',
        '$node_children(S_error,HARRAY n_args) = [HARRAY n_input]', *arrays('S_error'),
        'S_error.STORE[n_cell] = DEFINED (PINT 31)',
        '$weakref_get(S_error,n_weak_call) = PNULL', '~(HOBJECT n_callee <- S_error.ALLOCATIONS)',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_error.USERCONSTANTS = S.USERCONSTANTS',
        '$test_outputs(S_error.EVENTS) = ' + term(before),
        *reach('S_cow','S_error',2),
        '$lookup(S_cow.ENV,$ptascii("rawArgs")) = (n_args_cv)',
        '$lookup(S_cow.ENV,$ptascii("copy")) = (n_copy_cv)',
        'S_cow.STORE[n_args_cv] = DEFINED (PARRAY n_args)',
        'S_cow.STORE[n_copy_cv] = DEFINED (PARRAY n_copy)',
        'S_cow.STORE[n_name_cv] = DEFINED (PARRAY n_live)', *arrays('S_cow',True),
        'S_cow.STORE[n_cell] = DEFINED (PINT 53)',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_cow).EDGES,[HARRAY n_input,HARRAY n_live,HARRAY n_copy]) = 3',
        '$heap_owners($heap_graph(S_cow),HARRAY n_input) = 1',
        '$test_outputs(S_cow.EVENTS) = ' + term(cow), *budget('S_cow'),
        *reach('S_raw','S_cow',3),
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)', '~(HARRAY n_trace <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_api <- S_raw.ALLOCATIONS)',
        'S_raw.STORE[n_args_cv] = DEFINED (PARRAY n_args)',
        'S_raw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_input))]',
        '$heap_owners($heap_graph(S_raw),HARRAY n_args) = 1', *arrays('S_raw',True),
        'S_raw.STORE[n_cell] = DEFINED (PINT 53)',
        '$test_outputs(S_raw.EVENTS) = ' + term(raw), *budget('S_raw'),
        *reach('S_release','S_raw',4),
        '~(HARRAY n_args <- S_release.ALLOCATIONS)', '~(HARRAY n_input <- S_release.ALLOCATIONS)',
        'S_release.STORE[n_copy_cv] = DEFINED (PARRAY n_copy)',
        'S_release.STORE[n_name_cv] = DEFINED (PARRAY n_live)',
        'S_release.ARRAYS[n_copy].ITEMS = ' + items(47),
        'S_release.ARRAYS[n_live].ITEMS = ' + items(29),
        'S_release.STORE[n_cell] = DEFINED (PINT 59)',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_release).EDGES,[HARRAY n_live,HARRAY n_copy]) = 2',
        '$test_outputs(S_release.EVENTS) = ' + term(released),
        *reach('S_read','S_release',5),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_reader)', 'n_reader =/= n_callee',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '~(HARRAY n_copy <- S_read.ALLOCATIONS)', '~(HARRAY n_live <- S_read.ALLOCATIONS)',
        '~(HCELL n_cell <- S_read.ALLOCATIONS)',
        'S_read.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_read.STORE[n_effects_cv] = DEFINED (PINT 1)',
        'S_read.USERCONSTANTS = S.USERCONSTANTS',
        '$test_outputs(S_read.EVENTS) = ' + term(released),
        *common.step('S_value_pending','S_read'), *settle('S_value','S_value_pending'),
        'S_value.TODO = ptask_read*', 'S_value.RESULT = KNOWN (PINT 23)',
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_callee','HOBJECT n_weak_call','HOBJECT n_error','HOBJECT n_reader',
            'HARRAY n_input','HARRAY n_live','HARRAY n_copy','HCELL n_cell',
            'HARRAY n_trace','HARRAY n_api','HARRAY n_args']:
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
