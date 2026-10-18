#!/usr/bin/env python3
"""Reached pending-cycle suppression and rejected copied-array retirement."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_array_true_flag_protocol as case
import define_array_true_pending_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, PREFIX = prior.ROOT, prior.text, case.PREFIX


def checks(initial, name, stdout):
    selected = name.startswith('selected-')
    target = 'V75_DUPLICATE' if selected else 'V75_CYCLE'
    side = 'V75_DUPLICATE_SIDE' if selected else 'V75_CYCLE_SIDE'
    message = 'V75_DUP_PENDING' if selected else 'V75_PENDING'
    edge, tag = text('edge'), text('tag')
    source_items = f'[ENTRY (KSTRING {edge}) (ALIAS n_cell)]'
    values = [*initial, *define.reach('S', 'S_initial', 0, target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_constant_case_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((' + text(target) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (false)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_seed)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        'S.ARRAYS[n_input].ITEMS = ' + source_items,
        *common.step('S_dispatch', 'S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_case) :: ptask_tail*',
        'perrorcall_case.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall_case.MESSAGE = $dynamic_constant_case_message()',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        *case.reach('S_throw', 'S_dispatch', 2, target),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall_case.RESUME',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = (' + text(message) + ')',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_result] = DEFINED pvalue_sentinel',
        'S_throw.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '$user_constant_at(S_throw.USERCONSTANTS,' + text(side) + ') = (puserconstant_side)',
        'puserconstant_side.VALUE = PINT ' + ('31' if selected else '19'),
        '$dynamic_constant_case_valid(S_throw,pconfigcall)',
        '~$destructor_operational(S_throw)',
        # These malformed projections are queried only, never driven.
        'S_no_pending = S_throw[.TODO = eps]',
        'S_no_pending_result = $dynamic_constant_case_pending(S_no_pending,pconfigcall)',
        'S_no_pending_result.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_dead = S_throw[.ALLOCATIONS = $destruction_node_delete(S_throw.ALLOCATIONS,HOBJECT n_error)]',
        'S_dead_result = $dynamic_constant_case_pending(S_dead,pconfigcall)',
        'S_dead_result.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_missing = S_throw[.STORE[n_cell] = UNDEFINED]',
        '$dynamic_array_recursive(S_missing,PARRAY n_input,eps) = eps',
        'S_missing_result = $dynamic_constant_case_pending(S_missing,pconfigcall)',
        'S_missing_result.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"']
    if selected:
        values += ['pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
            'pconfigcall.SITE = PORIGIN 1 pcpath_call',
            '$user_constant_at(S.USERCONSTANTS,' + text(target) + ') = (puserconstant_old)',
            'puserconstant_old.VALUE = PINT 17',
            'S_throw.USERCONSTANTS = [puserconstant_old,puserconstant_side]',
            'S.ARRAYS[n_input].NEXT = 91',
            'S_throw.STORE[n_cell] = DEFINED (PARRAY n_leaf23)',
            f'S_throw.ARRAYS[n_leaf23].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 23))]',
            '$lookup(S_throw.ENV,$ptascii("flag")) = (n_flag)',
            'S_throw.STORE[n_flag] = DEFINED (PBOOL false)',
            '$lookup(S_throw.ENV,$ptascii("api")) = (n_api)',
            'S_throw.STORE[n_api] = DEFINED pvalue_api',
            '$string_bytes(pvalue_api) = ($ptascii("defined"))',
            '$dynamic_array_recursive(S_throw,PARRAY n_input,eps) = (false)',
            '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 3',
            'n_before = |S_throw.ARRAYS|']
    else:
        values += ['S.USERCONSTANTS = eps', 'S_throw.USERCONSTANTS = [puserconstant_side]',
            '$source_constant_lookup(S_throw,' + text(target) + ') = eps',
            'S_throw.STORE[n_cell] = DEFINED (PARRAY n_input)',
            '$dynamic_array_recursive(S_throw,PARRAY n_input,eps) = (true)',
            '$dynamic_array_value(S_throw,PARRAY n_input,eps,true) = eps',
            '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 4',
            'S_pause = $drive_steps(S_throw,0)', 'S_pause = S_throw[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)', 'S_resume = S_throw']
    values += [*common.step('S_after', 'S_throw' if selected else 'S_resume'),
        *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_after.RESULT = S_throw.RESULT', 'S_after.OBJECTS = S_throw.OBJECTS',
        'S_after.OBJECTTABLES = S_throw.OBJECTTABLES',
        'S_after.OBJECTPROPS = S_throw.OBJECTPROPS',
        'S_after.STORE = S_throw.STORE', 'S_after.EVENTS = S_throw.EVENTS',
        'S_after.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_after.ALLOCATIONS = S_throw.ALLOCATIONS',
        '$throwable_field(S_after,n_error,"previous") = PNULL',
        '$throwable_field(S_after,n_error,"trace") = PARRAY n_trace',
        '$error_handler_eligible(S_after,2)',
        '$gc_state_valid(S_after)']
    if selected:
        values += ['n_child = n_before', 'n_candidate = $(n_before + 1)',
            f'parray_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 23))',
            f'parray_candidate = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
            'S_after.ARRAYS = S_throw.ARRAYS ++ [parray_child,parray_candidate]',
            '~(HARRAY n_child <- S_after.ALLOCATIONS)',
            '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_after),HARRAY n_input) = 2']
    else:
        values += ['S_after.ARRAYS = S_throw.ARRAYS',
            '$source_constant_lookup(S_after,' + text(target) + ') = eps',
            '$heap_owners($heap_graph(S_after),HARRAY n_input) = 3']
    values += [*define.finish('S_after', stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)',
        'HARRAY n_seed <- $pools_nodes(S_final.POOLS)']
    if selected:
        values += ['~(HARRAY n_child <- S_final.ALLOCATIONS)',
            '~(HARRAY n_candidate <- S_final.ALLOCATIONS)']
    return values


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
