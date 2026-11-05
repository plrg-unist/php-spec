#!/usr/bin/env python3
"""Reach intermediate Echo ticks before a delayed operand and final line marker."""
import argparse
import json

import fiber_state_review as review
import tick_echo_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


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

name = 'review-first-operand-tick-throw-skips-later-print'
review.CASES = {
    'intermediate-marker-precedes-later-print-and-callback-abort': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('A'),
        'checks': [
            'porigin = PORIGIN n pcpath',
            'pcpath_echo = [PCINDEX 2, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
            'porigin_echo = PORIGIN n pcpath_echo',
            'pcpath = pcpath_echo ++ [PCFIELD 0, PCINDEX 0]',
            '$origin_node(S.SOURCES, porigin_echo) = (NStmtEcho (SEQUENCE ([expression_first, expression_late])) metadata)',
            '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 1]) = (porigin_late)',
            'expression_late = NExprPrint expression_print metadata_print',
            'ptask_tail* = (ORIGIN_RETURN (porigin_echo)) :: (AT porigin_late (EVAL expression_late)) :: (AT porigin_late (EMIT z_late)) :: (TICK porigin_echo ptickmarker_final) :: ptask_after*',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 6',
            'ptickmarker_final.FREQUENCY = 1', 'z_late = 6', 'S.TICKCOUNT = 0',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            '$echo_emit_source(S, porigin, ptickmarker.LINE)',
            '$tick_marker_valid(S, porigin_echo, ptickmarker_final)',
            'S_bad = S[.TODO = (TICK porigin ptickmarker[.FREQUENCY = 2]) :: ptask_tail*]',
            '~$call_descriptors_valid(S_bad)',
            'S_duplicate = S[.TODO = (AT porigin (TICK porigin ptickmarker)) :: S.TODO]',
            '~$tick_state_valid(S_duplicate)', '~$call_descriptors_valid(S_duplicate)',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output('A', 'T', 'C', 'Z'),
        ],
    },
}

name = 'review-later-callable-declarables-do-not-retime-earlier-operand'
review.CASES['earlier-marker-retains-frequency-before-later-callable-compilation'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('A', '1'),
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath_echo = [PCINDEX 2, PCFIELD 1, PCINDEX 0]',
        'porigin_echo = PORIGIN n pcpath_echo',
        'pcpath = pcpath_echo ++ [PCFIELD 0, PCINDEX 0]',
        '$origin_node(S.SOURCES, porigin_echo) = (NStmtEcho (SEQUENCE ([expression_first, expression_late])) metadata)',
        '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 1]) = (porigin_late)',
        'ptask_tail* = (ORIGIN_RETURN (porigin_echo)) :: (AT porigin_late (EVAL expression_late)) :: (AT porigin_late (EMIT z_late)) :: (TICK porigin_echo ptickmarker_final) :: ptask_after*',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 5',
        'ptickmarker_final.FREQUENCY = 2', 'ptickmarker_final.LINE = 5', 'z_late = 5',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        '$tick_marker_valid(S, porigin_echo, ptickmarker_final)',
        '$origin_child((porigin_late), [PCFIELD 0, PCFIELD 6, PCINDEX 0]) = (porigin_declare)',
        '$tick_marker(S, porigin_declare) = (ptickmarker_declare)',
        'ptickmarker_declare.FREQUENCY = 2', 'S.TICKCOUNT = 0',
        *valid('S'), *PAUSE,
        'S_done.EVENTS = ' + output('A', '1', 'T', 'B', 'T', 'Z'),
    ],
}

name = 'review-multiline-operands-keep-separate-marker-lines'
review.CASES['multiline-final-marker-follows-real-earlier-line-callback'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('A', '[6]', 'B'),
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath = [PCINDEX 2, PCFIELD 1, PCINDEX 0]',
        '$origin_node(S.SOURCES, porigin) = (NStmtEcho (SEQUENCE ([expression_first, expression_last])) metadata)',
        '$origin_child((porigin), [PCFIELD 0, PCINDEX 0]) = (porigin_first)',
        '$tick_marker(S, porigin_first) = (ptickmarker_first)',
        'ptickmarker_first.FREQUENCY = 1', 'ptickmarker_first.LINE = 6',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 7', 'S.TICKCOUNT = 0',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        '$tick_source_plan(S, n) = (T)', '|T.MARKERS| = 2',
        'S_bad = S[.TODO = (TICK porigin ptickmarker[.LINE = 6]) :: ptask_tail*]',
        '~$call_descriptors_valid(S_bad)',
        *valid('S'), *PAUSE,
        'S_done.EVENTS = ' + output('A', '[6]', 'B', '[7]'),
    ],
}

DERIVED_GUARDS = {
    'intermediate-marker-precedes-later-print-and-callback-abort': 3,
    'earlier-marker-retains-frequency-before-later-callable-compilation': 0,
    'multiline-final-marker-follows-real-earlier-line-callback': 1,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
