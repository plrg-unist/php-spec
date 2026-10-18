#!/usr/bin/env python3
"""Reached ignored-case Warning order, live validation and pending registration."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_array_true_flag_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
MESSAGE = 'define(): Argument #2 ($value) cannot be a recursive array'
PREFIX = define.PREFIX + r'''
dec $test_array_case_front(pstate, nat, preqbytes) : bool
def $test_array_case_front(S,0,preqbytes) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_array_case_front(S,1,preqbytes) = true
  -- if S.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_array_case_front(S,2,preqbytes) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_array_case_front(S,3,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_bucket) metadata_variable) :: expression_tail*
  -- if $base64(text_bucket) = $ptascii("bucket")
  -- if $lookup(S.ENV,$ptascii("bucket")) = (n_cell)
def $test_array_case_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_array_case_seek(pstate, nat, preqbytes, nat) : pstate
def $test_array_case_seek(S,n_phase,preqbytes,0) = S
def $test_array_case_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_array_case_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_case_seek(S,n_phase,preqbytes,n) = $test_array_case_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_case_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, target):
    return [f'{state}_found = $test_array_case_seek({start},{phase},{text(target)},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_case_front({state},{phase},{text(target)})', *common.public(state)]


def capture(initial, target, budget=False):
    values = [*initial, *define.reach('S', 'S_initial', 0, target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$dynamic_define_values(pconfigcall) = ((' + text(target) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$dynamic_array_call_valid(S,pconfigcall)', '$dynamic_constant_case_valid(S,pconfigcall)',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (false)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S.ARRAYS[n_input].NEXT = 91',
        # Validator-only projections are never executed.
        '$dynamic_array_known_matches(S,PARRAY n_input,eps)',
        '~$dynamic_array_known_matches(S,PARRAY n_input,(PINT 17))',
        'pconfigcall_false = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PBOOL false))]',
        '$dynamic_array_call_valid(S,pconfigcall_false)',
        '~$dynamic_constant_case_valid(S,pconfigcall_false)',
        'pconfigcall_nonbool = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PINT 1))]',
        '$dynamic_define_values(pconfigcall_nonbool) = eps',
        '~$dynamic_array_call_valid(S,pconfigcall_nonbool)',
        'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text(target),
        '~$string_carrier_valid(S,pvalue_bad_name)',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '$dynamic_array_call_valid(S,pconfigcall_bad_name)',
        '~$dynamic_constant_case_valid(S,pconfigcall_bad_name)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '~$dynamic_constant_case_valid(S_dead,pconfigcall)']
    start = 'S'
    if budget:
        values += ['S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)', 'S_resume = S']
        start = 'S_resume'
    values += [*common.step('S_dispatch', start), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_case) :: ptask_tail*',
        'perrorcall_case.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall_case.LEVEL = 2', 'perrorcall_case.SITE = pconfigcall.SITE',
        'perrorcall_case.LINE = pconfigcall.LINE',
        'perrorcall_case.MESSAGE = $dynamic_constant_case_message()',
        '$error_call_valid(S_dispatch,perrorcall_case)',
        '$task_nodes(perrorcall_case.RESUME) = [HARRAY n_input]',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS', 'S_dispatch.EVENTS = S.EVENTS']
    return values


def query(state, start, target):
    return [*common.reach(state, start, 0, target), *common.public(state),
        f'$dynamic_global_constant_value({state},{text(target)}) = (PARRAY n_root)',
        f'n_query_owners = $heap_owners($heap_graph({state}),HARRAY n_root)',
        *common.step('S_value', state, 'PARRAY n_root'),
        f'S_value.ARRAYS = {state}.ARRAYS', f'S_value.ALLOCATIONS = {state}.ALLOCATIONS',
        f'$heap_graph(S_value).EDGES = $heap_graph({state}).EDGES',
        '$heap_owners($heap_graph(S_value),HARRAY n_root) = $(n_query_owners + 1)']


def literal(initial, stdout):
    head, nested, again = text('head'), text('nested'), text('again')
    values = capture(initial, 'V74_TREE', True)
    values += ['$user_constant_at(S.USERCONSTANTS,$ptascii("V74_LEFT")) = (puserconstant_left)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V74_RIGHT")) = (puserconstant_right)',
        'puserconstant_left.VALUE = POBJECT n_left',
        'puserconstant_right.VALUE = POBJECT n_right',
        'puserconstant_right.CLASS = PVSTDCLASS n_right porigin_right',
        'S.STORE[n_cell] = DEFINED (POBJECT n_left)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {head}) (ALIAS n_cell),ENTRY (KSTRING {nested}) (DIRECT (PARRAY n_input_child))]',
        f'S.ARRAYS[n_input_child].ITEMS = [ENTRY (KSTRING {again}) (ALIAS n_cell)]',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        *reach('S_done', 'S_dispatch', 0, 'V74_TREE'),
        'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_done*',
        'perrorcall_done.RESUME = perrorcall_case.RESUME',
        'S_done.RESULT = KNOWN (PBOOL true)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_cell] = DEFINED (POBJECT n_right)',
        'S_done.STORE[n_input_cell] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        '$entry_lookup(S_done.ARRAYS[n_caller].ITEMS,KSTRING ($ptascii("caller"))) = (DIRECT pvalue_caller)',
        '$string_bytes(pvalue_caller) = ($ptascii("case"))',
        'S_done.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_done.ARRAYS[n_input_child] = S.ARRAYS[n_input_child]',
        'S_done.USERCONSTANTS = S.USERCONSTANTS',
        '$dynamic_constant_case_valid(S_done,pconfigcall)',
        '$dynamic_array_recursive(S_done,PARRAY n_input,eps) = (false)',
        '~$destructor_operational(S_done)',
        *common.step('S_case', 'S_done'), *common.public('S_case'),
        'S_case.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) :: ptask_done*',
        'S_case.ARRAYS = S_done.ARRAYS', 'n_before = |S_case.ARRAYS|',
        *common.step('S_row', 'S_case', 'PBOOL true'),
        'S_row.TODO = ptask_done*',
        '$user_constant_at(S_row.USERCONSTANTS,$ptascii("V74_TREE")) = (puserconstant_tree)',
        'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_tree]',
        'puserconstant_tree.VALUE = PARRAY n_root', 'n_root = $(n_before + 1)',
        'n_child = n_before',
        f'parray_child = $array_insert($array_empty(),KSTRING {again},DIRECT (POBJECT n_right))',
        f'parray_root = $array_insert($array_insert($array_empty(),KSTRING {head},DIRECT (POBJECT n_right)),KSTRING {nested},DIRECT (PARRAY n_child))',
        f'pvalueclass_child = PVARRAY false ([(KSTRING {again},PVSTDCLASS n_right porigin_right)])',
        f'puserconstant_tree.CLASS = PVARRAY false ([(KSTRING {head},PVSTDCLASS n_right porigin_right),(KSTRING {nested},pvalueclass_child)])',
        'puserconstant_tree.ORIGIN = pconfigcall.SITE',
        'S_row.ARRAYS = S_case.ARRAYS ++ [parray_child,parray_root]',
        '$heap_owners($heap_graph(S_row),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_row),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_row),HOBJECT n_right) = 4',
        '$heap_edge_owners(HOBJECT n_right,$heap_graph(S_row).EDGES,[HARRAY n_root,HARRAY n_child]) = 2',
        *query('S_query', 'S_row', 'V74_TREE'),
        *reach('S_bucket', 'S_value', 3, 'V74_TREE'),
        '$lookup(S_bucket.ENV,$ptascii("bucket")) = (n_bucket)', 'n_bucket =/= n_cell',
        'S_bucket.STORE[n_bucket] = DEFINED (POBJECT n_left)',
        '$lookup(S_bucket.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_bucket.STORE[n_copy_cell] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
        f'$entry_lookup(S_bucket.ARRAYS[n_copy_root].ITEMS,KSTRING {nested}) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_child',
        f'S_bucket.ARRAYS[n_copy_child].ITEMS = [ENTRY (KSTRING {again}) (ALIAS n_bucket)]',
        'S_bucket.ARRAYS[n_root] = parray_root', 'S_bucket.ARRAYS[n_child] = parray_child',
        *define.reach('S_cycle', 'S_bucket', 1, 'V74_OLD'),
        'S_cycle.TODO = (CONFIG_INVOKE pconfigcall_cycle) :: ptask_cycle*',
        '$dynamic_define_values(pconfigcall_cycle) = (($ptascii("V74_OLD"),PARRAY n_cycle_input))',
        'n_cycle_input = n_caller', '$dynamic_constant_case_valid(S_cycle,pconfigcall_cycle)',
        '$dynamic_array_recursive(S_cycle,PARRAY n_cycle_input,eps) = (false)',
        *common.step('S_cycle_dispatch', 'S_cycle'),
        *reach('S_cycle_done', 'S_cycle_dispatch', 0, 'V74_OLD'),
        'S_cycle_done.STORE[n_calls] = DEFINED (PINT 2)',
        'S_cycle_done.STORE[n_cell] = DEFINED (PARRAY n_cycle_input)',
        '$dynamic_constant_case_valid(S_cycle_done,pconfigcall_cycle)',
        '$dynamic_array_recursive(S_cycle_done,PARRAY n_cycle_input,eps) = (true)',
        '$dynamic_array_value(S_cycle_done,PARRAY n_cycle_input,eps,true) = eps',
        'S_cycle_done.USERCONSTANTS = S_row.USERCONSTANTS',
        *common.step('S_cycle_case', 'S_cycle_done'), *common.public('S_cycle_case'),
        'S_cycle_case.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall_cycle) :: ptask_cycle_tail*',
        'n_before_error = |S_cycle_case.ARRAYS|',
        'n_cycle_owners = $heap_owners($heap_graph(S_cycle_case),HARRAY n_cycle_input)',
        *common.step('S_error', 'S_cycle_case'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_cycle_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "ValueError"',
        'pthrowable_error.ORIGIN = (pconfigcall_cycle.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text(MESSAGE) + ')',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_cycle_input))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        'n_trace = n_before_error', 'n_args = $(n_before_error + 1)', 'n_frame = $(n_before_error + 2)',
        'S_error.ARRAYS = S_cycle_case.ARRAYS ++ [S_error.ARRAYS[n_trace],S_error.ARRAYS[n_args],S_error.ARRAYS[n_frame]]',
        'S_error.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_error.STORE = S_cycle_case.STORE', 'S_error.EVENTS = S_cycle_case.EVENTS',
        '$heap_owners($heap_graph(S_error),HARRAY n_cycle_input) = n_cycle_owners',
        *define.finish('S_error', stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 3',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        *define.property_value('S_final', 'n_right', 31, 'right'),
        *define.property_value('S_final', 'n_left', 17, 'left'),
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_cycle_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy_root <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy_child <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)', '~(HCELL n_bucket <- S_final.ALLOCATIONS)']
    return values


def selected(initial, stdout):
    edge, tag = text('edge'), text('tag')
    values = capture(initial, 'V74_EVAL_TREE')
    values += ['pconfigcall.SITE = PORIGIN 1 pcpath_call',
        'S.STORE[n_cell] = DEFINED (PARRAY n_leaf7)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        *reach('S_throw', 'S_dispatch', 2, 'V74_EVAL_TREE'),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall_case.RESUME',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_leaf23)',
        f'S_throw.ARRAYS[n_leaf23].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 23))]',
        'S_throw.STORE[n_input_cell] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '$entry_lookup(S_throw.ARRAYS[n_caller].ITEMS,KSTRING ($ptascii("caller"))) = (DIRECT pvalue_caller)',
        '$string_bytes(pvalue_caller) = ($ptascii("case"))',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V74_EVAL_SIDE")) = (puserconstant_side)',
        'puserconstant_side.VALUE = PINT 19', 'S_throw.USERCONSTANTS = [puserconstant_side]',
        '$source_constant_lookup(S_throw,$ptascii("V74_EVAL_TREE")) = eps',
        '$dynamic_constant_case_valid(S_throw,pconfigcall)',
        '$dynamic_array_recursive(S_throw,PARRAY n_input,eps) = (false)',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V74_PENDING"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 2',
        '~$destructor_operational(S_throw)',
        'n_before = |S_throw.ARRAYS|',
        # Pending cyclic registration stays an explicit, undriven boundary.
        'S_cyclic = S_throw[.STORE[n_cell] = DEFINED (PARRAY n_input)]',
        '$dynamic_array_recursive(S_cyclic,PARRAY n_input,eps) = (true)',
        'S_cyclic_pending = $dynamic_constant_case_pending(S_cyclic,pconfigcall)',
        'S_cyclic_pending.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        *common.step('S_row', 'S_throw'), *common.public('S_row'),
        'S_row.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_row.RESULT = S_throw.RESULT',
        'S_row.STORE = S_throw.STORE', 'S_row.EVENTS = S_throw.EVENTS',
        '$user_constant_at(S_row.USERCONSTANTS,$ptascii("V74_EVAL_TREE")) = (puserconstant_tree)',
        'S_row.USERCONSTANTS = [puserconstant_side,puserconstant_tree]',
        'puserconstant_tree.VALUE = PARRAY n_root', 'n_root = $(n_before + 1)',
        'n_child = n_before',
        f'parray_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 23))',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
        f'pvalueclass_child = PVARRAY false ([(KSTRING {tag},PVSCALAR)])',
        f'puserconstant_tree.CLASS = PVARRAY false ([(KSTRING {edge},pvalueclass_child)])',
        'puserconstant_tree.ORIGIN = pconfigcall.SITE',
        'puserconstant_tree.READS = eps', 'puserconstant_tree.RECEIVES = eps',
        'S_row.ARRAYS = S_throw.ARRAYS ++ [parray_child,parray_root]',
        '$heap_owners($heap_graph(S_row),HARRAY n_input) = 1',
        '$heap_owners($heap_graph(S_row),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_row),HARRAY n_child) = 1',
        'S_row.STORE[n_result] = DEFINED pvalue_sentinel',
        # An existing array row does not silently use primitive pending cleanup.
        '$dynamic_constant_case_valid(S_row,pconfigcall)',
        'S_duplicate_pending = $dynamic_constant_case_pending(S_row,pconfigcall)',
        'S_duplicate_pending.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        *query('S_query', 'S_row', 'V74_EVAL_TREE'),
        *define.finish('S_value', stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        'HARRAY n_leaf7 <- $pools_nodes(S_final.POOLS)',
        'HARRAY n_leaf23 <- $pools_nodes(S_final.POOLS)']
    return values


def checks(initial, name, stdout):
    return selected(initial, stdout) if name.startswith('selected-') else literal(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
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
