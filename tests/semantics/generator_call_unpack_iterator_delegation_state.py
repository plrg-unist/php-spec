#!/usr/bin/env python3
"""Reach Iterator-leaf cached sends and ordered temporary key-error cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_iterator_delegation_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}
LEAF = [
    'n_data = pgeneratorunpack.OBJECT',
    'pgeneratorunpack.INPUT = KNOWN (POBJECT n_data)',
    'S.OBJECTS[n_data] = GENERATOR pgenerator',
    'pgenerator.PHASE = GENERATOR_DELEGATING',
    'pgenerator.VALUE = eps',
    'pgenerator.DELEGATE = (pgeneratorfrom)',
    'pgeneratorfrom.INPUT = (POBJECT n_iterator)',
    '$useriter_instance(S, n_iterator)',
    'pgeneratorfrom.ACQUISITION = eps',
    'pgeneratorfrom.POSITION = 1',
    'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
    '$generator_from_record_valid(S, n_data, pgenerator)',
    '$generator_unpack_iterator_delegate(S, n_data)',
    '$generator_unpack_chain(S, n_data, 1)',
    '~$generator_unpack_chain(S, n_data, 0)',
    '$generator_unpack_delegate(S, n_data)',
    '~$generator_unpack_array_delegate(S, n_data)',
    '~$generator_unpack_detached(S, n_data)',
    '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
    '$generator_from_nodes(pgenerator.DELEGATE) = [HOBJECT n_iterator, HOBJECT n_cache]',
    '$generator_cached_value(S, n_data, false) = POBJECT n_cache',
    '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_iterator) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
    '$call_descriptors_valid(S)',
    '$heap_valid($heap_graph(S))',
]
ZERO_ONE = [
    'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
    'S_one = S_one_budget[.COMPLETION = NORMAL]',
]
VALID_ONE = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
TWO = [
    'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
    '$drive(S, 2) = S_two_budget',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
    'S_two = S_two_budget[.COMPLETION = NORMAL]',
    '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
]
DONE = [
    'S_done = $drive(S_two, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_iterator) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
]
CASES = {
    'iterator-ready-named-send-keeps-cache-and-real-borrowed-resumer': {
        'source': SOURCES['generator-iterator-unpack-named-default-snapshot-before-callee'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* -- if pgeneratorunpack.COUNT = 0',
        'checks': [*LEAF,
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '~pgeneratorunpack.NAMED',
            '$string_bytes($generator_cached_value(S, n_data, true)) = ($ptascii("item"))',
            '$object_name(S, n_iterator) = $ptascii("GeneratorIteratorSource13")',
            '$object_name(S, n_cache) = $ptascii("GeneratorIteratorValue13")',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = [HOBJECT n_data, HOBJECT n_data]',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("K|")]',
            'S_missing = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.CURRENT = eps])])',
            '~$generator_unpack_iterator_delegate(S_missing, n_data)',
            '~$generator_unpack_valid(S_missing, pgeneratorunpack, "ready")',
            'S_position = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.POSITION = 0])])',
            '~$generator_unpack_iterator_delegate(S_position, n_data)',
            'pgeneratorunpack.CALL.CALLSITE = (porigin_call)',
            'S_source = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.SITE = porigin_call])])',
            '~$generator_unpack_iterator_delegate(S_source, n_data)',
            *ZERO_ONE,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorunpack_next.COUNT = 1', 'pgeneratorunpack_next.NAMED',
            'pgeneratorunpack_next.OBJECT = n_data',
            'pgeneratorunpack_next.INPUT = pgeneratorunpack.INPUT',
            'pgeneratorunpack_next.CALL.SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN (POBJECT n_cache))]',
            'pgeneratorunpack_next.CALL.SENT.NAMED = eps',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_iterator) = 1',
            *VALID_ONE, *TWO,
            'S_two.FRAMES = pframe_caller :: S.FRAMES',
            'pframe_caller.CONTEXT = S.CURRENT',
            'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop) :: (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorop.OBJECT = n_data', 'pgeneratorop.NAME = "next"',
            'pgeneratorop.STARTPACK', 'pgeneratorop.BORROWED',
            '~pgeneratorop.ADVANCE',
            '$task_nodes(GENERATOR_RESUME pgeneratorop) = eps',
            '$generator_operation_site(S_two, pgeneratorop)',
            '$generator_resumption_valid(S_two, pgeneratorop)',
            '$generator_operation_trace(S_two, pgeneratorop) = eps',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("N|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("I|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("17"), OUTPUT $ptascii("|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("U|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("23"), OUTPUT $ptascii("|E")]',
        ],
    },
    'iterator-temporary-key-error-retires-data-cache-before-sent': {
        'source': SOURCES['generator-iterator-unpack-temporary-key-error-releases-cache-before-sent'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* -- if pgeneratorunpack.COUNT = 1',
        'checks': [*LEAF,
            'pgeneratorunpack.NAMED',
            'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_sent))]',
            'pgeneratorunpack.CALL.SENT.NAMED = eps',
            'n_cache =/= n_sent',
            '$generator_cached_value(S, n_data, true) = PINT 0',
            '$heap_owners($heap_graph(S), HOBJECT n_sent) = 1',
            '$destructor_operational(S)',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("N|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("K|")]',
            *ZERO_ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail*',
            '$throwable_field(S_one, n_error, "line") = PINT 15',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = ($ptascii("Cannot use positional argument after named argument during unpacking"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            'S_one.ARRAYS[n_trace].ITEMS = eps',
            'S_one.EVENTS = S.EVENTS',
            *VALID_ONE, *TWO,
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_exit*',
            'pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "ready"',
            'pdestructionoperation.PENDING = (n_error)',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_sent)]',
            '$eager_operation_source_valid(S_two, pdestructionoperation)',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("I|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("B"), OUTPUT $ptascii("|"), OUTPUT $ptascii("A"), OUTPUT $ptascii("|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("15"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_sent) = 0',
            '$eager_operation_source_valid(S_done, pdestructionoperation)',
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
