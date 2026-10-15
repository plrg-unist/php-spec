#!/usr/bin/env python3
"""Reach detached cache/return receipts, real key errors and last-owner cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_detached_child_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}

DETACHED = [
    'n_data = pgeneratorunpack.OBJECT',
    'pgeneratorunpack.INPUT = VARIABLE ptbytes z',
    'ptbytes = $ptascii("parent")',
    '$lookup(S.ENV, ptbytes) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (POBJECT n_data)',
    'pgeneratorunpack.COUNT = 0',
    '~pgeneratorunpack.NAMED',
    'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
    'S.OBJECTS[n_data] = GENERATOR pgenerator',
    'pgenerator.PHASE = GENERATOR_DELEGATING',
    'pgenerator.FIRST',
    'pgenerator.VALUE = eps',
    'pgenerator.KEY = eps',
    'pgenerator.REFCELL = eps',
    'pgenerator.BORROWED = eps',
    'pgenerator.DELEGATE = (pgeneratorfrom)',
    'pgeneratorfrom.INPUT = eps',
    'pgeneratorfrom.ACQUISITION = eps',
    'pgeneratorfrom.POSITION = 1',
    'pgeneratorfrom.CURRENT = (poperand_cache)',
    'pgenerator.FRAME = (pframe_saved)',
    'pframe_saved.TODO = (GENERATOR_FROM_COMPLETE n_data pgeneratorfrom.SITE n_leaf pvalue_return) :: ptask_saved*',
    'pvalue_return = PINT 23',
    '$value_nodes(pvalue_return) = eps',
    'S.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf',
    'pgenerator_leaf.PHASE = GENERATOR_CLOSED',
    'pgenerator_leaf.RETURN = (pvalue_return)',
    '$generator_from_record_valid(S, n_data, pgenerator)',
    '$generator_from_complete_valid(S, n_data, pgeneratorfrom.SITE, n_leaf, pvalue_return)',
    '$generator_unpack_detached(S, n_data)',
    '$generator_unpack_delegate(S, n_data)',
    '~$generator_unpack_chain(S, n_data, $(|S.OBJECTS| + 1))',
    '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
    '$generator_cached_value(S, n_data, true) = PNULL',
    '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
    '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = [HOBJECT n_data]',
    '$call_descriptors_valid(S)',
    '$heap_valid($heap_graph(S))',
]

ERROR = [
    'S_zero = $drive(S, 0)',
    'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one_budget = $drive_steps(S, 1)',
    'S_one_budget.COMPLETION = BUDGET',
    'S_one = S_one_budget[.COMPLETION = NORMAL]',
    'S_one.TODO = (THROW_SEARCH n_error) :: (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail*',
    '$string_bytes($throwable_field(S_one, n_error, "message")) = ($ptascii("Keys must be of type int|string during argument unpacking"))',
    '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
    'S_one.ARRAYS[n_trace].ITEMS = eps',
    'S_one.OBJECTS[n_data] = S.OBJECTS[n_data]',
    'S_one.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_one)',
    '$heap_valid($heap_graph(S_one))',
    'S_two_budget = $drive_steps(S_one, 1)',
    'S_two_budget.COMPLETION = BUDGET',
    '$drive(S, 2) = S_two_budget',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
    'S_two = S_two_budget[.COMPLETION = NORMAL]',
    '$call_descriptors_valid(S_two)',
    '$heap_valid($heap_graph(S_two))',
]

DONE = [
    'S_done = $drive(S_two, 4000)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.FRAMES = eps',
    'S_done.CURRENT = eps',
    'S_done.HELD = eps',
    '$call_descriptors_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_leaf) = 0',
]

CASES = {
    'detached-scalar-ready-errors-without-consuming-real-return-tail': {
        'source': SOURCES['generator-detached-unpack-null-key-error-then-real-return-and-tail'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* -- if pgeneratorunpack.COUNT = 0',
        'checks': [*DETACHED,
            'poperand_cache = KNOWN (PINT 7)',
            'pgenerator_leaf.VALUE = (PINT 7)',
            '$heap_owners($heap_graph(S), HOBJECT n_leaf) = 1',
            '$generator_from_nodes(pgenerator.DELEGATE) = eps',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("7"), OUTPUT $ptascii("|K|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|")]',
            'S_missing = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.CURRENT = eps])])',
            '~$generator_unpack_detached(S_missing, n_data)',
            '~$generator_unpack_valid(S_missing, pgeneratorunpack, "ready")',
            'S_next = $generator_set(S, n_data, pgenerator[.FRAME = (pframe_saved[.TODO = (GENERATOR_FROM_NEXT n_data pgeneratorfrom.SITE) :: ptask_saved*])])',
            '~$generator_unpack_detached(S_next, n_data)',
            'S_position = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.POSITION = 0])])',
            '~$generator_unpack_detached(S_position, n_data)',
            'pgeneratorunpack.CALL.CALLSITE = (porigin_call)',
            'S_source = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.SITE = porigin_call])])',
            '~$generator_unpack_detached(S_source, n_data)',
            'S_key = $generator_set(S, n_data, pgenerator[.KEY = (PINT 4)])',
            '$generator_unpack_detached(S_key, n_data)',
            '$generator_cached_value(S_key, n_data, true) = PINT 4',
            *ERROR,
            '$throwable_field(S_one, n_error, "line") = PINT 8',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), OUTPUT $ptascii("8"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("N|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("23"), OUTPUT $ptascii("|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("13"), OUTPUT $ptascii("|K|"), OUTPUT $ptascii("0"), OUTPUT $ptascii("|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("29"), OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
        ],
    },
    'retired-child-receipt-keeps-only-parent-object-cache-owner': {
        'source': SOURCES['generator-detached-unpack-retired-child-object-cache-and-scalar-return'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* -- if pgeneratorunpack.COUNT = 0',
        'checks': [*DETACHED,
            'poperand_cache = KNOWN (POBJECT n_cache)',
            '~(HOBJECT n_leaf <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_leaf) = 0',
            '$generator_from_nodes(pgenerator.DELEGATE) = [HOBJECT n_cache]',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("M|")]',
            'pvalue_owning = POBJECT n_cache',
            '$value_nodes(pvalue_owning) = [HOBJECT n_cache]',
            'S_owning_child = $generator_set(S, n_leaf, pgenerator_leaf[.RETURN = (pvalue_owning)])',
            'pgenerator_owning = pgenerator[.FRAME = (pframe_saved[.TODO = (GENERATOR_FROM_COMPLETE n_data pgeneratorfrom.SITE n_leaf pvalue_owning) :: ptask_saved*])]',
            'S_owning = $generator_set(S_owning_child, n_data, pgenerator_owning)',
            '$generator_from_record_valid(S_owning, n_data, pgenerator_owning)',
            '$generator_from_complete_valid(S_owning, n_data, pgeneratorfrom.SITE, n_leaf, pvalue_owning)',
            '~$generator_unpack_detached(S_owning, n_data)',
            '~$generator_unpack_delegate(S_owning, n_data)',
            *ERROR,
            '$throwable_field(S_one, n_error, "line") = PINT 9',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 1',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), OUTPUT $ptascii("9"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            'n_cache <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'detached-present-null-key-error-precedes-byref-target': {
        'source': SOURCES['generator-detached-unpack-present-null-key-error-precedes-byref-target'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* -- if pgeneratorunpack.COUNT = 0',
        'checks': [*DETACHED,
            'poperand_cache = KNOWN PNULL',
            '$generator_cache_present(S, n_data)',
            '$generator_cached_value(S, n_data, false) = PNULL',
            '$target_function(S, pgeneratorunpack.CALL.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.BYREF',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|")]',
            *ERROR,
            '$throwable_field(S_one, n_error, "line") = PINT 6',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), OUTPUT $ptascii("6"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("E")]',
        ],
    },
}

assert all(case['source'] in SOURCES.values() for case in CASES.values())

def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in INPUTS}
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
    stable = before == {str(path): digest(path) for path in INPUTS}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                                     cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs=before, author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
