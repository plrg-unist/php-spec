#!/usr/bin/env python3
"""Reached Closure flag errors, lexical alias recovery and strict raw captures."""
import argparse
from pathlib import Path
import sys

import define_array_scalar_flag_protocol as prior
import define_closure_flag_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
PREFIX = define.PREFIX + r'''
dec $test_closure_flag_front(pstate, nat, preqbytes) : bool
def $test_closure_flag_front(S,0,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if $dynamic_define_invalid_flag_values(pconfigcall) = ((preqbytes,pvalue,POBJECT n_flag))
def $test_closure_flag_front(S,1,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_raw) metadata_raw) :: expression_tail*
  -- if $base64(text_raw) = $ptascii("rawFlag")
def $test_closure_flag_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_closure_flag_seek(pstate, nat, preqbytes, nat) : pstate
def $test_closure_flag_seek(S,n_phase,preqbytes,0) = S
def $test_closure_flag_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_closure_flag_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_flag_seek(S,n_phase,preqbytes,n) = $test_closure_flag_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_flag_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, target):
    return [f'{state}_found = $test_closure_flag_seek({start},{phase},{text(target)},{1000 if phase else 500})',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_flag_front({state},{phase},{text(target)})']


def error(value, node, strict=False):
    values = ['n_arrays = |S.ARRAYS|', 'n_error = |S.OBJECTS|',
        f'n_value_owners = $heap_owners($heap_graph(S),{node})',
        'n_flag_owners = $heap_owners($heap_graph(S),HOBJECT n_flag)',
        *common.step('S_error','S'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "TypeError"',
        'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, Closure given"))',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall.LINE',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        f'$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT ({value}))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (POBJECT n_flag))',
        'n_trace = n_arrays', 'n_args = $(n_arrays + 1)', 'n_frame = $(n_arrays + 2)',
        f'$heap_owners($heap_graph(S_error),{node}) = n_value_owners',
        '$heap_owners($heap_graph(S_error),HOBJECT n_flag) = n_flag_owners']
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
    values = [*initial, *reach('S','S_initial',0,'V82_OLD'), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_define_invalid_flag_values(pconfigcall) = (($ptascii("V82_OLD"),PARRAY n_input,POBJECT n_flag))',
        '$dynamic_define_invalid_flag_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HARRAY n_input,HOBJECT n_flag]',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("valueCell")) = (n_value_cell)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag_cv)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV,$ptascii("invocations")) = (n_invocations)',
        'S.STORE[n_value_cell] = DEFINED (PARRAY n_input)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {text("edge")}) (ALIAS n_value_cell)]',
        'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        'S.OBJECTS[n_flag] = REALCLOSURE porigin_flag ([ALIAS n_cell]) eps',
        '$function_at(S.CLOSURETEMPLATES,porigin_flag) = (pfunction_flag)',
        '$closure_lexicals(pfunction_flag.CODE.EXPRESSIONS) = [LEXICAL ($ptascii("cell")) true z_capture]',
        '$typed_closure(S,n_flag)', '$closure_callable(S,n_flag)',
        '$dynamic_define_invalid_flag_kind(S,POBJECT n_flag)',
        '$dynamic_define_value_class(S,POBJECT n_flag) = eps',
        '$node_children(S,HOBJECT n_flag) = [HCELL n_cell]',
        'n_cell <- S.REFCELLS', 'S.STORE[n_cell] = DEFINED (PINT 23)',
        'S.STORE[n_flag_cv] = DEFINED (PBOOL false)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_invocations] = DEFINED (PINT 0)',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V82_OLD")) = (puserconstant_old)',
        'puserconstant_old.VALUE = PINT 17', 'S.USERCONSTANTS = [puserconstant_old]',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_flag) = 1',
        '$heap_owners($heap_graph(S),HCELL n_cell) = 2',
        # Pure authority checks are never driven.
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall[.SELECTION = eps])',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_flag)]',
        '~$typed_closure(S_dead,n_flag)', '~$dynamic_define_invalid_flag_valid(S_dead,pconfigcall)',
        'S_no_template = S[.CLOSURETEMPLATES = eps]',
        '~$typed_closure(S_no_template,n_flag)', '~$dynamic_define_invalid_flag_valid(S_no_template,pconfigcall)',
        'S_incomplete = S[.OBJECTS[n_flag] = REALCLOSURE porigin_flag ([UNINITIALIZED]) eps]',
        '~$typed_closure(S_incomplete,n_flag)', '~$dynamic_define_invalid_flag_valid(S_incomplete,pconfigcall)',
        'S_busy = S[.TODO = (CLOSURE_CAPTURE n_flag 1) :: S.TODO]',
        '~$typed_closure(S_busy,n_flag)',
        'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("V82_OLD"))',
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)])',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S']
    values += error('PARRAY n_input','HARRAY n_input')
    values += ['$drive_steps($test_running(S_pause),1) = S_error_found',
        '$node_children(S_error,HOBJECT n_flag) = [HCELL n_cell]',
        '$heap_owners($heap_graph(S_error),HCELL n_cell) = 2',
        'S_error.STORE[n_invocations] = DEFINED (PINT 0)',
        *reach('S_recovered','S_error',1,'V82_OLD'), *common.public('S_recovered'),
        '$lookup(S_recovered.ENV,$ptascii("rawFlag")) = (n_raw_cv)',
        'S_recovered.STORE[n_raw_cv] = DEFINED (POBJECT n_flag)',
        'S_recovered.OBJECTS[n_flag] = S.OBJECTS[n_flag]',
        '$node_children(S_recovered,HOBJECT n_flag) = [HCELL n_cell]',
        'S_recovered.STORE[n_cell] = DEFINED (PINT 41)',
        'S_recovered.STORE[n_invocations] = DEFINED (PINT 2)',
        'S_recovered.STORE[n_calls] = DEFINED (PINT 0)',
        '$entry_lookup(S_recovered.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (POBJECT n_flag))',
        'S_recovered.STORE[n_value_cell] = DEFINED (PARRAY n_leaf)',
        f'S_recovered.ARRAYS[n_leaf].ITEMS = [ENTRY (KSTRING {text("tag")}) (DIRECT (PINT 43))]',
        'S_recovered.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_recovered.USERCONSTANTS = S.USERCONSTANTS',
        *define.finish('S_recovered',stdout), 'S_final.USERCONSTANTS = S.USERCONSTANTS',
        '~(HOBJECT n_flag <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HCELL n_value_cell <- S_final.ALLOCATIONS)', '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)', '~(HARRAY n_args <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)']
    return values


def strict(initial, stdout):
    values = [*initial, *reach('S','S_initial',0,'V82_STRICT'), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = PORIGIN 1 pcpath_call',
        '$dynamic_define_invalid_flag_values(pconfigcall) = (($ptascii("V82_STRICT"),POBJECT n_left,POBJECT n_flag))',
        '$dynamic_define_invalid_flag_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V82_LEFT")) = (puserconstant_left)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V82_RIGHT")) = (puserconstant_right)',
        'puserconstant_left.VALUE = POBJECT n_left', 'puserconstant_right.VALUE = POBJECT n_right',
        'n_left =/= n_right',
        'S.OBJECTS[n_flag] = NAMEDCLOSURE porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction_flag)',
        'pfunction_flag.NAME = ($ptascii("v82StrictFlag"))',
        '$typed_closure(S,n_flag)', '$node_children(S,HOBJECT n_flag) = eps',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_cv)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag_cv)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV,$ptascii("invocations")) = (n_invocations)',
        'S.STORE[n_cv] = DEFINED (POBJECT n_right)',
        'S.STORE[n_flag_cv] = DEFINED (PBOOL true)',
        'S.STORE[n_calls] = DEFINED (PINT 0)', 'S.STORE[n_invocations] = DEFINED (PINT 0)',
        '$heap_owners($heap_graph(S),HOBJECT n_flag) = 1',
        *define.property_value('S','n_left',43,'strict_left'),
        '$source_constant_lookup(S,$ptascii("V82_STRICT")) = eps']
    values += error('POBJECT n_left','HOBJECT n_left',True)
    values += [*define.finish('S_error',stdout), 'S_final.USERCONSTANTS = S.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '~(HOBJECT n_flag <- S_final.ALLOCATIONS)', '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)', '~(HARRAY n_args <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)', '~(HARRAY n_eval <- S_final.ALLOCATIONS)']
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
