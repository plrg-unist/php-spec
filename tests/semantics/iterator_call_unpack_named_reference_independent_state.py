#!/usr/bin/env python3
"""Independent named-reference admission and later positional-error states."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_named_reference_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCE = next(r['source'] for r in json.loads(INPUT_BYTES[CATALOG])
              if r['id'] == 'iterator-named-reference-review-named-then-positional-error')
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
RAW = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
       'piteratorunpack.CURRENT = REFERENCE n_raw',
       'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
       'S.STORE[n_raw] = DEFINED (POBJECT n_payload)', 'n_raw <- S.REFCELLS',
       'n_data =/= n_payload',
       '$node_children(S, HOBJECT n_data) = [HCELL n_raw]',
       '$node_children(S, HCELL n_raw) = [HOBJECT n_payload]',
       '$useriter_cursor_valid(S, n_cursor, n_data)',
       '$unpack_line(S, piteratorunpack.CALL) = 20']

CASES = {
    'first-named-reference-keeps-fixed-slot-and-named-history': {
        'source': SOURCE,
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [
            *RAW, 'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("item")))',
            'piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '~piteratorunpack.NAMED',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 0',
            'piteratorunpack.HOLD = KNOWN (POBJECT n_payload)',
            'piteratorunpack.SNAPSHOT = (POBJECT n_payload)',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$iterator_unpack_hold_allowed(S, piteratorunpack, "byref")',
            '$iterator_unpack_hold_live(S, piteratorunpack, "byref")',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_raw)]',
            'piteratorunpack_next.NAMED',
            'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
            'piteratorunpack_next.CALL.SENT.NAMED = eps',
            'n_private =/= n_raw', 'n_private <- S_one.REFCELLS',
            'S_one.STORE[n_private] = DEFINED (POBJECT n_payload)',
            'S_one.STORE[n_raw] = DEFINED (POBJECT n_payload)',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            'piteratorunpack_next.SNAPSHOT = eps',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
            'piteratorunpack_later = piteratorunpack[.KEY = KNOWN (PSTRING $ptascii("later"))]',
            '$iterator_unpack_named_target(S, piteratorunpack_later) = NAMED_POSITION 1',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack_later)',
            '~$iterator_unpack_hold_allowed(S, piteratorunpack_later, "byref")',
            'piteratorunpack_unknown = piteratorunpack[.KEY = KNOWN (PSTRING $ptascii("ITEM"))]',
            '$iterator_unpack_named_target(S, piteratorunpack_unknown) = NAMED_UNKNOWN ($ptascii("ITEM"))',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack_unknown)',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack[.NAMED = true])',
            'piteratorunpack_hole = piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.SENT = {SLOTS ([NAMED_HOLE]), NAMED eps}]]',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack_hole)',
            'piteratorunpack_bad = piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.LINE = $(piteratorunpack.CALL.LINE + 1)]]',
            'S_bad = S[.TODO = (ITERATOR_UNPACK piteratorunpack_bad "byref") :: ptask_tail*]',
            '~$iterator_unpack_result_valid(S_bad, piteratorunpack_bad, "byref")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'later-positional-error-retains-first-private-send-and-source': {
        'source': SOURCE,
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.NAMED'),
        'checks': [
            *RAW, 'piteratorunpack.KEY = KNOWN (PINT 0)',
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
            'piteratorunpack.CALL.SENT.NAMED = eps',
            'n_private =/= n_raw', 'n_private <- S.REFCELLS',
            'S.STORE[n_private] = DEFINED (POBJECT n_payload)',
            'piteratorunpack.HOLD = KNOWN PNULL', 'piteratorunpack.SNAPSHOT = eps',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$heap_owners($heap_graph(S), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(ITERATOR_UNPACK piteratorunpack "error") :: ptask_tail*',
            '$throwable_live(S_one, n_error)',
            '$object_name(S_one, n_error) = $ptascii("Error")',
            '$throwable_field(S_one, n_error, "message") = PSTRING '
            '$ptascii("Cannot use positional argument after named argument during unpacking")',
            '$throwable_field(S_one, n_error, "line") = PINT 20',
            'S_one.EVENTS = S.EVENTS',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = '
            '(OBJECTITER n_cursor n_data 0 false)', *POST,
            'S_two_budget = $drive_steps(S_one, 1)',
            'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            '$drive_steps(S, 2) = S_two_budget',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error"',
            'pdestructionoperation.PENDING = (n_error)',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_raw), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HCELL n_private)]',
            '$iterator_lookup(S_two.ITERATORS, n_cursor) = eps',
            '$destructor_release_valid(S_two, pdestructionrelease)',
            '$destructor_operation_valid(S_two, pdestructionoperation)',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
        ],
    },
}


def run(selected):
    review.CASES = CASES
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(selected)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    report_path = raw / 'report.json'
    report = json.loads(report_path.read_bytes())
    report.update(independent_inputs={str(p): hashlib.sha256(b).hexdigest()
                                     for p, b in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, passed=passed and stable)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert stable, 'named-reference review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
