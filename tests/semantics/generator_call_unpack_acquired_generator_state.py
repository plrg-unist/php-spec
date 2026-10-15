#!/usr/bin/env python3
"""Reach acquired Generator copies, retained method receivers and queued close."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_acquired_generator_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
BUDGET = [
    'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
    'S_one = S_one_budget[.COMPLETION = NORMAL]',
    '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    'S_one.EVENTS = S.EVENTS',
    'S_two_budget = $drive_steps(S_one, 1)',
    '$drive(S, 2) = S_two_budget',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
]
DONE = [
    'S_done = $drive(S_one, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT n_parent) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
]
CASES = {
    'acquired-method-generator-send-keeps-distinct-cache-and-owned-receiver': {
        'source': SOURCES['generator-acquired-generator-unpack-method-keeps-receiver-and-discards-owning-return'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* -- if pgeneratorunpack.COUNT = 0',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'n_parent = pgeneratorunpack.OBJECT',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_parent)',
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '~pgeneratorunpack.NAMED',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_DELEGATING',
            'pgenerator_parent.VALUE = eps',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            'pgeneratorfrom.POSITION = 1',
            'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
            'pgeneratorfrom.SITE = pyieldfromreceipt.SITE',
            'pyieldfromreceipt.FUNCTION = pgenerator_parent.FUNCTION',
            'pyieldfromreceipt.LINE = 14',
            '$yield_from_receipt_valid(S, pyieldfromreceipt)',
            '~$generator_from_shared(S, pgenerator_parent.DELEGATE)',
            '$generator_from_record_valid(S, n_parent, pgenerator_parent)',
            '$generator_unpack_acquired_generator_delegate(S, n_parent)',
            '$generator_unpack_chain(S, n_parent, 1)',
            '~$generator_unpack_chain(S, n_parent, 0)',
            '$generator_unpack_delegate(S, n_parent)',
            '~$generator_unpack_iterator_delegate(S, n_parent)',
            '~$generator_unpack_array_delegate(S, n_parent)',
            '~$generator_unpack_detached(S, n_parent)',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            '$generator_from_nodes(pgenerator_parent.DELEGATE) = [HOBJECT n_child, HOBJECT n_cache]',
            '$generator_cached_value(S, n_parent, false) = POBJECT n_cache',
            '$string_bytes($generator_cached_value(S, n_parent, true)) = ($ptascii("item"))',
            '$object_name(S, n_cache) = $ptascii("AcquiredMethodA15")',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            'pgenerator_child.VALUE = (POBJECT n_cache)',
            'pgenerator_child.REFCELL = eps',
            'pgenerator_child.DELEGATE = eps',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.CONTEXT = (pcallcontext_child)',
            'n_aggregate = pyieldfromreceipt.AGGREGATE',
            'pcallcontext_child.RECEIVER = (n_aggregate)',
            'pcallcontext_child.TARGET = YIELD_FROM_AGGREGATE_GENERATOR_TARGET n_aggregate porigin_get n_parent pyieldfromreceipt.SITE 14',
            '$yield_from_aggregate_generator_context(S, pcallcontext_child)',
            '$object_name(S, n_aggregate) = $ptascii("AcquiredMethodAggregate15")',
            '$heap_count(HOBJECT n_aggregate, $node_children(S, HOBJECT n_child)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_aggregate) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_parent) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = [HOBJECT n_parent, HOBJECT n_parent]',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("GET|")]',
            'S_missing = $generator_set(S, n_parent, pgenerator_parent[.DELEGATE = (pgeneratorfrom[.CURRENT = eps])])',
            '~$generator_unpack_acquired_generator_delegate(S_missing, n_parent)',
            '~$generator_unpack_valid(S_missing, pgeneratorunpack, "ready")',
            'S_position = $generator_set(S, n_parent, pgenerator_parent[.DELEGATE = (pgeneratorfrom[.POSITION = 0])])',
            '~$generator_unpack_acquired_generator_delegate(S_position, n_parent)',
            'S_mode = $generator_set(S, n_parent, pgenerator_parent[.DELEGATE = (pgeneratorfrom[.ACQUISITION = eps])])',
            '$heap_graph(S_mode) = $heap_graph(S)',
            '~$generator_unpack_delegate(S_mode, n_parent)',
            'S_receipt = $generator_set(S, n_parent, pgenerator_parent[.DELEGATE = (pgeneratorfrom[.ACQUISITION = (pyieldfromreceipt[.LINE = $(pyieldfromreceipt.LINE + 1)])])])',
            '$heap_graph(S_receipt) = $heap_graph(S)',
            '~$generator_unpack_acquired_generator_delegate(S_receipt, n_parent)',
            '~$call_descriptors_valid(S_receipt)',
            'pgeneratorunpack.CALL.CALLSITE = (porigin_call)',
            'S_source = $generator_set(S, n_parent, pgenerator_parent[.DELEGATE = (pgeneratorfrom[.SITE = porigin_call])])',
            '~$generator_unpack_acquired_generator_delegate(S_source, n_parent)',
            '~$generator_unpack_valid(S[.ORIGIN = eps], pgeneratorunpack, "ready")',
            *VALID, *BUDGET,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorunpack_next.COUNT = 1', 'pgeneratorunpack_next.NAMED',
            'pgeneratorunpack_next.OBJECT = n_parent',
            'pgeneratorunpack_next.INPUT = pgeneratorunpack.INPUT',
            'pgeneratorunpack_next.CALL.SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN (POBJECT n_cache))]',
            'pgeneratorunpack_next.CALL.SENT.NAMED = eps',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_aggregate) = 1',
            *DONE,
            '$heap_owners($heap_graph(S_done), HOBJECT n_aggregate) = 0',
            'n_aggregate <- S_done.DESTRUCTION.CALLED',
            'n_cache <- S_done.DESTRUCTION.CALLED',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("N|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("AFTER|"), OUTPUT $ptascii("NULL|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("17"), OUTPUT $ptascii("|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("X|"), OUTPUT $ptascii("E")]',
        ],
    },
    'acquired-generator-queued-close-releases-child-before-parent-and-copied-cache': {
        'source': SOURCES['generator-acquired-generator-unpack-temporary-key-error-orders-child-and-cache'],
        'stage': 'S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_caller* -- if pgenrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)] -- if $generator_object(S, n_child)',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'pgenclose.STAGE = CLOSE_QUEUED',
            'n_parent = pgenclose.OBJECT',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_CLOSING',
            'pgenerator_parent.FRAME = eps',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
            'pyieldfromreceipt.SITE = pgenclose.SITE',
            'pyieldfromreceipt.FUNCTION = pgenerator_parent.FUNCTION',
            '$yield_from_receipt_valid(S, pyieldfromreceipt)',
            'pgenclose.FRAME = (pframe)',
            'pframe.TODO = (YIELD_FROM_ITERATOR_NEXT n_parent pyieldfromreceipt) :: ptask_parent*',
            '$generator_close_drop_claim(S, pframe.TODO, n_parent, pgenclose.SITE) = ptask_parent*',
            'pyieldfromreceipt_bad = pyieldfromreceipt[.LINE = $(pyieldfromreceipt.LINE + 1)]',
            'pframe_bad = pframe[.TODO = (YIELD_FROM_ITERATOR_NEXT n_parent pyieldfromreceipt_bad) :: ptask_parent*]',
            '$generator_close_drop_claim(S, pframe_bad.TODO, n_parent, pgenclose.SITE) = pframe_bad.TODO',
            '~$generator_close_enter_valid(S, pgenclose[.FRAME = (pframe_bad)])',
            'pgenrelease.PENDING = (n_error)',
            '$throwable_field(S, n_error, "line") = PINT 16',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = eps',
            '$destructor_operation_for(S) = (pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            'pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "ready"',
            'pgeneratorunpack.COUNT = 1', 'pgeneratorunpack.NAMED',
            'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN (POBJECT n_sent))]',
            'pgeneratorunpack.CALL.SENT.NAMED = eps',
            'n_sent =/= n_cache',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            'pgenerator_child.VALUE = (POBJECT n_cache)',
            '$object_name(S, n_cache) = $ptascii("AcquiredKeyB15")',
            '$object_name(S, n_sent) = $ptascii("AcquiredKeyA15")',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_sent) = 1',
            '$generator_close_enter_valid(S, pgenclose)',
            '$generator_close_destructor_ready(S, pgenrelease)',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("GET|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("C|")]',
            *VALID, *BUDGET, *DONE,
            '$heap_owners($heap_graph(S_done), HOBJECT n_sent) = 0',
            'n_cache <- S_done.DESTRUCTION.CALLED',
            'n_sent <- S_done.DESTRUCTION.CALLED',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("L|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("16"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("E")]',
        ],
    },
}


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
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs=before, author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
