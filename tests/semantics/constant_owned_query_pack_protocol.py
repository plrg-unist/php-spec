#!/usr/bin/env python3
"""Query binding replays a captured pack after its runtime container retires."""
from pathlib import Path

import constant_owned_stringable_query_protocol as lifetime
import typed_static_invoke_set_protocol as process_base
import constant_owned_query_pack_sources as sources

define, packet, common = lifetime.define, lifetime.packet, lifetime.common
ROOT, text, term = lifetime.ROOT, lifetime.text, lifetime.term
PREFIX = lifetime.PREFIX + r'''
dec $test_query_pack_front(pstate, pintrinsic, nat) : bool
def $test_query_pack_front(S,pintrinsic,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ pconfigcall.OWNER =/= eps /\ pconfigcall.INDEX = 0
def $test_query_pack_front(S,pintrinsic,1) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_array)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ pconfigcall.OWNER =/= eps
def $test_query_pack_front(S,pintrinsic,2) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ pconfigcall.OWNER =/= eps /\ pconfigcall.INDEX = 1
def $test_query_pack_front(S,pintrinsic,n_phase) = false -- otherwise
dec $test_query_pack_seek(pstate, pintrinsic, nat, nat) : pstate
def $test_query_pack_seek(S,pintrinsic,n_phase,0) = S
def $test_query_pack_seek(S,pintrinsic,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_query_pack_front(S,pintrinsic,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_pack_seek(S,pintrinsic,n_phase,n) = $test_query_pack_seek($drive_steps($test_running(S),1),pintrinsic,n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_pack_front(S,pintrinsic,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, kind, phase):
    return [f'{state}_found = $test_query_pack_seek({start},{kind},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_query_pack_front({state},{kind},{phase})', *common.public(state)]


def variable(state, name, value):
    return [f'$lookup({state}.ENV,{text(name)}) = (n_cv_{name}_{state})',
        f'{state}.STORE[n_cv_{name}_{state}] = DEFINED ({value})']


def capture(state, start, kind):
    return [*reach(state,start,kind,0),
        f'{state}.TODO = (CONFIG_ARGS pconfigcall_{state}) :: ptask_{state}*',
        f'pconfigcall_{state}.OWNER = (n_owner)', f'pconfigcall_{state}.SELECTION = eps',
        f'pconfigcall_{state}.PACKS = eps', f'pconfigcall_{state}.SENT = eps',
        f'$config_selected_valid({state},pconfigcall_{state})',
        f'$config_nodes(pconfigcall_{state}) = [HOBJECT n_owner]',
        *variable(state,'call','POBJECT n_owner'),
        f'$heap_owners($heap_graph({state}),HOBJECT n_owner) = 2',
        *lifetime.captured.intrinsic(state,'n_owner',kind)]


def packed(label, start, kind, key, name, prefix, literal=False):
    unpack, ready, invoke = [label+x for x in ['_unpack','_ready','_invoke']]
    call, pack, array, value = [x+label for x in ['pconfigcall_','pconfigpack_','n_array_','pvalue_']]
    values = [*reach(unpack,start,kind,1),
        f'{unpack}.TODO = (CONFIG_UNPACK_NEXT pconfigcall_pre_{label} (KNOWN (PARRAY {array})) 0) :: ptask_{label}*',
        f'pconfigcall_pre_{label}.OWNER = (n_owner)', f'pconfigcall_pre_{label}.INDEX = 0',
        f'pconfigcall_pre_{label}.SENT = eps', f'pconfigcall_pre_{label}.PACKS = [{pack}]',
        f'{pack}.INDEX = 0', f'{pack}.ARRAY = {array}',
        f'{pack}.ITEMS = [ENTRY ({key}) (DIRECT {value})]',
        f'$string_bytes({value}) = ({text(name)})', f'$string_carrier_valid({unpack},{value})',
        f'$config_unpack_valid({unpack},pconfigcall_pre_{label},KNOWN (PARRAY {array}),0)',
        f'$config_pack_source_valid({unpack},pconfigcall_pre_{label},{pack})',
        f'$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_pre_{label} (KNOWN (PARRAY {array})) 0) = [HOBJECT n_owner,HARRAY {array}]',
        f'(HARRAY {array}) <- {unpack}.ALLOCATIONS',
        f'$test_outputs({unpack}.EVENTS) = ' + term(prefix),
        *lifetime.budget(unpack), *reach(ready,unpack,kind,2),
        f'{ready}.TODO = (CONFIG_ARGS {call}) :: ptask_{label}*',
        f'{call}.OWNER = (n_owner)', f'{call}.SELECTION = eps',
        f'{call}.INDEX = 1', f'{call}.PACKS = [{pack}]',
        f'{call}.SENT = [NAMED_SENT (KNOWN {value})]',
        f'{"" if key.startswith("KSTRING") else "~"}{call}.NAMED',
        f'$intrinsic_count({ready},{call}.SITE) = (1)',
        f'$config_invoke_valid({ready},{call})',
        f'$config_source_replay({ready},{call},{call}[.INDEX = 0][.SENT = eps][.NAMED = false][.PACKS = eps],{call}.PACKS) = (({call}[.PACKS = eps],eps))',
        f'$config_nodes({call}) = [HOBJECT n_owner]',
        f'$config_pack_source_valid({ready},{call},{pack})',
        f'$config_ini_pack_known({ready},{pack}.ITEMS,$compiled_read({ready},{pack}.SITE))',
        f'$dynamic_owned_global_query_valid({ready},{call})',
        f'$test_outputs({ready}.EVENTS) = ' + term(prefix)]
    if literal:
        values += [f'$compiled_read({ready},{pack}.SITE) = (PARRAY n_known_{label})',
            f'$($heap_count(HARRAY n_known_{label},$pools_nodes({ready}.POOLS)) > 0)',
            f'(HARRAY {array}) <- {ready}.ALLOCATIONS',
            f'$dynamic_array_same_entries({ready},{pack}.ITEMS,{ready}.ARRAYS[n_known_{label}].ITEMS)']
    else:
        values += [f'$compiled_read({ready},{pack}.SITE) = eps',
            f'~(HARRAY {array} <- {ready}.ALLOCATIONS)',
            f'$heap_count(HARRAY {array},$pools_nodes({ready}.POOLS)) = 0',
            f'S_history_{label} = {ready}[.ARRAYS[{array}].ITEMS = [ENTRY ({key}) (DIRECT PNULL)]]',
            f'$dynamic_owned_global_query_valid(S_history_{label},{call})']
    values += [*common.step(invoke,ready),
        f'{invoke}.TODO = (CONFIG_INVOKE {call}) :: ptask_{label}*',
        f'$config_invoke_valid({invoke},{call})',
        f'$dynamic_owned_global_query_valid({invoke},{call})',
        f'{invoke}.EVENTS = {ready}.EVENTS', *common.public(invoke)]
    return values


def controls(state, label, literal=False):
    call, pack, value = [x+label for x in ['pconfigcall_','pconfigpack_','pvalue_']]
    values = [f'S_dead_{label} = {state}[.ALLOCATIONS = $destruction_node_delete({state}.ALLOCATIONS,HOBJECT n_owner)]',
        f'~$dynamic_owned_global_query_valid(S_dead_{label},{call})']
    for change in ['.OWNER = eps', f'.OWNER = (|{state}.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.INDEX = 0', '.SITE = PORIGIN 0 eps',
            f'.LINE = $({call}.LINE + 1)', f'.NAMED = ~{call}.NAMED', '.SENT = eps',
            f'.SENT = {call}.SENT ++ {call}.SENT', f'.PACKS = [{pack},{pack}]']:
        values += [f'~$dynamic_owned_global_query_valid({state},{call}[{change}])']
    for change in ['.INDEX = 1', '.SITE = PORIGIN 0 eps', f'.LINE = $({pack}.LINE + 1)',
            f'.ARRAY = |{state}.ARRAYS|', '.ITEMS = eps',
            f'.ITEMS = {pack}.ITEMS ++ {pack}.ITEMS',
            f'.ITEMS = [ENTRY (KSTRING ($ptascii("wrong_name"))) (DIRECT {value})]']:
        values += [f'~$dynamic_owned_global_query_valid({state},{call}[.PACKS = [{pack}[{change}]]])']
    for raw in ['PNULL','PINT 0','PSTRING ($ptascii("X::Y"))',
            'PSTRING ($ptascii("__COMPILER_HALT_OFFSET__"))','PSTRING ([65,0,66])']:
        values += [f'~$dynamic_owned_global_query_valid({state},{call}[.SENT = [NAMED_SENT (KNOWN ({raw}))]])']
    if literal:
        values += [f'pvalue_other_{label} = PSTRING_CARRIER INTERNED_STRING ($ptascii("V106_OTHER"))',
            f'$string_carrier_valid({state},pvalue_other_{label})',
            f'pconfigpack_other_{label} = {pack}[.ITEMS = [ENTRY (KSTRING ($ptascii("constant_name"))) (DIRECT pvalue_other_{label})]]',
            f'pconfigcall_other_{label} = {call}[.SENT = [NAMED_SENT (KNOWN pvalue_other_{label})]][.PACKS = [pconfigpack_other_{label}]]',
            f'$config_invoke_valid({state},pconfigcall_other_{label})',
            f'~$dynamic_owned_global_query_valid({state},pconfigcall_other_{label})']
    return values


def result(state, start, value, gone=True):
    values = [*common.step(state+'_pending',start),
        *lifetime.settle(state,state+'_pending',value),
        f'{state}.USERCONSTANTS = {start}.USERCONSTANTS']
    if gone:
        values += [f'$weakref_get({state},n_weak_call) = PNULL',
            f'~(HOBJECT n_owner <- {state}.ALLOCATIONS)']
    else: values += [f'$weakref_get({state},n_weak_call) = POBJECT n_owner']
    return values


def checks(initial, name, stdout):
    named = name == sources.NAMED
    kind = 'INTRINSIC_DEFINED' if named else 'INTRINSIC_CONSTANT'
    key, number = ('V106_NAMED',23) if named else ('V106_POSITIONAL',17)
    before = b'B|F|held|P|held|' if named else b'B|P|held|'
    assert stdout == (b'B|F|held|P|held|T|1|constant|null|calleeGone|V106_NAMED|23|A|' if named else
        b'B|P|held|17|1|defined|V106_WRONG|calleeGone|V106_POSITIONAL|A|')
    values = [*initial, *capture('S_capture','S_initial',kind),
        *lifetime.weak('S_capture','weakCall','n_owner','call'),
        *variable('S_capture','result','PINT 97'),
        *variable('S_capture','effects','PINT 0')]
    if named:
        values += [*packed('S_literal','S_capture',kind,'KSTRING ($ptascii("constant_name"))',key,b'B|',True),
            'S_literal_invoke.USERCONSTANTS = eps',
            '$config_strict(S_literal_invoke,pconfigcall_S_literal)',
            *controls('S_literal_invoke','S_literal',True),
            *result('S_false','S_literal_invoke','PBOOL false',False),
            '(HARRAY n_array_S_literal) <- S_false.ALLOCATIONS',
            *capture('S_second','S_false',kind),
            '$test_outputs(S_second.EVENTS) = ' + term(b'B|F|held|')]
        start = 'S_second'
    else: start = 'S_capture'
    values += [*packed('S_runtime',start,kind,'KSTRING ($ptascii("constant_name"))' if named else 'KINT 9',key,before),
        *variable('S_runtime_invoke','result','PINT 97'),
        *variable('S_runtime_invoke','effects','PINT 1'),
        *variable('S_runtime_invoke','call','pvalue_current'),
        '$string_bytes(pvalue_current) = (' + text('constant' if named else 'defined') + ')',
        'S_runtime_invoke.USERCONSTANTS = [puserconstant]',
        'puserconstant.NAME = ' + text(key), f'puserconstant.VALUE = PINT {number}',
        'puserconstant.CLASS = PVSCALAR',
        f'{"" if named else "~"}$config_strict(S_runtime_invoke,pconfigcall_S_runtime)',
        *controls('S_runtime_invoke','S_runtime'), *lifetime.budget('S_runtime_invoke')]
    if named: values += [*variable('S_runtime_invoke','pack','PNULL')]
    else:
        values += [*variable('S_runtime_invoke','pack','PARRAY n_live_pack'),
            'n_live_pack =/= n_array_S_runtime',
            'S_runtime_invoke.ARRAYS[n_live_pack].ITEMS = [ENTRY (KINT 9) (DIRECT pvalue_live)]',
            '$string_bytes(pvalue_live) = ($ptascii("V106_WRONG"))']
    values += [*result('S_value','S_runtime_invoke','PBOOL true' if named else 'PINT 17'),
        *define.finish('S_value',stdout), 'S_final.USERCONSTANTS = S_runtime_invoke.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0',
        '~(HARRAY n_array_S_runtime <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_owner <- S_final.ALLOCATIONS)', '~(HOBJECT n_weak_call <- S_final.ALLOCATIONS)']
    if named: values += ['(HARRAY n_array_S_literal) <- S_final.ALLOCATIONS']
    else: values += ['~(HARRAY n_live_pack <- S_final.ALLOCATIONS)']
    return values


base = lifetime.captured.prior
base.sources, base.checks, base.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, base.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
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
