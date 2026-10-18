#!/usr/bin/env python3
"""Reached pooled versus copied empty duplicate roots and normal disposal."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_empty_array_duplicate_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
PREFIX = prior.PREFIX


def checks(initial, name, stdout):
    mutable = name.startswith('selected-')
    target = 'V69_EVAL_TARGET' if mutable else 'V69_LITERAL_TARGET'
    flag = 'false' if mutable else 'true'
    wrong = 'true' if mutable else 'false'
    marker = 'DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants'
    values = [*initial, *define.reach('S', 'S_initial', 1, target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        'n_constants = |S.USERCONSTANTS|', 'n_constants = 1',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))',
        'preqbytes = ' + text(target),
        '$user_constant_at(S.USERCONSTANTS,preqbytes) = (puserconstant_old)',
        'puserconstant_old.VALUE = PINT ' + ('23' if mutable else '17'),
        'parray_input = S.ARRAYS[n_input]', 'parray_input.ITEMS = eps',
        'HARRAY n_input <- S.ALLOCATIONS',
        '$array_immutable(S,n_input) = ' + flag,
        'n_before = |S.ARRAYS|', 'H_before = $heap_graph(S)',
        'n_input_owners = $heap_owners(H_before,HARRAY n_input)',
        '$config_nodes(pconfigcall) = [HARRAY n_input]']
    if mutable:
        values += ['parray_input.NEXT = 91', 'parray_input.SERIAL = 1',
            'parray_input.POSITIONS = eps',
            '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
            'pconfigcall.SITE = PORIGIN 1 pcpath_call',
            'pconfigcall.SELECTION = (n_selection)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL false))]']
    else:
        values += ['parray_input = $array_empty()',
            '$dynamic_define_known(S,pconfigcall.SITE,1) = (PARRAY n_known)',
            '$array_immutable(S,n_known)',
            'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)', 'S_resume = S']
    values += [*common.step('S_dispatch', 'S' if mutable else 'S_resume'),
        *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker,
        '$error_call_valid(S_dispatch,perrorcall)',
        'perrorcall.LEVEL = 2', 'perrorcall.SITE = pconfigcall.SITE',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(preqbytes)',
        'S_dispatch.RESULT = KNOWN PNULL', 'S_dispatch.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        'S_dispatch.EVENTS = S.EVENTS',
        'pvalueclass = PVARRAY ' + flag + ' eps',
        'S_dispatch.ARRAYS[n_candidate] = $array_empty()',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,n_constants)',
        '$task_nodes(' + marker + ') = [HARRAY n_candidate,HARRAY n_input]',
        'H_dispatch = $heap_graph(S_dispatch)']
    if mutable:
        values += ['n_candidate = n_before', 'n_candidate =/= n_input',
            'S_dispatch.ARRAYS = S.ARRAYS ++ [$array_empty()]',
            'S_dispatch.ARRAYS[n_input] = parray_input',
            '~$array_immutable(S_dispatch,n_candidate)',
            '$heap_owners(H_dispatch,HARRAY n_candidate) = 1',
            '$heap_owners(H_dispatch,HARRAY n_input) = n_input_owners',
            # Canonicalizing the input makes the pure self-candidate control
            # discriminate the identity guard rather than append metadata.
            'S_same = S_dispatch[.ARRAYS = $array_replace(S_dispatch.ARRAYS,n_input,$array_empty())]',
            '$dynamic_array_value(S_same,PARRAY n_input,eps,false) = ((S_same,PARRAY n_input,PVARRAY false eps))',
            '~$dynamic_array_duplicate_valid(S_same,pconfigcall,n_input,PVARRAY false eps,n_constants)',
            'S_history = S_dispatch[.ARRAYS = $array_replace(S_dispatch.ARRAYS,n_candidate,$array_empty()[.NEXT = 91])]',
            '~$dynamic_array_duplicate_valid(S_history,pconfigcall,n_candidate,pvalueclass,n_constants)',
            'S_mixed = $allocate_array(S_dispatch,$array_insert($array_empty(),KINT 0,DIRECT (PINT 1)))',
            'S_mixed.RESULT = KNOWN (PARRAY n_mixed)',
            'pvalueclass_mixed = PVARRAY false ([(KINT 0,PVSCALAR)])',
            '$dynamic_array_value(S_mixed,PARRAY n_mixed,eps,false) = ((S_mixed,PARRAY n_mixed,pvalueclass_mixed))',
            '~$dynamic_array_duplicate_valid(S_mixed,pconfigcall,n_mixed,pvalueclass_mixed,n_constants)',
            '~$dynamic_array_duplicate_valid(S_dispatch[.SELECTEDCALLS = eps][.SELECTSEQ = 0],pconfigcall,n_candidate,pvalueclass,n_constants)']
    else:
        values += ['n_candidate = n_input',
            'S_dispatch.ARRAYS = S.ARRAYS',
            'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners(H_dispatch,HARRAY n_input) = $(n_input_owners + 1)',
            '$dynamic_array_known_matches(S_dispatch,PARRAY n_input,(PARRAY n_known))',
            'S_clone = $allocate_array(S_dispatch,$array_empty())',
            'S_clone.RESULT = KNOWN (PARRAY n_clone)', 'n_clone =/= n_input',
            '$dynamic_array_value(S_clone,PARRAY n_clone,eps,false) = ((S_clone,PARRAY n_clone,PVARRAY false eps))',
            '~$dynamic_array_known_matches(S_clone,PARRAY n_clone,(PARRAY n_known))',
            '~$dynamic_array_duplicate_valid(S_clone,pconfigcall,n_clone,PVARRAY false eps,n_constants)']
    # Pure malformed projections are never driven.
    values += ['~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,PVARRAY ' + wrong + ' eps,n_constants)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,0)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,$(n_constants + 1))',
        'S_dead = S_dispatch[.ALLOCATIONS = $destruction_node_delete(S_dispatch.ALLOCATIONS,HARRAY n_candidate)]',
        '~$dynamic_array_duplicate_valid(S_dead,pconfigcall,n_candidate,pvalueclass,n_constants)',
        *prior.reach('S_done', 'S_dispatch', 0, target),
        'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_tail*',
        'perrorcall_done.RESUME = ' + marker,
        'S_done.RESULT = KNOWN (PBOOL ' + ('false' if mutable else 'true') + ')',
        'S_done.USERCONSTANTS = S.USERCONSTANTS',
        'S_done.ARRAYS[n_input] = parray_input',
        'S_done.ARRAYS[n_candidate] = $array_empty()',
        '$dynamic_array_duplicate_valid(S_done,pconfigcall,n_candidate,pvalueclass,n_constants)',
        '$lookup(S_done.ENV,$ptascii("input")) = (n_caller_cell)',
        'S_done.STORE[n_caller_cell] = DEFINED (PARRAY n_caller)',
        'n_caller =/= n_input',
        '$entry_lookup(S_done.ARRAYS[n_caller].ITEMS,KINT ' + ('91' if mutable else '0') + ') = (DIRECT pvalue_handler)',
        '$string_bytes(pvalue_handler) = (' + text('handler') + ')',
        *common.step('S_pending', 'S_done'), *common.public('S_pending'),
        'S_pending.TODO = (' + marker + ') :: ptask_tail*',
        'S_pending.EVENTS = S_done.EVENTS' + (' ++ [DIAGNOSTIC_SOURCE 1 "Warning" perrorcall_done.MESSAGE pconfigcall.LINE]' if mutable else ''),
        'n_pending_input = $heap_owners($heap_graph(S_pending),HARRAY n_input)',
        *common.step('S_false', 'S_pending', 'PBOOL false'),
        'S_false.TODO = ptask_tail*', 'S_false.USERCONSTANTS = S.USERCONSTANTS']
    if mutable:
        values += ['S_done.ERRORFATALTRACE = eps', '$display_state_mode(S_done) = 2',
            'n_pending_input = 1',
            '~(HARRAY n_candidate <- S_false.ALLOCATIONS)',
            '~(HARRAY n_input <- S_false.ALLOCATIONS)']
    else:
        values += ['$(n_pending_input >= 3)',
            '$heap_owners($heap_graph(S_false),HARRAY n_input) = $(n_pending_input - 2)',
            'HARRAY n_input <- S_false.ALLOCATIONS',
            '$array_immutable(S_false,n_input)',
            'S_false.ARRAYS[n_input] = parray_input']
    values += [*define.finish('S_false', stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)']
    if mutable:
        values += ['~(HARRAY n_input <- S_final.ALLOCATIONS)',
            '~(HARRAY n_candidate <- S_final.ALLOCATIONS)']
    else:
        values += ['HARRAY n_input <- S_final.ALLOCATIONS',
            '$array_immutable(S_final,n_input)',
            'S_final.ARRAYS[n_input] = $array_empty()',
            '$dynamic_array_known_matches(S_final,PARRAY n_input,(PARRAY n_known))']
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
