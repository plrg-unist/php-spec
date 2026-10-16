#!/usr/bin/env python3
"""Reach unused-target cache COW and supplied-throw Generator cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_unused_send_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
ROW = 'generator-pending-unused-send-review-reference-snapshot-before-argument-cow'
THROW = 'generator-pending-unused-send-review-null-cache-argument-throw-and-last-receiver'
EVENTS = {
    ROW: ['P|', 'O|', 'M|', 'C|', 'D|', 'W|', 'S|', 'OLD|', 'A|', 'X|',
          'V|', 'LIVE|', 'BODY|', 'N|', '17', '|', 'T|', 'J|', 'I|', '23',
          '|', 'K|', 'F|', '29', '|', 'Z|', 'Q|', 'DONE|', 'CACHE|', 'E'],
    THROW: ['P|', 'O|', 'M|', 'C|', 'H|', '1', '|', 'F|', 'DROP|', 'D|',
            'J|', 'K|', 'CATCH|', '1', '|', 'E'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def outputs(parts):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
BUDGET = [
    'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
    'S_one = S_one_budget[.COMPLETION = NORMAL]', 'S_one.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
]
DONE = [
    'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
    'S_done.HELD = eps', 'S_done.GENERATORINPUTS = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
]

CASES = {
    'old-reference-row-survives-ignored-argument-destructor-cow': {
        'source': ROWS[ROW]['source'],
        'stage': ('S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)]) '
                  '-- if pgeneratorop.NAME = "send" '
                  '-- if pdestructionoperation.VALUE = KNOWN (PARRAY n_old_row)'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GENERATORINPUTS = eps',
            'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.CALLER = eps',
            '$destructor_operation_for(S) = (pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            'pgeneratorop.ARGUMENTS = eps', 'pgeneratorop.LINE = 11',
            'n_middle = pgeneratorop.OBJECT',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.VALUE = eps', 'pgenerator_middle.REFCELL = eps',
            'pgenerator_middle.FRAME = (pframe_middle)',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.CURRENT = eps',
            'pgeneratorfrom.POSITION = 1',
            'pframe_middle.TODO = (GENERATOR_FROM_NEXT n_middle pgeneratorfrom.SITE) :: ptask_middle*',
            '$generator_from_record_valid(S, n_middle, pgenerator_middle)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            'pgenerator_child.VALUE = eps',
            'pgenerator_child.REFCELL = (n_cache_cell)',
            'pgenerator_child.KEY = (PINT 0)',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (porigin_yield)',
            '$generator_unused_send_tail(S, porigin_yield, pframe_child.TODO)',
            '~$generator_send_target(pframe_child.TODO)',
            '$generator_unused_send_leaf(S, n_middle, |S.OBJECTS|) = (n_child)',
            '$generator_send_leaf(S, n_middle, |S.OBJECTS|) = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("cache")) = (n_cache_cell)',
            'S.STORE[n_cache_cell] = DEFINED (PARRAY n_live_row)',
            'n_old_row =/= n_live_row',
            'S.ARRAYS[n_old_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
            'S.ARRAYS[n_live_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_live))]',
            '$object_name(S, n_old) = $ptascii("ReviewUnusedOld19")',
            '$object_name(S, n_live) = $ptascii("ReviewUnusedNew19")',
            '$generator_cached_value(S, n_middle, false) = PARRAY n_live_row',
            '$node_children(S, HOBJECT n_middle) = $generator_frame_nodes(pgenerator_middle.FRAME) ++ [HOBJECT n_child]',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 2',
            '$heap_owners($heap_graph(S), HCELL n_cache_cell) = 3',
            '$heap_owners($heap_graph(S), HARRAY n_old_row) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_live_row) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_live) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 0',
            '~((HOBJECT n_argument) <- S.ALLOCATIONS)',
            'n_argument <- S.DESTRUCTION.CALLED',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HARRAY n_old_row]',
            'S.EVENTS = ' + outputs(EVENTS[ROW][:6]),
            *VALID, *BUDGET,
            'S_one.TODO = ptask_tail*',
            'S_one.RESULT = KNOWN (PARRAY n_old_row)',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.GENERATORINPUTS = eps',
            '$heap_owners($heap_graph(S_one), HARRAY n_old_row) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_cache_cell) = 3',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[ROW]),
            '$heap_owners($heap_graph(S_done), HARRAY n_old_row) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_live_row) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_live) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            'n_old <- S_done.DESTRUCTION.CALLED',
            'n_live <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'supplied-argument-throw-survives-real-last-receiver-close': {
        'source': ROWS[THROW]['source'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
                  '-- if $trace_context_function(S, pgenclose.CONTEXT) = $ptascii("reviewUnusedNullMiddle19") '
                  '-- if pgenclose.PENDING = (n_exception) '
                  '-- if pgenclose.FRAME = (pframe_middle) '
                  '-- if pframe_middle.TODO = (GENERATOR_FROM_NEXT pgenclose.OBJECT pgenclose.SITE) :: ptask_middle*'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GENERATORINPUTS = eps',
            'n_middle = pgenclose.OBJECT',
            'pgenclose.STAGE = CLOSE_QUEUED',
            'pgenclose.PENDING = (n_exception)',
            'pframe_middle.ORIGIN = (pgenclose.SITE)',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_CLOSING',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.FRAME = eps',
            'pgenerator_middle.VALUE = eps', 'pgenerator_middle.REFCELL = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.CURRENT = eps',
            '~$generator_own_cache(pgenerator_middle)',
            '~$generator_close_pending_init(S, pgenclose)',
            '$generator_close_enter_valid(S, pgenclose)',
            '$generator_close_drop_claim(S, pframe_middle.TODO, n_middle, pgenclose.SITE) = ptask_middle*',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
            '$node_children(S, HOBJECT n_middle) = eps',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])',
            'pgeneratorop.OBJECT = n_middle', 'pgeneratorop.NAME = "send"',
            'pgeneratorop.LINE = 10', 'pgeneratorop.ARGUMENTS = eps',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.PENDING = (n_exception)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 0',
            '~((HOBJECT n_argument) <- S.ALLOCATIONS)',
            'n_argument <- S.DESTRUCTION.CALLED',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("middle")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$lookup(S_global.ENV, $ptascii("exception")) = (n_exception_cell)',
            'S.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
            '$string_bytes($throwable_field(S, n_exception, "message")) = ($ptascii("unused19"))',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            '$throwable_live(S, n_exception)',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 3',
            'S.EVENTS = ' + outputs(EVENTS[THROW][:11]),
            *VALID, *BUDGET,
            'S_one.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_ENTER pgenclose_next) :: ptask_tail*',
            'pgenrelease.JOBS = eps', 'pgenrelease.PENDING = (n_exception)',
            'pgenclose_next = pgenclose[.FRAME = (pframe_middle[.TODO = ptask_middle*])][.PENDING = eps]',
            '$generator_close_enter_valid(S_one, pgenclose_next)',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.GENERATORINPUTS = eps',
            '$heap_owners($heap_graph(S_one), HOBJECT n_middle) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 3',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[THROW]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            'n_argument <- S_done.DESTRUCTION.CALLED',
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
