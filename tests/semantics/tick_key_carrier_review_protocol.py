#!/usr/bin/env python3
"""Reach real carrier-key mutations and prove one-step progress with identity intact."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review
import tick_key_carrier_review_cases as sources


def output(raw):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chr(byte)) + ')'
                           for byte in raw) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.STRINGDATA = S.STRINGDATA',
    'S_paused.EVENTS = S.EVENTS', *valid('S_paused'),
    'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
]

review.CASES = {
    'original-coalesce-carrier-write-consumes-its-task': {
        'source': Path(__file__).with_name('tick_coalesce_reader.php').read_text(),
        'stage': 'S.TODO = (KEY_WRITE_DIM (KNOWN pvalue_key) z false) :: ptask_tail* -- if pvalue_key = PSTRING_CARRIER INTERNED_STRING n_bytes* -- if n_bytes* = $ptascii("k") -- if S.CURRENT = eps -- if S.EVENTS = ' + output(b'KTR'),
        'checks': [
            'z = 7', 'S.TICKCOUNT = 2', '$string_carrier_valid(S, pvalue_key)',
            '$key_selected_key(pvalue_key) = (KSTRING n_bytes*)',
            'ptask_tail* = (ORIGIN_RETURN (porigin_assign)) :: (KEY_WRITE_FINISH pkeywriter) :: ptask_after*',
            'pkeywriter.TASK = COALESCE_ASSIGN_WRITE pbase false z_assign',
            'pbase = BASE_DIM pbase_prefix (KNOWN pvalue_key) z_key',
            'pkeywriter.RHS = KNOWN (PINT 9)',
            'S_after = $drive_steps(S, 1)', 'S_after.COMPLETION = BUDGET',
            'S_after.TODO = ptask_tail*',
            'S_after.LOCATION = ELEMENT n_array (KSTRING n_bytes*)',
            'S_after.STRINGDATA = S.STRINGDATA',
            'S_after.EVENTS = S.EVENTS', 'S_after.TICKCOUNT = S.TICKCOUNT',
            *valid('S_after'), *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output(b'KTRT9ZWT'),
        ],
    },
}

name = 'review-interned-numeric-and-padded-keys-stay-distinct'
review.CASES['padded-carrier-write-keeps-the-prior-integer-key'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (KEY_WRITE_DIM (KNOWN pvalue_key) z false) :: ptask_tail* -- if pvalue_key = PSTRING_CARRIER INTERNED_STRING n_bytes* -- if n_bytes* = $ptascii("07") -- if S.CURRENT = eps -- if S.EVENTS = eps',
    'checks': [
        'z = 7', '$string_carrier_valid(S, pvalue_key)',
        '$key_selected_key(pvalue_key) = (KSTRING n_bytes*)',
        '$lookup(S.ENV, $ptascii("values")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_array_before)',
        '$entry_lookup(S.ARRAYS[n_array_before].ITEMS, KINT 7) = (DIRECT pvalue_numeric)',
        '$echo_value(pvalue_numeric) = $ptascii("N")',
        'S_after = $drive_steps(S, 1)', 'S_after.COMPLETION = BUDGET',
        'S_after.TODO = ptask_tail*',
        'S_after.LOCATION = ELEMENT n_array_after (KSTRING n_bytes*)',
        '$entry_lookup(S_after.ARRAYS[n_array_after].ITEMS, KINT 7) = (DIRECT pvalue_numeric)',
        'S_after.STRINGDATA = S.STRINGDATA', 'S_after.EVENTS = eps',
        *valid('S_after'), *valid('S'), *PAUSE,
        'S_done.EVENTS = ' + output(sources.CASES[name][1]),
    ],
}

name = 'review-request-carrier-byte-keys-progress-through-write-and-unset'
review.CASES['request-carrier-unset-deletes-the-equal-byte-key'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = UNSET_ARRAY :: ptask_tail* -- if S.BASE = BASE_DIM pbase (KNOWN pvalue_key) z -- if pvalue_key = PSTRING_CARRIER (REQUEST_STRING n_string) n_bytes* -- if n_bytes* = $ptascii("07") -- if S.CURRENT = eps -- if S.EVENTS = eps',
    'checks': [
        'z = 6', 'S.ORIGIN = (porigin)', '$key_unset_pending(S)',
        '$string_carrier_valid(S, pvalue_key)', 'S.STRINGDATA[n_string] = n_bytes*',
        '$key_selected_key(pvalue_key) = (KSTRING n_bytes*)',
        '$lookup(S.ENV, $ptascii("values")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_array_before)',
        '$entry_lookup(S.ARRAYS[n_array_before].ITEMS, KSTRING n_bytes*) = (DIRECT (PINT 5))',
        'S_after = $drive_steps(S, 1)', 'S_after.COMPLETION = BUDGET',
        'S_after.TODO = (KEY_UNSET_FINISH porigin S.BASE) :: ptask_tail*',
        'S_after.LOCATION = NOWHERE', 'S_after.STRINGDATA = S.STRINGDATA',
        '$lookup(S_after.ENV, $ptascii("values")) = (n_cell_after)',
        'S_after.STORE[n_cell_after] = DEFINED (PARRAY n_array_after)',
        'S_after.ARRAYS[n_array_after].ITEMS = eps', 'S_after.EVENTS = eps',
        *valid('S_after'), *valid('S'), *PAUSE,
        'S_done.EVENTS = ' + output(sources.CASES[name][1]),
    ],
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
