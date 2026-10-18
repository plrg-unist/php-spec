#!/usr/bin/env python3
"""Reach parked used-input orphaning and late aliased-cache destruction."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_buffered_throw_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
REF = 'generator-pending-buffered-throw-review-reference-row-and-input-array'
ALIAS = 'generator-pending-buffered-throw-review-cache-input-alias-sole-receiver'
EVENTS = {
    REF: ['P|', 'O|', 'M|', 'L|', 'C|', 'S|', 'OLD|', 'W|', 'CATCH|',
          '1', '|', '1', '|', 'GET|', '1', '|', '7', '|', '1', '|',
          'A|', 'ROW|', 'Z|', 'OUT|', 'K|', 'UP|', 'J|', 'LOW|',
          'CHILD|', 'CACHE|', 'E', 'B|'],
    ALIAS: ['P|', 'O|', 'M|', 'L|', 'C|', 'S|', '1', '|', 'T|', 'Z|',
            'DROP|', 'J|', 'K|', 'CALLER|', '1', '|', '1', '|', 'E', 'A|'],
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
    'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
]

CASES = {
    'parked-reference-child-close-orphans-live-input-without-a-decrement': {
        'source': ROWS[REF]['source'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: ptask_tail* '
                  '-- if pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_child)) :: pdestructionjob_tail* '
                  '-- if S.GENERATORINPUTS = [pgeneratorinput] '
                  '-- if pgeneratorinput.LIVE -- if pgeneratorinput.OBJECT = n_child '
                  '-- if S.OBJECTS[n_child] = GENERATOR pgenerator_child '
                  '-- if pgenerator_child.PARKED =/= eps '
                  '-- if $heap_owners($heap_graph(S[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease[.JOBS = pdestructionjob_tail*]) :: ptask_tail*]), HOBJECT n_child) = 0'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.COMPLETION = NORMAL', 'pgenrelease.PENDING = eps',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            '~pgenerator_child.PENDING_INIT',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (porigin_yield)',
            'pframe_child.CONTEXT = (pcallcontext_child)',
            'pgenerator_child.PARKED = (porigin_yield)',
            'pframe_child.HELD = eps', '$tasks_nodes(pframe_child.TODO) = eps',
            'pframe_child.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_name* z_write) :: ptask_child*',
            'pgenerator_child.VALUE = eps', 'pgenerator_child.REFCELL = (n_cache_cell)',
            'pgenerator_child.KEY = (PINT 7)', 'pgenerator_child.RETURN = eps',
            'pgenerator_child.DELEGATE = eps',
            '$generator_input_site(S, n_child, porigin_yield)',
            '$generator_input_tail(S, porigin_yield, pframe_child.TODO)',
            '$generator_parked_valid(S, pgenerator_child)',
            '$generator_parked(S, n_child, |S.OBJECTS|)',
            '$generator_pending_throw_leaf(S, n_child, |S.OBJECTS|) = eps',
            'S_unparked = $generator_set(S, n_child, pgenerator_child[.PARKED = eps])',
            '$heap_graph(S_unparked) = $heap_graph(S)',
            '$generator_pending_throw_leaf(S_unparked, n_child, |S.OBJECTS|) = (n_child)',
            'pgeneratorinput.SITE = porigin_yield',
            'pgeneratorinput.SOURCE.OBJECT = n_lower',
            'pgeneratorinput.SOURCE.NAME = "send"', 'pgeneratorinput.SOURCE.LINE = 12',
            '~pgeneratorinput.SOURCE.ADVANCE', '~pgeneratorinput.SOURCE.BORROWED',
            '~pgeneratorinput.SOURCE.STARTPACK', 'pgeneratorinput.SOURCE.LOOP = eps',
            'pgeneratorinput.SOURCE.ARGUMENTS = [PARRAY n_buffer]',
            'S.ARRAYS[n_buffer].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]',
            '$object_name(S, n_payload) = $ptascii("ReviewBufferedPendingPayload22")',
            '$generator_input_count(S.GENERATORINPUTS, n_child) = 1',
            '$generator_input_live_valid(S, pgeneratorinput)',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HARRAY n_buffer]',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_buffer) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_count(HARRAY n_buffer, $machine_roots(S)) = 1',
            '$heap_count(HARRAY n_buffer, $node_children(S, HOBJECT n_child)) = 0',
            '$node_children(S, HOBJECT n_child) = [HCELL n_cache_cell, HCELL n_cache_cell]',
            '$generator_close_frame_nodes(S, pframe_child) = [HCELL n_cache_cell]',
            '$heap_owners($heap_graph(S), HCELL n_cache_cell) = 3',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("upper")) = eps',
            '$lookup(S_global.ENV, $ptascii("lower")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$lookup(S_global.ENV, $ptascii("row")) = eps',
            '$lookup(S_global.ENV, $ptascii("cache")) = (n_cache_cell)',
            '$lookup(S_global.ENV, $ptascii("exception")) = (n_exception_cell)',
            '$lookup(S_global.ENV, $ptascii("caught")) = (n_caught_cell)',
            'S.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
            'S.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            'S.STORE[n_cache_cell] = DEFINED (PARRAY n_cache_row)',
            'S.ARRAYS[n_cache_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_cache))]',
            '$object_name(S, n_cache) = $ptascii("ReviewBufferedPendingLive22")',
            'n_cache_row =/= n_buffer',
            '$heap_owners($heap_graph(S), HARRAY n_cache_row) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '~(n_payload <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_lower] = GENERATOR pgenerator_lower',
            'pgenerator_lower.PHASE = GENERATOR_CLOSED', 'pgenerator_lower.PARKED = eps',
            '~((HOBJECT n_lower) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_lower) = 0',
            'pgeneratorinput_bad = pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = 0]]',
            'S_bad = S[.GENERATORINPUTS = [pgeneratorinput_bad]]',
            '$heap_graph(S_bad) = $heap_graph(S)', '$heap_valid($heap_graph(S_bad))',
            '~$generator_inputs_valid(S_bad, S_bad.GENERATORINPUTS)',
            '~$call_descriptors_valid(S_bad)',
            'S_wrong_tail = $generator_set(S_unparked, n_child, pgenerator_child[.PARKED = eps][.FRAME = (pframe_child[.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME ($ptascii("wrong22")) z_write) :: ptask_child*])])',
            '$heap_graph(S_wrong_tail) = $heap_graph(S)',
            '~$generator_inputs_valid(S_wrong_tail, S_wrong_tail.GENERATORINPUTS)',
            '$generator_pending_throw_leaf(S_wrong_tail, n_child, |S.OBJECTS|) = eps',
            '~$call_descriptors_valid(S_wrong_tail)',
            'S.EVENTS = ' + outputs(EVENTS[REF][:EVENTS[REF].index('LOW|') + 1]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]',
            '$generator_input_count(S_one.GENERATORINPUTS, n_child) = 0',
            'S_one.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease_input) :: (GENERATOR_CLOSE_ENTER pgenclose) :: (GENERATOR_CLOSE_RELEASE pgenrelease_next) :: ptask_tail*',
            'pgenrelease_input.JOBS = eps', 'pgenrelease_input.PENDING = eps',
            'pgenrelease_input.VALUE = S.RESULT', 'pgenrelease_input.BASE = S.BASE',
            'pgenrelease_input.COMPLETION = NORMAL',
            'pgenrelease_next = pgenrelease[.JOBS = pdestructionjob_tail*][.PENDING = eps]',
            'pgenclose.OBJECT = n_child', 'pgenclose.SITE = porigin_yield',
            'pgenclose.CONTEXT = pcallcontext_child', 'pgenclose.FRAME = (pframe_child)',
            'pgenclose.STAGE = CLOSE_QUEUED', 'pgenclose.NEXT = 0',
            'pgenclose.CALLER = eps', 'pgenclose.CALLSITE = S.ORIGIN',
            'pgenclose.PENDING = eps', 'pgenclose.STORE = eps',
            '$generator_close_enter_valid(S_one, pgenclose)',
            '$generator_close_parked(S_one, pgenclose)',
            'S_expected = $generator_set(S, n_child, pgenerator_child[.FRAME = eps][.PHASE = GENERATOR_CLOSING])',
            'S_one.OBJECTS = S_expected.OBJECTS',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_one), HCELL n_cache_cell) = 3',
            '$heap_owners($heap_graph(S_one), HARRAY n_buffer) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2',
            '~(n_payload <- S_one.DESTRUCTION.CALLED)',
            *DONE,
            'S_done.GENERATORINPUTS = S_one.GENERATORINPUTS',
            'S_done.EVENTS = ' + outputs(EVENTS[REF]),
            '$heap_owners($heap_graph(S_done), HARRAY n_buffer) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 1',
            '(HOBJECT n_payload) <- S_done.ALLOCATIONS',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        ],
    },
    'parked-cache-input-alias-is-an-orphan-only-owner-at-object-store': {
        'source': ROWS[ALIAS]['source'],
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
            'pgeneratorinput.SOURCE.OBJECT = n_lower',
            'pgeneratorinput.SOURCE.NAME = "send"', 'pgeneratorinput.SOURCE.LINE = 11',
            '$object_name(S, n_payload) = $ptascii("ReviewBufferedPendingAlias22")',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_input_count(S.GENERATORINPUTS, n_child) = 0',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_payload]',
            '$heap_count(HOBJECT n_payload, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '(HOBJECT n_payload) <- S.ALLOCATIONS',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED', 'pgenerator_child.FRAME = eps',
            'pgenerator_child.PARKED = eps',
            'S.OBJECTS[n_lower] = GENERATOR pgenerator_lower',
            'pgenerator_lower.PHASE = GENERATOR_CLOSED', 'pgenerator_lower.FRAME = eps',
            'pgenerator_lower.PARKED = eps',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '~((HOBJECT n_lower) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_lower) = 0',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("upper")) = eps',
            '$lookup(S_global.ENV, $ptascii("lower")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$lookup(S_global.ENV, $ptascii("row")) = eps',
            '$lookup(S_global.ENV, $ptascii("exception")) = eps',
            '$lookup(S_global.ENV, $ptascii("caught")) = eps',
            'pgeneratorinput_bad = pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = 0]]',
            'S_bad = S[.GENERATORINPUTS = [pgeneratorinput_bad]]',
            '$heap_graph(S_bad) = $heap_graph(S)', '$heap_valid($heap_graph(S_bad))',
            '~$generator_inputs_valid(S_bad, S_bad.GENERATORINPUTS)',
            '~$call_descriptors_valid(S_bad)',
            '~$generator_inputs_valid(S, [pgeneratorinput[.LIVE = true]])',
            '~$generator_inputs_valid(S, [pgeneratorinput[.SITE = pgeneratorinput.SOURCE.SITE]])',
            'S.EVENTS = ' + outputs(EVENTS[ALIAS][:-1]),
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
            'S_done.EVENTS = ' + outputs(EVENTS[ALIAS]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 1',
            '(HOBJECT n_payload) <- S_done.ALLOCATIONS',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_lower) <- S_done.ALLOCATIONS)',
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
