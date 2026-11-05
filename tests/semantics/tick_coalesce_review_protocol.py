#!/usr/bin/env python3
"""Reach quiet coalesce selection, a memoized write and its inherited marker."""
import argparse
import json

import fiber_state_review as review
import tick_coalesce_review_cases as sources


def output(raw):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chr(byte)) + ')'
                           for byte in raw) + ']'


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

name = 'review-quiet-cv-read-and-runtime-unselected-fallback-declarables'
review.CASES = {
    'quiet-present-cv-skips-runtime-fallback-with-compiled-declarables': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.TODO = (COALESCE_QUIET expression_rhs z_left z_right) :: ptask_tail* -- if S.CURRENT = eps -- if S.BASE = BASE_VALUE (VARIABLE n_name* z_name) -- if n_name* = $ptascii("present") -- if S.EVENTS = ' + output(b'MT'),
        'checks': [
            'S.ORIGIN = (porigin)', 'porigin = PORIGIN n pcpath',
            'pcpath = [PCINDEX 4, PCFIELD 1, PCINDEX 1, PCFIELD 0, PCFIELD 1]',
            '$origin_node(S.SOURCES, porigin) = (NExprBinaryOpCoalesce expression_left expression_rhs metadata)',
            '$coalesce_quiet_operand(expression_left)',
            'S.TICKCOUNT = 1',
            'S_quiet = $quiet_base(S, S.BASE, z_left)',
            'S_quiet.COMPLETION = NORMAL', 'S_quiet.EVENTS = S.EVENTS',
            'S_quiet.RESULT = KNOWN pvalue_selected',
            '$echo_value(pvalue_selected) = $ptascii("P")',
            'S_selected = $drive_steps(S, 1)', 'S_selected.COMPLETION = BUDGET',
            'S_selected.TODO = ptask_tail*',
            'S_selected.RESULT = S_quiet.RESULT',
            'S_selected.EVENTS = S.EVENTS', 'S_selected.TICKCOUNT = 1',
            *valid('S_selected'), *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output(sources.CASES[name][1]),
        ],
    },
}

name = 'review-missing-dimension-coalesce-assignment-memoizes-key'
review.CASES['missing-dimension-retains-one-key-before-memoized-write'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (COALESCE_ASSIGN_WRITE pbase false z) :: ptask_tail* -- if S.CURRENT = eps -- if S.RESULT = KNOWN (PINT 9) -- if S.EVENTS = ' + output(b'KTR'),
    'checks': [
        'S.ORIGIN = (porigin)', 'porigin = PORIGIN n pcpath',
        '$code_at(S.CODE, n) = (pcode)',
        'pcpath = [PCINDEX 4, PCFIELD 1, PCINDEX 0, PCFIELD 0]',
        '$origin_node(S.SOURCES, porigin) = (NExprAssignOpCoalesce expression_target expression_rhs metadata)',
        'pbase = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_base)) (KNOWN pvalue_key) z_key',
        'n_name* = $ptascii("values")', '$echo_value(pvalue_key) = $ptascii("k")',
        '$origin_child((porigin), [PCFIELD 0]) = (porigin_target)',
        '$memoized_write_ready(S, pbase, [PCFIELD 0])',
        '$key_coalesce_write_source(S, porigin, pbase, false, z) = (porigin_target)',
        '$lookup(S.ENV, n_name*) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_array)', 'S.ARRAYS[n_array].ITEMS = eps',
        'S.TICKCOUNT = 2',
        'pcpath_statement = [PCINDEX 4, PCFIELD 1, PCINDEX 0]',
        '$tick_marker(S, PORIGIN n pcpath_statement) = (ptickmarker)',
        'ptickmarker.FREQUENCY = 3', 'ptickmarker.LINE = 7',
        *valid('S'), *PAUSE,
        'S_paused.BASE = S.BASE', 'S_paused.RESULT = S.RESULT',
        'S_done.EVENTS = ' + output(sources.CASES[name][1]),
    ],
}

name = 'review-present-dimension-coalesce-assignment-skips-runtime-fallback'
review.CASES['present-dimension-parks-marker-after-one-key-and-no-rhs'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output(b'KT'),
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath = [PCINDEX 3, PCFIELD 1, PCINDEX 0]',
        '$origin_node(S.SOURCES, porigin) = (NStmtExpression (NExprAssignOpCoalesce expression_target expression_rhs metadata) metadata_statement)',
        'ptickmarker.FREQUENCY = 3', 'ptickmarker.LINE = 6',
        'S.TICKCOUNT = 0', '$tick_marker_valid(S, porigin, ptickmarker)',
        '$lookup(S.ENV, $ptascii("values")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING $ptascii("k")) (DIRECT (PINT 4))]',
        'S_counted = $drive_steps(S, 1)', 'S_counted.COMPLETION = BUDGET',
        'S_counted.TODO = ptask_tail*', 'S_counted.TICKCOUNT = 1',
        'S_counted.EVENTS = S.EVENTS', *valid('S_counted'),
        'S_bad = S[.TODO = (TICK porigin ptickmarker[.FREQUENCY = 2]) :: ptask_tail*]',
        '~$call_descriptors_valid(S_bad)',
        *valid('S'), *PAUSE,
        'S_done.EVENTS = ' + output(sources.CASES[name][1]),
    ],
}

DERIVED_GUARDS = {
    'quiet-present-cv-skips-runtime-fallback-with-compiled-declarables': 0,
    'missing-dimension-retains-one-key-before-memoized-write': 0,
    'present-dimension-parks-marker-after-one-key-and-no-rhs': 1,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
