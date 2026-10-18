#!/usr/bin/env python3
"""Reach pending owning-foreach invocation and late nested-Generator store close."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_foreach_throw_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
DIRECT = 'generator-pending-foreach-throw-temporary-array-and-local-close'
NESTED = 'generator-pending-foreach-throw-sole-receiver-and-nested-generator'
EVENTS = {
    DIRECT: ['P|','O|','M|','C|','H|','1','|T|','CALLER|','SAME|','NOPREV|',
             'GET|','1','|','5','|','0','|','Z|','J|','D|','CLOSED|','E','A|','B|'],
    NESTED: ['P|','O|','M|','C|','N|','T|','H|','Z|','DROP|','J|','D|',
             'CALLER|','SAME|','NOPREV|','E','I|','B|'],
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
    'S_done.HELD = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
]

CASES = {
    'pending-foreach-throw-keeps-live-loop-until-physical-close': {
        'source': ROWS[DIRECT]['source'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_exception)])) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "throw"'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GC.ACTIVE = eps', 'S.GENERATORINPUTS = eps',
            'S.GENERATORLOOPRETAINED = eps',
            'S.ORIGIN = (pgeneratorop.SITE)', 'pgeneratorop.LINE = 9',
            'pgeneratorop.ARGUMENTS = eps', '~pgeneratorop.ADVANCE',
            'pgeneratorop.LOOP = eps', '~pgeneratorop.STARTPACK', '~pgeneratorop.BORROWED',
            'n_middle = pgeneratorop.OBJECT',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.PENDING_INIT', 'pgenerator_middle.PARKED = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.CURRENT = eps',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            '~pgenerator_child.PENDING_INIT', 'pgenerator_child.PARKED = eps',
            'pgenerator_child.DELEGATE = eps', 'pgenerator_child.VALUE = (PINT 5)',
            'pgenerator_child.KEY = (PINT 0)', 'pgenerator_child.REFCELL = eps',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (porigin_yield)', 'pframe_child.HELD = eps',
            '$generator_unused_send_tail(S, porigin_yield, pframe_child.TODO)',
            '$generator_foreach_saved(S, pgenerator_child, pframe_child) = (ptask_foreach)',
            'ptask_foreach = FOREACH_NEXT n_iterator (HARRAY n_array) statement (porigin_loop) z',
            '$tasks_nodes(pframe_child.TODO) = [HARRAY n_array]',
            '$generator_foreach_site(S, pgenerator_child, porigin_yield, porigin_loop)',
            '$goto_marker_valid(S, ptask_foreach)',
            '$iterator_lookup(S.ITERATORS, n_iterator) = (piterator)',
            'piterator = ITERATOR n_iterator n_array false pcursor*',
            '$generator_foreach_drop(pframe_child.TODO, ptask_foreach) = ptask_trimmed*',
            '$tasks_nodes(ptask_trimmed*) = eps',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_visited)), ENTRY (KINT 1) (DIRECT (POBJECT n_unvisited))]',
            '$object_name(S, n_visited) = $ptascii("PendingForeachVisited23")',
            '$object_name(S, n_unvisited) = $ptascii("PendingForeachUnvisited23")',
            'pframe_child.LOCALS = (psymboltable)',
            '$lookup(psymboltable.ENV, $ptascii("local")) = (n_local_cell)',
            'S.STORE[n_local_cell] = DEFINED (POBJECT n_local)',
            '$object_name(S, n_local) = $ptascii("PendingForeachLocal23")',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_visited) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_unvisited) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_local) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            '$heap_count(HARRAY n_array, $node_children(S, HOBJECT n_child)) = 1',
            '$heap_count(HARRAY n_array, $machine_roots(S)) = 0',
            'pgeneratorop_throw = pgeneratorop[.ARGUMENTS = [POBJECT n_exception]]',
            '$generator_pending_throw_ready(S, pgeneratorop_throw)',
            '$generator_pending_throw_leaf(S, n_middle, |S.OBJECTS|) = (n_child)',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.LINE = 0])',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.BORROWED = true])',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.ARGUMENTS = [PINT 1]])',
            'S_wrong = $generator_set(S, n_child, pgenerator_child[.FRAME = (pframe_child[.TODO = $generator_foreach_drop(pframe_child.TODO, ptask_foreach) ++ [FOREACH_NEXT n_iterator (HARRAY n_array) statement (porigin_yield) z]])])',
            '$heap_graph(S_wrong) = $heap_graph(S)', '$heap_valid($heap_graph(S_wrong))',
            '$generator_foreach_saved(S_wrong, pgenerator_child, pframe_child[.TODO = $generator_foreach_drop(pframe_child.TODO, ptask_foreach) ++ [FOREACH_NEXT n_iterator (HARRAY n_array) statement (porigin_yield) z]]) = eps',
            '~$generator_pending_throw_ready(S_wrong, pgeneratorop_throw)',
            '~$call_descriptors_valid(S_wrong)',
            '$generator_foreach_saved(S, pgenerator_child, pframe_child[.TODO = pframe_child.TODO ++ [ptask_foreach]]) = eps',
            '$generator_foreach_saved(S, pgenerator_child, pframe_child[.HELD = [HOBJECT n_local]]) = eps',
            'S.EVENTS = ' + outputs(EVENTS[DIRECT][:7]),
            *VALID, *BUDGET,
            'S_one.GENERATORLOOPRETAINED = eps', 'S_one.GENERATORINPUTS = eps',
            'S_one.ITERATORS = S.ITERATORS',
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]',
            'S_one.OBJECTS[n_child] = GENERATOR pgenerator_child[.PARKED = (porigin_yield)]',
            '$generator_parked_foreach_any(S_one, S_one.ALLOCATIONS)',
            '~$generator_parked_foreach_any(S, S.ALLOCATIONS)',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (GENERATOR_PENDING_THROW pgeneratorpendingthrow) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_middle)]',
            'pdestructionoperation.PENDING = (n_exception)',
            'pgeneratorpendingthrow.VALUE = PINT 5',
            'pgeneratorpendingthrow.LEAF = n_child', 'pgeneratorpendingthrow.SITE = porigin_yield',
            'pgeneratorpendingthrow.SOURCE = pgeneratorop_throw',
            '$generator_pending_throw_carried(S_one, pgeneratorpendingthrow, S_one.TODO)',
            'pconfigcall_gc = {SITE pgeneratorop.SITE, KIND INTRINSIC_GC_COLLECT, INDEX 0, SENT eps, NAMED false, OWNER eps, SELECTION eps, LINE pgeneratorop.LINE, PACKS eps}',
            'S_gc = S_one[.TODO = (CONFIG_INVOKE pconfigcall_gc) :: S_one.TODO]',
            '$heap_graph(S_gc) = $heap_graph(S_one)',
            'S_gc_stop = $gc_begin(S_gc, pconfigcall_gc)',
            'S_gc_stop.COMPLETION = UNSUPPORTED "parked Generator foreach collection"',
            'S_gc_stop[.COMPLETION = NORMAL] = S_gc',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.FRAMES = S.FRAMES', 'S_one.GC = S.GC',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_visited) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_unvisited) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_local) = 1',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[DIRECT]),
            'S_done.GENERATORLOOPRETAINED = [pgeneratorloopretained]',
            'pgeneratorloopretained.OBJECT = n_child',
            'pgeneratorloopretained.SITE = porigin_yield', 'pgeneratorloopretained.TASK = ptask_foreach',
            '$generator_foreach_retained_record(S_done, pgeneratorloopretained)',
            '$generator_foreach_retained_nodes(S_done.GENERATORLOOPRETAINED) = [HARRAY n_array]',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_visited) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_unvisited) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_local) = 0',
            'n_visited <- S_done.DESTRUCTION.CALLED', 'n_unvisited <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
            '$iterator_lookup(S_done.ITERATORS, n_iterator) = eps',
            '~$generator_foreach_retained_valid(S_done, [pgeneratorloopretained, pgeneratorloopretained])',
            '~$generator_foreach_retained_record(S_done, pgeneratorloopretained[.TASK = FOREACH_NEXT n_iterator (HARRAY n_array) statement (porigin_loop) 0])',
            '~$generator_foreach_retained_record(S_done, pgeneratorloopretained[.OBJECT = n_middle])',
        ],
    },
    'retained-loop-nested-generator-closes-in-object-store': {
        'source': ROWS[NESTED]['source'],
        'stage': ('S.TODO = [DESTRUCTOR_STORE] '
                  '-- if S.GENERATORLOOPRETAINED = [pgeneratorloopretained] '
                  '-- if $destructor_handle(S, S.DESTRUCTION.INDEX, 0) = (n_nested) '
                  '-- if S.OBJECTS[n_nested] = GENERATOR pgenerator_nested '
                  '-- if $function_at($all_functions(S), pgenerator_nested.FUNCTION) = (pfunction_nested) '
                  '-- if pfunction_nested.NAME = $ptascii("pendingForeachNested23b")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ORIGIN = eps', 'S.ACTIVEFIBER = eps',
            'S.GENERATORINPUTS = eps', 'S.ITERATORS = eps',
            'S.DESTRUCTION.PHASE = DESTRUCTION_STORE',
            'pgeneratorloopretained.TASK = FOREACH_NEXT n_iterator (HARRAY n_array) statement (porigin_loop) z',
            'n_child = pgeneratorloopretained.OBJECT',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED', 'pgenerator_child.PARKED = eps',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$generator_foreach_retained_record(S, pgeneratorloopretained)',
            '$generator_foreach_retained_nodes(S.GENERATORLOOPRETAINED) = [HARRAY n_array]',
            '$heap_count(HOBJECT n_child, $generator_foreach_retained_nodes(S.GENERATORLOOPRETAINED)) = 0',
            '$heap_count(HARRAY n_array, $machine_roots(S)) = 1',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload)), ENTRY (KINT 1) (DIRECT (POBJECT n_nested))]',
            '$object_name(S, n_payload) = $ptascii("PendingForeachPayload23b")',
            'pgenerator_nested.PHASE = GENERATOR_PAUSED', 'pgenerator_nested.PARKED = eps',
            'pgenerator_nested.FIRST', '~pgenerator_nested.PENDING_INIT',
            'pgenerator_nested.VALUE = (PINT 9)', 'pgenerator_nested.KEY = (PINT 0)',
            'pgenerator_nested.FRAME = (pframe_nested)', 'pgenerator_nested.DELEGATE = eps',
            '$generator_request_frame_valid(S, pgenerator_nested)',
            '$generator_request_store_ready(S, n_nested)',
            '~$generator_foreach_retained_record(S, pgeneratorloopretained[.OBJECT = n_nested])',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_nested) = 1',
            '~(n_nested <- S.DESTRUCTION.CALLED)', '~(n_payload <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = ' + outputs(EVENTS[NESTED][:15]),
            *VALID, *BUDGET,
            'S_one.GENERATORLOOPRETAINED = S.GENERATORLOOPRETAINED',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.FRAMES = S.FRAMES',
            'S_one.DESTRUCTION.INDEX = $(S.DESTRUCTION.INDEX + 1)',
            'n_nested <- S_one.DESTRUCTION.CALLED', '~(n_payload <- S_one.DESTRUCTION.CALLED)',
            'S_one.OBJECTS[n_nested] = GENERATOR pgenerator_nested[.FRAME = eps][.PHASE = GENERATOR_CLOSING]',
            'S_one.TODO = [GENERATOR_CLOSE_RELEASE pgenrelease_input, GENERATOR_CLOSE_ENTER pgenclose, GENERATOR_CLOSE_RELEASE pgenrelease_tail, DESTRUCTOR_STORE]',
            'pgenrelease_input.JOBS = eps', 'pgenrelease_tail.JOBS = eps',
            'pgenclose.OBJECT = n_nested', 'pgenclose.FRAME = (pframe_nested)',
            'pgenclose.STORE = (S.DESTRUCTION.INDEX)',
            'pgenclose.STAGE = CLOSE_QUEUED', 'pgenclose.PENDING = eps',
            '$generator_request_store_valid(S_one, pgenclose)',
            '$generator_close_enter_valid(S_one, pgenclose)',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_nested) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[NESTED]),
            'S_done.GENERATORLOOPRETAINED = S.GENERATORLOOPRETAINED',
            '$generator_foreach_retained_record(S_done, pgeneratorloopretained)',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_nested) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 1',
            'S_done.OBJECTS[n_nested] = GENERATOR pgenerator_nested_done',
            'pgenerator_nested_done.PHASE = GENERATOR_CLOSED',
            'n_nested <- S_done.DESTRUCTION.CALLED', 'n_payload <- S_done.DESTRUCTION.CALLED',
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
