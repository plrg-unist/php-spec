#!/usr/bin/env python3
"""Reach shared leaf snapshots and a child retained after temporary-parent abort."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_generator_delegation_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'two-shared-links-send-the-real-leaf-row-without-outer-cache-owners': {
        'source': SOURCES['generator-call-unpack-generator-delegation-review-two-link-row-cow'],
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 0'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps', 'S.HELD = eps',
            'n_outer = pgeneratorunpack.OBJECT',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_outer)',
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            'pgeneratorunpack.CALL.LINE = 7', '~pgeneratorunpack.NAMED',
            'S.OBJECTS[n_outer] = GENERATOR pgenerator_outer',
            'pgenerator_outer.PHASE = GENERATOR_DELEGATING',
            'pgenerator_outer.VALUE = eps', 'pgenerator_outer.KEY = eps',
            'pgenerator_outer.REFCELL = eps',
            'pgenerator_outer.DELEGATE = (pgeneratorfrom_outer)',
            'pgeneratorfrom_outer.INPUT = (POBJECT n_middle)',
            'pgeneratorfrom_outer.CURRENT = eps',
            'pgeneratorfrom_outer.ACQUISITION = eps',
            'pgeneratorfrom_outer.POSITION = 1',
            '$generator_from_record_valid(S, n_outer, pgenerator_outer)',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.VALUE = eps', 'pgenerator_middle.KEY = eps',
            'pgenerator_middle.REFCELL = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)',
            'pgeneratorfrom_middle.INPUT = (POBJECT n_leaf)',
            'pgeneratorfrom_middle.CURRENT = eps',
            'pgeneratorfrom_middle.ACQUISITION = eps',
            'pgeneratorfrom_middle.POSITION = 1',
            '$generator_from_record_valid(S, n_middle, pgenerator_middle)',
            'S.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf',
            'pgenerator_leaf.PHASE = GENERATOR_PAUSED',
            'pgenerator_leaf.DELEGATE = eps', 'pgenerator_leaf.REFCELL = eps',
            'pgenerator_leaf.VALUE = (PARRAY n_snapshot)',
            'pgenerator_leaf.KEY = (PINT 0)',
            'pgenerator_leaf.FRAME = (pframe_leaf)',
            'pframe_leaf.CONTEXT = (pcallcontext_leaf)',
            'pcallcontext_leaf.NAME = $ptascii("reviewGeneratorChainLeaf11")',
            '$generator_frame_valid(S, pgenerator_leaf, pframe_leaf)',
            'pframe_leaf.LOCALS = (psymboltable_leaf)',
            '$lookup(psymboltable_leaf.ENV, $ptascii("row")) = (n_local)',
            'S.STORE[n_local] = DEFINED (PARRAY n_snapshot)',
            'S.ARRAYS[n_snapshot].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            '$object_name(S, n_child) = $ptascii("ReviewGeneratorChainChild11")',
            '$node_children(S, HOBJECT n_outer) = [HOBJECT n_middle]',
            '$node_children(S, HOBJECT n_middle) = [HOBJECT n_leaf]',
            '$node_children(S, HOBJECT n_leaf) = '
            '$generator_frame_nodes(pgenerator_leaf.FRAME) ++ [HARRAY n_snapshot]',
            '$node_children(S, HCELL n_local) = [HARRAY n_snapshot]',
            '$node_children(S, HARRAY n_snapshot) = [HOBJECT n_child]',
            '$generator_cached_value(S, n_outer, false) = PARRAY n_snapshot',
            '$generator_cached_value(S, n_outer, true) = PINT 0',
            '$generator_unpack_delegate(S, n_outer)',
            '$generator_unpack_chain(S, n_outer, 3)',
            '~$generator_unpack_chain(S, n_outer, 2)',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = '
            '[HOBJECT n_outer, HOBJECT n_outer]',
            '$heap_owners($heap_graph(S), HOBJECT n_outer) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_leaf) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_snapshot) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            'S_missing = $generator_set(S, n_leaf, pgenerator_leaf[.VALUE = eps][.KEY = eps])',
            '~$generator_unpack_delegate(S_missing, n_outer)',
            '~$call_descriptors_valid(S_missing)',
            'S_cycle = $generator_set(S, n_middle, pgenerator_middle[.DELEGATE = '
            '(pgeneratorfrom_middle[.INPUT = (POBJECT n_outer)])])',
            '~$generator_unpack_delegate(S_cycle, n_outer)',
            'pgeneratorunpack.CALL.CALLSITE = (porigin_call)',
            'S_source = $generator_set(S, n_middle, pgenerator_middle[.DELEGATE = '
            '(pgeneratorfrom_middle[.SITE = porigin_call])])',
            '~$generator_unpack_delegate(S_source, n_outer)',
            '~$generator_unpack_valid(S[.ORIGIN = eps], pgeneratorunpack, "ready")',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("L|")]',
            *VALID, *ZERO, *ONE,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorunpack_next = pgeneratorunpack[.COUNT = 1]'
            '[.CALL.SENT = {SLOTS ([NAMED_SENT (KNOWN (PARRAY n_snapshot))]), NAMED eps}]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack_next "next") = '
            '[HOBJECT n_outer, HOBJECT n_outer, HARRAY n_snapshot]',
            '$heap_owners($heap_graph(S_one), HARRAY n_snapshot) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            '$generator_unpack_valid(S_one, pgeneratorunpack_next, "next")', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("N|"), OUTPUT $ptascii("C|"), '
            'OUTPUT $ptascii("I|"), OUTPUT $ptascii("J|"), OUTPUT $ptascii("O|"), '
            'OUTPUT $ptascii("D|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("X|"), '
            'OUTPUT $ptascii("A|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_outer) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_leaf) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_snapshot) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_local) = 0',
            'n_child <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'temporary-parent-key-error-leaves-independent-child-cv-and-real-leaf-cache': {
        'source': SOURCES['generator-call-unpack-generator-delegation-review-retained-child-after-temporary-outer-error'],
        'stage': ('S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.CURRENT = eps '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("M|"))'),
        'checks': [
            'S.FRAMES = eps', 'S.ACTIVEFIBER = eps', 'S.ITERATORS = eps',
            'S.HELD = eps', '$generator_unpack_count(S.TODO) = 0',
            '$lookup(S.ENV, $ptascii("child")) = (n_child_cell)',
            'S.STORE[n_child_cell] = DEFINED (POBJECT n_generator)',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED', '~pgenerator.FIRST',
            'pgenerator.VALUE = (POBJECT n_current)', 'pgenerator.KEY = (PINT 0)',
            'pgenerator.REFCELL = eps', 'pgenerator.DELEGATE = eps',
            'pgenerator.FRAME = (pframe_saved)',
            'pframe_saved.CONTEXT = (pcallcontext)',
            'pcallcontext.NAME = $ptascii("reviewGeneratorRetainedChild11")',
            '$generator_frame_valid(S, pgenerator, pframe_saved)',
            '$object_name(S, n_current) = $ptascii("ReviewGeneratorRetainedCurrent11")',
            '$generator_cached_value(S, n_generator, false) = POBJECT n_current',
            '$generator_cached_value(S, n_generator, true) = PINT 0',
            '$node_children(S, HOBJECT n_generator) = [HOBJECT n_current]',
            '$node_children(S, HCELL n_child_cell) = [HOBJECT n_generator]',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '~(n_current <- S.DESTRUCTION.CALLED)',
            '~$generator_unpack_delegate(S, n_generator)',
            '$lookup(S.ENV, $ptascii("caught")) = (n_error_cell)',
            'S.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
            '$throwable_member(S, n_error)',
            '$throwable_field(S, n_error, "line") = PINT 8',
            '$string_bytes($throwable_field(S, n_error, "message")) = '
            '($ptascii("Cannot use positional argument after named argument during unpacking"))',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("L|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("T|"), OUTPUT $ptascii("8"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("NOFRAME|")]', *VALID, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("M|")]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.FRAMES = S.FRAMES',
            '$heap_owners($heap_graph(S_one), HOBJECT n_generator) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 1', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("M|"), OUTPUT $ptascii("C|"), '
            'OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_generator) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_child_cell) = 0',
            'n_current <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
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
