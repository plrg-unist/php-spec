#!/usr/bin/env python3
"""Reach forwarded used-slot consumption and request-late orphan destruction."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_shared_send_review_cases.json')
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
        '$heap_valid($heap_graph(S_done))']

CASES = {
    'forwarded-next-transfers-used-slot-after-reference-cache-cow': {
        'source': SOURCES['generator-pending-shared-send-review-reference-row-snapshot-and-forwarded-next'],
        'stage': ('S.TODO = (GENERATOR_FROM_NEXT n_middle porigin) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $trace_context_function(S, pcallcontext) = $ptascii("reviewSharedSendMiddle18") '
                  '-- if S.GENERATORINPUTS = [pgeneratorinput] '
                  '-- if pgeneratorinput.LIVE'),
        'checks': [
            'S.ACTIVEFIBER = eps',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("cache")) = (n_cache_cell)',
            '$lookup(psymboltable_global.ENV, $ptascii("outer")) = (n_outer_cell)',
            'S.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)',
            '$lookup(psymboltable_global.ENV, $ptascii("row")) = eps',
            'S.STORE[n_cache_cell] = DEFINED (PARRAY n_cache_row)',
            'S.ARRAYS[n_cache_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_cache))]',
            '$object_name(S, n_cache) = $ptascii("ReviewSharedSendNew18")',
            'pgeneratorinput.OBJECT = n_child',
            'pgeneratorinput.SOURCE.OBJECT = n_middle',
            'pgeneratorinput.SOURCE.NAME = "send"',
            'pgeneratorinput.SOURCE.LINE = 11',
            '~pgeneratorinput.SOURCE.ADVANCE',
            '~pgeneratorinput.SOURCE.BORROWED',
            '~pgeneratorinput.SOURCE.STARTPACK',
            'pgeneratorinput.SOURCE.LOOP = eps',
            'pgeneratorinput.SOURCE.ARGUMENTS = [PARRAY n_buffer]',
            'S.ARRAYS[n_buffer].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]',
            '$object_name(S, n_payload) = $ptascii("ReviewSharedSendPayload18")',
            'n_buffer =/= n_cache_row',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_input_count(S.GENERATORINPUTS, n_child) = 1',
            '$generator_input_count(S.GENERATORINPUTS, n_middle) = 0',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HARRAY n_buffer]',
            '$heap_owners($heap_graph(S), HARRAY n_buffer) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_cache_row) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '$heap_owners($heap_graph(S), HCELL n_cache_cell) = 3',
            '$heap_count(HARRAY n_buffer, $machine_roots(S)) = 1',
            '$heap_count(HARRAY n_buffer, $node_children(S, HOBJECT n_child)) = 0',
            '$heap_count(HOBJECT n_middle, $generator_inputs_nodes(S.GENERATORINPUTS)) = 0',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_RUNNING',
            'pgenerator_middle.FRAME = eps',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.SITE = porigin',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.CURRENT = eps',
            'pgeneratorfrom.POSITION = 1',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            'pgenerator_child.DELEGATE = eps',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (pgeneratorinput.SITE)',
            'pgenerator_child.VALUE = eps',
            'pgenerator_child.REFCELL = (n_cache_cell)',
            'pgenerator_child.KEY = (PINT 0)',
            '~pgenerator_child.FIRST',
            '~pgenerator_child.PENDING_INIT',
            'pframe_child.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_name* z_write) :: ptask_child*',
            '$generator_input_tail(S, pgeneratorinput.SITE, pframe_child.TODO)',
            'S_wrong_tail = $generator_set(S, n_child, pgenerator_child[.FRAME = (pframe_child[.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME ($ptascii("wrong18")) z_write) :: ptask_child*])])',
            '$heap_graph(S_wrong_tail) = $heap_graph(S)',
            '$heap_valid($heap_graph(S_wrong_tail))',
            '~$generator_inputs_valid(S_wrong_tail, S_wrong_tail.GENERATORINPUTS)',
            '~$call_descriptors_valid(S_wrong_tail)',
            'S.DESTRUCTION.CALLED = [n_old]',
            '$object_name(S, n_old) = $ptascii("ReviewSharedSendOld18")',
            '~((HOBJECT n_old) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 0',
            '~(n_payload <- S.DESTRUCTION.CALLED)',
            'pgeneratorinput_bad = pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = $(pgeneratorinput.SOURCE.LINE + 1)]]',
            '~$generator_inputs_valid(S, [pgeneratorinput_bad])',
            'S_bad = S[.GENERATORINPUTS = [pgeneratorinput_bad]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '$heap_valid($heap_graph(S_bad))',
            '~$call_descriptors_valid(S_bad)',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("S|"), OUTPUT $ptascii("OLD|"), OUTPUT $ptascii("W|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("LIVE|")]',
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = eps',
            'S_one.RESULT = KNOWN (PARRAY n_buffer)',
            'S_one.TODO = pframe_child.TODO',
            'S_expected = $generator_set(S, n_child, pgenerator_child[.FRAME = eps][.PHASE = GENERATOR_RUNNING])',
            'S_one.OBJECTS = S_expected.OBJECTS',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.FRAMES = pframe_resumer :: S.FRAMES',
            'pframe_resumer.CONTEXT = S.CURRENT',
            'pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_middle porigin n_child) :: ptask_tail*',
            'pgeneratorop_child.OBJECT = n_child',
            'pgeneratorop_child.NAME = "next"',
            'pgeneratorop_child.ARGUMENTS = eps',
            'pgeneratorop_child.SITE = porigin',
            '~$generator_resume_root(S_one, pgeneratorop_child)',
            '$generator_from_operation_valid(S_one, pgeneratorop_child)',
            '$heap_owners($heap_graph(S_one), HARRAY n_buffer) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_cache_cell) = 3',
            *DONE,
            'S_done.GENERATORINPUTS = eps',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("R|"), OUTPUT $ptascii("PAYLOAD|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("N|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("17"), OUTPUT $ptascii("|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("J|"), OUTPUT $ptascii("I|"), OUTPUT $ptascii("23"), OUTPUT $ptascii("|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("29"), OUTPUT $ptascii("|"), OUTPUT $ptascii("Z|"), OUTPUT $ptascii("Q|"), OUTPUT $ptascii("DONE|"), OUTPUT $ptascii("CACHE|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HARRAY n_buffer) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_cache_row) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_outer) = 0',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            'n_cache <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'orphaned-cache-alias-survives-real-close-until-request-object-store': {
        'source': SOURCES['generator-pending-shared-send-review-cache-alias-becomes-sole-slot-owner-on-close'],
        'stage': ('S.TODO = [DESTRUCTOR_STORE] '
                  '-- if S.GENERATORINPUTS = [pgeneratorinput] '
                  '-- if ~pgeneratorinput.LIVE '
                  '-- if pgeneratorinput.SOURCE.ARGUMENTS = [POBJECT n_payload] '
                  '-- if $destructor_handle(S, S.DESTRUCTION.INDEX, 0) = (n_payload) '
                  '-- if ~(n_payload <- S.DESTRUCTION.CALLED)'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.DESTRUCTION.PHASE = DESTRUCTION_STORE',
            'S.DESTRUCTION.RELEASES = eps', 'S.DESTRUCTION.CALLS = eps',
            'pgeneratorinput.OBJECT = n_child',
            'pgeneratorinput.SOURCE.OBJECT = n_middle',
            'pgeneratorinput.SOURCE.NAME = "send"',
            'pgeneratorinput.SOURCE.LINE = 9',
            '$object_name(S, n_payload) = $ptascii("ReviewSharedSendAlias18")',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_input_count(S.GENERATORINPUTS, n_child) = 0',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_payload]',
            '$heap_count(HOBJECT n_payload, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '(HOBJECT n_payload) <- S.ALLOCATIONS',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.FRAME = eps',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_CLOSED',
            'pgenerator_middle.FRAME = eps',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '~((HOBJECT n_middle) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 0',
            'pgeneratorinput_bad = pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = $(pgeneratorinput.SOURCE.LINE + 1)]]',
            '~$generator_inputs_valid(S, [pgeneratorinput_bad])',
            'S_bad = S[.GENERATORINPUTS = [pgeneratorinput_bad]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '$heap_valid($heap_graph(S_bad))',
            '~$call_descriptors_valid(S_bad)',
            '~$generator_inputs_valid(S, [pgeneratorinput[.LIVE = true]])',
            '~$generator_inputs_valid(S, [pgeneratorinput[.SITE = pgeneratorinput.SOURCE.SITE]])',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("S|"), OUTPUT $ptascii("OLD|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("U|"), OUTPUT $ptascii("J|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("Z|"), OUTPUT $ptascii("E")]',
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = S.GENERATORINPUTS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: [DESTRUCTOR_STORE]',
            'pdestructorcall.OBJECT = n_payload', 'pdestructorcall.STORE',
            '~pdestructorcall.USER', 'pdestructorcall.CALLER = eps',
            'pdestructorcall.ORIGIN = eps', 'pdestructorcall.RELEASE = eps',
            '$destructor_enter_valid(S_one, pdestructorcall)',
            'n_payload <- S_one.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 3',
            *DONE,
            'S_done.GENERATORINPUTS = S.GENERATORINPUTS',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("A|")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 1',
            '(HOBJECT n_payload) <- S_done.ALLOCATIONS',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
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
