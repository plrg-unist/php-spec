#!/usr/bin/env python3
"""Reached byte-only flags, normal duplicate copies and strict raw traces."""
import argparse
from pathlib import Path
import sys

import define_array_scalar_flag_protocol as scalar
import define_array_byte_flag_sources as sources

define, packet, common = scalar.define, scalar.packet, scalar.common
ROOT, text = scalar.ROOT, scalar.text
PREFIX = define.PREFIX + r'''
dec $test_array_byte_front(pstate, nat) : bool
def $test_array_byte_front(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall
def $test_array_byte_front(S,1) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
def $test_array_byte_front(S,n_phase) = false -- otherwise
dec $test_array_byte_seek(pstate, nat, nat) : pstate
def $test_array_byte_seek(S,n_phase,0) = S
def $test_array_byte_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_array_byte_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_byte_seek(S,n_phase,n) = $test_array_byte_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_byte_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_array_byte_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_byte_front({state},{phase})', *common.public(state)]


def literal(initial, stdout):
    assert stdout == b'B|T|7|H|1|2|H|2|2|F|7|41|split|31|empty|T|19|2|A|'
    edge, tag = text('edge'), text('tag')
    values = [*initial, *define.reach('S', 'S_initial', 0, 'V78_ROW'),
        'S.TODO = (CONFIG_INVOKE pconfigcall_zero) :: ptask_zero*',
        '$dynamic_scalar_define_flag_values(pconfigcall_zero) = (($ptascii("V78_ROW"),PARRAY n_input,pvalue_zero))',
        'pvalue_zero = PSTRING ($ptascii("0"))',
        '$dynamic_constant_class(pvalue_zero) = eps', '$value_nodes(pvalue_zero) = eps',
        '$dynamic_array_quiet_flag(pvalue_zero)', '$dynamic_scalar_define_flag_valid(S,pconfigcall_zero)',
        '~$dynamic_scalar_define_flag_case_valid(S,pconfigcall_zero)',
        '$dynamic_array_call_valid(S,pconfigcall_zero)',
        '$lookup(S.ENV,$ptascii("flags")) = (n_flags_cell)',
        'S.STORE[n_flags_cell] = DEFINED (PARRAY n_pool)',
        'parray_flags = S.ARRAYS[n_pool]',
        '$entry_lookup(parray_flags.ITEMS,KINT 0) = (DIRECT pvalue_zero)',
        '$entry_lookup(parray_flags.ITEMS,KINT 1) = (DIRECT (PSTRING ($ptascii("false"))))',
        '$entry_lookup(parray_flags.ITEMS,KINT 2) = (DIRECT (PSTRING eps))',
        'HARRAY n_pool <- $pools_nodes(S.POOLS)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S.ARRAYS[n_input].NEXT = 91', 'S.USERCONSTANTS = eps',
        'n_child = |S.ARRAYS|', 'n_root = $(n_child + 1)',
        f'parray_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 7))',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
        *common.step('S_row', 'S', 'PBOOL true'), *common.public('S_row'),
        'S_row.TODO = ptask_zero*', 'S_row.ARRAYS = S.ARRAYS ++ [parray_child,parray_root]',
        'S_row.EVENTS = S.EVENTS', 'S_row.STRINGDATA = S.STRINGDATA',
        '$user_constant_at(S_row.USERCONSTANTS,$ptascii("V78_ROW")) = (puserconstant_old)',
        'S_row.USERCONSTANTS = [puserconstant_old]', 'puserconstant_old.VALUE = PARRAY n_root',
        f'puserconstant_old.CLASS = PVARRAY false ([(KSTRING {edge},PVARRAY false ([(KSTRING {tag},PVSCALAR)]))])',
        '$heap_owners($heap_graph(S_row),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_row),HARRAY n_child) = 1',
        *common.reach('S_query', 'S_row', 0, 'V78_ROW'), *common.public('S_query'),
        'n_query_owners = $heap_owners($heap_graph(S_query),HARRAY n_root)',
        *common.step('S_value', 'S_query', 'PARRAY n_root'),
        'S_value.ARRAYS = S_query.ARRAYS', 'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
        '$heap_owners($heap_graph(S_value),HARRAY n_root) = $(n_query_owners + 1)',
        *define.reach('S_true', 'S_value', 0, 'V78_ROW'),
        'S_true.TODO = (CONFIG_INVOKE pconfigcall_true) :: ptask_true*',
        'pconfigcall_true.NAMED', 'pconfigcall_true.SELECTION = (n_selection)',
        'S_true.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_scalar_define_flag_values(pconfigcall_true) = (($ptascii("V78_ROW"),PARRAY n_input,pvalue_raw))',
        'pvalue_raw = PSTRING ($ptascii("false"))', '$dynamic_constant_class(pvalue_raw) = eps',
        '$dynamic_scalar_define_flag_valid(S_true,pconfigcall_true)',
        '$dynamic_scalar_define_flag_case_valid(S_true,pconfigcall_true)',
        '$dynamic_array_call_valid(S_true,pconfigcall_true)',
        'S_true.STORE[n_flags_cell] = DEFINED (PARRAY n_flags)', 'n_flags =/= n_pool',
        '$entry_lookup(S_true.ARRAYS[n_flags].ITEMS,KINT 1) = (DIRECT pvalue_live_zero)',
        '$string_bytes(pvalue_live_zero) = ($ptascii("0"))',
        'S_true.ARRAYS[n_pool] = parray_flags', 'S_true.USERCONSTANTS = [puserconstant_old]',
        # Pure byte/carrier/header controls, never driven.
        '$dynamic_array_quiet_flag(PSTRING eps)', '~$truth(S_true,PSTRING eps)',
        '~$truth(S_true,pvalue_zero)', '$truth(S_true,pvalue_raw)',
        '~$dynamic_array_quiet_flag(PSTRING ([256]))',
        'pconfigcall_bad = pconfigcall_true[.SENT = $named_slot_set(pconfigcall_true.SENT,2,KNOWN (PSTRING ([256])))]',
        '~$dynamic_scalar_define_flag_valid(S_true,pconfigcall_bad)',
        '~$dynamic_array_call_valid(S_true,pconfigcall_bad)',
        'n_bad_string = |S_true.STRINGDATA|',
        'pvalue_bad_carrier = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("false"))',
        'pconfigcall_carrier = pconfigcall_true[.SENT = $named_slot_set(pconfigcall_true.SENT,2,KNOWN pvalue_bad_carrier)]',
        '~$dynamic_scalar_define_flag_valid(S_true,pconfigcall_carrier)',
        'S_pause = $drive_steps(S_true,0)', 'S_pause = S_true[.COMPLETION = BUDGET]',
        'S_resume = $test_running(S_pause)', 'S_resume = S_true',
        *common.step('S_dispatch', 'S_resume'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_true*',
        'perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_true',
        'perrorcall.MESSAGE = $dynamic_constant_case_message()', 'perrorcall.LEVEL = 2',
        'S_dispatch.ARRAYS = S_true.ARRAYS', 'S_dispatch.ALLOCATIONS = S_true.ALLOCATIONS',
        'S_dispatch.USERCONSTANTS = S_true.USERCONSTANTS',
        *reach('S_done', 'S_dispatch', 0),
        'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_done*',
        'perrorcall_done.RESUME = perrorcall.RESUME', 'S_done.RESULT = KNOWN (PBOOL true)',
        'S_done.STORE[n_cell] = DEFINED (PARRAY n_leaf23)',
        f'S_done.ARRAYS[n_leaf23].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 23))]',
        'S_done.STORE[n_input_cell] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'$entry_lookup(S_done.ARRAYS[n_caller].ITEMS,KSTRING {edge}) = (ALIAS n_cell)',
        '$entry_lookup(S_done.ARRAYS[n_caller].ITEMS,KINT 90) = (DIRECT (PINT 31))',
        'S_done.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '$entry_lookup(S_done.ARRAYS[n_flags].ITEMS,KINT 1) = (DIRECT pvalue_empty)',
        '$string_bytes(pvalue_empty) = (eps)', 'S_done.ARRAYS[n_pool] = parray_flags',
        'S_done.USERCONSTANTS = S_true.USERCONSTANTS',
        '~$destructor_operational(S_done)',
        *common.step('S_body', 'S_done'), *common.public('S_body'),
        'S_body.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_true) :: ptask_done*',
        '$dynamic_array_duplicate_call_valid(S_body,pconfigcall_true,1)',
        '~$dynamic_scalar_define_flag_duplicate_valid(S_body,pconfigcall_true,1)',
        'n_candidate_child = |S_body.ARRAYS|', 'n_candidate = $(n_candidate_child + 1)',
        f'parray_candidate_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 23))',
        f'parray_candidate = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_candidate_child))',
        *common.step('S_duplicate', 'S_body'), *common.public('S_duplicate'),
        'S_duplicate.TODO = (ERROR_HANDLER_INVOKE perrorcall_duplicate) :: ptask_done*',
        'perrorcall_duplicate.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall_true n_candidate pvalueclass_candidate 1',
        'perrorcall_duplicate.LEVEL = 2',
        'perrorcall_duplicate.MESSAGE = $global_constant_duplicate_message($ptascii("V78_ROW"))',
        'S_duplicate.ARRAYS = S_body.ARRAYS ++ [parray_candidate_child,parray_candidate]',
        'S_duplicate.USERCONSTANTS = [puserconstant_old]',
        '$dynamic_array_duplicate_valid(S_duplicate,pconfigcall_true,n_candidate,pvalueclass_candidate,1)',
        '$heap_owners($heap_graph(S_duplicate),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_duplicate),HARRAY n_candidate_child) = 1',
        *reach('S_warning_done', 'S_duplicate', 1),
        'S_warning_done.TODO = (ERROR_HANDLER_RESULT perrorcall_warning) :: ptask_warning*',
        'perrorcall_warning.RESUME = perrorcall_duplicate.RESUME',
        'S_warning_done.STORE[n_cell] = DEFINED (PARRAY n_leaf41)',
        f'S_warning_done.ARRAYS[n_leaf41].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 41))]',
        'S_warning_done.ARRAYS[n_candidate_child] = parray_candidate_child',
        '$dynamic_array_duplicate_valid(S_warning_done,pconfigcall_true,n_candidate,pvalueclass_candidate,1)',
        *common.step('S_pending', 'S_warning_done'), *common.public('S_pending'),
        'S_pending.TODO = perrorcall_duplicate.RESUME :: ptask_warning*',
        *common.step('S_false', 'S_pending', 'PBOOL false'), *common.public('S_false'),
        'S_false.TODO = ptask_warning*', 'S_false.USERCONSTANTS = [puserconstant_old]',
        '~(HARRAY n_candidate <- S_false.ALLOCATIONS)',
        '~(HARRAY n_candidate_child <- S_false.ALLOCATIONS)',
        '~(HARRAY n_input <- S_false.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_false),HARRAY n_caller) = 1',
        *define.reach('S_empty', 'S_false', 0, 'V78_EMPTY'),
        'S_empty.TODO = (CONFIG_INVOKE pconfigcall_empty) :: ptask_empty*',
        '$dynamic_scalar_define_flag_values(pconfigcall_empty) = (($ptascii("V78_EMPTY"),PARRAY n_empty_input,PSTRING eps))',
        '$dynamic_scalar_define_flag_valid(S_empty,pconfigcall_empty)',
        '~$dynamic_scalar_define_flag_case_valid(S_empty,pconfigcall_empty)',
        'n_empty_root = |S_empty.ARRAYS|',
        f'parray_empty = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 19))',
        *common.step('S_empty_row', 'S_empty', 'PBOOL true'), *common.public('S_empty_row'),
        'S_empty_row.ARRAYS = S_empty.ARRAYS ++ [parray_empty]',
        '$user_constant_at(S_empty_row.USERCONSTANTS,$ptascii("V78_EMPTY")) = (puserconstant_empty)',
        'S_empty_row.USERCONSTANTS = [puserconstant_old,puserconstant_empty]',
        'puserconstant_empty.VALUE = PARRAY n_empty_root', 'S_empty_row.EVENTS = S_empty.EVENTS',
        *define.finish('S_empty_row', stdout),
        'S_final.USERCONSTANTS = S_empty_row.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        'S_final.ARRAYS[n_empty_root] = parray_empty',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_empty_root) = 1',
        'S_final.ARRAYS[n_pool] = parray_flags', 'HARRAY n_pool <- $pools_nodes(S_final.POOLS)',
        '~(HARRAY n_flags <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)']
    return values

def strict(initial, stdout):
    values = [*initial, *define.reach('S', 'S_initial', 0, 'V78_STRICT_BYTES'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SITE = PORIGIN 1 pcpath_call',
        'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_scalar_define_flag_values(pconfigcall) = (($ptascii("V78_STRICT_BYTES"),PARRAY n_input,pvalue_flag))',
        'pvalue_flag = PSTRING ($ptascii("false"))',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '~$dynamic_array_call_valid(S,pconfigcall)',
        '~$dynamic_scalar_define_flag_case_valid(S,pconfigcall)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        '$lookup(S.ENV,$ptascii("flags")) = (n_flags_cell)', '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)', '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_input)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S.STORE[n_flags_cell] = DEFINED (PARRAY n_flags)',
        '$entry_lookup(S.ARRAYS[n_flags].ITEMS,KINT 0) = (DIRECT pvalue_current)',
        '$string_bytes(pvalue_current) = ($ptascii("0"))',
        '$dynamic_constant_class(pvalue_flag) = eps', '$value_nodes(pvalue_flag) = eps', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_result] = DEFINED pvalue_result', '$string_bytes(pvalue_result) = ($ptascii("kept"))',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = eps',
        'S.USERCONSTANTS = eps', '$heap_owners($heap_graph(S),HARRAY n_input) = 3',
        'n_arrays = |S.ARRAYS|', 'n_error = |S.OBJECTS|',
        *common.step('S_error', 'S'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "TypeError"',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, string given"))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT pvalue_flag)',
        'n_trace = n_arrays', 'n_args = $(n_arrays + 1)', 'n_frame = $(n_arrays + 2)',
        'n_eval = $(n_arrays + 3)',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_eval))',
        '$trace_array_field(S_error,n_eval,$ptascii("function")) = PSTRING ($ptascii("eval"))',
        'parray_trace = S_error.ARRAYS[n_trace]', 'parray_args = S_error.ARRAYS[n_args]',
        'parray_frame = S_error.ARRAYS[n_frame]', 'parray_eval = S_error.ARRAYS[n_eval]',
        'S_error.ARRAYS = S.ARRAYS ++ [parray_trace,parray_args,parray_frame,parray_eval]',
        'S_error.STORE = S.STORE',
        'S_error.USERCONSTANTS = S.USERCONSTANTS', 'S_error.EVENTS = S.EVENTS',
        '$heap_owners($heap_graph(S_error),HARRAY n_input) = 3',
        *define.finish('S_error', stdout), 'S_final.USERCONSTANTS = eps',
        '~(HARRAY n_flags <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)', '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)', '~(HARRAY n_frame <- S_final.ALLOCATIONS)']
    return values


scalar.sources, scalar.literal, scalar.strict, scalar.PREFIX = sources, literal, strict, PREFIX
packet.sources, packet.prepare = sources, scalar.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == "pooled-byte-flags-and-normal-duplicate-snapshot":
        timeout = 150
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
