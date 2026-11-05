#!/usr/bin/env python3
"""Reach compiled empty-loop markers and an abrupt value target's saved iterator."""
import argparse
import json

import fiber_state_review as review
import tick_foreach_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.ITERATORS = S.ITERATORS',
    'S_paused.TICKCOUNT = S.TICKCOUNT', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'), 'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
    'S_done.ITERATORS = eps', *valid('S_done'),
]

name = 'review-empty-foreach-compiles-value-before-key-without-evaluation'
review.CASES = {
    'empty-loop-marker-retains-compiled-target-frequency-without-target-effects': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('P', 'T'),
        'checks': [
            'porigin = PORIGIN n pcpath',
            'pcpath = [PCINDEX 4, PCFIELD 1, PCINDEX 1]',
            '$origin_node(S.SOURCES, porigin) = (NStmtForeach expression_iterable expression_key (BOOLEAN false) expression_value phpType23 (BOOLEAN false) metadata)',
            'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 8',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            '$origin_child((porigin), [PCFIELD 3, PCFIELD 1, PCFIELD 0, PCFIELD 6, PCINDEX 0]) = (porigin_value_declare)',
            '$origin_child((porigin), [PCFIELD 1, PCFIELD 1, PCFIELD 0, PCFIELD 6, PCINDEX 0]) = (porigin_key_declare)',
            '$tick_marker(S, porigin_value_declare) = (ptickmarker_value)',
            '$tick_marker(S, porigin_key_declare) = (ptickmarker_key)',
            'ptickmarker_value.FREQUENCY = 3', 'ptickmarker_key.FREQUENCY = 2',
            'S.ITERATORS = eps', 'S.TICKCOUNT = 0',
            '$lookup(S.ENV, $ptascii("keys")) = (n_keys_cell)',
            '$lookup(S.ENV, $ptascii("values")) = (n_values_cell)',
            'S.STORE[n_keys_cell] = DEFINED (PARRAY n_keys)',
            'S.STORE[n_values_cell] = DEFINED (PARRAY n_values)',
            'S.ARRAYS[n_keys].ITEMS = eps', 'S.ARRAYS[n_values].ITEMS = eps',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output('P', 'T', 'Z', 'T'),
        ],
    },
}

name = 'review-abrupt-value-target-skips-key-body-and-releases-iterator'
review.CASES['value-target-tick-retains-pending-key-body-and-iterator-before-throw'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('V'),
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath_foreach = [PCINDEX 4, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
        'porigin_foreach = PORIGIN n pcpath_foreach',
        'pcpath = pcpath_foreach ++ [PCFIELD 3, PCFIELD 1, PCFIELD 0, PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
        '$origin_node(S.SOURCES, porigin_foreach) = (NStmtForeach expression_iterable expression_key (BOOLEAN false) expression_value (SEQUENCE ([statement_body])) (BOOLEAN false) metadata)',
        'statement_foreach = NStmtForeach expression_iterable expression_key (BOOLEAN false) expression_value (SEQUENCE ([statement_body])) (BOOLEAN false) metadata',
        '$origin_child((porigin_foreach), [PCFIELD 1]) = (porigin_key)',
        '$origin_child((porigin_foreach), [PCFIELD 4, PCINDEX 0]) = (porigin_body)',
        '$code_expression_at_source(S, porigin_key, eps) = (z_key)',
        'S.ITERATORS = [ITERATOR n_iterator n_array false ([(CURSOR n_array 1)])]',
        'S.FRAMES = [pframe_caller]', 'pframe_caller.CONTEXT = eps',
        '(AT porigin_key (LIST_STORE expression_key (KNOWN (PINT 7)) false z_key)) <- pframe_caller.TODO',
        '(AT porigin_body (STMT statement_body)) <- pframe_caller.TODO',
        '(FOREACH_NEXT n_iterator (HARRAY n_array) statement_foreach (porigin_foreach) 8) <- pframe_caller.TODO',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe_caller.TODO)) = 1',
        '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = 2',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 12',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        '$tick_marker(S, porigin_foreach) = (ptickmarker_foreach)',
        'ptickmarker_foreach.FREQUENCY = 2', 'ptickmarker_foreach.LINE = 8',
        *valid('S'), *PAUSE,
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 1',
        '$lookup(S_done.ENV, $ptascii("keys")) = (n_keys_cell)',
        '$lookup(S_done.ENV, $ptascii("values")) = (n_values_cell)',
        'S_done.STORE[n_keys_cell] = DEFINED (PARRAY n_keys)',
        'S_done.STORE[n_values_cell] = DEFINED (PARRAY n_values)',
        'S_done.ARRAYS[n_keys].ITEMS = eps', 'S_done.ARRAYS[n_values].ITEMS = eps',
        'S_done.EVENTS = ' + output('V', 'T', 'C', 'K', 'W', 'Z'),
    ],
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
