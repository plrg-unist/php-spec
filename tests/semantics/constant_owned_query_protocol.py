#!/usr/bin/env python3
"""Captured query identities, late lookup, returned roots and query COW."""
from pathlib import Path

import define_stdclass_array_duplicate_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_query_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = sources.DIRECT
PREFIX = common.PREFIX + r'''
dec $test_owned_query_front(pstate, pintrinsic, nat) : bool
def $test_owned_query_front(S,pintrinsic,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0
def $test_owned_query_front(S,pintrinsic,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ pconfigcall.OWNER =/= eps
def $test_owned_query_front(S,pintrinsic,2) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ pconfigcall.OWNER = eps
  -- if pconfigcall.SELECTION =/= eps
def $test_owned_query_front(S,pintrinsic,n_phase) = false -- otherwise
dec $test_owned_query_seek(pstate, pintrinsic, nat, nat) : pstate
def $test_owned_query_seek(S,pintrinsic,n_phase,0) = S
def $test_owned_query_seek(S,pintrinsic,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_query_front(S,pintrinsic,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_query_seek(S,pintrinsic,n_phase,n) = $test_owned_query_seek($drive_steps($test_running(S),1),pintrinsic,n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_query_front(S,pintrinsic,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, kind, phase):
    return [f'{state}_found = $test_owned_query_seek({start},{kind},{phase},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_query_front({state},{kind},{phase})', *common.public(state)]


def intrinsic(state, obj, kind):
    return [f'{state}.OBJECTS[{obj}] = INTRINSICCLOSURE {kind}',
        f'$typed_closure({state},{obj})', f'$closure_live_object_valid({state},{obj})',
        f'$node_children({state},HOBJECT {obj}) = eps']


def unchanged(before, after):
    return [f'{after}.{key} = {before}.{key}' for key in (
        'USERCONSTANTS', 'SELECTEDCALLS', 'SELECTSEQ', 'ARRAYS', 'STORE', 'OBJECTS', 'POOLS')]


def controls(state, call, owner, label):
    # Local authority projections are undriven. Same-kind owner substitution
    # has no historical nonce refusal under the existing query fallback.
    values = [f'S_dead_{label} = {state}[.ALLOCATIONS = $destruction_node_delete({state}.ALLOCATIONS,HOBJECT {owner})]',
        f'~$dynamic_owned_global_query_valid(S_dead_{label},{call})']
    for change in ['.OWNER = eps', f'.OWNER = (|{state}.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.INDEX = 0', '.SITE = PORIGIN 0 eps',
            f'.LINE = $({call}.LINE + 1)', f'.NAMED = ~{call}.NAMED']:
        values += [f'~$dynamic_owned_global_query_valid({state},{call}[{change}])']
    for raw in ('PNULL', 'PBOOL false', 'PSTRING ($ptascii("Unknown::VALUE"))',
            'PSTRING ($ptascii("__COMPILER_HALT_OFFSET__"))', 'PSTRING ([86,0,57])'):
        values += [f'~$dynamic_owned_global_query_valid({state},{call}[.SENT = [NAMED_SENT (KNOWN ({raw}))]])']
    return values


def direct(initial, stdout):
    before = b'B|N|held|'
    read = before + b'T|gone|null|V99_MISSING|17|R|held|'
    legacy = read + b'17|gone|defined|V99_MISSING|'
    assert stdout == legacy + b'F|A|'
    values = [*initial, *reach('S_capture','S_initial','INTRINSIC_DEFINED',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_has)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.SENT = eps', 'S_capture.SELECTEDCALLS = eps', 'S_capture.SELECTSEQ = 0',
        'S_capture.USERCONSTANTS = eps',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("other")) = (n_other)',
        '$lookup(S_capture.ENV,$ptascii("name")) = (n_name)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("weakRead")) = (n_weak_read_cv)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_has)',
        'S_capture.STORE[n_other] = DEFINED (POBJECT n_read)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.STORE[n_weak_read_cv] = DEFINED (POBJECT n_weak_read)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_has)',
        'S_capture.OBJECTS[n_weak_read] = WEAKREFERENCE (n_read)',
        *intrinsic('S_capture','n_has','INTRINSIC_DEFINED'),
        *intrinsic('S_capture','n_read','INTRINSIC_CONSTANT'), 'n_has =/= n_read',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_has]',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_has) = 2',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_read) = 1',
        *reach('S','S_capture','INTRINSIC_DEFINED',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_has*',
        'pconfigcall.OWNER = (n_has)', 'pconfigcall.SELECTION = eps',
        'pconfigcall.PACKS = eps', 'pconfigcall.NAMED', 'pconfigcall.INDEX = 1',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name)]',
        '$string_bytes(pvalue_name) = (' + text('\\V99_LATE') + ')',
        '$dynamic_global_constant_known(S,pconfigcall.SITE) = eps',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_owned_global_query_valid(S,pconfigcall)',
        '~$dynamic_global_constant_valid(S,pconfigcall)',
        'S.USERCONSTANTS = [puserconstant_late]',
        'puserconstant_late.NAME = $ptascii("V99_LATE")',
        'puserconstant_late.VALUE = PINT 17', 'puserconstant_late.CLASS = PVSCALAR',
        '$dynamic_define_source(S,puserconstant_late.ORIGIN)',
        '$dynamic_global_constant_value(S,$ptascii("V99_LATE")) = (PINT 17)',
        'S.STORE[n_call] = DEFINED (POBJECT n_read)',
        'S.STORE[n_other] = DEFINED PNULL', 'S.STORE[n_name] = DEFINED pvalue_current_name',
        '$string_bytes(pvalue_current_name) = ($ptascii("V99_MISSING"))',
        '$heap_owners($heap_graph(S),HOBJECT n_has) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_read) = 1',
        '$weakref_get(S,n_weak) = POBJECT n_has',
        'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0', '~$destructor_operational(S)',
        '$test_outputs(S.EVENTS) = ' + term(before), *controls('S','pconfigcall','n_has','has'),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_has','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_has_found',
        'S_has.TODO = ptask_has*', '~(HOBJECT n_has <- S_has.ALLOCATIONS)',
        '$weakref_get(S_has,n_weak) = PNULL', *unchanged('S','S_has'),
        *reach('S_reader_capture','S_has','INTRINSIC_CONSTANT',0),
        'S_reader_capture.TODO = (CONFIG_ARGS pconfigcall_reader_capture) :: ptask_reader_capture*',
        'pconfigcall_reader_capture.OWNER = (n_read)',
        'pconfigcall_reader_capture.SELECTION = eps', 'pconfigcall_reader_capture.SENT = eps',
        'S_reader_capture.STORE[n_call] = DEFINED (POBJECT n_read)',
        '$heap_owners($heap_graph(S_reader_capture),HOBJECT n_read) = 2',
        'S_reader_capture.USERCONSTANTS = S.USERCONSTANTS',
        'S_reader_capture.SELECTEDCALLS = eps', 'S_reader_capture.SELECTSEQ = 0',
        *reach('S_read','S_reader_capture','INTRINSIC_CONSTANT',1),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_read)', 'pconfigcall_read.SELECTION = eps',
        'pconfigcall_read.NAMED', 'pconfigcall_read.PACKS = eps',
        'pconfigcall_read.SENT = [NAMED_SENT (KNOWN pvalue_read_name)]',
        '$string_bytes(pvalue_read_name) = (' + text('\\V99_LATE') + ')',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '$dynamic_global_constant_valid(S_read,pconfigcall_read)',
        'S_read.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        '$heap_owners($heap_graph(S_read),HOBJECT n_read) = 1',
        '$weakref_get(S_read,n_weak_read) = POBJECT n_read',
        'S_read.SELECTEDCALLS = eps', 'S_read.SELECTSEQ = 0',
        '$test_outputs(S_read.EVENTS) = ' + term(read),
        *common.step('S_value','S_read','PINT 17'),
        'S_value.TODO = ptask_read*', '~(HOBJECT n_read <- S_value.ALLOCATIONS)',
        '$weakref_get(S_value,n_weak_read) = PNULL', *unchanged('S_read','S_value'),
        *reach('S_legacy','S_value','INTRINSIC_DEFINED',2),
        'S_legacy.TODO = (CONFIG_INVOKE pconfigcall_legacy) :: ptask_legacy*',
        'pconfigcall_legacy.OWNER = eps', 'pconfigcall_legacy.SELECTION = (0)',
        'S_legacy.SELECTEDCALLS = [pselectedcall_legacy]', 'S_legacy.SELECTSEQ = 1',
        'pselectedcall_legacy.OWNER = eps', 'pselectedcall_legacy.KIND = INTRINSIC_DEFINED',
        '$selected_entry_source_valid(S_legacy,pselectedcall_legacy)',
        '$config_selected_valid(S_legacy,pconfigcall_legacy)',
        '~$dynamic_owned_global_query_valid(S_legacy,pconfigcall_legacy)',
        '$test_outputs(S_legacy.EVENTS) = ' + term(legacy),
        *common.step('S_absent','S_legacy','PBOOL false'),
        'S_absent.TODO = ptask_legacy*', *unchanged('S_legacy','S_absent'),
        *define.finish('S_absent',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.SELECTEDCALLS = S_legacy.SELECTEDCALLS', 'S_final.SELECTSEQ = 1',
        '~(HOBJECT n_has <- S_final.ALLOCATIONS)', '~(HOBJECT n_read <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak <- S_final.ALLOCATIONS)', '~(HOBJECT n_weak_read <- S_final.ALLOCATIONS)']
    return values


def array(initial, stdout):
    leaf = text('leaf')
    prefix = b'B|N|held|'
    queried = prefix + b'17|23|31|defined|V99_MISSING|'
    assert stdout == queried + b'17|41|history|same|held|A|'
    values = [*initial, *reach('S_capture','S_initial','INTRINSIC_CONSTANT',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_reader)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.SENT = eps', 'S_capture.SELECTEDCALLS = eps', 'S_capture.SELECTSEQ = 0',
        *intrinsic('S_capture','n_reader','INTRINSIC_CONSTANT'),
        'S_capture.USERCONSTANTS = [puserconstant_reader,puserconstant_tree]',
        'puserconstant_reader.NAME = $ptascii("V99_READER")',
        'puserconstant_reader.VALUE = POBJECT n_reader', 'puserconstant_reader.CLASS = PVOBJECT',
        'puserconstant_tree.NAME = $ptascii("V99_TREE")',
        'puserconstant_tree.VALUE = PARRAY n_root',
        f'puserconstant_tree.CLASS = PVARRAY false ([(KSTRING {leaf},PVSCALAR)])',
        'parray_root = S_capture.ARRAYS[n_root]',
        f'parray_root.ITEMS = [ENTRY (KSTRING {leaf}) (DIRECT (PINT 17))]',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S_capture.ENV,$ptascii("raw")) = (n_raw_cv)',
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_reader)',
        'S_capture.STORE[n_input_cv] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_raw_cv] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_cell] = DEFINED (PINT 17)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_reader)',
        f'S_capture.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        'S_capture.ARRAYS[n_input].NEXT = 91',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_reader) = 3',
        *reach('S','S_capture','INTRINSIC_CONSTANT',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_reader)', 'pconfigcall.SELECTION = eps',
        'pconfigcall.NAMED', 'pconfigcall.PACKS = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name)]',
        '$string_bytes(pvalue_name) = (' + text('\\V99_TREE') + ')',
        '$dynamic_owned_global_query_valid(S,pconfigcall)', '$dynamic_global_constant_valid(S,pconfigcall)',
        '$dynamic_global_constant_value(S,$ptascii("V99_TREE")) = (PARRAY n_root)',
        'S.ARRAYS[n_root] = parray_root', 'S.STORE[n_cell] = DEFINED (PINT 23)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)',
        '$entry_lookup(S.ARRAYS[n_caller].ITEMS,KINT 90) = (DIRECT (PINT 31))',
        'HARRAY n_caller <- $pools_nodes(S.POOLS)',
        'S.STORE[n_call] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = ($ptascii("defined"))',
        '$heap_owners($heap_graph(S),HOBJECT n_reader) = 2',
        '$heap_owners($heap_graph(S),HARRAY n_root) = 1',
        '$config_nodes(pconfigcall) = [HOBJECT n_reader]',
        'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0', '~$destructor_operational(S)',
        '$test_outputs(S.EVENTS) = ' + term(prefix),
        *controls('S','pconfigcall','n_reader','array'),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        *common.step('S_value','S','PARRAY n_root'),
        '$drive_steps($test_running(S_pause),1) = S_value_found',
        'S_value.TODO = ptask_initial*', *unchanged('S','S_value'),
        '$heap_owners($heap_graph(S_value),HARRAY n_root) = 2',
        '$heap_owners($heap_graph(S_value),HOBJECT n_reader) = 1',
        '$weakref_get(S_value,n_weak) = POBJECT n_reader',
        *common.reach('S_query','S_value',0,'V99_TREE'), *common.public('S_query'),
        'S_query.TODO = (CONFIG_INVOKE pconfigcall_query) :: ptask_query*',
        'pconfigcall_query.OWNER = eps', '$dynamic_global_constant_valid(S_query,pconfigcall_query)',
        '$lookup(S_query.ENV,$ptascii("local")) = (n_local_cv)',
        'S_query.STORE[n_local_cv] = DEFINED (PARRAY n_local)', 'n_local =/= n_root',
        f'S_query.ARRAYS[n_local].ITEMS = [ENTRY (KSTRING {leaf}) (DIRECT (PINT 41)),ENTRY (KINT 0) (DIRECT (PINT 5))]',
        f'$entry_lookup(S_query.ARRAYS[n_input].ITEMS,KSTRING {leaf}) = (ALIAS n_cell)',
        '$entry_lookup(S_query.ARRAYS[n_input].ITEMS,KINT 91) = (DIRECT (PINT 7))',
        'S_query.ARRAYS[n_input].NEXT = 92', 'S_query.STORE[n_cell] = DEFINED (PINT 23)',
        'S_query.ARRAYS[n_root] = parray_root',
        '$array_append_key(S_query.ARRAYS[n_root]) = KINT 0',
        '$test_outputs(S_query.EVENTS) = ' + term(queried),
        *common.step('S_queried','S_query','PARRAY n_root'),
        *define.finish('S_queried',stdout),
        'S_final.USERCONSTANTS = S_capture.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0',
        'S_final.ARRAYS[n_root] = parray_root',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_reader) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_local <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)', '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        'HARRAY n_caller <- $pools_nodes(S_final.POOLS)',
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
