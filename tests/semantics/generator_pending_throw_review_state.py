#!/usr/bin/env python3
"""Reach parked reference-child and detached-middle close after caller catch."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_throw_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
REF = 'generator-pending-throw-review-reference-cache-snapshot-and-explicit-close'
DETACHED = 'generator-pending-throw-review-detached-current-with-node-free-return'
EVENTS = {
    REF: ['P|', 'O|', 'M|', 'C|', 'W|', 'CATCH|', '1', '|', '1', '|',
          'GET|', '1', '|', '7', '|', '1', '|', 'A|', 'ROW|', 'Z|', 'OUT|',
          'J|', 'MID|', 'CHILD|', 'B|', 'E'],
    DETACHED: ['P|', 'O|', 'M|', 'C|', 'L|', 'HELD|', '1', '|', 'DROP|',
               'CATCH|', '1', '|', '1', '|', 'GET|', '1', '|', '1', '|',
               '1', '|', 'ROW|', 'Z|', 'OUT|', 'A|', 'MID|', 'E'],
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
    'caught-exception-does-not-own-parked-reference-child-close': {
        'source': ROWS[REF]['source'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
                  '-- if pgenclose.STAGE = CLOSE_QUEUED '
                  '-- if $trace_context_function(S, pgenclose.CONTEXT) = $ptascii("reviewPendingLeaf21") '
                  '-- if pgenclose.FRAME = (pframe_child) '
                  '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator_child '
                  '-- if pgenerator_child.PARKED = (pgenclose.SITE)'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GENERATORINPUTS = eps', 'S.COMPLETION = NORMAL',
            'n_child = pgenclose.OBJECT',
            'pgenclose.PENDING = eps',
            'pgenclose.CALLER = eps',
            'pframe_child.ORIGIN = (pgenclose.SITE)',
            'pgenerator_child.PHASE = GENERATOR_CLOSING',
            '~pgenerator_child.PENDING_INIT',
            'pgenerator_child.FRAME = eps',
            'pgenerator_child.VALUE = eps',
            'pgenerator_child.REFCELL = (n_cache_cell)',
            'pgenerator_child.KEY = (PINT 7)',
            'pgenerator_child.RETURN = eps',
            'pgenerator_child.DELEGATE = eps',
            '$generator_unused_send_tail(S, pgenclose.SITE, pframe_child.TODO)',
            '$generator_close_parked(S, pgenclose)',
            '~$generator_close_pending_init(S, pgenclose)',
            '$generator_close_enter_valid(S, pgenclose)',
            'S_no_park = $generator_set(S, n_child, pgenerator_child[.PARKED = eps])',
            '$heap_graph(S_no_park) = $heap_graph(S)',
            '~$generator_close_parked(S_no_park, pgenclose)',
            '$generator_parked_valid(S, pgenerator_child)',
            'pgenerator_wrong = pgenerator_child[.PARKED = (pgenerator_child.FUNCTION)]',
            'S_wrong_site = $generator_set(S, n_child, pgenerator_wrong)',
            '$heap_graph(S_wrong_site) = $heap_graph(S)',
            '~$generator_parked_valid(S_wrong_site, pgenerator_wrong)',
            '~$call_descriptors_valid(S_wrong_site)',
            '$node_children(S, HOBJECT n_child) = [HCELL n_cache_cell]',
            '$generator_close_frame_nodes(S, pframe_child) = [HCELL n_cache_cell]',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HCELL n_cache_cell) = 3',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("middle")) = eps',
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
            'S.ARRAYS[n_cache_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_live))]',
            '$object_name(S, n_live) = $ptascii("ReviewPendingLive21")',
            '$heap_owners($heap_graph(S), HARRAY n_cache_row) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_live) = 1',
            'S.EVENTS = ' + outputs(EVENTS[REF][:23]),
            *VALID, *BUDGET,
            'S_one.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_DONE pgenclose_done) :: ptask_tail*',
            'pgenrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cache_cell)]',
            'pgenrelease.PENDING = eps',
            'pgenclose_done = pgenclose[.FRAME = eps][.STAGE = CLOSE_FINISHED][.PENDING = eps]',
            'S_closed = $generator_set(S, n_child, pgenerator_child[.PHASE = GENERATOR_CLOSED][.PENDING_INIT = false][.PARKED = eps])',
            'S_one.OBJECTS = S_closed.OBJECTS',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_one), HCELL n_cache_cell) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_live) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[REF]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_live) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            'n_live <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'detached-pending-throw-preserves-copy-before-caller-search': {
        'source': ROWS[DETACHED]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_exception) :: (GENERATOR_PENDING_THROW pgeneratorpendingthrow) :: ptask_tail* '
                  '-- if pgeneratorpendingthrow.SOURCE.OBJECT = pgeneratorpendingthrow.LEAF '
                  '-- if pgeneratorpendingthrow.VALUE = POBJECT n_cache '
                  '-- if $object_name(S, n_cache) = $ptascii("ReviewPendingDetached21")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GENERATORINPUTS = eps', 'S.COMPLETION = NORMAL',
            'S.DESTRUCTION.OPERATIONS = eps', 'S.RESULT = KNOWN PNULL',
            'pgeneratorop = pgeneratorpendingthrow.SOURCE',
            'n_middle = pgeneratorop.OBJECT',
            'pgeneratorpendingthrow.LEAF = n_middle',
            'pgeneratorop.NAME = "throw"', 'pgeneratorop.LINE = 11',
            'pgeneratorop.ARGUMENTS = [POBJECT n_exception]',
            'pgeneratorop.LOOP = eps', '~pgeneratorop.ADVANCE',
            '~pgeneratorop.STARTPACK', '~pgeneratorop.BORROWED',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.PARKED = (pgeneratorpendingthrow.SITE)',
            'pgenerator_middle.FRAME = (pframe_middle)',
            'pframe_middle.ORIGIN = (pgeneratorpendingthrow.SITE)',
            'pframe_middle.HELD = eps', '$tasks_nodes(pframe_middle.TODO) = eps',
            'pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorpendingthrow.SITE n_child (PINT 23)) :: ptask_middle*',
            'pgenerator_middle.VALUE = eps', 'pgenerator_middle.REFCELL = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.SITE = pgeneratorpendingthrow.SITE',
            'pgeneratorfrom.INPUT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            '$generator_from_complete_valid(S, n_middle, pgeneratorpendingthrow.SITE, n_child, PINT 23)',
            '$generator_from_record_valid(S, n_middle, pgenerator_middle)',
            '$generator_parked_valid(S, pgenerator_middle)',
            '$generator_parked(S, n_middle, |S.OBJECTS|)',
            '$generator_pending_throw_leaf(S, n_middle, |S.OBJECTS|) = eps',
            'S_unparked = $generator_set(S, n_middle, pgenerator_middle[.PARKED = eps])',
            '$heap_graph(S_unparked) = $heap_graph(S)',
            '$generator_pending_throw_leaf(S_unparked, n_middle, |S.OBJECTS|) = (n_middle)',
            '~$generator_pending_throw_ready(S, pgeneratorop)',
            '$generator_pending_throw_valid(S, pgeneratorpendingthrow)',
            '$generator_pending_throw_discard(S, S.TODO[0]) = (pgeneratorpendingthrow)',
            '$call_task_valid(S, GENERATOR_PENDING_THROW pgeneratorpendingthrow)',
            '$task_nodes(GENERATOR_PENDING_THROW pgeneratorpendingthrow) = [HOBJECT n_cache]',
            '$generator_cached_value(S, n_middle, false) = POBJECT n_cache',
            '$generator_cached_value(S, n_middle, true) = PNULL',
            '$node_children(S, HOBJECT n_middle) = [HOBJECT n_cache]',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.RETURN = (PINT 23)',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$lookup(S_global.ENV, $ptascii("caught")) = eps',
            '$lookup(S_global.ENV, $ptascii("snapshot")) = (n_snapshot_cell)',
            '$lookup(S_global.ENV, $ptascii("exception")) = (n_exception_cell)',
            'S.STORE[n_snapshot_cell] = DEFINED (POBJECT n_cache)',
            'S.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.SITE = pgeneratorop.SITE])',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.LEAF = n_child])',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.SOURCE = pgeneratorop[.LINE = 0]])',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.SOURCE = pgeneratorop[.ARGUMENTS = [PINT 1]]])',
            'S.EVENTS = ' + outputs(EVENTS[DETACHED][:9]),
            *VALID, *BUDGET,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HOBJECT n_cache)]',
            'pdestructionoperation.SOURCE = GENERATOR_PENDING_THROW pgeneratorpendingthrow',
            'pdestructionoperation.PENDING = (n_exception)',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.NOGC = ({OPERAND KNOWN (POBJECT n_cache), PENDING true})',
            '$generator_pending_throw_here(S_one, pdestructionoperation)',
            '$generator_pending_throw_receipt(S_one, pdestructionoperation)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation)',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.GC = S.GC',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2',
            'S_two_budget.GC = S.GC',
            '$heap_owners($heap_graph(S_two_budget), HOBJECT n_cache) = 2',
            '~(n_cache <- S_two_budget.DESTRUCTION.CALLED)',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[DETACHED]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
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
