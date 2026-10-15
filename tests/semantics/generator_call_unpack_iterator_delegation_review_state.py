#!/usr/bin/env python3
"""Reach Iterator-leaf reference SEND and COW row ownership during next throw."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_iterator_delegation_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
DONE = ['S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']

CASES = {
    'iterator-key-mutated-reference-cache-sends-an-independent-value-snapshot': {
        'source': SOURCES['generator-call-unpack-iterator-delegation-review-reference-key-mutation-and-send-snapshot'],
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 0'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps', 'S.HELD = eps',
            'n_generator = pgeneratorunpack.OBJECT',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_generator)',
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            'pgeneratorunpack.CALL.LINE = 16', '~pgeneratorunpack.NAMED',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_DELEGATING',
            'pgenerator.VALUE = eps', 'pgenerator.REFCELL = eps',
            'pgenerator.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_iterator)',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.POSITION = 1',
            'pgeneratorfrom.CURRENT = (REFERENCE n_raw)',
            '$useriter_instance(S, n_iterator)',
            '$object_name(S, n_iterator) = $ptascii("ReviewGeneratorIteratorReference13")',
            '$objectprops_record_at(S.OBJECTPROPS, n_iterator) = (pobjectprops)',
            '$property_slot_at(pobjectprops.SLOTS, $ptascii("item")) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (ALIAS n_raw)',
            'n_raw <- S.REFCELLS', 'S.STORE[n_raw] = DEFINED (POBJECT n_value)',
            '$object_name(S, n_value) = $ptascii("ReviewGeneratorIteratorSecond13")',
            '$generator_from_record_valid(S, n_generator, pgenerator)',
            '$generator_from_nodes(pgenerator.DELEGATE) = [HOBJECT n_iterator, HCELL n_raw]',
            '$node_children(S, HOBJECT n_iterator) = [HCELL n_raw]',
            '$node_children(S, HCELL n_raw) = [HOBJECT n_value]',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_iterator) = 1',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_value) = 1',
            '~(n_value <- S.DESTRUCTION.CALLED)',
            '$generator_cached_value(S, n_generator, false) = POBJECT n_value',
            '$string_bytes($generator_cached_value(S, n_generator, true)) = ($ptascii("item"))',
            '$generator_unpack_chain(S, n_generator, 1)',
            '$generator_unpack_delegate(S, n_generator)',
            '~$generator_unpack_array_delegate(S, n_generator)',
            '~$generator_unpack_detached(S, n_generator)',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = '
            '[HOBJECT n_generator, HOBJECT n_generator]',
            'S_missing = $generator_set(S, n_generator, '
            'pgenerator[.DELEGATE = (pgeneratorfrom[.CURRENT = eps])])',
            '~$generator_unpack_delegate(S_missing, n_generator)',
            'S_position = $generator_set(S, n_generator, '
            'pgenerator[.DELEGATE = (pgeneratorfrom[.POSITION = 0])])',
            '~$generator_unpack_delegate(S_position, n_generator)',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), '
            'OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("C|"), '
            'OUTPUT $ptascii("K|"), OUTPUT $ptascii("A|")]',
            *VALID, *ZERO, *ONE,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorunpack_next = pgeneratorunpack[.COUNT = 1][.NAMED = true]'
            '[.CALL.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_value))]), NAMED eps}]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack_next "next") = '
            '[HOBJECT n_generator, HOBJECT n_generator, HOBJECT n_value]',
            '$heap_owners($heap_graph(S_one), HCELL n_raw) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_value) = 2',
            '$generator_unpack_valid(S_one, pgeneratorunpack_next, "next")', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("N|"), OUTPUT $ptascii("V|"), '
            'OUTPUT $ptascii("I|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("F|"), '
            'OUTPUT $ptascii("D|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("B|"), '
            'OUTPUT $ptascii("X|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_generator) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_iterator) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_value) = 0',
            'n_value <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'iterator-next-throw-keeps-cow-snapshot-and-real-callback-owners': {
        'source': SOURCES['generator-call-unpack-iterator-delegation-review-row-cow-and-next-throw-owners'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.RECEIVER = (n_iterator) '
                  '-- if $object_name(S, n_iterator) = $ptascii("ReviewGeneratorIteratorRow13")'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.ITERATORS = eps',
            '$trace_context_function(S, pcallcontext) = $ptascii("next")',
            'pcallcontext.ARGC = 0', 'pcallcontext.EXTRA = eps',
            'S.FRAMES = [pframe_producer, pframe_caller]',
            '$generator_from_callback_frame(S, pcallcontext, pframe_producer)',
            'pframe_producer.TODO = (GENERATOR_FROM_CALLBACK n_generator porigin "next") '
            ':: ptask_producer*',
            'pframe_producer.CONTEXT = (pcallcontext_producer)',
            'pcallcontext_producer.NAME = $ptascii("reviewGeneratorIteratorRow13")',
            'pframe_caller.CONTEXT = eps',
            'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop) :: '
            '(GENERATOR_UNPACK pgeneratorunpack "next") :: ptask_caller*',
            'pgeneratorop.OBJECT = n_generator', 'pgeneratorop.STARTPACK',
            'pgeneratorop.BORROWED', 'pgeneratorop.NAME = "next"',
            '$task_nodes(GENERATOR_RESUME pgeneratorop) = eps',
            '$generator_operation_trace(S, pgeneratorop) = eps',
            'pgeneratorunpack.OBJECT = n_generator',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_generator)',
            'pgeneratorunpack.COUNT = 1', '~pgeneratorunpack.NAMED',
            'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PARRAY n_snapshot))]',
            'pgeneratorunpack.CALL.SENT.NAMED = eps',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_RUNNING', 'pgenerator.FRAME = eps',
            'pgenerator.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.SITE = porigin',
            'pgeneratorfrom.INPUT = (POBJECT n_iterator)',
            'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (PARRAY n_snapshot))',
            '$objectprops_record_at(S.OBJECTPROPS, n_iterator) = (pobjectprops)',
            '$property_slot_at(pobjectprops.SLOTS, $ptascii("row")) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (DIRECT (PARRAY n_live))',
            'n_snapshot =/= n_live',
            'S.ARRAYS[n_snapshot].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
            'S.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new))]',
            '$object_name(S, n_old) = $ptascii("ReviewGeneratorIteratorRowFirst13")',
            '$object_name(S, n_new) = $ptascii("ReviewGeneratorIteratorRowSecond13")',
            '$node_children(S, HOBJECT n_iterator) = [HARRAY n_live]',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_iterator) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_snapshot) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_live) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_new) = 1',
            '~(n_old <- S.DESTRUCTION.CALLED)', '~(n_new <- S.DESTRUCTION.CALLED)',
            '$throwable_field(S, n_error, "code") = PINT 71',
            '$throwable_field(S, n_error, "line") = PINT 11',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_method)), '
            'ENTRY (KINT 1) (DIRECT (PARRAY n_frame_producer))]',
            '$entry_lookup(S.ARRAYS[n_frame_method].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("next")))',
            '$entry_lookup(S.ARRAYS[n_frame_producer].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("reviewGeneratorIteratorRow13")))',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), '
            'OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("C|"), '
            'OUTPUT $ptascii("K|"), OUTPUT $ptascii("N|")]',
            *VALID, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("I|"), OUTPUT $ptascii("B|"), '
            'OUTPUT $ptascii("F|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("T|"), '
            'OUTPUT $ptascii("71"), OUTPUT $ptascii("|"), OUTPUT $ptascii("next"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("reviewGeneratorIteratorRow13"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_generator) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_iterator) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_snapshot) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_live) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_new) = 0',
            'n_old <- S_done.DESTRUCTION.CALLED', 'n_new <- S_done.DESTRUCTION.CALLED',
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
