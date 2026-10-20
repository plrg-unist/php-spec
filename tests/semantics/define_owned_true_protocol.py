#!/usr/bin/env python3
"""Owned ignored-case callbacks precede duplicate lookup and ARRAY snapshotting."""
import argparse
from pathlib import Path
import sys

import define_owned_closure_protocol as owned
import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_protocol as prior
import typed_static_invoke_set_protocol as process_base
import define_owned_true_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = sources.DIRECT
PREFIX = owned.PREFIX + runtime.PREFIX[len(define.PREFIX):] + r'''
dec $test_owned_true_case(pstate, preqbytes) : bool
def $test_owned_true_case(S,preqbytes) = true
  -- if S.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_owned_true_case(S,preqbytes) = false -- otherwise
dec $test_owned_true_case_seek(pstate, preqbytes, nat) : pstate
def $test_owned_true_case_seek(S,preqbytes,0) = S
def $test_owned_true_case_seek(S,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_owned_true_case(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_true_case_seek(S,preqbytes,n) = $test_owned_true_case_seek($drive_steps($test_running(S),1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_true_case(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def case(state, start, target):
    return [f'{state}_found = $test_owned_true_case_seek({start},{text(target)},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_true_case({state},{text(target)})', *common.public(state)]


def begin(initial):
    return [*initial, *owned.capture('S_capture','S_initial'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        *owned.receipt('S_capture','pconfigcall_capture','first',0,0),
        'S_capture.SELECTEDCALLS = [pselectedcall_first]', 'S_capture.SELECTSEQ = 1',
        'S_capture.USERCONSTANTS = eps', 'pconfigcall_capture.SENT = eps',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_first)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_first)',
        '$node_children(S_capture,HOBJECT n_weak) = eps',
        'S_capture.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_first) = 2']


def controls():
    values = [
        '~$dynamic_constant_case_valid(S,pconfigcall[.OWNER = eps])',
        '~$dynamic_constant_case_valid(S,pconfigcall[.SELECTION = eps])',
        'S_missing = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$heap_graph(S_missing) = $heap_graph(S)',
        '~$dynamic_constant_case_valid(S_missing,pconfigcall)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_first)]',
        '$selected_entry_source_valid(S_dead,pselectedcall_first)',
        '~$dynamic_constant_case_valid(S_dead,pconfigcall)',
        'pconfigcall_object = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_first))]',
        '$dynamic_owned_define_valid(S,pconfigcall_object)',
        '$dynamic_constant_case_valid(S,pconfigcall_object)']
    # These originals spell TRUE literally; the compiled argument also refuses FALSE.
    for label, value in [('false','PBOOL false'),('null','PNULL'),('quiet','PINT 0')]:
        call = 'pconfigcall_' + label
        values += [f'{call} = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN ({value}))]',
            f'$config_invoke_valid(S,{call})',
            f'~$dynamic_owned_define_header(S,{call})',
            f'~$dynamic_constant_case_valid(S,{call})']
    return values


def direct(initial, stdout):
    before = b'B|N|held|'
    installed = before + b'H|2|1|held|I|53|'
    warned = installed + b'H|2|2|held|O|53|'
    values = [*begin(initial),
        '$lookup(S_capture.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_capture.ENV,$ptascii("snapshot")) = (n_snapshot)',
        'S_capture.STORE[n_value] = DEFINED (PINT 17)',
        'S_capture.STORE[n_snapshot] = DEFINED PNULL',
        *owned.capture('S_args','S_capture',1),
        'S_args.TODO = (CONFIG_ARGS pconfigcall_args) :: ptask_capture*',
        'pconfigcall_args.OWNER = (n_first)', 'pconfigcall_args.SELECTION = (0)',
        'pconfigcall_args.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PINT 17)),NAMED_SENT (KNOWN (PBOOL true))]',
        'pconfigcall_args.NAMED', 'S_args.STORE[n_value] = DEFINED (PINT 17)',
        *define.reach('S','S_args',0,'V96_OWNED_TRUE'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_first)', 'pconfigcall.SELECTION = (0)',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V96_OWNED_TRUE"),PINT 17))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_owned_define_header(S,pconfigcall)', '$dynamic_owned_define_valid(S,pconfigcall)',
        '$dynamic_constant_case_valid(S,pconfigcall)', '~$dynamic_array_call_valid(S,pconfigcall)',
        'S.STORE[n_value] = DEFINED (PINT 31)',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.USERCONSTANTS = eps', 'S.STORE[n_snapshot] = DEFINED PNULL',
        '$heap_owners($heap_graph(S),HOBJECT n_first) = 1',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_first]',
        '~$destructor_operational(S)', '$test_outputs(S.EVENTS) = ' + term(before),
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        '$drive_steps($test_running(S_pause),1) = S_dispatch_found',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_case) :: ptask_initial*',
        'perrorcall_case.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall_case.LEVEL = 2', 'perrorcall_case.MESSAGE = $dynamic_constant_case_message()',
        '$error_call_valid(S_dispatch,perrorcall_case)',
        'S_dispatch.USERCONSTANTS = eps', 'S_dispatch.STORE = S.STORE',
        'S_dispatch.EVENTS = S.EVENTS',
        *define.reach('S_inner','S_dispatch',0,'V96_OWNED_TRUE'),
        'S_inner.TODO = (CONFIG_INVOKE pconfigcall_inner) :: ptask_inner*',
        'pconfigcall_inner.OWNER = eps', 'pconfigcall_inner.SELECTION = eps',
        'pconfigcall_inner.SITE =/= pconfigcall.SITE',
        '$dynamic_define_values(pconfigcall_inner) = (($ptascii("V96_OWNED_TRUE"),PINT 53))',
        'S_inner.CURRENT = (pcallcontext_handler)',
        '$error_context_call(S_inner,pcallcontext_handler) = (perrorcall_handler)',
        'perrorcall_handler.RESUME = perrorcall_case.RESUME',
        'S_inner.STORE[n_value] = DEFINED (PINT 41)',
        'S_inner.STORE[n_calls] = DEFINED (PINT 1)',
        'S_inner.STORE[n_snapshot] = DEFINED (PARRAY n_trace)',
        '|S_inner.ARRAYS[n_trace].ITEMS| = 2',
        '$entry_lookup(S_inner.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_report))',
        '$entry_lookup(S_inner.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_api))',
        '$trace_array_field(S_inner,n_frame_report,$ptascii("function")) = PSTRING ($ptascii("v96Report"))',
        '$trace_array_field(S_inner,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_inner,n_frame_api,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_inner.ARRAYS[n_args].ITEMS,KINT 0) = (DIRECT pvalue_name)',
        '$string_bytes(pvalue_name) = ($ptascii("V96_OWNED_TRUE"))',
        '$entry_lookup(S_inner.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PINT 17))',
        '$entry_lookup(S_inner.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        'S_inner.USERCONSTANTS = eps',
        '$heap_owners($heap_graph(S_inner),HOBJECT n_first) = 1',
        *common.step('S_inner_row','S_inner','PBOOL true'),
        'S_inner_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = $ptascii("V96_OWNED_TRUE")',
        'puserconstant_row.ORIGIN = pconfigcall_inner.SITE',
        'puserconstant_row.VALUE = PINT 53', 'puserconstant_row.CLASS = PVSCALAR',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        *case('S_case','S_inner_row','V96_OWNED_TRUE'),
        'S_case.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) :: ptask_initial*',
        'S_case.USERCONSTANTS = [puserconstant_row]',
        'S_case.STORE[n_calls] = DEFINED (PINT 1)',
        'S_case.STORE[n_value] = DEFINED (PINT 41)',
        '$dynamic_constant_case_valid(S_case,pconfigcall)',
        '$heap_owners($heap_graph(S_case),HOBJECT n_first) = 1',
        '$test_outputs(S_case.EVENTS) = ' + term(installed),
        *common.step('S_duplicate_dispatch','S_case'), *common.public('S_duplicate_dispatch'),
        'S_duplicate_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_duplicate) :: ptask_initial*',
        'perrorcall_duplicate.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1',
        'perrorcall_duplicate.LEVEL = 2',
        'perrorcall_duplicate.MESSAGE = $global_constant_duplicate_message($ptascii("V96_OWNED_TRUE"))',
        '$error_call_valid(S_duplicate_dispatch,perrorcall_duplicate)',
        'S_duplicate_dispatch.USERCONSTANTS = [puserconstant_row]',
        *define.reach('S_duplicate','S_duplicate_dispatch',4,'V96_OWNED_TRUE'),
        'S_duplicate.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1) :: ptask_initial*',
        'S_duplicate.USERCONSTANTS = [puserconstant_row]',
        'S_duplicate.STORE[n_calls] = DEFINED (PINT 2)',
        'S_duplicate.STORE[n_value] = DEFINED (PINT 41)',
        '$dynamic_constant_duplicate_valid(S_duplicate,pconfigcall,1)',
        '$heap_owners($heap_graph(S_duplicate),HOBJECT n_first) = 1',
        '$test_outputs(S_duplicate.EVENTS) = ' + term(warned),
        *owned.transfer('S_false','S_duplicate','n_first','false','ptask_initial*'),
        'S_false.USERCONSTANTS = [puserconstant_row]',
        '$weakref_get(S_false,n_weak) = PNULL',
        *common.reach('S_query','S_false',0,'V96_OWNED_TRUE'), *common.public('S_query'),
        'S_query.CURRENT = eps', 'S_query.FRAMES = eps',
        '$dynamic_global_constant_value(S_query,$ptascii("V96_OWNED_TRUE")) = (PINT 53)',
        '$selected_entry_source_valid(S_query,pselectedcall_first)',
        'S_query.ARRAYS[n_args] = S_inner.ARRAYS[n_args]',
        'S_query.STORE[n_calls] = DEFINED (PINT 2)',
        'S_query_missing = S_query[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$user_constants_valid(S_query_missing,S_query_missing.USERCONSTANTS)',
        '$dynamic_global_constant_value(S_query_missing,$ptascii("V96_OWNED_TRUE")) = (PINT 53)',
        *define.finish('S_query',stdout),
        'S_final.USERCONSTANTS = [puserconstant_row]',
        'S_final.SELECTEDCALLS = [pselectedcall_first]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        '~(HOBJECT n_first <- S_final.ALLOCATIONS)', '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)', '~(HARRAY n_args <- S_final.ALLOCATIONS)']
    return values


def array(initial, stdout):
    leaf = text('leaf')
    values = [*begin(initial),
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S_capture.ENV,$ptascii("raw")) = (n_raw)',
        'S_capture.STORE[n_cell] = DEFINED (PINT 17)', 'n_cell <- S_capture.REFCELLS',
        'S_capture.STORE[n_input_cv] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_raw] = DEFINED (PARRAY n_input)',
        f'S_capture.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        'S_capture.ARRAYS[n_input].NEXT = 91',
        *owned.capture('S_args','S_capture',1),
        'S_args.TODO = (CONFIG_ARGS pconfigcall_args) :: ptask_capture*',
        'pconfigcall_args.OWNER = (n_first)', 'pconfigcall_args.SELECTION = (0)',
        'pconfigcall_args.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL true))]',
        'S_args.STORE[n_cell] = DEFINED (PINT 17)',
        *define.reach('S','S_args',0,'V96_ARRAY_TRUE'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_first)', 'pconfigcall.SELECTION = (0)',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V96_ARRAY_TRUE"),PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_owned_define_header(S,pconfigcall)', '~$dynamic_owned_define_valid(S,pconfigcall)',
        '$dynamic_array_call_valid(S,pconfigcall)', '$dynamic_constant_case_valid(S,pconfigcall)',
        'S.USERCONSTANTS = eps', 'S.STORE[n_cell] = DEFINED (PINT 23)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S.ARRAYS[n_caller].ITEMS = [ENTRY (KINT 90) (DIRECT (PINT 31))]',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.ARRAYS[n_input] = S_capture.ARRAYS[n_input]',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HARRAY n_input,HOBJECT n_first]',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_first) = 1',
        *controls(),
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_initial*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $dynamic_constant_case_message()',
        '$error_call_valid(S_dispatch,perrorcall)',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.EVENTS = S.EVENTS',
        *case('S_case','S_dispatch','V96_ARRAY_TRUE'),
        'S_case.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) :: ptask_initial*',
        'S_case.STORE[n_cell] = DEFINED (PINT 41)',
        'S_case.STORE[n_calls] = DEFINED (PINT 1)',
        'S_case.ARRAYS[n_input] = S.ARRAYS[n_input]', 'S_case.USERCONSTANTS = eps',
        '$dynamic_constant_case_valid(S_case,pconfigcall)',
        '~$destructor_operational(S_case)',
        '$heap_owners($heap_graph(S_case),HOBJECT n_first) = 1',
        '$test_outputs(S_case.EVENTS) = ' + term(b'B|N|held|H|2|held|'),
        'n_root = |S_case.ARRAYS|',
        f'parray_root = $array_insert($array_empty(),KSTRING {leaf},DIRECT (PINT 41))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {leaf},PVSCALAR)])',
        '$dynamic_array_value(S_case,PARRAY n_input,eps,true) = ((S_copy,PARRAY n_root,pvalueclass_tree))',
        'S_copy.ARRAYS = S_case.ARRAYS ++ [parray_root]',
        'S_pause = $drive_steps(S_case,0)', 'S_pause = S_case[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S_case',
        *common.step('S_row','S_case','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.ARRAYS = S_copy.ARRAYS',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = $ptascii("V96_ARRAY_TRUE")',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0',
        '$node_children(S_row,HARRAY n_root) = eps',
        '$heap_owners($heap_graph(S_row),HARRAY n_root) = 1',
        '~(HOBJECT n_first <- S_row.ALLOCATIONS)', '$weakref_get(S_row,n_weak) = PNULL',
        *common.reach('S_query','S_row',0,'V96_ARRAY_TRUE'), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,$ptascii("V96_ARRAY_TRUE")) = (PARRAY n_root)',
        'S_query_missing = S_query[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$user_constants_valid(S_query_missing,S_query_missing.USERCONSTANTS)',
        '$dynamic_global_constant_value(S_query_missing,$ptascii("V96_ARRAY_TRUE")) = (PARRAY n_root)',
        *common.step('S_value','S_query','PARRAY n_root'),
        'S_value.ARRAYS = S_query.ARRAYS',
        *runtime.unset('S_observed','S_value','stored'),
        '$test_outputs(S_observed.EVENTS) = ' + term(stdout),
        '$lookup(S_observed.ENV,$ptascii("stored")) = (n_stored)',
        '$lookup(S_observed.ENV,$ptascii("again")) = (n_again)',
        '$lookup(S_observed.ENV,$ptascii("fresh")) = (n_fresh)',
        'S_observed.STORE[n_stored] = DEFINED (PARRAY n_local)', 'n_local =/= n_root',
        'S_observed.STORE[n_again] = DEFINED (PARRAY n_root)',
        'S_observed.STORE[n_fresh] = DEFINED (PARRAY n_root)',
        f'$entry_lookup(S_observed.ARRAYS[n_local].ITEMS,KSTRING {leaf}) = (DIRECT (PINT 0))',
        '$entry_lookup(S_observed.ARRAYS[n_local].ITEMS,KINT 0) = (DIRECT pvalue_local)',
        '$string_bytes(pvalue_local) = ($ptascii("local"))',
        'S_observed.ARRAYS[n_root] = parray_root',
        'S_observed.STORE[n_cell] = DEFINED (PINT 53)',
        f'$entry_lookup(S_observed.ARRAYS[n_input].ITEMS,KSTRING {leaf}) = (ALIAS n_cell)',
        '$entry_lookup(S_observed.ARRAYS[n_input].ITEMS,KINT 91) = (DIRECT pvalue_raw)',
        '$string_bytes(pvalue_raw) = ($ptascii("raw"))',
        '$entry_lookup(S_observed.ARRAYS[n_input].ITEMS,KINT 0) = eps',
        'S_observed.ARRAYS[n_input].NEXT = 92',
        'S_observed.ARRAYS[n_caller] = S.ARRAYS[n_caller]',
        'S_observed.STORE[n_calls] = DEFINED (PINT 1)',
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = [puserconstant_row]',
        'S_final.SELECTEDCALLS = [pselectedcall_first]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        'S_final.ARRAYS[n_root] = parray_root',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '~(HOBJECT n_first <- S_final.ALLOCATIONS)', '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)', '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        'HARRAY n_caller <- $pools_nodes(S_final.POOLS)',
        'HARRAY n_caller <- S_final.ALLOCATIONS',
        '$heap_owners($heap_graph(S_final),HARRAY n_caller) = 1',
        '~(HARRAY n_local <- S_final.ALLOCATIONS)']
    return values


def checks(initial, name, stdout):
    return (direct if name == DIRECT else array)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 420 if directory.parent.name == DIRECT else 240
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES)
    args, remaining = parser.parse_known_args()
    if args.case:
        sources.family.CASES = {args.case: sources.family.CASES[args.case]}
    sys.argv = [sys.argv[0], *remaining]
    raise SystemExit(0 if packet.main() else 1)
