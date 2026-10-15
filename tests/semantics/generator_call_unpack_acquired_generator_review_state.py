#!/usr/bin/env python3
"""Reach acquired-Generator reference caches, outer links and child COW owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_acquired_generator_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}

CASES = {
    'active-outer-borrows-acquired-parent-reference-cache-before-byvalue-send': {
        'source': SOURCES['generator-call-unpack-acquired-generator-review-reference-snapshot-through-active-parent'],
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 0'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps', 'S.HELD = eps',
            'n_outer = pgeneratorunpack.OBJECT',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_outer)',
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '~pgeneratorunpack.NAMED',
            'S.OBJECTS[n_outer] = GENERATOR pgenerator_outer',
            'pgenerator_outer.PHASE = GENERATOR_DELEGATING',
            'pgenerator_outer.VALUE = eps', 'pgenerator_outer.KEY = eps',
            'pgenerator_outer.DELEGATE = (pgeneratorfrom_outer)',
            'pgeneratorfrom_outer.INPUT = (POBJECT n_parent)',
            'pgeneratorfrom_outer.ACQUISITION = eps',
            'pgeneratorfrom_outer.CURRENT = eps',
            'pgeneratorfrom_outer.POSITION = 1',
            '$generator_from_record_valid(S, n_outer, pgenerator_outer)',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_DELEGATING',
            'pgenerator_parent.VALUE = eps', 'pgenerator_parent.REFCELL = eps',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
            'pgeneratorfrom.CURRENT = (REFERENCE n_raw)',
            'pgeneratorfrom.POSITION = 1',
            'pgeneratorfrom.SITE = pyieldfromreceipt.SITE',
            '$generator_from_record_valid(S, n_parent, pgenerator_parent)',
            '$yield_from_receipt_valid(S, pyieldfromreceipt)',
            'n_aggregate = pyieldfromreceipt.AGGREGATE',
            '$object_name(S, n_aggregate) = $ptascii("ReviewAcquiredReferenceAggregate15")',
            '~((HOBJECT n_aggregate) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_aggregate) = 0',
            'n_aggregate <- S.DESTRUCTION.CALLED',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            'pgenerator_child.VALUE = eps', 'pgenerator_child.REFCELL = (n_raw)',
            'pgenerator_child.DELEGATE = eps',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.CONTEXT = (pcallcontext_child)',
            '$trace_context_function(S, pcallcontext_child) = $ptascii("reviewAcquiredReferenceChild15")',
            '$lookup(S.ENV, $ptascii("child")) = (n_alias)',
            'S.STORE[n_alias] = DEFINED (POBJECT n_child)',
            '$lookup(S.ENV, $ptascii("payload")) = (n_raw)',
            'n_raw <- S.REFCELLS',
            'S.STORE[n_raw] = DEFINED (POBJECT n_old)',
            '$object_name(S, n_old) = $ptascii("ReviewAcquiredReferenceFirst15")',
            '$node_children(S, HOBJECT n_outer) = [HOBJECT n_parent]',
            '$node_children(S, HOBJECT n_parent) = [HOBJECT n_child, HCELL n_raw]',
            '$node_children(S, HOBJECT n_child) = $generator_frame_nodes(pgenerator_child.FRAME) ++ [HCELL n_raw]',
            '$heap_owners($heap_graph(S), HOBJECT n_outer) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_parent) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 4',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$generator_cached_value(S, n_outer, false) = POBJECT n_old',
            '$string_bytes($generator_cached_value(S, n_outer, true)) = ($ptascii("item"))',
            '$generator_unpack_acquired_generator_delegate(S, n_parent)',
            '~$generator_unpack_acquired_generator_delegate(S, n_outer)',
            '$generator_unpack_chain(S, n_outer, 2)',
            '~$generator_unpack_chain(S, n_outer, 1)',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            'pyieldfromreceipt_bad = pyieldfromreceipt[.LINE = $(pyieldfromreceipt.LINE + 1)]',
            'S_bad = $generator_set(S, n_parent, pgenerator_parent[.DELEGATE = (pgeneratorfrom[.ACQUISITION = (pyieldfromreceipt_bad)])])',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$generator_unpack_delegate(S_bad, n_outer)',
            '~$call_descriptors_valid(S_bad)',
            'S_missing = $generator_set(S, n_parent, pgenerator_parent[.DELEGATE = (pgeneratorfrom[.CURRENT = eps])])',
            '~$generator_unpack_delegate(S_missing, n_outer)',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("GET|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("C|")]',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorunpack_next.COUNT = 1', 'pgeneratorunpack_next.NAMED',
            'pgeneratorunpack_next.CALL.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_old))]), NAMED eps}',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HCELL n_raw) = 4',
            '$heap_owners($heap_graph(S_one), HOBJECT n_old) = 2',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("N|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("OL|"), OUTPUT $ptascii("OF|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("LIVE|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("X|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_outer) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_parent) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 0',
            'n_old <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'acquired-generator-child-throw-keeps-copied-cache-and-independent-cv': {
        'source': SOURCES['generator-call-unpack-acquired-generator-review-child-throw-retains-independent-cache-and-cow-row'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext_child) '
                  '-- if $trace_context_function(S, pcallcontext_child) = $ptascii("reviewAcquiredRowChild15")'),
        'checks': [
            'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps',
            'pcallcontext_child.ARGC = 0',
            'pcallcontext_child.EXTRA = eps',
            'S.FRAMES = [pframe_parent, pframe_caller]',
            'pframe_parent.CONTEXT = (pcallcontext_parent)',
            '$trace_context_function(S, pcallcontext_parent) = $ptascii("reviewAcquiredRowParent15")',
            'pframe_parent.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (YIELD_FROM_ITERATOR_RESULT n_parent pyieldfromreceipt n_child) :: ptask_parent*',
            'pgeneratorop_child.OBJECT = n_child',
            'pgeneratorop_child.NAME = "next"',
            '~pgeneratorop_child.STARTPACK',
            'pgeneratorop_child.BORROWED',
            'pgeneratorop_child.SITE = pyieldfromreceipt.SITE',
            'pgeneratorop_child.LINE = pyieldfromreceipt.LINE',
            '$task_nodes(GENERATOR_RESUME pgeneratorop_child) = eps',
            '$generator_operation_trace(S, pgeneratorop_child) = eps',
            '$yield_from_iterator_operation_valid(S, pgeneratorop_child)',
            '~$yield_from_iterator_operation_valid(S, pgeneratorop_child[.STARTPACK = true])',
            'pframe_caller.CONTEXT = eps',
            'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop_parent) :: (GENERATOR_UNPACK pgeneratorunpack "next") :: ptask_caller*',
            'pgeneratorop_parent.OBJECT = n_parent',
            'pgeneratorop_parent.NAME = "next"',
            'pgeneratorop_parent.STARTPACK',
            'pgeneratorop_parent.BORROWED',
            '$task_nodes(GENERATOR_RESUME pgeneratorop_parent) = eps',
            '$generator_operation_trace(S, pgeneratorop_parent) = eps',
            'pgeneratorunpack.OBJECT = n_parent',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_parent)',
            'pgeneratorunpack.COUNT = 1',
            '~pgeneratorunpack.NAMED',
            'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PARRAY n_snapshot))]',
            'pgeneratorunpack.CALL.SENT.NAMED = eps',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_RUNNING',
            'pgenerator_parent.FRAME = eps',
            'pgenerator_parent.VALUE = eps',
            'pgenerator_parent.KEY = (PINT 0)',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
            'pgeneratorfrom.CURRENT = (KNOWN (PARRAY n_snapshot))',
            'pgeneratorfrom.POSITION = 1',
            'pgeneratorfrom.SITE = pyieldfromreceipt.SITE',
            'pyieldfromreceipt.FUNCTION = pcallcontext_parent.FUNCTION',
            'pyieldfromreceipt.LINE = 16',
            '$yield_from_receipt_valid(S, pyieldfromreceipt)',
            '$generator_from_record_valid(S, n_parent, pgenerator_parent)',
            '~$generator_from_shared(S, (pgeneratorfrom))',
            'n_aggregate = pyieldfromreceipt.AGGREGATE',
            '$object_name(S, n_aggregate) = $ptascii("ReviewAcquiredRowAggregate15")',
            '~((HOBJECT n_aggregate) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_aggregate) = 0',
            'n_aggregate <- S.DESTRUCTION.CALLED',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_RUNNING',
            'pgenerator_child.FRAME = eps',
            'pgenerator_child.VALUE = (PARRAY n_snapshot)',
            'pgenerator_child.REFCELL = eps',
            'pgenerator_child.DELEGATE = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("child")) = (n_alias)',
            'S.STORE[n_alias] = DEFINED (POBJECT n_child)',
            '(HCELL n_alias) <- S.ALLOCATIONS',
            '$lookup(S.ENV, $ptascii("row")) = (n_local)',
            'S.STORE[n_local] = DEFINED (PARRAY n_live)',
            'n_snapshot =/= n_live',
            'S.ARRAYS[n_snapshot].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
            'S.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new))]',
            '$object_name(S, n_old) = $ptascii("ReviewAcquiredRowFirst15")',
            '$object_name(S, n_new) = $ptascii("ReviewAcquiredRowSecond15")',
            '$node_children(S, HOBJECT n_parent) = [HOBJECT n_child, HARRAY n_snapshot]',
            '$node_children(S, HOBJECT n_child) = [HARRAY n_snapshot]',
            '$heap_owners($heap_graph(S), HOBJECT n_parent) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_snapshot) = 3',
            '$heap_owners($heap_graph(S), HARRAY n_live) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_new) = 1',
            'pyieldfromreceipt_bad = pyieldfromreceipt[.LINE = $(pyieldfromreceipt.LINE + 1)]',
            '~$yield_from_receipt_valid(S, pyieldfromreceipt_bad)',
            'S_bad = $generator_set(S, n_parent, pgenerator_parent[.DELEGATE = (pgeneratorfrom[.ACQUISITION = (pyieldfromreceipt_bad)])])',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$yield_from_iterator_result_valid(S_bad, n_parent, pyieldfromreceipt_bad, n_child)',
            '~$call_descriptors_valid(S_bad)',
            '$throwable_field(S, n_error, "code") = PINT 71',
            '$throwable_field(S, n_error, "line") = PINT 9',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_child)), ENTRY (KINT 1) (DIRECT (PARRAY n_frame_parent))]',
            '$entry_lookup(S.ARRAYS[n_frame_child].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING $ptascii("reviewAcquiredRowChild15")))',
            '$entry_lookup(S.ARRAYS[n_frame_parent].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING $ptascii("reviewAcquiredRowParent15")))',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("GET|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("N|")]',
            '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_zero = $drive(S, 0)',
            'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_one_budget = $drive_steps(S, 1)',
            'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_one)',
            '$heap_valid($heap_graph(S_one))',
            'S_two_budget = $drive_steps(S_one, 1)',
            '$drive(S, 2) = S_two_budget',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.FRAMES = eps',
            'S_done.CURRENT = eps',
            'S_done.HELD = eps',
            '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("H|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("71"), OUTPUT $ptascii("|"), OUTPUT $ptascii("reviewAcquiredRowChild15"), OUTPUT $ptascii("|"), OUTPUT $ptascii("reviewAcquiredRowParent15"), OUTPUT $ptascii("|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_parent) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_snapshot) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_live) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_new) = 0',
            'n_old <- S_done.DESTRUCTION.CALLED',
            'n_new <- S_done.DESTRUCTION.CALLED',
        ],
    },
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
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
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(independent_inputs={str(p): hashlib.sha256(b).hexdigest()
                                     for p, b in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
