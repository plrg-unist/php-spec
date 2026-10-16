#!/usr/bin/env python3
"""Reach copied SEND results and close after argument-cleanup exceptions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_init_send_review_cases.json')
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
        '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0']

CASES = {
    'copied-reference-row-result-survives-argument-referent-replacement': {
        'source': SOURCES['generator-pending-init-send-review-reference-row-snapshot-before-argument-destructor'],
        'stage': ('S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)]) '
                  '-- if pgeneratorop.NAME = "send" '
                  '-- if pdestructionoperation.VALUE = KNOWN (PARRAY n_old_row)'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.CALLER = eps',
            '$destructor_operation_for(S) = (pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            'pgeneratorop.ARGUMENTS = eps', 'pgeneratorop.LINE = 14',
            'n_middle = pgeneratorop.OBJECT',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.VALUE = eps', 'pgenerator_middle.REFCELL = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.POSITION = 1',
            'pgeneratorfrom.CURRENT = (REFERENCE n_payload)',
            'pgenerator_middle.FRAME = (pframe_middle)',
            'pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom.SITE n_child (PINT 23)) :: ptask_middle*',
            '$generator_from_complete_valid(S, n_middle, pgeneratorfrom.SITE, n_child, PINT 23)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.RETURN = (PINT 23)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$lookup(S.ENV, $ptascii("payload")) = (n_payload)',
            'S.STORE[n_payload] = DEFINED (PARRAY n_live_row)',
            'n_old_row =/= n_live_row',
            'S.ARRAYS[n_old_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
            'S.ARRAYS[n_live_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_live))]',
            '$object_name(S, n_old) = $ptascii("ReviewPendingSendFirst17")',
            '$object_name(S, n_live) = $ptascii("ReviewPendingSendSecond17")',
            '$generator_cached_value(S, n_middle, false) = PARRAY n_live_row',
            '$generator_cached_value(S, n_middle, true) = PNULL',
            '$node_children(S, HOBJECT n_middle) = $generator_frame_nodes(pgenerator_middle.FRAME) ++ [HCELL n_payload]',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 2',
            '$heap_owners($heap_graph(S), HCELL n_payload) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_old_row) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_live_row) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_live) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 0',
            '~((HOBJECT n_argument) <- S.ALLOCATIONS)',
            'n_argument <- S.DESTRUCTION.CALLED',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HARRAY n_old_row]',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("S|"), OUTPUT $ptascii("W|")]',
            *VALID, *BUDGET,
            'S_one.TODO = ptask_tail*',
            'S_one.RESULT = KNOWN (PARRAY n_old_row)',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_one), HARRAY n_old_row) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_payload) = 2',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("X|"), OUTPUT $ptascii("OLD|"), OUTPUT $ptascii("LIVE|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("N|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("KEY|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("23"), OUTPUT $ptascii("|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("13"), OUTPUT $ptascii("|"), OUTPUT $ptascii("J|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("29"), OUTPUT $ptascii("|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HARRAY n_old_row) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_live_row) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_live) = 0',
            'n_old <- S_done.DESTRUCTION.CALLED',
            'n_live <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'argument-throw-keeps-null-cache-and-cleared-initialization-for-real-close': {
        'source': SOURCES['generator-pending-init-send-review-null-cache-argument-throw-and-later-finally'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
                  '-- if $trace_context_function(S, pgenclose.CONTEXT) = $ptascii("reviewPendingSendNullMiddle17")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'n_middle = pgenclose.OBJECT',
            'pgenclose.STAGE = CLOSE_QUEUED', 'pgenclose.PENDING = eps',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_CLOSING',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.FRAME = eps',
            'pgenerator_middle.VALUE = eps', 'pgenerator_middle.REFCELL = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.POSITION = 1',
            'pgeneratorfrom.CURRENT = (KNOWN PNULL)',
            '$generator_own_cache(pgenerator_middle)',
            '~$generator_close_pending_init(S, pgenclose)',
            '$generator_close_enter_valid(S, pgenclose)',
            'pgenclose.FRAME = (pframe_middle)',
            'pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom.SITE n_child (PINT 23)) :: ptask_middle*',
            '~$generator_from_complete_valid(S, n_middle, pgeneratorfrom.SITE, n_child, PINT 23)',
            '$generator_close_drop_claim(S, pframe_middle.TODO, n_middle, pgeneratorfrom.SITE) = ptask_middle*',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.RETURN = (PINT 23)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
            '$node_children(S, HOBJECT n_middle) = eps',
            '$lookup(S.ENV, $ptascii("error")) = (n_error_cell)',
            'S.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
            '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("argument17"))',
            '$throwable_field(S, n_error, "previous") = PNULL',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("NULL|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("S|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("ARG|"), OUTPUT $ptascii("NOPREV|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("NULL|"), OUTPUT $ptascii("U|")]',
            *VALID, *BUDGET, *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("J|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("E")]',
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
