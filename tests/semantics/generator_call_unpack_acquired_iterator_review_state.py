#!/usr/bin/env python3
"""Reach acquired-Iterator receipt, COW and independent data roots during next throw."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_acquired_iterator_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}

CASES = {
    'acquired-iterator-next-throw-keeps-documentary-receipt-and-independent-data-owner': {
        'source': SOURCES['generator-call-unpack-acquired-iterator-review-next-throw-retains-independent-iterator-and-cow-row'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.RECEIVER = (n_iterator) '
                  '-- if $object_name(S, n_iterator) = $ptascii("ReviewAcquiredRowIterator14")'),
        'checks': [
            'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps',
            '$trace_context_function(S, pcallcontext) = $ptascii("next")',
            'pcallcontext.ARGC = 0',
            'pcallcontext.EXTRA = eps',
            'S.FRAMES = [pframe_producer, pframe_caller]',
            '$generator_from_callback_frame(S, pcallcontext, pframe_producer)',
            'pframe_producer.TODO = (GENERATOR_FROM_CALLBACK n_generator porigin "next") :: ptask_producer*',
            'pframe_producer.CONTEXT = (pcallcontext_producer)',
            'pcallcontext_producer.NAME = $ptascii("reviewAcquiredRowGenerator14")',
            'pframe_caller.CONTEXT = eps',
            'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop) :: (GENERATOR_UNPACK pgeneratorunpack "next") :: ptask_caller*',
            'pgeneratorop.OBJECT = n_generator',
            'pgeneratorop.STARTPACK',
            'pgeneratorop.BORROWED',
            'pgeneratorop.NAME = "next"',
            '$task_nodes(GENERATOR_RESUME pgeneratorop) = eps',
            '$generator_operation_trace(S, pgeneratorop) = eps',
            'pgeneratorunpack.OBJECT = n_generator',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_generator)',
            'pgeneratorunpack.COUNT = 1',
            '~pgeneratorunpack.NAMED',
            'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PARRAY n_snapshot))]',
            'pgeneratorunpack.CALL.SENT.NAMED = eps',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_RUNNING',
            'pgenerator.FRAME = eps',
            'pgenerator.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.SITE = porigin',
            'pgeneratorfrom.INPUT = (POBJECT n_iterator)',
            'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
            '$yield_from_receipt_valid(S, pyieldfromreceipt)',
            'pyieldfromreceipt.SITE = porigin',
            'pyieldfromreceipt.FUNCTION = pcallcontext_producer.FUNCTION',
            'pyieldfromreceipt.LINE = 18',
            'n_aggregate = pyieldfromreceipt.AGGREGATE',
            '$object_name(S, n_aggregate) = $ptascii("ReviewAcquiredRowAggregate14")',
            '~((HOBJECT n_aggregate) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_aggregate) = 0',
            'n_aggregate <- S.DESTRUCTION.CALLED',
            '$generator_from_mode_valid(S, pgeneratorfrom)',
            '$task_nodes(YIELD_FROM_ITERATOR_NEXT n_generator pyieldfromreceipt) = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("iterator")) = (n_alias)',
            'S.STORE[n_alias] = DEFINED (POBJECT n_iterator)',
            '(HCELL n_alias) <- S.ALLOCATIONS',
            'pgeneratorfrom.CURRENT = (KNOWN (PARRAY n_snapshot))',
            '$objectprops_record_at(S.OBJECTPROPS, n_iterator) = (pobjectprops)',
            '$property_slot_at(pobjectprops.SLOTS, $ptascii("row")) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (DIRECT (PARRAY n_live))',
            'n_snapshot =/= n_live',
            'S.ARRAYS[n_snapshot].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
            'S.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new))]',
            '$object_name(S, n_old) = $ptascii("ReviewAcquiredRowFirst14")',
            '$object_name(S, n_new) = $ptascii("ReviewAcquiredRowSecond14")',
            '$node_children(S, HOBJECT n_iterator) = [HARRAY n_live]',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_iterator) = 3',
            '$heap_owners($heap_graph(S), HARRAY n_snapshot) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_live) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_new) = 1',
            '~(n_old <- S.DESTRUCTION.CALLED)',
            '~(n_new <- S.DESTRUCTION.CALLED)',
            '$throwable_field(S, n_error, "code") = PINT 71',
            '$throwable_field(S, n_error, "line") = PINT 11',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_method)), ENTRY (KINT 1) (DIRECT (PARRAY n_frame_producer))]',
            '$entry_lookup(S.ARRAYS[n_frame_method].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING $ptascii("next")))',
            '$entry_lookup(S.ARRAYS[n_frame_producer].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING $ptascii("reviewAcquiredRowGenerator14")))',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("GET|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("N|")]',
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
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("71"), OUTPUT $ptascii("|"), OUTPUT $ptascii("next"), OUTPUT $ptascii("|"), OUTPUT $ptascii("reviewAcquiredRowGenerator14"), OUTPUT $ptascii("|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("I|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_generator) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_iterator) = 0',
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
