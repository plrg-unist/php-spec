#!/usr/bin/env python3
"""Reach a borrowed Generator resume snapshot and retained-CV unpack failure."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'saved-generator-resume-borrows-data-and-keeps-sent-array-snapshot': {
        'source': SOURCES['generator-call-unpack-review-array-snapshot-before-resume-cow'],
        'stage': ('S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("reviewGeneratorValues09") '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("N|"))'),
        'checks': [
            'pcallcontext.ARGC = 0', 'pcallcontext.EXTRA = eps',
            'S.ACTIVEFIBER = eps', 'S.ITERATORS = eps',
            'S.FRAMES = [pframe_caller]', 'pframe_caller.CONTEXT = eps',
            'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop) :: '
            '(GENERATOR_UNPACK pgeneratorunpack "next") :: ptask_caller*',
            'pgeneratorop.OBJECT = pgeneratorunpack.OBJECT',
            'n_generator = pgeneratorunpack.OBJECT',
            'pgeneratorop.NAME = "next"', 'pgeneratorop.STARTPACK',
            'pgeneratorop.BORROWED', '~pgeneratorop.ADVANCE',
            'pgeneratorop.LOOP = eps', 'pgeneratorop.ARGUMENTS = eps',
            'pgeneratorop.LINE = 5', 'pframe_caller.ORIGIN = (pgeneratorop.SITE)',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_generator)',
            'pgeneratorunpack.COUNT = 1', '~pgeneratorunpack.NAMED',
            'pgeneratorunpack.CALL.INDEX = 0', 'pgeneratorunpack.CALL.ARGUMENTS = eps',
            'pgeneratorunpack.CALL.LINE = 5',
            'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PARRAY n_snapshot))]',
            'pgeneratorunpack.CALL.SENT.NAMED = eps',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_RUNNING', 'pgenerator.FRAME = eps',
            'pgenerator.FUNCTION = pcallcontext.FUNCTION', '~pgenerator.FIRST',
            'pgenerator.VALUE = (PARRAY n_snapshot)', 'pgenerator.KEY = (PINT 0)',
            'pgenerator.REFCELL = eps', 'pgenerator.DELEGATE = eps',
            '$lookup(S.ENV, $ptascii("items")) = (n_local)',
            'S.STORE[n_local] = DEFINED (PARRAY n_snapshot)',
            'S.ARRAYS[n_snapshot].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            '$object_name(S, n_child) = $ptascii("ReviewGeneratorChild09")',
            '$node_children(S, HOBJECT n_generator) = [HARRAY n_snapshot]',
            '$node_children(S, HCELL n_local) = [HARRAY n_snapshot]',
            '$node_children(S, HARRAY n_snapshot) = [HOBJECT n_child]',
            '$task_nodes(GENERATOR_RESUME pgeneratorop) = eps',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "next") = '
            '[HOBJECT n_generator, HOBJECT n_generator, HARRAY n_snapshot]',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_snapshot) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '~(n_child <- S.DESTRUCTION.CALLED)',
            'S_scope = $constant_frame_scope(S, pframe_caller, eps)',
            '$generator_unpack_header(S_scope, pgeneratorop, pgeneratorunpack, "next")',
            '$generator_unpack_valid(S_scope, pgeneratorunpack, "next")',
            '$generator_unpack_operation_valid(S, pgeneratorop)',
            '$generator_resumption_valid(S, pgeneratorop)',
            '$generator_operation_trace(S, pgeneratorop) = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION,
            'pgeneratorop_bad = pgeneratorop[.LINE = $(pgeneratorop.LINE + 1)]',
            'pframe_bad = pframe_caller[.TODO = (GENERATOR_RESUME pgeneratorop_bad) :: '
            '(GENERATOR_UNPACK pgeneratorunpack "next") :: ptask_caller*]',
            'S_bad = S[.FRAMES = [pframe_bad]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$generator_unpack_operation_valid(S_bad, pgeneratorop_bad)',
            '~$call_descriptors_valid(S_bad)',
            '~$generator_unpack_valid(S_scope, pgeneratorunpack[.COUNT = 99], "next")',
            '~$generator_unpack_header(S_scope, pgeneratorop[.BORROWED = false], '
            'pgeneratorunpack, "next")', *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("N|")]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.FRAMES = S.FRAMES', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("N|"), OUTPUT $ptascii("F|"), '
            'OUTPUT $ptascii("D|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("M|"), OUTPUT $ptascii("17"), OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_generator) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_snapshot) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_local) = 0',
            'n_child <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'caught-key-order-error-retires-sent-value-but-keeps-cv-generator-cache': {
        'source': SOURCES['generator-call-unpack-review-cv-bad-order-keeps-generator-until-unset'],
        'stage': ('S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.CURRENT = eps '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("M|"))'),
        'checks': [
            'S.FRAMES = eps', 'S.ACTIVEFIBER = eps', 'S.ITERATORS = eps',
            '$lookup(S.ENV, $ptascii("generator")) = (n_generator_cell)',
            'S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED', '~pgenerator.FIRST',
            'pgenerator.VALUE = (POBJECT n_current)', 'pgenerator.KEY = (PINT 0)',
            'pgenerator.REFCELL = eps', 'pgenerator.DELEGATE = eps',
            'pgenerator.FRAME = (pframe_saved)', 'pframe_saved.CONTEXT = (pcallcontext)',
            'pcallcontext.NAME = $ptascii("reviewGeneratorOrder09")',
            '$generator_frame_valid(S, pgenerator, pframe_saved)',
            '$object_name(S, n_current) = $ptascii("ReviewGeneratorCurrent09")',
            '$heap_owners($heap_graph(S), HCELL n_generator_cell) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            'S.DESTRUCTION.CALLED = n_first :: n_called_tail*',
            '$object_name(S, n_first) = $ptascii("ReviewGeneratorFirst09")',
            '~((HOBJECT n_first) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 0',
            '~(n_current <- S.DESTRUCTION.CALLED)',
            '$lookup(S.ENV, $ptascii("e")) = (n_error_cell)',
            'S.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
            'S.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
            '$throwable_field(S, n_error, "line") = PINT 7',
            '$string_bytes($throwable_field(S, n_error, "message")) = '
            '($ptascii("Cannot use positional argument after named argument during unpacking"))',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = eps', '$trace_graph_valid(S, n_trace)',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("N|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("T|"), OUTPUT $ptascii("7"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|")]',
            *ADMISSION, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("M|")]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("M|"), OUTPUT $ptascii("F|"), '
            'OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_generator_cell) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_error_cell) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_generator) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_trace) = 0',
            'n_first <- S_done.DESTRUCTION.CALLED', 'n_current <- S_done.DESTRUCTION.CALLED',
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
