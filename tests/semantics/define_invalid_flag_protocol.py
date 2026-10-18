#!/usr/bin/env python3
"""Reached invalid flag rejection, raw trace owners and real alias writes."""
import argparse
from pathlib import Path
import sys

import define_array_scalar_flag_protocol as prior
import define_invalid_flag_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
PREFIX = define.PREFIX + r'''
dec $test_invalid_flag_front(pstate, nat, preqbytes) : bool
def $test_invalid_flag_front(S,0,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if $dynamic_define_invalid_flag_values(pconfigcall) = ((preqbytes,pvalue,pvalue_flag))
def $test_invalid_flag_front(S,1,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_slot) metadata_slot) :: expression_tail*
  -- if $base64(text_slot) = $ptascii("slot")
def $test_invalid_flag_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_invalid_flag_seek(pstate, nat, preqbytes, nat) : pstate
def $test_invalid_flag_seek(S,n_phase,preqbytes,0) = S
def $test_invalid_flag_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_invalid_flag_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_invalid_flag_seek(S,n_phase,preqbytes,n) = $test_invalid_flag_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_invalid_flag_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, target):
    return [f'{state}_found = $test_invalid_flag_seek({start},{phase},{text(target)},{1000 if phase == 1 else 500})',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_invalid_flag_front({state},{phase},{text(target)})']


def error(value, value_node, strict=False):
    values = ['n_arrays = |S.ARRAYS|', 'n_error = |S.OBJECTS|',
        f'n_value_owners = $heap_owners($heap_graph(S),{value_node})',
        'n_flag_owners = $heap_owners($heap_graph(S),HARRAY n_flag_root)',
        *common.step('S_error','S'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "TypeError"',
        'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, array given"))',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall.LINE',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        f'$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT ({value}))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PARRAY n_flag_root))',
        'n_trace = n_arrays', 'n_args = $(n_arrays + 1)', 'n_frame = $(n_arrays + 2)',
        f'$heap_owners($heap_graph(S_error),{value_node}) = n_value_owners',
        '$heap_owners($heap_graph(S_error),HARRAY n_flag_root) = n_flag_owners']
    tables = ['S_error.ARRAYS[n_trace]', 'S_error.ARRAYS[n_args]', 'S_error.ARRAYS[n_frame]']
    if strict:
        values += ['n_eval = $(n_arrays + 3)',
            '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_eval))',
            '$trace_array_field(S_error,n_eval,$ptascii("function")) = PSTRING ($ptascii("eval"))']
        tables += ['S_error.ARRAYS[n_eval]']
    values += ['S_error.ARRAYS = S.ARRAYS ++ [' + ','.join(tables) + ']']
    values += [f'S_error.{field} = S.{field}' for field in
        ['STORE','ENV','USERCONSTANTS','CONSTANTOBJECTS','CONSTANTSTDOBJECTS','EVENTS','ERRORHANDLER']]
    return values


def literal(initial, stdout):
    edge, ref = text('edge'), text('ref')
    values = [*initial, *reach('S','S_initial',0,'V81_OLD'), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_define_invalid_flag_values(pconfigcall) = (($ptascii("V81_OLD"),PARRAY n_input,PARRAY n_flag_root))',
        '$dynamic_define_invalid_flag_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HARRAY n_input,HARRAY n_flag_root]',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("flagCell")) = (n_flag_cell)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag_cv)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_input)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S.ARRAYS[n_input].NEXT = 91',
        f'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        f'S.ARRAYS[n_flag_root].ITEMS = [ENTRY (KSTRING {ref}) (ALIAS n_flag_cell)]',
        'S.ARRAYS[n_flag_root].NEXT = 91',
        'S.STORE[n_flag_cell] = DEFINED (PINT 23)',
        'S.STORE[n_flag_cv] = DEFINED (PBOOL false)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V81_OLD")) = (puserconstant_old)',
        'puserconstant_old.VALUE = PINT 17', 'S.USERCONSTANTS = [puserconstant_old]',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 2',
        '$heap_owners($heap_graph(S),HARRAY n_flag_root) = 1',
        # Pure malformed/source/domain controls are never driven.
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall[.SELECTION = eps])',
        'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("V81_OLD"))',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '$config_invoke_valid(S,pconfigcall_bad_name)',
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall_bad_name)',
        'pconfigcall_bad_value = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN pvalue_bad_name)]',
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall_bad_value)',
        'S_dead_flag = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_flag_root)]',
        '~$dynamic_define_invalid_flag_valid(S_dead_flag,pconfigcall)',
        'S_dead_value = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '~$dynamic_define_invalid_flag_valid(S_dead_value,pconfigcall)',
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PARRAY (|S.ARRAYS|)))])',
        '~$dynamic_define_rejected_flag(PBOOL true)', '~$dynamic_define_rejected_flag(PNULL)',
        '~$dynamic_define_rejected_flag(PINT 0)',
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN (PSTRING ($ptascii("A::B"))))])',
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN (PSTRING ($ptascii("PHP_VERSION"))))])',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S']
    values += error('PARRAY n_input','HARRAY n_input')
    values += ['$drive_steps($test_running(S_pause),1) = S_error_found',
        *reach('S_bucket','S_error',1,'V81_OLD'), *common.public('S_bucket'),
        '$lookup(S_bucket.ENV,$ptascii("rawFlag")) = (n_raw_flag_cv)',
        '$lookup(S_bucket.ENV,$ptascii("slot")) = (n_flag_cell)',
        'n_flag_cell <- S_bucket.REFCELLS', 'S_bucket.STORE[n_flag_cell] = DEFINED (PINT 41)',
        'S_bucket.STORE[n_raw_flag_cv] = DEFINED (PARRAY n_flag_copy)', 'n_flag_copy =/= n_flag_root',
        f'S_bucket.ARRAYS[n_flag_copy] = $array_insert(S.ARRAYS[n_flag_root],KINT 91,DIRECT (PINT 53))',
        'S_bucket.ARRAYS[n_flag_root] = S.ARRAYS[n_flag_root]',
        '$entry_lookup(S_bucket.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PARRAY n_flag_root))',
        'S_bucket.STORE[n_cell] = DEFINED (PARRAY n_leaf)',
        f'S_bucket.ARRAYS[n_leaf].ITEMS = [ENTRY (KSTRING {text("tag")}) (DIRECT (PINT 43))]',
        'S_bucket.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_bucket.USERCONSTANTS = S.USERCONSTANTS',
        'S_bucket.STORE[n_calls] = DEFINED (PINT 0)',
        *define.finish('S_bucket',stdout), 'S_final.USERCONSTANTS = S.USERCONSTANTS',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_flag_root <- S_final.ALLOCATIONS)', '~(HARRAY n_flag_copy <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)', '~(HCELL n_flag_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)', '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)', '~(HARRAY n_frame <- S_final.ALLOCATIONS)']
    return values


def strict(initial, stdout):
    values = [*initial, *reach('S','S_initial',0,'V81_STRICT'), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = PORIGIN 1 pcpath_call',
        '$dynamic_define_invalid_flag_values(pconfigcall) = (($ptascii("V81_STRICT"),POBJECT n_left,PARRAY n_flag_root))',
        '$dynamic_define_invalid_flag_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V81_LEFT")) = (puserconstant_left)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V81_RIGHT")) = (puserconstant_right)',
        'puserconstant_left.VALUE = POBJECT n_left', 'puserconstant_right.VALUE = POBJECT n_right',
        'n_left =/= n_right', '$array_immutable(S,n_flag_root)',
        'S.ARRAYS[n_flag_root] = $array_empty()',
        '$dynamic_define_invalid_flag_kind(S,POBJECT n_left)',
        'S_internal = S[.OBJECTS[n_left] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '$dynamic_define_invalid_flag_kind(S_internal,POBJECT n_left)',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_cv)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag_cv)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_cv] = DEFINED (POBJECT n_right)',
        'S.STORE[n_flag_cv] = DEFINED (PBOOL true)',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        *define.property_value('S','n_left',43,'strict_left'),
        '$source_constant_lookup(S,$ptascii("V81_STRICT")) = eps']
    values += error('POBJECT n_left','HOBJECT n_left',True)
    values += [*define.finish('S_error',stdout), 'S_final.USERCONSTANTS = S.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)', '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)', '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
        '~(HARRAY n_eval <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.literal, prior.strict, prior.PREFIX = sources, literal, strict, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
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
