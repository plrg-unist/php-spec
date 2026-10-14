#!/usr/bin/env python3
"""Independent sparse reference slots, frozen keys and default preflight."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_reference_holes_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCE = next(r['source'] for r in json.loads(INPUT_BYTES[CATALOG])
              if r['id'] == 'iterator-reference-holes-review-third-slot-object-frozen-key')
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'third-slot-warning-freezes-key-and-creates-two-holes': {
        'source': SOURCE,
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
            'piteratorunpack.CURRENT = REFERENCE n_raw',
            'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
            'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("item")))',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 2',
            'piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '~piteratorunpack.NAMED', '$unpack_line(S, piteratorunpack.CALL) = 24',
            '$lookup(S.ENV, $ptascii("alias")) = (n_raw)',
            '$lookup(S.ENV, $ptascii("keyAlias")) = (n_key)',
            'n_key =/= n_raw', 'n_raw <- S.REFCELLS', 'n_key <- S.REFCELLS',
            'S.STORE[n_raw] = DEFINED (POBJECT n_payload)',
            'S.STORE[n_key] = DEFINED pvalue_changed_key',
            '$string_bytes(pvalue_changed_key) = ($ptascii("a"))',
            '$node_children(S, HOBJECT n_data) = [HCELL n_raw, HCELL n_key]',
            '$node_children(S, HCELL n_raw) = [HOBJECT n_payload]',
            'piteratorunpack.HOLD = KNOWN (POBJECT n_payload)',
            'piteratorunpack.SNAPSHOT = (POBJECT n_payload)',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$iterator_unpack_hold_allowed(S, piteratorunpack, "byref")',
            '$iterator_unpack_hold_live(S, piteratorunpack, "byref")',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 3',
            '$heap_owners($heap_graph(S), HCELL n_key) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2',
            '$useriter_cursor_valid(S, n_cursor, n_data)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_raw)]',
            'piteratorunpack_next.NAMED',
            'piteratorunpack_next.CALL.SENT.SLOTS = '
            '[NAMED_HOLE, NAMED_HOLE, NAMED_SENT (REFERENCE n_private)]',
            'piteratorunpack_next.CALL.SENT.NAMED = eps',
            'n_private =/= n_raw', 'n_private =/= n_key', 'n_private <- S_one.REFCELLS',
            'S_one.STORE[n_private] = DEFINED (POBJECT n_payload)',
            'S_one.STORE[n_raw] = DEFINED (POBJECT n_payload)',
            'S_one.STORE[n_key] = S.STORE[n_key]',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            'piteratorunpack_next.SNAPSHOT = eps',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
            'piteratorunpack_bad = piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.SENT.SLOTS = ([NAMED_HOLE])]]',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack_bad)',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack[.NAMED = true])',
        ],
    },
    'two-defaults-fill-without-changing-private-or-source-cells': {
        'source': SOURCE,
        'stage': ('S.TODO = [NAMED_PREFLIGHT porigin 0] '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("reviewHoleThird02")'),
        'checks': [
            'pcallcontext.FUNCTION = porigin', 'pcallcontext.ARGC = 3',
            'pcallcontext.HOLES = [0, 1]',
            'pcallcontext.PARAMS = [$ptascii("a"), $ptascii("b"), $ptascii("item")]',
            'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = eps',
            'pcallcontext.LINE = 24',
            '~$named_defined(S, $ptascii("a"))', '~$named_defined(S, $ptascii("b"))',
            '$lookup(S.ENV, $ptascii("item")) = (n_private)',
            'S.STORE[n_private] = DEFINED (POBJECT n_payload)',
            'n_private <- S.REFCELLS',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("alias")) = (n_raw)',
            '$lookup(psymboltable_global.ENV, $ptascii("keyAlias")) = (n_key)',
            'n_private =/= n_raw', 'n_private =/= n_key',
            'S.STORE[n_raw] = DEFINED (POBJECT n_payload)',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 1',
            '$heap_owners($heap_graph(S), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("ReviewHoleIterator02")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '$named_preflight_valid(S, porigin, 0)', *ADMISSION, *ZERO,
            'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
            'S_first = S_first_budget[.COMPLETION = NORMAL]',
            'S_first.TODO = [NAMED_PREFLIGHT porigin 1]',
            '$lookup(S_first.ENV, $ptascii("a")) = (n_a)',
            'S_first.STORE[n_a] = DEFINED (PINT 17)',
            '~$named_defined(S_first, $ptascii("b"))',
            'S_second_budget = $drive_steps(S_first, 1)',
            'S_second_budget.COMPLETION = BUDGET',
            '$drive_steps(S, 2) = S_second_budget',
            'S_second = S_second_budget[.COMPLETION = NORMAL]',
            'S_second.TODO = [NAMED_PREFLIGHT porigin 2]',
            '$lookup(S_second.ENV, $ptascii("b")) = (n_b)',
            'S_second.STORE[n_b] = DEFINED pvalue_default',
            '$string_bytes(pvalue_default) = ($ptascii("seed"))',
            'S_second.CURRENT = S.CURRENT', 'S_second.EVENTS = S.EVENTS',
            'S_second.STORE[n_private] = S.STORE[n_private]',
            'S_second.STORE[n_raw] = S.STORE[n_raw]',
            'S_second.STORE[n_key] = S.STORE[n_key]',
            '$heap_owners($heap_graph(S_second), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S_second), HOBJECT n_payload) = 2',
            '$named_preflight_valid(S_second, porigin, 2)',
            '$call_descriptors_valid(S_second)', '$heap_valid($heap_graph(S_second))',
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
    return passed and stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
