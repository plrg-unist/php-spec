#!/usr/bin/env python3
"""Reach reference-foreach parking and a real replacement-cache callback."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_reference_foreach_throw_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
DIRECT = 'generator-pending-reference-foreach-throw-temporary-wrapper'
REPLACE = 'generator-pending-reference-foreach-throw-sole-receiver-cache-replacement'
EVENTS = {
    DIRECT: ['P|','O|','M|','C|','V|','H|','1','|T|','CALLER|','SAME|',
             'NOPREV|','GET|','5','|','7','|','1','|','Z|','OUT|','J|',
             'MID|','CHILD|','E','A|','B|'],
    REPLACE: ['P|','O|','M|','C|','H|','T|','Z|','DROP|','J|','D|',
              'CALLER|','OTHER|','PREV|','E','A|','B|'],
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
    'pending-reference-loop-keeps-wrapper-and-item-alias-distinct': {
        'source': ROWS[DIRECT]['source'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_exception)])) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "throw"'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GC.ACTIVE = eps', 'S.GENERATORINPUTS = eps',
            'S.GENERATORLOOPRETAINED = eps', 'S.ORIGIN = (pgeneratorop.SITE)',
            'pgeneratorop.LINE = 8', 'pgeneratorop.ARGUMENTS = eps',
            '~pgeneratorop.ADVANCE', '~pgeneratorop.BORROWED',
            'n_middle = pgeneratorop.OBJECT',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.PENDING_INIT', 'pgenerator_middle.PARKED = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.CURRENT = eps',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            'pgenerator_child.PARKED = eps', 'pgenerator_child.DELEGATE = eps',
            'pgenerator_child.VALUE = (PINT 5)', 'pgenerator_child.KEY = (PINT 7)',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (porigin_yield)', 'pframe_child.HELD = eps',
            '$generator_unused_send_tail(S, porigin_yield, pframe_child.TODO)',
            '~$generator_input_tail(S, porigin_yield, pframe_child.TODO)',
            '$generator_foreach_saved(S, pgenerator_child, pframe_child) = (ptask_foreach)',
            'ptask_foreach = FOREACH_NEXT n_iterator (HCELL n_wrapper) statement (porigin_loop) z_loop',
            '$generator_foreach_reference_site(S, pgenerator_child, porigin_yield, porigin_loop)',
            '~$generator_foreach_site(S, pgenerator_child, porigin_yield, porigin_loop)',
            '$generator_foreach_reference_cell(S, n_wrapper)',
            'S.ITERATORS = [ITERATOR n_iterator n_array true pcursor*]',
            '$tasks_nodes(pframe_child.TODO) = [HCELL n_wrapper]',
            'S.STORE[n_wrapper] = DEFINED (PARRAY n_array)',
            'S_frame = $generator_frame_scope(S, pframe_child)',
            '$lookup(S_frame.ENV, $ptascii("item")) = (n_item)',
            'n_wrapper =/= n_item', 'n_item <- S.REFCELLS',
            'S.STORE[n_item] = DEFINED (POBJECT n_visited)',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_item), ENTRY (KINT 1) (DIRECT (POBJECT n_unvisited))]',
            '$object_name(S, n_visited) = $ptascii("ReferenceLoopA25")',
            '$object_name(S, n_unvisited) = $ptascii("ReferenceLoopB25")',
            '$node_children(S, HCELL n_wrapper) = [HARRAY n_array]',
            '$node_children(S, HARRAY n_array) = [HCELL n_item, HOBJECT n_unvisited]',
            '$node_children(S, HCELL n_item) = [HOBJECT n_visited]',
            '$heap_owners($heap_graph(S), HCELL n_wrapper) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HCELL n_item) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_visited) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_unvisited) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            'pgeneratorop_throw = pgeneratorop[.ARGUMENTS = [POBJECT n_exception]]',
            '$generator_pending_throw_ready(S, pgeneratorop_throw)',
            '$generator_pending_throw_leaf(S, n_middle, |S.OBJECTS|) = (n_child)',
            '$generator_pending_throw_leaf(S, n_middle, 0) = eps',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.LINE = 0])',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.ARGUMENTS = [PINT 1]])',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.BORROWED = true])',
            'S_unmarked = S[.REFCELLS = eps]',
            '$heap_graph(S_unmarked) = $heap_graph(S)',
            '~$generator_foreach_reference_cell(S_unmarked, n_wrapper)',
            '$generator_foreach_saved(S_unmarked, pgenerator_child, pframe_child) = eps',
            'S_mode = S[.ITERATORS = [ITERATOR n_iterator n_array false pcursor*]]',
            '$heap_graph(S_mode) = $heap_graph(S)',
            '$generator_foreach_saved(S_mode, pgenerator_child, pframe_child) = eps',
            '$generator_foreach_saved(S, pgenerator_child, pframe_child[.HELD = [HCELL n_wrapper]]) = eps',
            '$generator_foreach_saved(S, pgenerator_child, pframe_child[.TODO = pframe_child.TODO ++ [ptask_foreach]]) = eps',
            '$generator_foreach_saved(S, pgenerator_child, pframe_child[.TODO = DISCARD :: pframe_child.TODO]) = eps',
            'S.EVENTS = ' + outputs(EVENTS[DIRECT][:8]),
            *VALID, *BUDGET,
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]',
            'S_one.OBJECTS[n_child] = GENERATOR pgenerator_child[.PARKED = (porigin_yield)]',
            'S_one.GENERATORINPUTS = eps', 'S_one.GENERATORLOOPRETAINED = eps',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (GENERATOR_PENDING_THROW pgeneratorpendingthrow) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_middle)]',
            'pdestructionoperation.PENDING = (n_exception)',
            'pgeneratorpendingthrow.VALUE = PNULL',
            'pgeneratorpendingthrow.SOURCE = pgeneratorop_throw',
            'pgeneratorpendingthrow.LEAF = n_child',
            '$generator_pending_throw_carried(S_one, pgeneratorpendingthrow, S_one.TODO)',
            '$heap_owners($heap_graph(S_one), HCELL n_wrapper) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_item) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_visited) = 1',
            '$generator_parked_foreach_any(S_one, S_one.ALLOCATIONS)',
            'pconfigcall_gc = {SITE pgeneratorop.SITE, KIND INTRINSIC_GC_COLLECT, INDEX 0, SENT eps, NAMED false, OWNER eps, SELECTION eps, LINE pgeneratorop.LINE, PACKS eps}',
            'S_gc = S_one[.TODO = (CONFIG_INVOKE pconfigcall_gc) :: S_one.TODO]',
            '$heap_graph(S_gc) = $heap_graph(S_one)',
            'S_gc_stop = $gc_begin(S_gc, pconfigcall_gc)',
            'S_gc_stop.COMPLETION = UNSUPPORTED "parked Generator foreach collection"',
            'S_gc_stop[.COMPLETION = NORMAL] = S_gc',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[DIRECT]),
            'S_done.GENERATORINPUTS = eps',
            'S_done.GENERATORLOOPRETAINED = [pgeneratorloopretained]',
            'pgeneratorloopretained.OBJECT = n_child',
            'pgeneratorloopretained.SITE = porigin_yield',
            'pgeneratorloopretained.TASK = ptask_foreach',
            '$generator_foreach_retained_record(S_done, pgeneratorloopretained)',
            '$generator_foreach_retained_nodes(S_done.GENERATORLOOPRETAINED) = [HCELL n_wrapper]',
            '$generator_foreach_reference_cell(S_done, n_wrapper)',
            'S_done.STORE[n_wrapper] = DEFINED (PARRAY n_array)',
            '$heap_owners($heap_graph(S_done), HCELL n_wrapper) = 1',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HCELL n_item) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_visited) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_unvisited) = 1',
            'n_visited <- S_done.DESTRUCTION.CALLED', 'n_unvisited <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
            '$iterator_lookup(S_done.ITERATORS, n_iterator) = eps',
        ],
    },
    'retained-wrapper-survives-real-cache-replacement-callback': {
        'source': ROWS[REPLACE]['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) '
                  '-- if $object_name(S, n_cache) = $ptascii("ReferenceLoopCache25b") '
                  '-- if S.FRAMES = pframe_caller :: pframe_tail* '
                  '-- if pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_return* '
                  '-- if pdestructorcall.OPERATION = (pdestructionoperation) '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_PENDING_THROW pgeneratorpendingthrow'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.GENERATORINPUTS = eps',
            'S.GENERATORLOOPRETAINED = [pgeneratorloopretained]',
            'pgeneratorloopretained.OBJECT = pgeneratorpendingthrow.LEAF',
            'pgeneratorloopretained.SITE = pgeneratorpendingthrow.SITE',
            'pgeneratorloopretained.TASK = FOREACH_NEXT n_iterator (HCELL n_wrapper) statement (porigin_loop) z_loop',
            '$generator_foreach_retained_record(S, pgeneratorloopretained)',
            '$generator_foreach_retained_nodes(S.GENERATORLOOPRETAINED) = [HCELL n_wrapper]',
            '$generator_foreach_reference_cell(S, n_wrapper)',
            'S.STORE[n_wrapper] = DEFINED (PARRAY n_array)',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_item), ENTRY (KINT 1) (DIRECT (POBJECT n_unvisited))]',
            'S.STORE[n_item] = DEFINED (POBJECT n_visited)', 'n_item <- S.REFCELLS',
            '$object_name(S, n_visited) = $ptascii("ReferenceLoopVisited25b")',
            '$object_name(S, n_unvisited) = $ptascii("ReferenceLoopUnvisited25b")',
            '$heap_owners($heap_graph(S), HCELL n_wrapper) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HCELL n_item) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_visited) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_unvisited) = 1',
            '~(n_visited <- S.DESTRUCTION.CALLED)', '~(n_unvisited <- S.DESTRUCTION.CALLED)',
            'pcallcontext.INSTANCE = eps', 'pdestructorcall.OBJECT = n_cache',
            'pgeneratorpendingthrow.VALUE = POBJECT n_cache',
            'pgeneratorop = pgeneratorpendingthrow.SOURCE',
            'pgeneratorop.ARGUMENTS = [POBJECT n_exception]',
            'pgeneratorop.NAME = "throw"', 'pgeneratorop.LINE = 10',
            'n_middle = pgeneratorop.OBJECT', 'n_child = pgeneratorpendingthrow.LEAF',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_middle.PHASE = GENERATOR_CLOSED', 'pgenerator_middle.PARKED = eps',
            'pgenerator_child.PHASE = GENERATOR_CLOSED', 'pgenerator_child.PARKED = eps',
            '~((HOBJECT n_middle) <- S.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            'pdestructionoperation.CALLER = eps',
            'pdestructorcall.CALLER = eps', 'pframe_caller.CONTEXT = eps',
            'pdestructionoperation.CALLER =/= S.CURRENT',
            'pdestructionoperation.PENDING = (n_exception)',
            'pdestructorcall.PENDING = (n_exception)',
            'pdestructionoperation.NOGC = ({OPERAND KNOWN (POBJECT n_cache), PENDING false})',
            'pdestructionoperation.CLEANUP = eps',
            'pdestructionoperation.ORIGIN = (pgeneratorop.SITE)',
            'pframe_caller.ORIGIN = (pgeneratorop.SITE)',
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) <- pframe_caller.TODO',
            '$generator_pending_throw_valid(S, pgeneratorpendingthrow)',
            '~$generator_pending_throw_here(S, pdestructionoperation)',
            '$generator_pending_throw_frames(S, pdestructionoperation, S.FRAMES)',
            '$generator_pending_throw_receipt(S, pdestructionoperation)',
            '$destructor_operation_live(S, pdestructionoperation)',
            '~$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_context_valid(S, pcallcontext)',
            '$gc_operation_metadata_valid(S, pdestructionoperation)',
            '~$generator_pending_throw_receipt(S, pdestructionoperation[.CALLER = S.CURRENT])',
            '~$gc_operation_metadata_valid(S, pdestructionoperation[.ORIGIN = eps])',
            '~$generator_pending_throw_receipt(S, pdestructionoperation[.SOURCE = GENERATOR_PENDING_THROW pgeneratorpendingthrow[.SOURCE = pgeneratorop[.LINE = 0]]])',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            'S.EVENTS = ' + outputs(EVENTS[REPLACE][:9]),
            *VALID, *BUDGET,
            '$generator_pending_throw_receipt(S_one, pdestructionoperation)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation)',
            'S_one.GENERATORINPUTS = eps',
            'S_one.GENERATORLOOPRETAINED = S.GENERATORLOOPRETAINED',
            '$heap_owners($heap_graph(S_one), HCELL n_wrapper) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[REPLACE]),
            'S_done.GENERATORINPUTS = eps',
            'S_done.GENERATORLOOPRETAINED = S.GENERATORLOOPRETAINED',
            '$heap_owners($heap_graph(S_done), HCELL n_wrapper) = 1',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HCELL n_item) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_visited) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_unvisited) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            'n_visited <- S_done.DESTRUCTION.CALLED', 'n_unvisited <- S_done.DESTRUCTION.CALLED',
            'n_cache <- S_done.DESTRUCTION.CALLED',
        ],
    },
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in INPUTS}
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
    stable = before == {str(path): digest(path) for path in INPUTS}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs=before, author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
