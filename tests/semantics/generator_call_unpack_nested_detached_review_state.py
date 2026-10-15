#!/usr/bin/env python3
"""Reach detached-chain caches and distinct real-root initialization histories."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_nested_detached_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
BUDGET = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
          'S_zero[.COMPLETION = NORMAL] = S',
          'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
          'S_one = S_one_budget[.COMPLETION = NORMAL]',
          'S_one.EVENTS = S.EVENTS',
          '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
          'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
          '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget']
DONE = ['S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$heap_owners($heap_graph(S_done), HOBJECT n_outer) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0']

CASES = {
    'retained-detached-middle-borrows-no-outer-cache-and-preserves-real-return-tail': {
        'source': SOURCES['generator-call-unpack-nested-detached-review-retained-middle-row-cow-and-real-return-tail'],
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 0'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps', 'S.HELD = eps',
            'n_outer = pgeneratorunpack.OBJECT',
            'pgeneratorunpack.INPUT = VARIABLE ($ptascii("outer")) 13',
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '~pgeneratorunpack.NAMED',
            'S.OBJECTS[n_outer] = GENERATOR pgenerator_outer',
            'pgenerator_outer.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_outer.PENDING_INIT',
            'pgenerator_outer.VALUE = eps', 'pgenerator_outer.REFCELL = eps',
            'pgenerator_outer.DELEGATE = (pgeneratorfrom_outer)',
            'pgeneratorfrom_outer.INPUT = (POBJECT n_middle)',
            'pgeneratorfrom_outer.ACQUISITION = eps',
            'pgeneratorfrom_outer.CURRENT = eps',
            'pgeneratorfrom_outer.POSITION = 1',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.VALUE = eps', 'pgenerator_middle.REFCELL = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)',
            'pgeneratorfrom_middle.INPUT = eps',
            'pgeneratorfrom_middle.ACQUISITION = eps',
            'pgeneratorfrom_middle.POSITION = 1',
            'pgeneratorfrom_middle.CURRENT = (KNOWN (PARRAY n_snapshot))',
            'pgenerator_middle.FRAME = (pframe_middle)',
            'pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 23)) :: ptask_middle*',
            '$generator_from_complete_valid(S, n_middle, pgeneratorfrom_middle.SITE, n_child, PINT 23)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.RETURN = (PINT 23)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$lookup(S.ENV, $ptascii("outer")) = (n_outer_cell)',
            'S.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)',
            '$lookup(S.ENV, $ptascii("middle")) = (n_middle_cell)',
            'S.STORE[n_middle_cell] = DEFINED (POBJECT n_middle)',
            'S.ARRAYS[n_snapshot].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
            '$object_name(S, n_old) = $ptascii("ReviewNestedDetachedFirst16")',
            '$node_children(S, HOBJECT n_outer) = [HOBJECT n_middle]',
            '$node_children(S, HOBJECT n_middle) = $generator_frame_nodes(pgenerator_middle.FRAME) ++ [HARRAY n_snapshot]',
            '$heap_owners($heap_graph(S), HOBJECT n_outer) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_snapshot) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$generator_cached_value(S, n_outer, false) = PARRAY n_snapshot',
            '$generator_cached_value(S, n_outer, true) = PNULL',
            '$generator_unpack_detached(S, n_middle)',
            '$generator_unpack_chain(S, n_outer, 2)',
            '~$generator_unpack_chain(S, n_outer, 1)',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            'pgeneratorunpack.CALL.CALLSITE = (porigin_call)',
            'S_bad = $generator_set(S, n_middle, pgenerator_middle[.FRAME = (pframe_middle[.TODO = (GENERATOR_FROM_COMPLETE n_middle porigin_call n_child (PINT 23)) :: ptask_middle*])])',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$generator_unpack_delegate(S_bad, n_outer)',
            '~$call_descriptors_valid(S_bad)',
            'S_missing = $generator_set(S, n_middle, pgenerator_middle[.DELEGATE = (pgeneratorfrom_middle[.CURRENT = eps])])',
            '~$generator_unpack_delegate(S_missing, n_outer)',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("M|")]',
            *VALID, *BUDGET,
            'S_one.TODO = (THROW_SEARCH n_error) :: (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail*',
            '$throwable_field(S_one, n_error, "line") = PINT 13',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = ($ptascii("Keys must be of type int|string during argument unpacking"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            'S_one.ARRAYS[n_trace].ITEMS = eps',
            'S_one.OBJECTS[n_outer] = S.OBJECTS[n_outer]',
            'S_one.OBJECTS[n_middle] = S.OBJECTS[n_middle]',
            '$heap_owners($heap_graph(S_one), HARRAY n_snapshot) = 1',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), OUTPUT $ptascii("KEY|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("N|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("23"), OUTPUT $ptascii("|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("13"), OUTPUT $ptascii("|"), OUTPUT $ptascii("J|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("29"), OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HARRAY n_snapshot) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 0',
            'n_old <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'directly-initialized-detached-middle-runs-finally-before-cache-and-outer': {
        'source': SOURCES['generator-call-unpack-nested-detached-review-temporary-outer-unowned-middle-close'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_caller* '
                  '-- if pgenrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_middle)] '
                  '-- if $generator_object(S, n_middle)'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'n_outer = pgenclose.OBJECT', 'pgenclose.STAGE = CLOSE_QUEUED',
            'S.OBJECTS[n_outer] = GENERATOR pgenerator_outer',
            'pgenerator_outer.PHASE = GENERATOR_CLOSING',
            '~pgenerator_outer.PENDING_INIT', 'pgenerator_outer.FRAME = eps',
            'pgenerator_outer.DELEGATE = (pgeneratorfrom_outer)',
            'pgeneratorfrom_outer.INPUT = eps',
            'pgeneratorfrom_outer.CURRENT = eps',
            'pgeneratorfrom_outer.ACQUISITION = eps',
            'pgenclose.FRAME = (pframe_outer)',
            'pframe_outer.TODO = (GENERATOR_FROM_NEXT n_outer pgenclose.SITE) :: ptask_outer*',
            '$generator_close_drop_claim(S, pframe_outer.TODO, n_outer, pgenclose.SITE) = ptask_outer*',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)',
            'pgeneratorfrom_middle.INPUT = eps',
            'pgeneratorfrom_middle.ACQUISITION = eps',
            'pgeneratorfrom_middle.CURRENT = (KNOWN (POBJECT n_cache))',
            'pgenerator_middle.FRAME = (pframe_middle)',
            'pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (PINT 23)) :: ptask_middle*',
            '$generator_from_complete_valid(S, n_middle, pgeneratorfrom_middle.SITE, n_child, PINT 23)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$object_name(S, n_cache) = $ptascii("ReviewNestedDetachedCache16")',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            'pgenrelease.PENDING = (n_error)',
            '$throwable_field(S, n_error, "line") = PINT 12',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = eps',
            '$destructor_operation_for(S) = (pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            'pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "ready"',
            'pgeneratorunpack.OBJECT = n_outer',
            'pgeneratorunpack.COUNT = 0', '~pgeneratorunpack.NAMED',
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '$generator_close_enter_valid(S, pgenclose)',
            '$generator_close_destructor_ready(S, pgenrelease)',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("G|")]',
            *VALID, *BUDGET, *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("J|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("KEY|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            'n_cache <- S_done.DESTRUCTION.CALLED',
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
