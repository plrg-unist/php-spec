#!/usr/bin/env python3
"""Reach parked foreach container transfer and a later embedded-cell write."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_foreach_throw_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
COW = 'generator-pending-foreach-throw-review-source-array-cow'
CELL = 'generator-pending-foreach-throw-review-embedded-reference-rebind'
EVENTS = {
    COW: ['P|', 'O|', 'M|', 'C|', 'V|', 'H|', 'W|', 'CNEW|', 'DNEW|',
          'DROP|', 'CALLER|', '1', '|', '1', '|', 'GET|', '5', '|', '7', '|',
          '1', '|', 'Z|', 'OUT|', 'J|', 'MID|', 'CHILD|', 'E', 'A|', 'B|'],
    CELL: ['P|', 'O|', 'M|', 'C|', 'V|', 'H|', 'CALLER|', '1', '|', '1', '|',
           'GET|', '11', '|', '3', '|', '1', '|', 'Z|', 'OUT|', 'J|', 'MID|',
           'CHILD|', 'A|', 'WRITE|', 'UNSET|', 'E', 'CNEW|', 'B|'],
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
    'parked-cow-foreach-close-transfers-array-without-retiring-it': {
        'source': ROWS[COW]['source'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
                  '-- if $generator_close_parked(S, pgenclose) '
                  '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator_child '
                  '-- if pgenclose.FRAME = (pframe_child) '
                  '-- if $generator_foreach_saved(S, pgenerator_child, pframe_child) = (ptask_foreach)'),
        'checks': [
            'n_child = pgenclose.OBJECT',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'pgenerator_child.PHASE = GENERATOR_CLOSING',
            'pgenerator_child.FRAME = eps', '~pgenerator_child.PENDING_INIT',
            'pgenerator_child.PARKED = (porigin_yield)',
            'pgenerator_child.VALUE = (PINT 5)',
            'pgenerator_child.KEY = (PINT 7)', 'pgenerator_child.REFCELL = eps',
            'pgenerator_child.DELEGATE = eps', 'pgenerator_child.RETURN = eps',
            'pgenclose.STAGE = CLOSE_QUEUED', 'pgenclose.PENDING = eps',
            'pgenclose.SITE = porigin_yield', 'pframe_child.ORIGIN = (porigin_yield)',
            'pframe_child.HELD = eps',
            'ptask_foreach = FOREACH_NEXT n_iterator (HARRAY n_array) statement (porigin_loop) z_loop',
            '$generator_foreach_site(S, pgenerator_child, porigin_yield, porigin_loop)',
            '$goto_marker_valid(S, ptask_foreach)',
            '$iterator_lookup(S.ITERATORS, n_iterator) = (ITERATOR n_iterator n_array false pcursor*)',
            'S.NEXTITER = $(n_iterator + 1)',
            '$tasks_nodes(pframe_child.TODO) = [HARRAY n_array]',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_visited)), ENTRY (KINT 1) (DIRECT (POBJECT n_unvisited))]',
            '$object_name(S, n_visited) = $ptascii("ReviewParkedLoopOldA23")',
            '$object_name(S, n_unvisited) = $ptascii("ReviewParkedLoopOldB23")',
            'S_frame = $generator_frame_scope(S, pframe_child)',
            '$lookup(S_frame.ENV, $ptascii("item")) = (n_item_cell)',
            'S.STORE[n_item_cell] = DEFINED (POBJECT n_visited)',
            '~(n_item_cell <- S.REFCELLS)',
            '$lookup(S_frame.ENV, $ptascii("items")) = eps',
            '$generator_close_frame_nodes(S, pframe_child) = [HCELL n_item_cell, HARRAY n_array]',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_visited) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_unvisited) = 1',
            '~(n_visited <- S.DESTRUCTION.CALLED)',
            '~(n_unvisited <- S.DESTRUCTION.CALLED)',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("items")) = eps',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("middle")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$lookup(S_global.ENV, $ptascii("exception")) = (n_exception_cell)',
            '$lookup(S_global.ENV, $ptascii("caught")) = (n_caught_cell)',
            'S.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
            'S.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            'pgeneratorloopretained = {OBJECT n_child, SITE porigin_yield, TASK ptask_foreach}',
            '~$generator_foreach_retained_record(S, pgeneratorloopretained)',
            '$generator_foreach_retained_nodes([pgeneratorloopretained]) = [HARRAY n_array]',
            'pframe_trimmed = pframe_child[.TODO = $generator_foreach_drop(pframe_child.TODO, ptask_foreach)]',
            '$tasks_nodes(pframe_trimmed.TODO) = eps',
            '$generator_close_frame_nodes(S, pframe_trimmed) = [HCELL n_item_cell]',
            'S.EVENTS = ' + outputs(EVENTS[COW][:EVENTS[COW].index('MID|') + 1]),
            *VALID, *BUDGET,
            'S_one.GENERATORLOOPRETAINED = [pgeneratorloopretained]',
            '$generator_foreach_retained_record(S_one, pgeneratorloopretained)',
            '$generator_foreach_retained_valid(S_one, S_one.GENERATORLOOPRETAINED)',
            '$generator_foreach_retained_nodes(S_one.GENERATORLOOPRETAINED) = [HARRAY n_array]',
            'S_one.ITERATORS = eps', '$iterator_lookup(S_one.ITERATORS, n_iterator) = eps',
            'S_one.NEXTITER = S.NEXTITER',
            'S_one.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_DONE pgenclose_done) :: ptask_tail*',
            'pgenrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_item_cell)]',
            'pgenrelease.PENDING = eps', 'pgenrelease.VALUE = S.RESULT',
            'pgenrelease.BASE = S.BASE', 'pgenrelease.COMPLETION = NORMAL',
            'pgenclose_done = pgenclose[.FRAME = eps][.STAGE = CLOSE_FINISHED][.PENDING = eps]',
            'S_expected = $generator_set(S, n_child, pgenerator_child[.PHASE = GENERATOR_CLOSED][.PENDING_INIT = false][.PARKED = eps])',
            'S_one.OBJECTS = S_expected.OBJECTS',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_count(HARRAY n_array, $machine_roots(S_one)) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_visited) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_unvisited) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2',
            '~(n_visited <- S_one.DESTRUCTION.CALLED)',
            '~(n_unvisited <- S_one.DESTRUCTION.CALLED)',
            'pgeneratorloopretained_bad = pgeneratorloopretained[.TASK = FOREACH_NEXT n_iterator (HARRAY n_array) statement (porigin_loop) 0]',
            'S_bad = S_one[.GENERATORLOOPRETAINED = [pgeneratorloopretained_bad]]',
            '$heap_graph(S_bad) = $heap_graph(S_one)', '$heap_valid($heap_graph(S_bad))',
            '~$generator_foreach_retained_record(S_bad, pgeneratorloopretained_bad)',
            '~$call_descriptors_valid(S_bad)',
            '~$generator_foreach_retained_record(S_one, pgeneratorloopretained[.SITE = porigin_loop])',
            '~$generator_foreach_retained_valid(S_one, [pgeneratorloopretained, pgeneratorloopretained])',
            *DONE,
            'S_done.GENERATORLOOPRETAINED = S_one.GENERATORLOOPRETAINED',
            '$generator_foreach_retained_valid(S_done, S_done.GENERATORLOOPRETAINED)',
            'S_done.EVENTS = ' + outputs(EVENTS[COW]),
            'S_done.ITERATORS = eps',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_visited) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_unvisited) = 1',
            'n_visited <- S_done.DESTRUCTION.CALLED',
            'n_unvisited <- S_done.DESTRUCTION.CALLED',
            '(HOBJECT n_visited) <- S_done.ALLOCATIONS',
            '(HOBJECT n_unvisited) <- S_done.ALLOCATIONS',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        ],
    },
    'retained-foreach-reference-follows-a-real-global-write': {
        'source': ROWS[CELL]['source'],
        'stage': ('S.TODO = (WRITE_NAME n_name* z_write) :: ptask_tail* '
                  '-- if n_name* = $ptascii("slot") '
                  '-- if S.GENERATORLOOPRETAINED = [pgeneratorloopretained] '
                  '-- if S.RESULT = KNOWN (POBJECT n_new) '
                  '-- if $object_name(S, n_new) = $ptascii("ReviewParkedLoopCellC23")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps',
            'S.GENERATORINPUTS = eps', 'S.ITERATORS = eps',
            'pgeneratorloopretained.OBJECT = n_child',
            'pgeneratorloopretained.SITE = porigin_yield',
            'pgeneratorloopretained.TASK = FOREACH_NEXT n_iterator (HARRAY n_array) statement (porigin_loop) z_loop',
            '$generator_foreach_retained_record(S, pgeneratorloopretained)',
            '$generator_foreach_retained_valid(S, S.GENERATORLOOPRETAINED)',
            '$generator_foreach_retained_nodes(S.GENERATORLOOPRETAINED) = [HARRAY n_array]',
            '$heap_count(HARRAY n_array, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_shared), ENTRY (KINT 1) (DIRECT (POBJECT n_unvisited))]',
            '$object_name(S, n_unvisited) = $ptascii("ReviewParkedLoopCellB23")',
            'n_shared <- S.REFCELLS', '(HCELL n_shared) <- S.ALLOCATIONS',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, n_name*) = (n_shared)',
            'S.STORE[n_shared] = DEFINED (POBJECT n_old)',
            '$object_name(S, n_old) = $ptascii("ReviewParkedLoopCellA23")',
            '$node_children(S, HARRAY n_array) = [HCELL n_shared, HOBJECT n_unvisited]',
            '$heap_owners($heap_graph(S), HCELL n_shared) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_new) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_unvisited) = 1',
            '~(n_old <- S.DESTRUCTION.CALLED)',
            '~(n_new <- S.DESTRUCTION.CALLED)',
            '~(n_unvisited <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED', 'pgenerator_child.FRAME = eps',
            'pgenerator_child.PARKED = eps',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$node_children(S, HOBJECT n_child) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$lookup(S_global.ENV, $ptascii("middle")) = eps',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$generator_foreach_retained_seen([pgeneratorloopretained], n_child, n_iterator)',
            '~$generator_foreach_retained_valid(S, [pgeneratorloopretained, pgeneratorloopretained])',
            'S_bad = S[.GENERATORLOOPRETAINED = [pgeneratorloopretained[.SITE = porigin_loop]]]',
            '$heap_graph(S_bad) = $heap_graph(S)', '$heap_valid($heap_graph(S_bad))',
            '~$generator_foreach_retained_valid(S_bad, S_bad.GENERATORLOOPRETAINED)',
            '~$call_descriptors_valid(S_bad)',
            'S.EVENTS = ' + outputs(EVENTS[CELL][:EVENTS[CELL].index('CHILD|') + 1]),
            *VALID, *BUDGET,
            'S_one.GENERATORLOOPRETAINED = S.GENERATORLOOPRETAINED',
            '$generator_foreach_retained_valid(S_one, S_one.GENERATORLOOPRETAINED)',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.OBJECTS = S.OBJECTS',
            'S_expected = S[.STORE[n_shared] = DEFINED (POBJECT n_new)]',
            'S_one.STORE = S_expected.STORE', 'S_one.ENV = S.ENV',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.ITERATORS = eps',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]',
            'pdestructionrelease.USER', 'pdestructionrelease.CALLER = eps',
            'pdestructionoperation.SOURCE = WRITE_NAME n_name* z_write',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.COMPLETION = NORMAL', 'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.CLEANUP = eps', 'pdestructionoperation.NOGC = eps',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_shared) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_new) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_unvisited) = 1',
            '~(n_old <- S_one.DESTRUCTION.CALLED)',
            *DONE,
            'S_done.GENERATORLOOPRETAINED = S.GENERATORLOOPRETAINED',
            '$generator_foreach_retained_valid(S_done, S_done.GENERATORLOOPRETAINED)',
            'S_done.EVENTS = ' + outputs(EVENTS[CELL]),
            'S_done.STORE[n_shared] = DEFINED (POBJECT n_new)',
            '$node_children(S_done, HARRAY n_array) = [HCELL n_shared, HOBJECT n_unvisited]',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HCELL n_shared) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_new) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_unvisited) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 0',
            '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
            'n_old <- S_done.DESTRUCTION.CALLED',
            'n_new <- S_done.DESTRUCTION.CALLED',
            'n_unvisited <- S_done.DESTRUCTION.CALLED',
            '(HOBJECT n_new) <- S_done.ALLOCATIONS',
            '(HOBJECT n_unvisited) <- S_done.ALLOCATIONS',
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
