#!/usr/bin/env python3
"""Reached NULL-array reception, post-Deprecated bodies and strict/raw traces."""
import argparse
from pathlib import Path
import sys

import define_array_scalar_flag_protocol as scalar
import define_array_null_flag_sources as sources

define, packet, common = scalar.define, scalar.packet, scalar.common
ROOT, text = scalar.ROOT, scalar.text
PREFIX = define.PREFIX + r'''
dec $test_array_null_front(pstate, nat, preqbytes) : bool
def $test_array_null_front(S,0,preqbytes) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))
def $test_array_null_front(S,1,preqbytes) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))
def $test_array_null_front(S,2,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_null_define_flag_values(pconfigcall) = ((preqbytes,PARRAY n_input))
def $test_array_null_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_array_null_seek(pstate, nat, preqbytes, nat) : pstate
def $test_array_null_seek(S,n_phase,preqbytes,0) = S
def $test_array_null_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_array_null_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_null_seek(S,n_phase,preqbytes,n) = $test_array_null_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_null_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, target):
    return [f'{state}_found = $test_array_null_seek({start},{phase},{text(target)},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_null_front({state},{phase},{text(target)})', *common.public(state)]


def capture(initial, target):
    return [*initial, *reach('S', 'S_initial', 2, target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_null_define_flag_values(pconfigcall) = ((' + text(target) + ',PARRAY n_input))',
        '$dynamic_define_values(pconfigcall) = $dynamic_null_define_flag_values(pconfigcall)',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN PNULL)',
        '$dynamic_null_define_flag_valid(S,pconfigcall)',
        '~$dynamic_scalar_define_flag_call(pconfigcall)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING ' + text('edge') + ') (ALIAS n_cell)]',
        'S.ARRAYS[n_input].NEXT = 91',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps']


def dispatch(values, budget=False):
    values += ['~$config_strict(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        '$call_task_valid(S,DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall)']
    if budget:
        values += ['S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)', 'S_resume = S']
    values += [*common.step('S_dispatch', 'S_resume' if budget else 'S'),
        *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall',
        'perrorcall.LEVEL = 8192', 'perrorcall.MESSAGE = $dynamic_null_define_flag_message()',
        '$error_call_valid(S_dispatch,perrorcall)',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_input]']
    return values


def literal(initial, stdout):
    assert stdout == b'B|D|8192|T|23|split|31|true|zero|53|23|D|8192|W|2|F|17|41|defined|2|1|false|A|'
    edge, tag = text('edge'), text('tag')
    values = capture(initial, 'V77_FRESH') + [
        'S.USERCONSTANTS = eps', 'S.STORE[n_flag] = DEFINED PNULL',
        'S.STORE[n_cell] = DEFINED (PARRAY n_input)',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 3',
        # Undriven source/carrier/liveness controls; no body traversal at reception.
        '~$dynamic_array_known_matches(S,PARRAY n_input,(PINT 17))',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '~$dynamic_null_define_flag_valid(S_dead,pconfigcall)',
        '~$dynamic_array_call_valid(S_dead,pconfigcall)',
        'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("V77_FRESH"))',
        'pconfigcall_bad = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '$dynamic_null_define_flag_call(pconfigcall_bad)',
        '~$dynamic_null_define_flag_valid(S,pconfigcall_bad)',
        '~$dynamic_array_call_valid(S,pconfigcall_bad)']
    dispatch(values, True)
    values += [*reach('S_done', 'S_dispatch', 0, 'V77_FRESH'),
        'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_done*',
        'perrorcall_done.RESUME = perrorcall.RESUME', 'S_done.RESULT = KNOWN (PBOOL true)',
        'S_done.STORE[n_flag] = DEFINED (PBOOL true)',
        'S_done.STORE[n_cell] = DEFINED (PARRAY n_leaf23)',
        f'S_done.ARRAYS[n_leaf23].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 23))]',
        'S_done.STORE[n_input_cell] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'$entry_lookup(S_done.ARRAYS[n_caller].ITEMS,KSTRING {edge}) = (ALIAS n_cell)',
        '$entry_lookup(S_done.ARRAYS[n_caller].ITEMS,KINT 90) = (DIRECT (PINT 31))',
        'S_done.ARRAYS[n_input] = S.ARRAYS[n_input]', 'S_done.USERCONSTANTS = eps',
        '$dynamic_array_recursive(S_done,PARRAY n_input,eps) = (false)',
        '$heap_owners($heap_graph(S_done),HARRAY n_input) = 1',
        '$dynamic_null_define_flag_valid(S_done,pconfigcall)', '~$destructor_operational(S_done)',
        *common.step('S_body', 'S_done'), *common.public('S_body'),
        'S_body.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall) :: ptask_done*',
        'S_body.ARRAYS = S_done.ARRAYS', 'n_child = |S_body.ARRAYS|', 'n_root = $(n_child + 1)',
        f'parray_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 23))',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
        *common.step('S_row', 'S_body', 'PBOOL true'), *common.public('S_row'),
        'S_row.TODO = ptask_done*', 'S_row.ARRAYS = S_body.ARRAYS ++ [parray_child,parray_root]',
        '$user_constant_at(S_row.USERCONSTANTS,$ptascii("V77_FRESH")) = (puserconstant_fresh)',
        'S_row.USERCONSTANTS = [puserconstant_fresh]',
        'puserconstant_fresh.VALUE = PARRAY n_root', 'puserconstant_fresh.ORIGIN = pconfigcall.SITE',
        f'puserconstant_fresh.CLASS = PVARRAY false ([(KSTRING {edge},PVARRAY false ([(KSTRING {tag},PVSCALAR)]))])',
        'puserconstant_fresh.READS = eps', 'puserconstant_fresh.RECEIVES = eps',
        '$heap_owners($heap_graph(S_row),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_row),HARRAY n_child) = 1',
        '~(HARRAY n_input <- S_row.ALLOCATIONS)',
        *common.reach('S_query', 'S_row', 0, 'V77_FRESH'), *common.public('S_query'),
        'n_query_owners = $heap_owners($heap_graph(S_query),HARRAY n_root)',
        *common.step('S_value', 'S_query', 'PARRAY n_root'),
        'S_value.ARRAYS = S_query.ARRAYS', 'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
        '$heap_owners($heap_graph(S_value),HARRAY n_root) = $(n_query_owners + 1)',
        *define.reach('S_second', 'S_value', 0, 'V77_DUPLICATE'),
        'S_second.TODO = (CONFIG_INVOKE pconfigcall_second) :: ptask_second*',
        '$dynamic_null_define_flag_values(pconfigcall_second) = (($ptascii("V77_DUPLICATE"),PARRAY n_caller))',
        'pconfigcall_second.NAMED', 'pconfigcall_second.SELECTION = (n_selection)',
        'S_second.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'S_second.USERCONSTANTS = [puserconstant_fresh]',
        'S_second.STORE[n_flag] = DEFINED PNULL',
        'S_second.ARRAYS[n_caller].NEXT = 91',
        f'S_second.ARRAYS[n_caller].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        '$lookup(S_second.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_second.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_root',
        f'$entry_lookup(S_second.ARRAYS[n_copy].ITEMS,KSTRING {edge}) = (DIRECT (PARRAY n_copy_child))',
        f'S_second.ARRAYS[n_copy_child].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 53))]',
        '$entry_lookup(S_second.ARRAYS[n_copy].ITEMS,KINT 0) = (DIRECT (PINT 19))',
        'S_second.ARRAYS[n_root] = parray_root', 'S_second.ARRAYS[n_child] = parray_child',
        *common.step('S_second_dispatch', 'S_second'), *common.public('S_second_dispatch'),
        'S_second_dispatch.ARRAYS = S_second.ARRAYS',
        *reach('S_second_done', 'S_second_dispatch', 0, 'V77_DUPLICATE'),
        'S_second_done.TODO = (ERROR_HANDLER_RESULT perrorcall_second_done) :: ptask_second_done*',
        'perrorcall_second_done.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_second',
        'S_second_done.STORE[n_flag] = DEFINED (PBOOL false)',
        'S_second_done.STORE[n_cell] = DEFINED (PARRAY n_leaf29)',
        f'S_second_done.ARRAYS[n_leaf29].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 29))]',
        '$user_constant_at(S_second_done.USERCONSTANTS,$ptascii("V77_DUPLICATE")) = (puserconstant_old)',
        'puserconstant_old.VALUE = PINT 17',
        'S_second_done.USERCONSTANTS = [puserconstant_fresh,puserconstant_old]',
        '$dynamic_null_define_flag_valid(S_second_done,pconfigcall_second)',
        '~$dynamic_null_define_flag_duplicate_valid(S_second_done,pconfigcall_second,2)',
        '$dynamic_array_duplicate_call_valid(S_second_done,pconfigcall_second,2)',
        *common.step('S_second_body', 'S_second_done'), *common.public('S_second_body'),
        'S_second_body.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_second) :: ptask_second_done*',
        'n_candidate_child = |S_second_body.ARRAYS|', 'n_candidate = $(n_candidate_child + 1)',
        f'parray_candidate_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 29))',
        f'parray_candidate = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_candidate_child))',
        *common.step('S_duplicate', 'S_second_body'), *common.public('S_duplicate'),
        'S_duplicate.TODO = (ERROR_HANDLER_INVOKE perrorcall_duplicate) :: ptask_second_done*',
        'perrorcall_duplicate.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall_second n_candidate pvalueclass_candidate 2',
        'perrorcall_duplicate.LEVEL = 2',
        'perrorcall_duplicate.MESSAGE = $global_constant_duplicate_message($ptascii("V77_DUPLICATE"))',
        'S_duplicate.ARRAYS = S_second_body.ARRAYS ++ [parray_candidate_child,parray_candidate]',
        'S_duplicate.USERCONSTANTS = S_second_done.USERCONSTANTS',
        '$heap_owners($heap_graph(S_duplicate),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_duplicate),HARRAY n_candidate_child) = 1',
        '$dynamic_array_duplicate_valid(S_duplicate,pconfigcall_second,n_candidate,pvalueclass_candidate,2)',
        *reach('S_warning_done', 'S_duplicate', 1, 'V77_DUPLICATE'),
        'S_warning_done.TODO = (ERROR_HANDLER_RESULT perrorcall_warning_done) :: ptask_warning_done*',
        'perrorcall_warning_done.RESUME = perrorcall_duplicate.RESUME',
        'S_warning_done.STORE[n_cell] = DEFINED (PARRAY n_leaf41)',
        f'S_warning_done.ARRAYS[n_leaf41].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 41))]',
        'S_warning_done.ARRAYS[n_candidate_child] = parray_candidate_child',
        '$dynamic_array_duplicate_valid(S_warning_done,pconfigcall_second,n_candidate,pvalueclass_candidate,2)',
        *common.step('S_duplicate_body', 'S_warning_done'), *common.public('S_duplicate_body'),
        'S_duplicate_body.TODO = perrorcall_duplicate.RESUME :: ptask_warning_done*',
        *common.step('S_false', 'S_duplicate_body', 'PBOOL false'), *common.public('S_false'),
        'S_false.TODO = ptask_warning_done*', 'S_false.USERCONSTANTS = S_second_done.USERCONSTANTS',
        '~(HARRAY n_candidate <- S_false.ALLOCATIONS)',
        '~(HARRAY n_candidate_child <- S_false.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_false),HARRAY n_caller) = 1',
        *define.finish('S_false', stdout),
        'S_final.USERCONSTANTS = S_second_done.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)', '~(HARRAY n_copy <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)']
    return values


def error(initial, stdout, strict):
    target = 'V77_STRICT_NULL' if strict else 'V77_CYCLE'
    values = capture(initial, target) + [
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))']
    if strict:
        values += ['$config_strict(S,pconfigcall)', '~$dynamic_array_call_valid(S,pconfigcall)',
            '~$call_task_valid(S,DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall)',
            'pconfigcall.SITE = PORIGIN 1 pcpath_call',
            'S.STORE[n_cell] = DEFINED (PARRAY n_input)',
            'S.STORE[n_flag] = DEFINED (PBOOL true)',
            'S.STORE[n_calls] = DEFINED (PINT 0)',
            '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
            'S.USERCONSTANTS = eps', 'S_before = S']
        tail = 'ptask_tail*'
    else:
        values += ['S.STORE[n_flag] = DEFINED PNULL',
            '$dynamic_array_recursive(S,PARRAY n_input,eps) = (false)',
            '$user_constant_at(S.USERCONSTANTS,$ptascii("V77_CYCLE")) = (puserconstant_old)',
            'puserconstant_old.VALUE = PINT 17', 'S.USERCONSTANTS = [puserconstant_old]']
        dispatch(values)
        values += [*reach('S_done', 'S_dispatch', 0, target),
            'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_done*',
            'perrorcall_done.RESUME = perrorcall.RESUME',
            'S_done.STORE[n_flag] = DEFINED (PBOOL true)',
            'S_done.STORE[n_calls] = DEFINED (PINT 1)',
            'S_done.STORE[n_cell] = DEFINED (PARRAY n_input)',
            'S_done.USERCONSTANTS = S.USERCONSTANTS',
            '$dynamic_array_recursive(S_done,PARRAY n_input,eps) = (true)',
            '$dynamic_array_value(S_done,PARRAY n_input,eps,true) = eps',
            *common.step('S_before', 'S_done'), *common.public('S_before'),
            'S_before.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall) :: ptask_done*']
        tail = 'ptask_done*'
    message = 'define(): Argument #3 ($case_insensitive) must be of type bool, null given' if strict else 'define(): Argument #2 ($value) cannot be a recursive array'
    values += ['$heap_owners($heap_graph(S_before),HARRAY n_input) = 3',
        'n_arrays = |S_before.ARRAYS|', 'n_error = |S_before.OBJECTS|',
        *common.step('S_error', 'S_before'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ' + tail,
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S_before.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "' + ('TypeError' if strict else 'ValueError') + '"',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text(message) + ')',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT PNULL)',
        'n_trace = n_arrays', 'n_args = $(n_arrays + 1)', 'n_frame = $(n_arrays + 2)',
        'parray_trace = S_error.ARRAYS[n_trace]', 'parray_args = S_error.ARRAYS[n_args]',
        'parray_frame = S_error.ARRAYS[n_frame]']
    if strict:
        values += ['n_eval = $(n_arrays + 3)',
            '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_eval))',
            '$trace_array_field(S_error,n_eval,$ptascii("function")) = PSTRING ($ptascii("eval"))',
            'parray_eval = S_error.ARRAYS[n_eval]',
            'S_error.ARRAYS = S_before.ARRAYS ++ [parray_trace,parray_args,parray_frame,parray_eval]']
    else:
        values += ['S_error.ARRAYS = S_before.ARRAYS ++ [parray_trace,parray_args,parray_frame]']
    values += ['S_error.STORE = S_before.STORE', 'S_error.EVENTS = S_before.EVENTS',
        'S_error.USERCONSTANTS = S_before.USERCONSTANTS',
        '$heap_owners($heap_graph(S_error),HARRAY n_input) = 3',
        *define.finish('S_error', stdout), 'S_final.USERCONSTANTS = S.USERCONSTANTS',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)', '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)', '~(HARRAY n_frame <- S_final.ALLOCATIONS)']
    return values


def non_eval(initial, stdout):
    return error(initial, stdout, False) if b'cannot be a recursive array' in stdout else literal(initial, stdout)


def strict(initial, stdout):
    return error(initial, stdout, True)


scalar.sources, scalar.literal, scalar.strict, scalar.PREFIX = sources, non_eval, strict, PREFIX
packet.sources, packet.prepare = sources, scalar.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == "null-deprecation-repairs-cycle-and-selects-late-duplicate":
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
