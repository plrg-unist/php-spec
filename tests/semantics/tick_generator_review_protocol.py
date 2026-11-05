#!/usr/bin/env python3
"""Check parked tick continuations and unchanged Generator send prefixes."""
import argparse
import json

import fiber_state_review as review
import tick_generator_review_cases as sources


def output(raw):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chr(byte)) + ')'
                           for byte in raw) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))',
            f'$generator_state_valid({state})', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.TICKCOUNT = S.TICKCOUNT',
    'S_paused.OBJECTS = S.OBJECTS', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'),
    'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
    'S_done.TICKCOUNT = 0', *valid('S_done'),
]

ROOT_GENERATOR = ('S.CURRENT = eps '
                  '-- if $lookup(S.ENV, $ptascii("g")) = (n_cell) '
                  '-- if S.STORE[n_cell] = DEFINED (POBJECT n) '
                  '-- if S.OBJECTS[n] = GENERATOR pgenerator ')


def send_case(name, used):
    raw, expected = sources.CASES[name]
    prefix = [
        'pframe.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_name* z) :: ptask_tail*',
        '$generator_input_tail(S, porigin_yield, pframe.TODO)',
        '$generator_send_target(pframe.TODO)',
        'n_name* = $ptascii("seen")',
    ] if used else [
        'pframe.TODO = (ORIGIN_RETURN (porigin_statement)) :: DISCARD :: (TICK porigin_statement ptickmarker) :: ptask_tail*',
        '$generator_unused_send_tail(S, porigin_yield, pframe.TODO)',
        '~$generator_send_target(pframe.TODO)',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 6',
        '$tick_marker_valid(S, porigin_statement, ptickmarker)',
        'pframe_bad = pframe[.TODO = (ORIGIN_RETURN (porigin_statement)) :: DISCARD :: (TICK porigin_statement ptickmarker[.LINE = 7]) :: ptask_tail*]',
        'S_bad = $generator_set(S, n, pgenerator[.FRAME = (pframe_bad)])',
        '~$generator_record_valid(S_bad, pgenerator[.FRAME = (pframe_bad)])',
    ]
    return {
        'source': raw.decode(),
        'stage': ROOT_GENERATOR + '-- if pgenerator.PHASE = GENERATOR_PAUSED -- if pgenerator.VALUE = (PINT 1) -- if pgenerator.FRAME = (pframe) -- if S.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("T")]',
        'checks': [
            'S.TICKCOUNT = 0', 'pframe.ORIGIN = (porigin_yield)',
            '$generator_record_valid(S, pgenerator)', *prefix,
            *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output(expected),
        ],
    }


raw, expected = sources.CASES['review-counter-across-yield-and-from']
review.CASES = {
    'bare-yield-parks-discard-before-pending-tick': send_case(
        'review-bare-yield-send-discards-input', False),
    'assigned-yield-parks-real-send-target-before-statement-tick': send_case(
        'review-assigned-yield-send-preserves-target', True),
    'array-delegation-keeps-one-later-marker-and-shared-counter': {
        'source': raw.decode(),
        'stage': ROOT_GENERATOR + '-- if pgenerator.PHASE = GENERATOR_DELEGATING -- if pgenerator.FRAME = (pframe) -- if pgenerator.DELEGATE = (pgeneratorfrom) -- if pgeneratorfrom.CURRENT = (KNOWN (PINT 2)) -- if S.EVENTS = ' + output(b'IA1OTBT'),
        'checks': [
            'S.TICKCOUNT = 0', 'pgeneratorfrom.POSITION = 1',
            'pgeneratorfrom.INPUT = (PARRAY n_array)',
            'pframe.ORIGIN = (pgeneratorfrom.SITE)',
            'pframe.TODO = (GENERATOR_FROM_NEXT n pgeneratorfrom.SITE) :: (ORIGIN_RETURN (porigin_statement)) :: DISCARD :: (TICK porigin_statement ptickmarker) :: ptask_tail*',
            'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 8',
            '$tick_marker_valid(S, porigin_statement, ptickmarker)',
            '$generator_from_record_valid(S, n, pgenerator)',
            'pframe_bad = pframe[.TODO = (GENERATOR_FROM_NEXT n pgeneratorfrom.SITE) :: (ORIGIN_RETURN (porigin_statement)) :: DISCARD :: (TICK porigin_statement ptickmarker[.FREQUENCY = 1]) :: ptask_tail*]',
            'S_bad = $generator_set(S, n, pgenerator[.FRAME = (pframe_bad)])',
            '~$generator_record_valid(S_bad, pgenerator[.FRAME = (pframe_bad)])',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output(expected),
        ],
    },
}

DERIVED_GUARDS = {
    'bare-yield-parks-discard-before-pending-tick': 1,
    'assigned-yield-parks-real-send-target-before-statement-tick': 0,
    'array-delegation-keeps-one-later-marker-and-shared-counter': 1,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
