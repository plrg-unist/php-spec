#!/usr/bin/env python3
"""Reach delegated reference snapshots and retained-table abort ownership."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_array_delegation_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'delegated-reference-cache-sends-an-object-snapshot-before-producer-mutation': {
        'source': SOURCES['generator-call-unpack-array-delegation-review-reference-cell-snapshot'],
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 0'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps', 'S.HELD = eps',
            'n_generator = pgeneratorunpack.OBJECT',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_DELEGATING',
            'pgenerator.VALUE = eps', 'pgenerator.REFCELL = eps',
            'pgenerator.KEY = (PINT 0)',
            'pgenerator.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (PARRAY n_table)',
            'pgeneratorfrom.CURRENT = (REFERENCE n_payload)',
            'pgeneratorfrom.POSITION = 1', 'pgeneratorfrom.ACQUISITION = eps',
            'pgenerator.FRAME = (pframe_saved)',
            'pframe_saved.CONTEXT = (pcallcontext)',
            'pcallcontext.NAME = $ptascii("reviewDelegatedReference10")',
            'pframe_saved.ORIGIN = (pgeneratorfrom.SITE)',
            '$generator_frame_valid(S, pgenerator, pframe_saved)',
            '$generator_from_record_valid(S, n_generator, pgenerator)',
            '$lookup(S.ENV, $ptascii("value")) = (n_payload)',
            'S.STORE[n_payload] = DEFINED (POBJECT n_child)',
            '$object_name(S, n_child) = $ptascii("ReviewDelegatedReferenceChild10")',
            '$lookup(S.ENV, $ptascii("items")) = (n_items)',
            'S.STORE[n_items] = DEFINED (PARRAY n_table)',
            'S.ARRAYS[n_table].ITEMS = [ENTRY (KINT 0) (ALIAS n_payload)]',
            '$node_children(S, HARRAY n_table) = [HCELL n_payload]',
            '$node_children(S, HCELL n_payload) = [HOBJECT n_child]',
            '$generator_from_nodes(pgenerator.DELEGATE) = [HARRAY n_table, HCELL n_payload]',
            '$generator_cached_value(S, n_generator, false) = POBJECT n_child',
            '$generator_cached_value(S, n_generator, true) = PINT 0',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_table) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_generator)',
            'pgeneratorunpack.CALL.SENT.SLOTS = eps',
            'pgeneratorunpack.CALL.SENT.NAMED = eps',
            'pgeneratorunpack.CALL.LINE = 7', '~pgeneratorunpack.NAMED',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = '
            '[HOBJECT n_generator, HOBJECT n_generator]',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            '~$generator_unpack_delegated_blocked(S[.COMPLETION = '
            'UNSUPPORTED "Generator unpack delegated producer"])',
            'S_bad = $generator_set(S, n_generator, pgenerator[.DELEGATE = '
            '(pgeneratorfrom[.CURRENT = eps])])',
            '~$generator_unpack_valid(S_bad, pgeneratorunpack, "ready")',
            '~$call_descriptors_valid(S_bad)',
            '~$generator_unpack_valid(S[.ORIGIN = eps], pgeneratorunpack, "ready")',
            '~$generator_unpack_valid(S, pgeneratorunpack[.COUNT = 1], "ready")',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *VALID, *ZERO, *ONE,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorunpack_next.COUNT = 1', '~pgeneratorunpack_next.NAMED',
            'pgeneratorunpack_next.INPUT = pgeneratorunpack.INPUT',
            'pgeneratorunpack_next.OBJECT = n_generator',
            'pgeneratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_child))]',
            'pgeneratorunpack_next.CALL.SENT.NAMED = eps',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack_next "next") = '
            '[HOBJECT n_generator, HOBJECT n_generator, HOBJECT n_child]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 2',
            '$heap_owners($heap_graph(S_one), HARRAY n_table) = 2',
            '$generator_unpack_valid(S_one, pgeneratorunpack_next, "next")', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("N|"), OUTPUT $ptascii("F|"), '
            'OUTPUT $ptascii("D|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("M|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_generator) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            'n_child <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'queued-delegated-table-child-release-reaches-caller-receipt-before-finally': {
        'source': SOURCES['generator-call-unpack-array-delegation-review-cv-order-error-table-before-finally'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: '
                  '(GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
                  '-- if pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_first)) :: pdestructionjob* '
                  '-- if $object_name(S, n_first) = $ptascii("ReviewDelegatedCvA10")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.ITERATORS = eps', '$destructor_operational(S)', '$destructor_user_source(S)',
            'n_generator = pgenclose.OBJECT',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_CLOSING', 'pgenerator.FRAME = eps',
            'pgenerator.VALUE = eps', 'pgenerator.REFCELL = eps',
            'pgenerator.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_current))',
            '$object_name(S, n_current) = $ptascii("ReviewDelegatedCvB10")',
            'pgenclose.STAGE = CLOSE_QUEUED', 'pgenclose.NEXT = 0',
            'pgenclose.STORE = eps', 'pgenclose.PENDING = eps',
            'pgenclose.CALLER = S.CURRENT', 'pgenclose.CALLSITE = S.ORIGIN',
            'pgenclose.FRAME = (pframe_saved)',
            'pframe_saved.CONTEXT = (pgenclose.CONTEXT)',
            'pgenclose.CONTEXT.NAME = $ptascii("reviewDelegatedCv10")',
            '$generator_close_enter_valid(S, pgenclose)',
            '$generator_close_release_valid(S, pgenrelease)',
            'pgenrelease.PENDING = eps', 'pgenrelease.COMPLETION = NORMAL',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pdestructionoperation.CALLER = S.CURRENT',
            'pdestructionoperation.ORIGIN = S.ORIGIN',
            'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES text_name) metadata)',
            '$base64(text_name) = $ptascii("generator")',
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) <- ptask_tail*',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$generator_close_destructor_tasks(S, S.TODO, eps, eps, '
            'DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
            '$generator_close_destructor_ready(S, pgenrelease)',
            '$lookup(S.ENV, $ptascii("generator")) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
            '~(n_first <- S.DESTRUCTION.CALLED)', '~(n_current <- S.DESTRUCTION.CALLED)',
            '$lookup(S.ENV, $ptascii("caught")) = (n_error_cell)',
            'S.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
            '$throwable_field(S, n_error, "line") = PINT 7',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = eps',
            'pgenclose_pending = pgenclose[.PENDING = (n_error)]',
            'S_pending = S[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: '
            '(GENERATOR_CLOSE_ENTER pgenclose_pending) :: ptask_tail*]',
            '~$generator_close_destructor_ready(S_pending, pgenrelease)',
            'S.ORIGIN = (porigin_unset)',
            'pgenclose_source = pgenclose[.SITE = porigin_unset]',
            'S_source = S[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: '
            '(GENERATOR_CLOSE_ENTER pgenclose_source) :: ptask_tail*]',
            '~$generator_close_destructor_ready(S_source, pgenrelease)',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("T|"), '
            'OUTPUT $ptascii("7"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), '
            'OUTPUT $ptascii("M|")]', *VALID, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(GENERATOR_CLOSE_RELEASE pgenrelease_after) :: '
            '(GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_first)]',
            'pgenrelease_after = pgenrelease[.JOBS = pdestructionjob*]',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'S_one.DESTRUCTION.OPERATIONS = S.DESTRUCTION.OPERATIONS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_first) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("A|"), OUTPUT $ptascii("F|"), '
            'OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_generator) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_first) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
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
