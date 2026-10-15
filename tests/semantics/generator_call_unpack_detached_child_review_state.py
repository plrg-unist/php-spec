#!/usr/bin/env python3
"""Reach detached reference caches and throwing cache retirement after finally."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_detached_child_review_cases.json')
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
    'detached-reference-cache-keeps-mutated-cell-after-child-storage-retires': {
        'source': SOURCES['generator-call-unpack-detached-child-review-reference-cache-after-cell-mutation'],
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 0'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps', 'S.HELD = eps',
            'n_parent = pgeneratorunpack.OBJECT',
            'pgeneratorunpack.INPUT = VARIABLE ptbytes z',
            'ptbytes = $ptascii("parent")',
            '$lookup(S.ENV, ptbytes) = (n_parent_cell)',
            'S.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
            'pgeneratorunpack.CALL.LINE = 11',
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '~pgeneratorunpack.NAMED',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_DELEGATING',
            'pgenerator_parent.VALUE = eps', 'pgenerator_parent.KEY = eps',
            'pgenerator_parent.REFCELL = eps', 'pgenerator_parent.BORROWED = eps',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.POSITION = 1',
            'pgeneratorfrom.CURRENT = (REFERENCE n_ref)',
            'pgenerator_parent.FRAME = (pframe_saved)',
            'pframe_saved.TODO = (GENERATOR_FROM_COMPLETE n_parent pgeneratorfrom.SITE '
            'n_child (PINT 23)) :: ptask_saved*',
            'pframe_saved.CONTEXT = (pcallcontext_saved)',
            'pcallcontext_saved.NAME = $ptascii("reviewDetachedReferenceParent12")',
            '$generator_frame_valid(S, pgenerator_parent, pframe_saved)',
            '$generator_from_record_valid(S, n_parent, pgenerator_parent)',
            '$generator_from_complete_valid(S, n_parent, pgeneratorfrom.SITE, n_child, PINT 23)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.FRAME = eps', 'pgenerator_child.RETURN = (PINT 23)',
            '~(HOBJECT n_child <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            'n_ref <- S.REFCELLS',
            'S.STORE[n_ref] = DEFINED (POBJECT n_cache)',
            '$object_name(S, n_cache) = $ptascii("ReviewDetachedReferenceCurrent12")',
            '$generator_from_nodes(pgenerator_parent.DELEGATE) = [HCELL n_ref]',
            '$node_children(S, HCELL n_ref) = [HOBJECT n_cache]',
            '$heap_owners($heap_graph(S), HOBJECT n_parent) = 2',
            '$heap_owners($heap_graph(S), HCELL n_ref) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '~(n_cache <- S.DESTRUCTION.CALLED)',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = [HOBJECT n_parent]',
            '$generator_cache_present(S, n_parent)',
            '$generator_cached_value(S, n_parent, false) = POBJECT n_cache',
            '$generator_cached_value(S, n_parent, true) = PNULL',
            '$generator_unpack_detached(S, n_parent)',
            '$generator_unpack_delegate(S, n_parent)',
            '~$generator_unpack_chain(S, n_parent, $(|S.OBJECTS| + 1))',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            'S_metadata = $generator_set(S, n_child, '
            'pgenerator_child[.VALUE = eps][.REFCELL = eps])',
            '$heap_graph(S_metadata) = $heap_graph(S)',
            '$generator_from_complete_valid(S_metadata, n_parent, pgeneratorfrom.SITE, '
            'n_child, PINT 23)',
            '$generator_unpack_detached(S_metadata, n_parent)',
            '$call_descriptors_valid(S_metadata)',
            'S_next = $generator_set(S, n_parent, pgenerator_parent[.FRAME = '
            '(pframe_saved[.TODO = (GENERATOR_FROM_NEXT n_parent pgeneratorfrom.SITE) '
            ':: ptask_saved*])])',
            '~$generator_unpack_detached(S_next, n_parent)',
            'S_return = $generator_set(S, n_child, pgenerator_child[.RETURN = (PINT 17)])',
            '~$generator_unpack_detached(S_return, n_parent)',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("L|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("C|"), '
            'OUTPUT $ptascii("V|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("K|"), '
            'OUTPUT $ptascii("NULL|"), OUTPUT $ptascii("X|")]',
            *VALID, *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail*',
            '$throwable_field(S_one, n_error, "line") = PINT 11',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Keys must be of type int|string during argument unpacking"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            'S_one.ARRAYS[n_trace].ITEMS = eps',
            'S_one.OBJECTS[n_parent] = S.OBJECTS[n_parent]',
            'S_one.STORE[n_ref] = S.STORE[n_ref]',
            '$heap_owners($heap_graph(S_one), HCELL n_ref) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 1',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)',
            '$drive(S, 2) = S_two_budget',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), OUTPUT $ptascii("11"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("M|"), '
            'OUTPUT $ptascii("F|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_parent) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_ref) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            'n_cache <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'cached-destructor-throw-crosses-real-generator-storage-pin-after-finally': {
        'source': SOURCES['generator-call-unpack-detached-child-review-cached-destructor-throw-after-finally'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.RECEIVER = (n_cache) '
                  '-- if $object_name(S, n_cache) = $ptascii("ReviewDetachedCacheThrow12")'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.ITERATORS = eps',
            '$consumer_destructor_target(S, pcallcontext.TARGET)',
            'pcallcontext.ARGC = 0', 'pcallcontext.EXTRA = eps',
            '$destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)',
            'pdestructorcall.OBJECT = n_cache', 'pdestructorcall.USER',
            '$destructor_context_valid(S, pcallcontext)',
            '$destructor_call_live(S, pdestructorcall)',
            '$destructor_operational(S)',
            '[pgenstorage] = $generator_storage_tasks(S.TODO) ++ '
            '$generator_storage_frames(S.FRAMES)',
            'n_parent = pgenstorage.OBJECT',
            'pgenstorage.NEXT = 2', 'pgenstorage.USER',
            'pgenstorage.CALLER = eps', 'pgenstorage.ORIGIN = (porigin_unset)',
            '$generator_storage_for(S, n_parent) = (pgenstorage)',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_CLOSED',
            'pgenerator_parent.FRAME = eps', 'pgenerator_parent.BORROWED = eps',
            'pgenerator_parent.VALUE = eps', 'pgenerator_parent.KEY = eps',
            'pgenerator_parent.REFCELL = eps', 'pgenerator_parent.RETURN = eps',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            '$generator_storage_basic(S, pgenstorage)',
            '$node_children(S, HOBJECT n_parent) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_parent) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            'n_parent <- S.DESTRUCTION.CALLED', 'n_cache <- S.DESTRUCTION.CALLED',
            'S.DESTRUCTION.HANDLES[n_parent] = pgenstorage.HANDLE',
            '~(pgenstorage.HANDLE <- S.DESTRUCTION.FREE)',
            '~$generator_storage_basic(S, pgenstorage[.NEXT = 5])',
            '~$generator_storage_basic(S, pgenstorage[.HANDLE = 0])',
            '$generator_unpack_count(S.TODO) = 0',
            '$throwable_field(S, n_error, "code") = PINT 51',
            '$throwable_field(S, n_error, "line") = PINT 2',
            '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("cache"))',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            '$entry_lookup(S.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_frame))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("__destruct")))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("class")) = '
            '(DIRECT (PSTRING $ptascii("ReviewDetachedCacheThrow12")))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("args")) = '
            '(DIRECT (PARRAY n_args))',
            'S.ARRAYS[n_args].ITEMS = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("L|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("K|"), '
            'OUTPUT $ptascii("NULL|"), OUTPUT $ptascii("X|"), OUTPUT $ptascii("T|"), '
            'OUTPUT $ptascii("9"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), '
            'OUTPUT $ptascii("M|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("A|")]',
            *VALID, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS',
            '$generator_storage_for(S_one, n_parent) = (pgenstorage)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_parent) = 1', *POST,
            'S_two_budget = $drive_steps(S_one, 1)',
            '$drive(S, 2) = S_two_budget',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("U|"), OUTPUT $ptascii("51"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_parent) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
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
