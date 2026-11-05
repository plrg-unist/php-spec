#!/usr/bin/env python3
"""Reach switch tick plans, certified markers and ordered subject release."""
import argparse

import fiber_state_review as review
import tick_switch_review_cases as sources
import tick_switch_sources as author


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.TICKCOUNT = S.TICKCOUNT',
    'S_paused.TICKENTRIES = S.TICKENTRIES', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'),
    'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
    *valid('S_done'),
]

review.CASES = {
    'cv-body-retains-adjacency-without-enclosing-marker': {
        'source': sources.CASES['review-cv-adjacency'].decode(),
        'stage': 'S.TODO = (SWITCH_SCAN statement porigin poperand 0) :: ptask_tail*',
        'checks': [
            'porigin = PORIGIN n pcpath', 'S.CURRENT = eps', 'S.EVENTS = eps',
            '$tick_source_plan(S, n) = (T)', 'T.DEPENDENCY = eps',
            '$code_at(S.CODE, n) = (pcode)', 'T.NAMES = pcode.NAMES',
            '$tick_marker(S, porigin) = eps',
            '$origin_child((porigin), [PCFIELD 1, PCINDEX 0, PCFIELD 1, PCINDEX 0]) = (porigin_body)',
            '$tick_marker(S, porigin_body) = (ptickmarker)',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 6',
            '$tick_marker_valid(S, porigin_body, ptickmarker)',
            '~$tick_marker_valid(S, porigin_body, ptickmarker[.LINE = 7])',
            '~$tick_marker_valid(S, porigin_body, ptickmarker[.FREQUENCY = 2])',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("T"), OUTPUT $ptascii("Z"), OUTPUT $ptascii("T")]',
        ],
    },
    'temporary-free-produces-real-enclosing-marker': {
        'source': sources.CASES['review-temporary-adjacency'].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("T")]',
        'checks': [
            '$origin_node(S.SOURCES, porigin) = (NStmtSwitch expression phpType60 metadata)',
            'S.CURRENT = eps', 'S.TICKCOUNT = 0',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 8',
            '$tick_marker(S, porigin) = (ptickmarker)',
            '$call_task_valid(S, TICK porigin ptickmarker)',
            'porigin = PORIGIN n_unit pcpath', 'S.CODE = [pcode]',
            '$code_name(pcode.NAMES, pcpath ++ [PCFIELD 0]) = (($ptascii("value"), eps))',
            'S_changed_name = S[.CODE = [pcode[.NAMES = (CODENAME (pcpath ++ [PCFIELD 0]) $ptascii("defined") eps) :: pcode.NAMES]]]',
            '$tick_source_plan(S_changed_name, n_unit) = eps',
            '~$call_task_valid(S_changed_name, TICK porigin ptickmarker)',
            'S_changed_fallback = S[.CODE = [pcode[.NAMES = (CODENAME (pcpath ++ [PCFIELD 0]) $ptascii("Local\\defined") ($ptascii("defined"))) :: pcode.NAMES]]]',
            '$tick_source_plan(S_changed_fallback, n_unit) = eps',
            '~$call_task_valid(S_changed_fallback, TICK porigin ptickmarker)',
            '~$tick_marker_valid(S, porigin, ptickmarker[.LINE = 9])',
            '~$tick_marker_valid(S, porigin, ptickmarker[.FREQUENCY = 2])',
            'S_bad = S[.TODO = (TICK porigin ptickmarker[.LINE = 9]) :: ptask_tail*]',
            '~$call_descriptors_valid(S_bad)',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("T"), OUTPUT $ptascii("T"), OUTPUT $ptascii("Z"), OUTPUT $ptascii("T")]',
        ],
    },
    'later-condition-declarables-precede-selected-body': {
        'source': sources.CASES['review-later-condition-declarables'].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if ptickmarker.FREQUENCY = 2 -- if S.EVENTS = [OUTPUT $ptascii("A")]',
        'checks': [
            'S.CURRENT = eps', 'S.TICKCOUNT = 0', 'ptickmarker.LINE = 7',
            '$origin_node(S.SOURCES, porigin) = (NStmtEcho phpType25 metadata)',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            '~$tick_marker_valid(S, porigin, ptickmarker[.FREQUENCY = 1])',
            'S_counted = $drive_steps(S, 1)', 'S_counted.COMPLETION = BUDGET',
            'S_counted.TODO = ptask_tail*', 'S_counted.TICKCOUNT = 1',
            'S_counted.EVENTS = S.EVENTS', *valid('S_counted'),
            *valid('S'), *PAUSE,
            'S_done.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("Z"), OUTPUT $ptascii("T")]',
        ],
    },
    'owning-subject-retires-before-enclosing-marker': {
        'source': author.CASES['temporary-owned-subject'][0].decode(),
        'stage': 'S.TODO = (SWITCH_NEXT statement porigin (KNOWN (POBJECT n))) :: ptask_tail* -- if S.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("T")]',
        'checks': [
            'S.CURRENT = eps', 'S.TICKCOUNT = 0',
            'poperand = KNOWN (POBJECT n)',
            '$heap_owners($heap_graph(S), HOBJECT n) = 1',
            '$task_nodes(SWITCH_NEXT statement porigin poperand) = [HOBJECT n]',
            '~(n <- S.DESTRUCTION.CALLED)', '(HOBJECT n) <- S.ALLOCATIONS',
            'ptask_tail* = (TICK porigin ptickmarker) :: ptask_after*',
            'ptickmarker.LINE = 1', 'ptickmarker.FREQUENCY = 1',
            '$tick_marker(S, porigin) = (ptickmarker)',
            *valid('S'), *PAUSE,
            '$heap_owners($heap_graph(S_done), HOBJECT n) = 0',
            '~((HOBJECT n) <- S_done.ALLOCATIONS)', 'n <- S_done.DESTRUCTION.CALLED',
            'S_done.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("T"), OUTPUT $ptascii("D"), OUTPUT $ptascii("T"), OUTPUT $ptascii("Z")]',
        ],
    },
}

DERIVED = {name: sum(check.startswith('~$tick_marker_valid')
                     or check == '~$call_descriptors_valid(S_bad)'
                     or check.startswith('$tick_source_plan(S_changed')
                     or check.startswith('~$call_task_valid(S_changed')
                     for check in case['checks'])
           for name, case in review.CASES.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
