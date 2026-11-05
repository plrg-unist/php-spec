#!/usr/bin/env python3
"""Reach inherited arm tick frequency and the committed Match result marker."""
import argparse
from pathlib import Path

import fiber_state_review as review
import tick_match_review_cases as sources


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.TICKCOUNT = S.TICKCOUNT',
    'S_paused.EVENTS = S.EVENTS', *valid('S_paused'),
    'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
]

review.CASES = {
    'selected-callable-inherits-later-condition-frequency': {
        'source': sources.CASES['review-later-condition-before-selected-callable-body'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT =/= eps -- if S.EVENTS = [OUTPUT $ptascii("A")]',
        'checks': [
            'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 6', 'S.TICKCOUNT = 0',
            '$origin_node(S.SOURCES, porigin) = (NStmtEcho phpType25 metadata)',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            'S_counted = $drive_steps(S, 1)', 'S_counted.COMPLETION = BUDGET',
            'S_counted.TICKCOUNT = 1', 'S_counted.TODO = ptask_tail*',
            'S_counted.EVENTS = S.EVENTS', *valid('S_counted'),
            'S_bad = S[.TODO = (TICK porigin ptickmarker[.FREQUENCY = 1]) :: ptask_tail*]',
            '~$call_descriptors_valid(S_bad)',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("T"), OUTPUT $ptascii("Z"), OUTPUT $ptascii("W"), OUTPUT $ptascii("T")]',
        ],
    },
    'table-result-assignment-restores-marker-line-after-last-arm': {
        'source': sources.CASES['review-table-assignment-restores-marker-line'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = [OUTPUT $ptascii("A")]',
        'checks': [
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 5', 'S.TICKCOUNT = 0',
            '$lookup(S.ENV, $ptascii("value")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PINT 1)',
            '$origin_child((porigin), [PCFIELD 0, PCFIELD 1]) = (porigin_match)',
            '$match_table(S, porigin_match) = (true)',
            '$match_line(S, porigin_match, [PCFIELD 1, PCINDEX 1, PCFIELD 1]) = (7)',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            'S_bad = S[.TODO = (TICK porigin ptickmarker[.LINE = 7]) :: ptask_tail*]',
            '~$call_descriptors_valid(S_bad)',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("T"), OUTPUT $ptascii("5"), OUTPUT $ptascii(";"), OUTPUT $ptascii("Z"), OUTPUT $ptascii("T"), OUTPUT $ptascii("9"), OUTPUT $ptascii(";")]',
        ],
    },
    'unselected-arm-declarables-survive-generator-pause': {
        'source': Path(__file__).with_name('tick_match_generator.php').read_text(),
        'stage': 'S.CURRENT = eps -- if $lookup(S.ENV, $ptascii("generator")) = (n_cell) -- if S.STORE[n_cell] = DEFINED (POBJECT n) -- if S.OBJECTS[n] = GENERATOR pgenerator -- if pgenerator.PHASE = GENERATOR_PAUSED -- if pgenerator.FRAME = (pframe) -- if S.EVENTS = [OUTPUT $ptascii("I")]',
        'checks': [
            'S.TICKCOUNT = 0', 'pgenerator.VALUE = (pvalue_yield)',
            '$type_bytes(pvalue_yield) = $ptascii("string")',
            '$echo_value(pvalue_yield) = $ptascii("V")',
            'pframe.TODO = (ORIGIN_RETURN (porigin_statement)) :: DISCARD :: (TICK porigin_statement ptickmarker) :: ptask_tail*',
            'ptickmarker.FREQUENCY = 1',
            '$tick_marker_valid(S, porigin_statement, ptickmarker)',
            '$generator_record_valid(S, pgenerator)', '$generator_state_valid(S)',
            *valid('S'), *PAUSE,
            'S_paused.OBJECTS = S.OBJECTS', '$generator_state_valid(S_paused)',
            'S_done.EVENTS = [OUTPUT $ptascii("I"), OUTPUT $ptascii("V"), OUTPUT $ptascii("|"), OUTPUT $ptascii("T"), OUTPUT $ptascii("G"), OUTPUT $ptascii("T"), OUTPUT $ptascii("Z")]',
        ],
    },
}

DERIVED_GUARDS = {
    'selected-callable-inherits-later-condition-frequency': 1,
    'table-result-assignment-restores-marker-line-after-last-arm': 1,
    'unselected-arm-declarables-survive-generator-pause': 0,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
