#!/usr/bin/env python3
"""Reach class-like emitter adjacency and uncalled-method declarable effects."""
import argparse
import json

import fiber_state_review as review
import tick_classlike_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.CLASSES = S.CLASSES',
    'S_paused.CLASSNAMES = S.CLASSNAMES',
    'S_paused.TICKCOUNT = S.TICKCOUNT', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'), 'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
]

name = 'review-early-interface-keeps-adjacent-declare-tick-suppressed'
review.CASES = {
    'early-interface-preserves-suppressed-later-declare-marker': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('T', 'Z'),
        'checks': [
            'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 5]',
            'porigin_interface = PORIGIN n ([PCINDEX 3])',
            'porigin_declare = PORIGIN n ([PCINDEX 4])',
            '$class_at(S.CLASSES, porigin_interface) = (pclassdesc)',
            'pclassdesc.KIND = "interface"', 'pclassdesc.EARLY',
            '$class_named(S.CLASSNAMES, $ptascii("tickinterface39")) = (porigin_interface)',
            '$tick_marker(S, porigin_interface) = eps',
            '$tick_marker(S, porigin_declare) = eps',
            'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 7',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            *valid('S'), *PAUSE,
            'S_done.TICKCOUNT = 1', 'S_done.EVENTS = ' + output('T', 'Z'),
        ],
    },
}

name = 'review-trait-uncalled-method-declarables-affect-following-markers'
review.CASES['uncalled-trait-method-compiles-frequency-without-runtime-body'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('T', 'Z'),
    'checks': [
        'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 4]',
        'porigin_trait = PORIGIN n ([PCINDEX 3])',
        '$class_at(S.CLASSES, porigin_trait) = (pclassdesc)',
        'pclassdesc.KIND = "trait"', 'pclassdesc.EARLY',
        '$class_named(S.CLASSNAMES, $ptascii("ticktrait39")) = (porigin_trait)',
        '$tick_marker(S, porigin_trait) = eps',
        '$origin_child((porigin_trait), [PCFIELD 2, PCINDEX 0, PCFIELD 6, PCINDEX 0]) = (porigin_method_declare)',
        '$tick_marker(S, porigin_method_declare) = (ptickmarker_method)',
        'ptickmarker_method.FREQUENCY = 2', 'ptickmarker_method.LINE = 6',
        'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 8',
        '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
        *valid('S'), *PAUSE,
        'S_done.TICKCOUNT = 0', 'S_done.EVENTS = ' + output('T', 'Z', 'W', 'T'),
    ],
}

name = 'review-empty-enum-emitter-breaks-adjacency-without-outer-tick'
review.CASES['enum-emitter-enables-following-declare-without-an-enum-marker'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('T', 'P'),
    'checks': [
        'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 6]',
        'porigin_enum = PORIGIN n ([PCINDEX 5])',
        '$class_at(S.CLASSES, porigin_enum) = (pclassdesc)',
        'pclassdesc.KIND = "enum"', '~pclassdesc.EARLY',
        '$class_named(S.CLASSNAMES, $ptascii("tickemptyenum39")) = (porigin_enum)',
        '$tick_marker(S, porigin_enum) = eps',
        '$origin_child((porigin_enum), [PCFIELD 4, PCINDEX 0, PCFIELD 6, PCINDEX 0]) = (porigin_method_declare)',
        '$tick_marker(S, porigin_method_declare) = (ptickmarker_method)',
        'ptickmarker_method.FREQUENCY = 2',
        'ptickmarker.FREQUENCY = 3', 'ptickmarker.LINE = 10',
        '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 1',
        'S_after = $drive_steps(S, 1)', 'S_after.COMPLETION = BUDGET',
        'S_after.TODO = ptask_tail*', 'S_after.TICKCOUNT = 2',
        'S_after.EVENTS = S.EVENTS', *valid('S_after'),
        *valid('S'), *PAUSE,
        'S_done.TICKCOUNT = 0', 'S_done.EVENTS = ' + output('T', 'P', 'Z', 'T'),
    ],
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
