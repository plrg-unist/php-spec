#!/usr/bin/env python3
"""Reached cyclic CONFIG errors, original trace ownership and acyclic retries."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_recursive_array_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
MESSAGE = 'define(): Argument #2 ($value) cannot be a recursive array'


def checks(initial, name, stdout):
    selected = name.startswith('selected-')
    target = 'V71_OLD' if selected else 'V71_SELF'
    key = text('peer' if selected else 'self')
    tag, empty = text('tag'), text('empty')
    values = [*initial, *define.reach('S','S_initial',1 if selected else 0,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))',
        'preqbytes = '+text(target),
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$lookup(S.ENV,$ptascii("'+('left' if selected else 'input')+'")) = (n_cell)',
        'n_cell <- S.REFCELLS', 'S.STORE[n_cell] = DEFINED (PARRAY n_input)',
        'n_before = |S.ARRAYS|',
        'n_input_owners = $heap_owners($heap_graph(S),HARRAY n_input)',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = eps']
    if selected:
        values += ['pconfigcall.SITE = PORIGIN 1 pcpath_call',
            'pconfigcall.SELECTION = (n_selection)',
            f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 11)),ENTRY (KSTRING {key}) (ALIAS n_right_cell)]',
            'S.STORE[n_right_cell] = DEFINED (PARRAY n_right)',
            f'S.ARRAYS[n_right].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 19)),ENTRY (KSTRING {key}) (ALIAS n_cell)]',
            '$lookup(S.ENV,$ptascii("warnings")) = (n_warnings)',
            'S.STORE[n_warnings] = DEFINED (PINT 0)',
            '$user_constant_at(S.USERCONSTANTS,preqbytes) = (puserconstant_old)',
            'puserconstant_old.VALUE = PINT 17',
            'n_constants = |S.USERCONSTANTS|', 'n_constants = 1']
    else:
        values += [f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {empty}) (DIRECT (PARRAY n_pooled)),ENTRY (KSTRING {tag}) (DIRECT (PINT 11)),ENTRY (KSTRING {key}) (ALIAS n_cell)]',
            '$array_immutable(S,n_pooled)', 'S.ARRAYS[n_pooled] = $array_empty()',
            '$user_constant_at(S.USERCONSTANTS,preqbytes) = eps',
            'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)', 'S_resume = S']
    values += ['$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED pvalue_result',
        # Partial helper controls are never driven.
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HCELL n_cell)]',
        '$dynamic_array_recursive(S_dead,PARRAY n_input,eps) = eps',
        'S_dead_root = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '$dynamic_array_recursive(S_dead_root,PARRAY n_input,eps) = eps',
        '$dynamic_array_recursive(S,PARRAY (|S.ARRAYS|),eps) = eps',
        'S_missing = S[.STORE[n_cell] = UNDEFINED]',
        '$dynamic_array_recursive(S_missing,PARRAY n_input,eps) = eps',
        '$dynamic_array_recursive(S,PINT 11,eps) = (false)',
        *common.step('S_error','S' if selected else 'S_resume'),
        *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "ValueError"',
        'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ('+text(MESSAGE)+')',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall.LINE',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        'n_trace = n_before','n_args = $(n_before + 1)','n_frame = $(n_before + 2)',
        'S_error.STORE = S.STORE','S_error.ENV = S.ENV',
        'S_error.USERCONSTANTS = S.USERCONSTANTS','S_error.EVENTS = S.EVENTS',
        'S_error.ERRORHANDLER = S.ERRORHANDLER',
        '$heap_owners($heap_graph(S_error),HARRAY n_input) = n_input_owners']
    if selected:
        values += ['$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_eval_frame))',
            '$trace_array_field(S_error,n_eval_frame,$ptascii("function")) = PSTRING ($ptascii("eval"))',
            'S_error.ARRAYS = S.ARRAYS ++ [S_error.ARRAYS[n_trace],S_error.ARRAYS[n_args],S_error.ARRAYS[n_frame],S_error.ARRAYS[n_eval_frame]]']
    else:
        values += ['S_error.ARRAYS = S.ARRAYS ++ [S_error.ARRAYS[n_trace],S_error.ARRAYS[n_args],S_error.ARRAYS[n_frame]]']
    values += [*define.reach('S_retry','S_error',0,target),
        'S_retry.TODO = (CONFIG_INVOKE pconfigcall_retry) :: ptask_retry*',
        '$dynamic_array_call_valid(S_retry,pconfigcall_retry)',
        '$dynamic_define_values(pconfigcall_retry) = ((preqbytes,PARRAY n_repaired))',
        'S_retry.STORE[n_cell] = DEFINED (PARRAY n_repaired)',
        'n_repaired =/= n_input',
        '$dynamic_array_recursive(S_retry,PARRAY n_repaired,eps) = (false)',
        'S_retry.USERCONSTANTS = S.USERCONSTANTS',
        'S_retry.STORE[n_result] = DEFINED pvalue_result',
        'n_retry_before = |S_retry.ARRAYS|']
    if selected:
        values += [f'parray_repaired = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 11))',
            'S_retry.ARRAYS[n_repaired] = parray_repaired',
            'S_retry.STORE[n_warnings] = DEFINED (PINT 0)',
            '~(HOBJECT n_error <- S_retry.ALLOCATIONS)',
            '~(HARRAY n_input <- S_retry.ALLOCATIONS)',
            *common.step('S_dispatch','S_retry'),*common.public('S_dispatch'),
            'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*',
            'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall_retry n_candidate pvalueclass n_constants',
            'n_candidate = n_retry_before',
            'S_dispatch.ARRAYS = S_retry.ARRAYS ++ [parray_repaired]',
            f'pvalueclass = PVARRAY false ([(KSTRING {tag},PVSCALAR)])',
            *prior.reach('S_done','S_dispatch',0,target),
            'S_done.RESULT = KNOWN (PBOOL true)',
            'S_done.STORE[n_warnings] = DEFINED (PINT 1)',
            *common.step('S_pending','S_done'),*common.public('S_pending'),
            'S_pending.EVENTS = S_done.EVENTS',
            'n_repaired_owners = $heap_owners($heap_graph(S_pending),HARRAY n_repaired)',
            *common.step('S_false','S_pending','PBOOL false'),
            '~(HARRAY n_candidate <- S_false.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_false),HARRAY n_repaired) = $(n_repaired_owners - 1)',
            *define.finish('S_false',stdout),
            'S_final.USERCONSTANTS = S.USERCONSTANTS',
            '~(HARRAY n_right <- S_final.ALLOCATIONS)',
            '~(HCELL n_right_cell <- S_final.ALLOCATIONS)']
    else:
        values += [f'parray_repaired = $array_insert($array_insert($array_empty(),KSTRING {empty},DIRECT (PARRAY n_pooled)),KSTRING {tag},DIRECT (PINT 11))',
            'S_retry.ARRAYS[n_repaired] = parray_repaired',
            'S_retry.ARRAYS[n_input] = S.ARRAYS[n_input]',
            '$dynamic_array_recursive(S_retry,PARRAY n_input,eps) = (false)',
            *common.step('S_row','S_retry','PBOOL true'),
            '$user_constant_at(S_row.USERCONSTANTS,preqbytes) = (puserconstant_row)',
            'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
            'puserconstant_row.VALUE = PARRAY n_root','n_root = n_retry_before',
            'S_row.ARRAYS = S_retry.ARRAYS ++ [parray_repaired]',
            f'puserconstant_row.CLASS = PVARRAY false ([(KSTRING {empty},PVARRAY true eps),(KSTRING {tag},PVSCALAR)])',
            *common.reach('S_query','S_row',0,target),*common.public('S_query'),
            'H_query = $heap_graph(S_query)',
            'n_root_owners = $heap_owners(H_query,HARRAY n_root)',
            *common.step('S_value','S_query','PARRAY n_root'),
            'S_value.ARRAYS = S_query.ARRAYS',
            'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
            '$heap_graph(S_value).EDGES = H_query.EDGES',
            '$heap_owners($heap_graph(S_value),HARRAY n_root) = $(n_root_owners + 1)',
            *define.finish('S_value',stdout),
            'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
            'S_final.ARRAYS[n_root] = parray_repaired',
            'S_final.ARRAYS[n_pooled] = $array_empty()',
            '$array_immutable(S_final,n_pooled)',
            '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1']
    values += ['~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_repaired <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks = sources, checks
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
