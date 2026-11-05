#!/usr/bin/env python3
"""Reach grouped-operation ticks before later binding, initialization and cleanup."""
import argparse
import json

import fiber_state_review as review
import tick_grouped_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.STATICS = S.STATICS',
    'S_paused.ALLOCATIONS = S.ALLOCATIONS', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'), 'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
]

name = 'review-global-tick-changes-later-dynamic-binding'
review.CASES = {
    'first-global-binding-commits-before-later-dynamic-name': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = eps',
        'checks': [
            'porigin = PORIGIN n pcpath',
            'pcpath_group = [PCINDEX 5, PCFIELD 5, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
            'porigin_group = PORIGIN n pcpath_group',
            'pcpath = pcpath_group ++ [PCFIELD 0, PCINDEX 0]',
            '$origin_node(S.SOURCES, porigin_group) = (NStmtGlobal (SEQUENCE ([expression_first, expression_late])) metadata)',
            '$origin_child((porigin_group), [PCFIELD 0, PCINDEX 1]) = (porigin_late)',
            'ptask_tail* = (ORIGIN_RETURN (porigin_group)) :: (AT porigin_late (GLOBAL_BIND expression_late z_late)) :: (TICK porigin_group ptickmarker_final) :: ptask_after*',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 9', 'z_late = 9',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            '$tick_marker_valid(S, porigin_group, ptickmarker_final)',
            'S_global = $global_table_view(S)',
            '$lookup(S.ENV, $ptascii("first")) = (n_first)',
            '$lookup(S_global.ENV, $ptascii("first")) = (n_first)',
            'S.STORE[n_first] = DEFINED (PINT 10)',
            '$lookup(S.ENV, $ptascii("later")) = eps',
            '$lookup(S.ENV, $ptascii("changed")) = eps',
            '$lookup(S_global.ENV, $ptascii("pick")) = (n_pick)',
            'S.STORE[n_pick] = DEFINED pvalue_pick',
            '$echo_value(pvalue_pick) = $ptascii("later")',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output('T', 'T', '10', '|', '30', '|', 'U'),
        ],
    },
}

name = 'review-static-tick-precedes-later-initializer-effects'
review.CASES['first-static-cell-exists-before-later-initializer'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = eps',
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath_group = [PCINDEX 3, PCFIELD 5, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
        'porigin_group = PORIGIN n pcpath_group',
        'pcpath = pcpath_group ++ [PCFIELD 0, PCINDEX 0]',
        '$origin_node(S.SOURCES, porigin_group) = (NStmtStatic (SEQUENCE ([phpType59_first, phpType59_late])) metadata)',
        '$origin_child((porigin_group), [PCFIELD 0, PCINDEX 1]) = (porigin_late)',
        'ptask_tail* = (ORIGIN_RETURN (porigin_group)) :: (AT porigin_late (STATIC_INIT porigin_late)) :: (TICK porigin_group ptickmarker_final) :: ptask_after*',
        '$static_descriptor(S, porigin) = (($ptascii("first"), 7, 7, true))',
        '$static_descriptor(S, porigin_late) = (($ptascii("second"), 7, 7, false))',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 7',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        '$tick_marker_valid(S, porigin_group, ptickmarker_final)',
        'S.STATICS = [pstaticcell_first]', 'pstaticcell_first.ORIGIN = porigin',
        'n_first = pstaticcell_first.CELL',
        '$lookup(S.ENV, $ptascii("first")) = (n_first)',
        'S.STORE[n_first] = DEFINED (PINT 0)',
        '$state_static_at(S, porigin_late) = eps',
        '$lookup(S.ENV, $ptascii("second")) = eps',
        *valid('S'), *PAUSE,
        'S_done.STATICS = [pstaticcell_first, pstaticcell_second]',
        'pstaticcell_second.ORIGIN = porigin_late',
        'n_second = pstaticcell_second.CELL',
        'S_done.STORE[n_second] = DEFINED (PINT 2)',
        'S_done.EVENTS = ' + output('T', 'I', 'T', '2'),
    ],
}

name = 'review-unset-cleanup-finishes-before-tick-aborts-next-target'
review.CASES['first-unset-destructor-finishes-before-tick-aborts-second'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('A'),
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath_group = [PCINDEX 6, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
        'porigin_group = PORIGIN n pcpath_group',
        'pcpath = pcpath_group ++ [PCFIELD 0, PCINDEX 0]',
        '$origin_node(S.SOURCES, porigin_group) = (NStmtUnset (SEQUENCE ([expression_first, expression_late])) metadata)',
        '$origin_child((porigin_group), [PCFIELD 0, PCINDEX 1]) = (porigin_late)',
        'ptask_tail* = (ORIGIN_RETURN (porigin_group)) :: (AT porigin_late (UNSET expression_late)) :: (TICK porigin_group ptickmarker_final) :: ptask_after*',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 10',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        '$lookup(S.ENV, $ptascii("a")) = eps',
        '$lookup(S.ENV, $ptascii("b")) = (n_b_cell)',
        'S.STORE[n_b_cell] = DEFINED (POBJECT n_b)',
        '$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_b) = 1',
        'S.DESTRUCTION.CALLED = [n_a]', '~((HOBJECT n_a) <- S.ALLOCATIONS)',
        'S.DESTRUCTION.CALLS = eps', 'S.DESTRUCTION.RELEASES = eps',
        'S.DESTRUCTION.OPERATIONS = eps', 'S.DESTRUCTION.CLEANUPS = eps',
        *valid('S'), *PAUSE,
        '~((HOBJECT n_b) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("b")) = eps',
        'S_done.EVENTS = ' + output('A', 'T', 'C', 'H', 'B', 'Z'),
    ],
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
