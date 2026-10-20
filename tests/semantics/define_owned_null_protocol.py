#!/usr/bin/env python3
"""Captured NULL flags separate strict rejection from weak post-callback copying."""
import argparse
from pathlib import Path
import sys

import define_null_flag_protocol as null
import define_owned_closure_protocol as owned
import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_protocol as prior
import typed_static_invoke_set_protocol as process_base
import define_owned_null_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = sources.DIRECT
PREFIX = owned.PREFIX + runtime.PREFIX[len(define.PREFIX):] + null.PREFIX


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
        '~$dynamic_null_define_flag_valid(S,pconfigcall[.OWNER = eps])',
        '~$dynamic_null_define_flag_valid(S,pconfigcall[.SELECTION = eps])',
        'S_missing = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$heap_graph(S_missing) = $heap_graph(S)',
        '~$dynamic_null_define_flag_valid(S_missing,pconfigcall)',
        '~$dynamic_define_source(S_missing,pconfigcall.SITE)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_first)]',
        '$selected_entry_source_valid(S_dead,pselectedcall_first)',
        '~$dynamic_null_define_flag_valid(S_dead,pconfigcall)',
        'pconfigcall_object = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_first))]',
        '$dynamic_define_value_class(S,POBJECT n_first) = (PVOBJECT)',
        '$dynamic_null_define_flag_valid(S,pconfigcall_object)']
    # These are pure validator projections, never replacement machine steps.
    for label, value in [('false','PBOOL false'),('true','PBOOL true'),('quiet','PINT 0')]:
        call = 'pconfigcall_' + label
        values += [f'{call} = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN ({value}))]',
            f'$config_invoke_valid(S,{call})',
            f'~$dynamic_null_define_flag_call({call})',
            f'~$dynamic_null_define_flag_valid(S,{call})']
    return values


def direct(initial, stdout):
    strict = b'B|N|held|S|define|V97_OWNED_NULL|17|null|gone|absent|0|97|31|'
    warned = strict + b'N|held|H|8192|1|held|'
    values = [*begin(initial),
        '$lookup(S_capture.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_capture.ENV,$ptascii("snapshot")) = (n_snapshot)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_value] = DEFINED (PINT 17)',
        'S_capture.STORE[n_snapshot] = DEFINED PNULL',
        'S_capture.STORE[n_result] = DEFINED (PINT 97)',
        *owned.capture('S_args','S_capture',1),
        'S_args.TODO = (CONFIG_ARGS pconfigcall_args) :: ptask_capture*',
        'pconfigcall_args.OWNER = (n_first)', 'pconfigcall_args.SELECTION = (0)',
        'pconfigcall_args.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PINT 17)),NAMED_SENT (KNOWN PNULL)]',
        'pconfigcall_args.NAMED',
        'S_args.STORE[n_value] = DEFINED (PINT 17)',
        *null.reach('S','S_args',0,'PINT 17'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_first)', 'pconfigcall.SELECTION = (0)',
        '$dynamic_null_define_flag_values(pconfigcall) = (($ptascii("V97_OWNED_NULL"),PINT 17))',
        '$config_invoke_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '$exit_strict(S,pconfigcall.SITE)', '~$config_method_receiver(S,pconfigcall)',
        '$dynamic_null_define_flag_call(pconfigcall)', '$dynamic_null_define_flag_valid(S,pconfigcall)',
        '~$dynamic_owned_define_header(S,pconfigcall)', '~$dynamic_owned_define_valid(S,pconfigcall)',
        '~$call_task_valid(S,DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall)',
        'S.USERCONSTANTS = eps', 'S.STORE[n_snapshot] = DEFINED PNULL',
        'S.STORE[n_value] = DEFINED (PINT 31)',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.STORE[n_calls] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 97)',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_first]',
        '$heap_owners($heap_graph(S),HOBJECT n_first) = 1',
        '~$destructor_operational(S)', '$test_outputs(S.EVENTS) = ' + term(b'B|N|held|'),
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_error','S'), *common.public('S_error'),
        '$drive_steps($test_running(S_pause),1) = S_error_found',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "TypeError"', 'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, null given"))',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall.LINE',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_strict_trace',
        'S_error.ARRAYS[n_strict_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_strict_frame))]',
        '$trace_array_field(S_error,n_strict_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_strict_frame,$ptascii("args")) = PARRAY n_strict_args',
        '$entry_lookup(S_error.ARRAYS[n_strict_args].ITEMS,KINT 0) = (DIRECT pvalue_strict_name)',
        '$string_bytes(pvalue_strict_name) = ($ptascii("V97_OWNED_NULL"))',
        '$entry_lookup(S_error.ARRAYS[n_strict_args].ITEMS,KINT 1) = (DIRECT (PINT 17))',
        '$entry_lookup(S_error.ARRAYS[n_strict_args].ITEMS,KINT 2) = (DIRECT PNULL)',
        'S_error.USERCONSTANTS = eps', 'S_error.STORE = S.STORE',
        'S_error.EVENTS = S.EVENTS', 'S_error.SELECTEDCALLS = S.SELECTEDCALLS',
        '~(HOBJECT n_first <- S_error.ALLOCATIONS)', '$weakref_get(S_error,n_weak) = PNULL',
        '$selected_entry_source_valid(S_error,pselectedcall_first)',
        *owned.capture('S_second','S_error'),
        'S_second.TODO = (CONFIG_ARGS pconfigcall_second) :: ptask_second*',
        *owned.receipt('S_second','pconfigcall_second','second',1,0),
        'S_second.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        'n_first =/= n_second', 'S_second.USERCONSTANTS = eps',
        'S_second.STORE[n_value] = DEFINED (PINT 41)',
        'S_second.STORE[n_calls] = DEFINED (PINT 0)',
        'S_second.STORE[n_weak_cv] = DEFINED (POBJECT n_weak_second)',
        'S_second.OBJECTS[n_weak_second] = WEAKREFERENCE (n_second)',
        '~(HOBJECT n_first <- S_second.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_second.ALLOCATIONS)',
        '$test_outputs(S_second.EVENTS) = ' + term(strict),
        *null.reach('S_weak','S_second',0,'PINT 41'),
        'S_weak.TODO = (CONFIG_INVOKE pconfigcall_weak) :: ptask_weak*',
        'pconfigcall_weak.OWNER = (n_second)', 'pconfigcall_weak.SELECTION = (1)',
        '$dynamic_null_define_flag_values(pconfigcall_weak) = (($ptascii("V97_OWNED_NULL"),PINT 41))',
        '$config_invoke_valid(S_weak,pconfigcall_weak)',
        '$exit_strict(S_weak,pconfigcall_weak.SITE)', '$config_method_receiver(S_weak,pconfigcall_weak)',
        '~$config_strict(S_weak,pconfigcall_weak)',
        '$dynamic_null_define_flag_valid(S_weak,pconfigcall_weak)',
        '~$dynamic_owned_define_header(S_weak,pconfigcall_weak)',
        'S_weak.USERCONSTANTS = eps', 'S_weak.STORE[n_value] = DEFINED (PINT 31)',
        'S_weak.STORE[n_call] = DEFINED pvalue_weak_call',
        '$string_bytes(pvalue_weak_call) = ($ptascii("defined"))',
        '$heap_owners($heap_graph(S_weak),HOBJECT n_second) = 1',
        *common.step('S_dispatch','S_weak'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_weak*',
        'perrorcall.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_weak',
        'perrorcall.LEVEL = 8192', 'perrorcall.MESSAGE = $dynamic_null_define_flag_message()',
        '$error_call_valid(S_dispatch,perrorcall)',
        'S_dispatch.STORE = S_weak.STORE', 'S_dispatch.EVENTS = S_weak.EVENTS',
        *null.reach('S_resume','S_dispatch',1,'PINT 41'),
        'S_resume.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_weak) :: ptask_weak*',
        '$call_task_valid(S_resume,DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_weak)',
        'S_resume.USERCONSTANTS = eps', 'S_resume.STORE[n_value] = DEFINED (PINT 53)',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.STORE[n_snapshot] = DEFINED (PARRAY n_trace)',
        '|S_resume.ARRAYS[n_trace].ITEMS| = 3',
        '$entry_lookup(S_resume.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_report))',
        '$entry_lookup(S_resume.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_api))',
        '$entry_lookup(S_resume.ARRAYS[n_trace].ITEMS,KINT 2) = (DIRECT (PARRAY n_frame_invoke))',
        '$trace_array_field(S_resume,n_frame_report,$ptascii("function")) = PSTRING ($ptascii("v97Report"))',
        '$trace_array_field(S_resume,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_resume,n_frame_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_resume,n_frame_api,$ptascii("args")) = PARRAY n_args_api',
        '$trace_array_field(S_resume,n_frame_invoke,$ptascii("args")) = PARRAY n_args_invoke',
        '$entry_lookup(S_resume.ARRAYS[n_args_api].ITEMS,KINT 1) = (DIRECT (PINT 41))',
        '$entry_lookup(S_resume.ARRAYS[n_args_api].ITEMS,KINT 2) = (DIRECT PNULL)',
        '$strict_check(S_resume,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_second) = 1',
        '~$destructor_operational(S_resume)',
        '$test_outputs(S_resume.EVENTS) = ' + term(warned),
        *owned.transfer('S_row','S_resume','n_second','true','ptask_weak*'),
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = $ptascii("V97_OWNED_NULL")',
        'puserconstant_row.ORIGIN = pconfigcall_weak.SITE',
        'pconfigcall_weak.SITE =/= pconfigcall.SITE',
        'puserconstant_row.VALUE = PINT 41', 'puserconstant_row.CLASS = PVSCALAR',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        '$weakref_get(S_row,n_weak_second) = PNULL',
        *common.reach('S_query','S_row',0,'V97_OWNED_NULL'), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,$ptascii("V97_OWNED_NULL")) = (PINT 41)',
        '$selected_entry_source_valid(S_query,pselectedcall_first)',
        '$selected_entry_source_valid(S_query,pselectedcall_second)',
        '$dynamic_define_source(S_query,pconfigcall_weak.SITE)',
        'S_query_missing = S_query[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$user_constants_valid(S_query_missing,S_query_missing.USERCONSTANTS)',
        *define.finish('S_query',stdout),
        'S_final.USERCONSTANTS = [puserconstant_row]',
        'S_final.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        '~(HOBJECT n_first <- S_final.ALLOCATIONS)', '~(HOBJECT n_second <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak_second <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_strict_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args_api <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args_invoke <- S_final.ALLOCATIONS)']
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
        *null.reach('S','S_capture',0,'PARRAY n_input'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_first)', 'pconfigcall.SELECTION = (0)',
        '$dynamic_null_define_flag_values(pconfigcall) = (($ptascii("V97_ARRAY_NULL"),PARRAY n_input))',
        '$exit_strict(S,pconfigcall.SITE)', '$config_method_receiver(S,pconfigcall)',
        '~$config_strict(S,pconfigcall)', '$dynamic_null_define_flag_valid(S,pconfigcall)',
        '~$dynamic_owned_define_header(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        '~$dynamic_constant_case_valid(S,pconfigcall)',
        'S.USERCONSTANTS = eps', 'S.STORE[n_cell] = DEFINED (PINT 23)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S.ARRAYS[n_caller].ITEMS = [ENTRY (KINT 90) (DIRECT (PINT 31))]',
        'HARRAY n_caller <- $pools_nodes(S.POOLS)',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.ARRAYS[n_input] = S_capture.ARRAYS[n_input]',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HARRAY n_input,HOBJECT n_first]',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_first) = 1',
        *controls(),
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_initial*',
        'perrorcall.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall',
        'perrorcall.LEVEL = 8192', 'perrorcall.MESSAGE = $dynamic_null_define_flag_message()',
        '$error_call_valid(S_dispatch,perrorcall)',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.EVENTS = S.EVENTS',
        *null.reach('S_resume','S_dispatch',1,'PARRAY n_input'),
        'S_resume.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall) :: ptask_initial*',
        'S_resume.STORE[n_cell] = DEFINED (PINT 41)',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.ARRAYS[n_input] = S.ARRAYS[n_input]', 'S_resume.USERCONSTANTS = eps',
        '$dynamic_array_call_valid(S_resume,pconfigcall)',
        '~$destructor_operational(S_resume)',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_first) = 1',
        '$test_outputs(S_resume.EVENTS) = ' + term(b'B|N|held|H|8192|held|'),
        'n_root = |S_resume.ARRAYS|',
        f'parray_root = $array_insert($array_empty(),KSTRING {leaf},DIRECT (PINT 41))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {leaf},PVSCALAR)])',
        '$dynamic_array_value(S_resume,PARRAY n_input,eps,true) = ((S_copy,PARRAY n_root,pvalueclass_tree))',
        'S_copy.ARRAYS = S_resume.ARRAYS ++ [parray_root]',
        'S_pause = $drive_steps(S_resume,0)', 'S_pause = S_resume[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S_resume',
        *common.step('S_row','S_resume','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.ARRAYS = S_copy.ARRAYS',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = $ptascii("V97_ARRAY_NULL")',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0',
        '$node_children(S_row,HARRAY n_root) = eps',
        '$heap_owners($heap_graph(S_row),HARRAY n_root) = 1',
        '~(HOBJECT n_first <- S_row.ALLOCATIONS)', '$weakref_get(S_row,n_weak) = PNULL',
        *common.reach('S_query','S_row',0,'V97_ARRAY_NULL'), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,$ptascii("V97_ARRAY_NULL")) = (PARRAY n_root)',
        'S_query_missing = S_query[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$user_constants_valid(S_query_missing,S_query_missing.USERCONSTANTS)',
        '$dynamic_global_constant_value(S_query_missing,$ptascii("V97_ARRAY_NULL")) = (PARRAY n_root)',
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
