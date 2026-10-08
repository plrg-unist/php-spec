#!/usr/bin/env python3
"""Reached ordinary-array START unwind preserves positional/receiver/named order."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_array_start_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'author-fiber-array-start-abrupt-positional-and-named-owner-order')
EVENTS = ('[OUTPUT $ptascii("Y"), OUTPUT $ptascii("|"), OUTPUT $ptascii("A|"), '
          'OUTPUT $ptascii("D"), OUTPUT $ptascii("0"), OUTPUT $ptascii("|"), '
          'OUTPUT $ptascii("F|"), OUTPUT $ptascii("argument"), OUTPUT $ptascii("|"), '
          'OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("Y"), '
          'OUTPUT $ptascii("|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("F|"), '
          'OUTPUT $ptascii("D"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
          'OUTPUT $ptascii("argument"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1")]')


def checks(named):
    slot = ('pfiberstart.SENT.NAMED = [($ptascii("first"), KNOWN (POBJECT n_arg))]'
            if named else
            'pfiberstart.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_arg))]')
    jobs = ('[DESTRUCTION_VALUE (HOBJECT pfiberstart.OBJECT), DESTRUCTION_VALUE (HOBJECT n_arg)]'
            if named else
            '[DESTRUCTION_VALUE (HOBJECT n_arg), DESTRUCTION_VALUE (HOBJECT pfiberstart.OBJECT)]')
    out = [
        'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps', 'S.CURRENT = eps',
        'S.FRAMES = eps', 'S.ORIGIN = (pfiberstart.SITE)', 'pfiberstart.INDEX = 1',
        '$intrinsic_count(S, pfiberstart.SITE) = (2)', slot,
        'S.OBJECTS[pfiberstart.OBJECT] = FIBER pfiber',
        'pfiber.STATUS = FIBER_SUSPENDED', 'pfiber.VM =/= eps',
        'pfiberarray.KIND = INTRINSIC_FIBER_START',
        'pfiberarray.INPUT = (pfiberstart.OBJECT)',
        'pfiberarray.NAME = $ptascii("start")',
        'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT pfiberstart.OBJECT)), '
        'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("start"))))]',
        '~((HARRAY pfiberarray.ARRAY) <- S.ALLOCATIONS)',
        '$lookup(S.ENV, $ptascii("pair")) = (n_pair_cell)',
        'S.STORE[n_pair_cell] = DEFINED PNULL',
        '$fiber_array_start_source_valid(S, pfiberarray)',
        '~$fiber_array_source_valid(S, pfiberarray)',
        '$fiber_array_start_buffer_valid(S, pfiberarray, pfiberstart)',
        '$fiber_start_valid(S, pfiberstart, true)',
        '$fiber_array_start_release_valid(S, pfiberarray)',
        '$task_nodes(FIBER_ARRAY_START_RELEASE pfiberarray) = eps',
        '$task_nodes(FIBER_SEND pfiberstart) = [HOBJECT pfiberstart.OBJECT, HOBJECT n_arg]',
        'H = $heap_graph(S)', '$heap_owners(H, HOBJECT pfiberstart.OBJECT) = 1',
        '$heap_owners(H, HOBJECT n_arg) = 1', *review.VALID,
        'S_after = S[.TODO = (THROW_SEARCH n_throwable) :: '
        '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
        '$fiber_array_start_unwind_valid(S_after, pfiberstart)',
    ]
    if not named:
        out += [
            'pfiberarray_line = pfiberarray[.LINE = $(pfiberarray.LINE + 1)]',
            'pfiberstart_line = pfiberstart[.LINE = pfiberarray_line.LINE]',
            'S_line = S[.TODO = (THROW_SEARCH n_throwable) :: (FIBER_SEND pfiberstart_line) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray_line) :: ptask_tail*]',
            '$heap_graph(S_line) = H', '~$fiber_start_valid(S_line, pfiberstart_line, true)',
            '~$call_descriptors_valid(S_line)',
            'S_line_after = S_line[.TODO = (THROW_SEARCH n_throwable) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray_line) :: ptask_tail*]',
            '~$fiber_array_start_unwind_valid(S_line_after, pfiberstart_line)',
            'pfiberarray_name = pfiberarray[.NAME = $ptascii("resume")]',
            'S_name = S[.TODO = (THROW_SEARCH n_throwable) :: (FIBER_SEND pfiberstart) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray_name) :: ptask_tail*]',
            '$heap_graph(S_name) = H', '~$fiber_array_start_source_valid(S_name, pfiberarray_name)',
            '~$call_descriptors_valid(S_name)',
            'S_missing = S[.TODO = (THROW_SEARCH n_throwable) :: (FIBER_SEND pfiberstart) :: ptask_tail*]',
            '$heap_graph(S_missing) = H', '~$fiber_start_valid(S_missing, pfiberstart, true)',
            '~$call_descriptors_valid(S_missing)',
            'S_duplicate = S[.TODO = (THROW_SEARCH n_throwable) :: (FIBER_SEND pfiberstart) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray) :: (FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
            '$heap_graph(S_duplicate) = H',
            '$fiber_array_count(S_duplicate.TODO, pfiberarray.SITE) = 2',
            '~$fiber_start_valid(S_duplicate, pfiberstart, true)',
            '~$call_descriptors_valid(S_duplicate)',
        ]
    return out + [
        'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S',
        'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
        'S_one = S_one_budget[.COMPLETION = NORMAL]',
        'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_throwable) :: '
        '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*',
        f'pdestructionrelease.JOBS = {jobs}',
        'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
        'pdestructionrelease.CONSTCONTEXT = S.CONSTCONTEXT',
        'S_one.DESTRUCTION.RELEASES = pdestructionrelease :: S.DESTRUCTION.RELEASES',
        'S_one.ALLOCATIONS = S.ALLOCATIONS',
        '$heap_owners($heap_graph(S_one), HOBJECT pfiberstart.OBJECT) = 1',
        '$heap_owners($heap_graph(S_one), HOBJECT n_arg) = 1',
        '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        'S_done = $drive(S_one, 4000)', *review.DONE, f'S_done.EVENTS = {EVENTS}',
    ]


CASES = {
    'array-start-positional-unwind-releases-payload-before-last-receiver': {
        'source': SOURCE,
        'stage': 'S.TODO = (THROW_SEARCH n_throwable) :: (FIBER_SEND pfiberstart) :: '
                 '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail* '
                 '-- if pfiberstart.SENT.NAMED = eps -- if pfiberstart.INDEX = 1',
        'checks': checks(False),
    },
    'array-start-named-unwind-releases-last-receiver-before-payload': {
        'source': SOURCE,
        'stage': 'S.TODO = (THROW_SEARCH n_throwable) :: (FIBER_SEND pfiberstart) :: '
                 '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail* '
                 '-- if pfiberstart.SENT.SLOTS = eps -- if pfiberstart.INDEX = 1',
        'checks': checks(True),
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = all(review.run([name]) for name in args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Array START catalog changed during run'
    raise SystemExit(0 if passed else 1)
