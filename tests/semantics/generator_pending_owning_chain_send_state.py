#!/usr/bin/env python3
"""Reach ancestor SEND refresh and its result after Generator retirement."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_owning_chain_send_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
CONSUME = 'generator-pending-owning-chain-send-refresh-and-real-consumption'
DROP = 'generator-pending-owning-chain-send-argument-retires-chain-before-used-cache-drop'
EVENTS = {
    CONSUME: ['P|','O|','U|','M|','C|','L|','H|','S|','ARG|','RETURN|','9','|',
              '1','|','1','|','N|','BODY|','1','|','R|','DROP|','CURRENT|','31','|',
              '1','|','N2|','TAIL|','J|','UPPER|','29','|','K|','OUTER|','29','|',
              'F|','DONE|','1','|','E'],
    DROP: ['P|','O|','U|','M|','C|','L|','H|','1','|','S|','ARG|','F|',
           'CLEARED|','K|','CALLER|','1','|','D|','DROPPED|','E','R|'],
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
    'ancestor-send-refreshes-the-owning-return-without-consuming-it': {
        'source': ROWS[CONSUME]['source'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "send"'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GC.ACTIVE = eps', 'S.HELD = eps', 'S.LITERALREFDEBTS = eps',
            'S.GENERATORRETURNRETAINED = eps', 'S.GENERATORINPUTS = eps',
            'S.GENERATORLOOPRETAINED = eps',
            'S.ORIGIN = (pgeneratorop.SITE)', 'S.RESULT = KNOWN PNULL',
            'pgeneratorop.LINE = 10', 'pgeneratorop.ARGUMENTS = eps',
            'pgeneratorop.LOOP = eps', '~pgeneratorop.BORROWED',
            '~pgeneratorop.STARTPACK', '~pgeneratorop.ADVANCE',
            'n_upper = pgeneratorop.OBJECT',
            'S.OBJECTS[n_upper] = GENERATOR pgenerator_upper',
            'pgenerator_upper.PHASE = GENERATOR_DELEGATING',
            'pgenerator_upper.PENDING_INIT', '~pgenerator_upper.FIRST',
            'pgenerator_upper.PARKED = eps',
            'pgenerator_upper.DELEGATE = (pgeneratorfrom_upper)',
            'pgeneratorfrom_upper.INPUT = (POBJECT n_middle)',
            'pgeneratorfrom_upper.ACQUISITION = eps',
            'pgeneratorfrom_upper.CURRENT = eps', 'pgeneratorfrom_upper.POSITION = 1',
            'pgenerator_upper.FRAME = (pframe_upper)',
            'pframe_upper.HELD = eps', '$tasks_nodes(pframe_upper.TODO) = eps',
            '$generator_from_record_valid(S, n_upper, pgenerator_upper)',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.PENDING_INIT', '~pgenerator_middle.FIRST',
            'pgenerator_middle.PARKED = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)',
            'pgeneratorfrom_middle.INPUT = (POBJECT n_child)',
            'pgeneratorfrom_middle.ACQUISITION = eps',
            'pgeneratorfrom_middle.CURRENT = eps', 'pgeneratorfrom_middle.POSITION = 1',
            'pgenerator_middle.FRAME = (pframe_middle)',
            'pframe_middle.HELD = eps',
            'pframe_middle.ORIGIN = (pgeneratorfrom_middle.SITE)',
            'pframe_middle.TODO = (GENERATOR_FROM_NEXT n_middle pgeneratorfrom_middle.SITE) :: ptask_used_tail*',
            '$generator_input_tail(S, pgeneratorfrom_middle.SITE, ptask_used_tail*)',
            '$tasks_nodes(ptask_used_tail*) = eps',
            '$generator_from_record_valid(S, n_middle, pgenerator_middle)',
            '~$generator_return_waiting(S, n_middle)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED', 'pgenerator_child.FRAME = eps',
            'pgenerator_child.VALUE = (PINT 9)',
            'pgenerator_child.RETURN = (POBJECT n_return)',
            '(HOBJECT n_child) <- S.ALLOCATIONS',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            'n_upper =/= n_middle', 'n_middle =/= n_child', 'n_upper =/= n_child',
            '$object_name(S, n_return) = $ptascii("PendingChainReturn31")',
            '$object_name(S, n_argument) = $ptascii("PendingChainArgument31")',
            '$heap_owners($heap_graph(S), HOBJECT n_return) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_upper) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 2',
            '$node_children(S, HOBJECT n_upper) = [HOBJECT n_middle]',
            '$node_children(S, HOBJECT n_middle) = [HOBJECT n_child]',
            '$heap_count(HOBJECT n_return, $node_children(S, HOBJECT n_child)) = 1',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = (n_outer_cell)',
            'S.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)',
            'S.OBJECTS[n_outer] = GENERATOR pgenerator_outer',
            '~pgenerator_outer.PENDING_INIT', 'pgenerator_outer.FIRST',
            'pgenerator_outer.DELEGATE = (pgeneratorfrom_outer)',
            'pgeneratorfrom_outer.INPUT = (POBJECT n_upper)',
            '$heap_owners($heap_graph(S), HOBJECT n_outer) = 1',
            'pgeneratorop_send = pgeneratorop[.ARGUMENTS = [POBJECT n_argument]]',
            '$generator_operation_valid(S, pgeneratorop_send)',
            '$generator_pending_resume(S, pgeneratorop_send)',
            '$generator_pending_return_leaf(S, n_upper, $(|S.OBJECTS| + 1)) = eps',
            '$generator_pending_detached_send(S, pgeneratorop_send)',
            '~$generator_pending_shared_send(S, pgeneratorop_send)',
            '~$generator_pending_unused_send(S, pgeneratorop_send)',
            '~$generator_pending_detached_send(S, pgeneratorop)',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.LINE = 0])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.NAME = "throw"])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.ADVANCE = true])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.BORROWED = true])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.STARTPACK = true])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.ARGUMENTS = [PNULL, PNULL]])',
            'S_refreshed = $generator_from_refresh(S, n_upper, $(|S.OBJECTS| + 1))',
            'S_refreshed.STORE = S.STORE', 'S_refreshed.ARRAYS = S.ARRAYS',
            'S_refreshed.ALLOCATIONS = S.ALLOCATIONS', 'S_refreshed.TODO = S.TODO',
            'S_refreshed.OBJECTS[n_upper] = GENERATOR pgenerator_upper',
            'S_refreshed.OBJECTS[n_middle] = GENERATOR pgenerator_refreshed',
            'pgenerator_refreshed.PENDING_INIT',
            'pgenerator_refreshed.DELEGATE = (pgeneratorfrom_refreshed)',
            'pgeneratorfrom_refreshed.INPUT = eps',
            'pgeneratorfrom_refreshed.CURRENT = (KNOWN (PINT 9))',
            'pgenerator_refreshed.FRAME = (pframe_refreshed)',
            'pframe_refreshed.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (POBJECT n_return)) :: ptask_used_tail*',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_child (POBJECT n_return)',
            '$generator_return_waiting(S_refreshed, n_middle)',
            '$generator_pending_return_leaf(S_refreshed, n_upper, 0) = eps',
            '$generator_pending_return_leaf(S_refreshed, n_upper, 1) = eps',
            '$generator_pending_return_leaf(S_refreshed, n_upper, 2) = (n_middle)',
            '$generator_pending_return_leaf(S_refreshed, n_middle, 1) = (n_middle)',
            '$generator_pending_return_leaf(S_refreshed, n_outer, 2) = eps',
            '$generator_pending_return_leaf(S_refreshed, n_outer, 3) = (n_middle)',
            '$generator_pending_detached_send(S_refreshed, pgeneratorop_send)',
            'S_clear = $generator_set(S_refreshed, n_upper, pgenerator_upper[.PENDING_INIT = false])',
            '$heap_graph(S_clear) = $heap_graph(S_refreshed)',
            '~$generator_pending_detached_send(S_clear, pgeneratorop_send)',
            'S_badlink = $generator_set(S_refreshed, n_upper, pgenerator_upper[.DELEGATE = (pgeneratorfrom_upper[.CURRENT = (KNOWN (PINT 9))])])',
            '$heap_graph(S_badlink) = $heap_graph(S_refreshed)',
            '$generator_pending_return_leaf(S_badlink, n_upper, 2) = eps',
            '~$generator_pending_detached_send(S_badlink, pgeneratorop_send)',
            'S_badsite = $generator_set(S_refreshed, n_upper, pgenerator_upper[.DELEGATE = (pgeneratorfrom_upper[.SITE = pgeneratorop.SITE])])',
            '$heap_graph(S_badsite) = $heap_graph(S_refreshed)',
            '$generator_pending_return_leaf(S_badsite, n_upper, 2) = eps',
            'S_badposition = $generator_set(S_refreshed, n_upper, pgenerator_upper[.DELEGATE = (pgeneratorfrom_upper[.POSITION = 0])])',
            '$heap_graph(S_badposition) = $heap_graph(S_refreshed)',
            '$generator_pending_return_leaf(S_badposition, n_upper, 2) = eps',
            'ptask_used_tail* = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_target* z_target) :: ptask_after*',
            'pframe_wrong = pframe_refreshed[.TODO = ptask_complete :: (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME $ptascii("wrong31") z_target) :: ptask_after*]',
            'S_wrong = $generator_set(S_refreshed, n_middle, pgenerator_refreshed[.FRAME = (pframe_wrong)])',
            '$heap_graph(S_wrong) = $heap_graph(S_refreshed)',
            '~$generator_return_waiting(S_wrong, n_middle)',
            '~$generator_pending_detached_send(S_wrong, pgeneratorop_send)',
            'S_held = $generator_set(S_refreshed, n_upper, pgenerator_upper[.FRAME = (pframe_upper[.HELD = [HOBJECT n_return]])])',
            '~$generator_pending_detached_send(S_held, pgeneratorop_send)',
            'S_double = $generator_set(S_refreshed, n_middle, pgenerator_refreshed[.FRAME = (pframe_refreshed[.TODO = pframe_refreshed.TODO ++ [ptask_complete]])])',
            '~$generator_pending_detached_send(S_double, pgeneratorop_send)',
            'S_parked = $generator_set(S_refreshed, n_middle, pgenerator_refreshed[.PARKED = (pgeneratorfrom_middle.SITE)])',
            '$heap_graph(S_parked) = $heap_graph(S_refreshed)',
            '~$generator_pending_detached_send(S_parked, pgeneratorop_send)',
            'S.EVENTS = ' + outputs(EVENTS[CONSUME][:8]),
            *VALID, *BUDGET,
            'S_one.OBJECTS[n_upper] = GENERATOR pgenerator_upper[.PENDING_INIT = false]',
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_refreshed',
            'S_one.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'S_one.OBJECTS[n_outer] = GENERATOR pgenerator_outer',
            'S_one.GENERATORRETURNRETAINED = eps', 'S_one.GENERATORINPUTS = eps',
            'S_one.GENERATORLOOPRETAINED = eps', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.FRAMES = S.FRAMES', 'S_one.CURRENT = S.CURRENT', 'S_one.GC = S.GC',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child), DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HOBJECT n_upper)]',
            'pdestructionrelease.USER', 'pdestructionrelease.CALLER = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])',
            'pdestructionoperation.VALUE = KNOWN (PINT 9)',
            'pdestructionoperation.PENDING = eps',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$generator_return_waiting(S_one, n_middle)',
            '$heap_count(HOBJECT n_return, $node_children(S_one, HOBJECT n_middle)) = 1',
            '$heap_count(HOBJECT n_return, $node_children(S_one, HOBJECT n_child)) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_upper) = 3',
            '~$generator_pending_resume(S_one, pgeneratorop_send)',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[CONSUME]),
            'S_done.GENERATORRETURNRETAINED = eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n_return) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_upper) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_outer) = 0',
            'n_return <- S_done.DESTRUCTION.CALLED',
            'n_argument <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'ancestor-send-used-cache-survives-the-retired-receiver': {
        'source': ROWS[DROP]['source'],
        'stage': ('S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)]) '
                  '-- if pgeneratorop.NAME = "send" '
                  '-- if pdestructionoperation.VALUE = KNOWN (POBJECT n_cache)'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps', 'S.LITERALREFDEBTS = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'S.GENERATORRETURNRETAINED = [ptask_complete]',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_middle porigin_site n_child (PARRAY n_array)',
            '$generator_return_retained_record(S, ptask_complete)',
            '$generator_return_retained_valid(S, S.GENERATORRETURNRETAINED)',
            '$task_nodes(ptask_complete) = [HARRAY n_array]',
            '$heap_count(HARRAY n_array, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_return))]',
            '$object_name(S, n_return) = $ptascii("PendingChainLate31")',
            '$heap_owners($heap_graph(S), HOBJECT n_return) = 1',
            '~(n_return <- S.DESTRUCTION.CALLED)',
            'n_upper = pgeneratorop.OBJECT', 'n_upper =/= n_middle',
            'S.OBJECTS[n_upper] = GENERATOR pgenerator_upper',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_upper.PHASE = GENERATOR_CLOSED',
            'pgenerator_middle.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_upper.FRAME = eps', 'pgenerator_middle.FRAME = eps',
            'pgenerator_child.FRAME = eps', '~pgenerator_upper.PENDING_INIT',
            'pgenerator_upper.PARKED = eps', 'pgenerator_middle.PARKED = eps',
            'pgenerator_child.RETURN = (PARRAY n_array)',
            '~((HOBJECT n_upper) <- S.ALLOCATIONS)',
            '~((HOBJECT n_middle) <- S.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_upper) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_children(HOBJECT n_upper, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            '$heap_children(HOBJECT n_middle, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            '$generator_storage_for(S, n_upper) = eps',
            '$generator_storage_for(S, n_middle) = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("upper")) = eps',
            '$lookup(S_global.ENV, $ptascii("middle")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$object_name(S, n_cache) = $ptascii("PendingChainCache31")',
            '$object_name(S, n_argument) = $ptascii("PendingChainDropRoots31")',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '~(n_cache <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 0',
            '~((HOBJECT n_argument) <- S.ALLOCATIONS)',
            'n_argument <- S.DESTRUCTION.CALLED',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_cache]',
            'S.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
            'S.DESTRUCTION.CALLS = eps',
            'pdestructionoperation.CALLER = eps',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.CLEANUP = eps', 'pdestructionoperation.NOGC = eps',
            'pgeneratorop.LINE = 11', 'pgeneratorop.ARGUMENTS = eps',
            'pgeneratorop.LOOP = eps', '~pgeneratorop.STARTPACK', '~pgeneratorop.BORROWED',
            '$destructor_operation_live(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '~$generator_operation_valid(S, pgeneratorop)',
            '~$destructor_operation_valid(S, pdestructionoperation[.ORIGIN = eps])',
            '~$generator_return_retained_valid(S, [ptask_complete, ptask_complete])',
            'porigin_site = PORIGIN n_unit pcpath_site',
            'porigin_wrong = PORIGIN n_unit (pcpath_site ++ [PCFIELD 999])',
            'S_badsite = S[.GENERATORRETURNRETAINED = [GENERATOR_FROM_COMPLETE n_middle porigin_wrong n_child (PARRAY n_array)]]',
            '$heap_graph(S_badsite) = $heap_graph(S)',
            '~$generator_return_retained_valid(S_badsite, S_badsite.GENERATORRETURNRETAINED)',
            '~$call_descriptors_valid(S_badsite)',
            'S.EVENTS = ' + outputs(EVENTS[DROP][:14]),
            *VALID, *BUDGET,
            'S_one.TODO = ptask_tail*', 'S_one.RESULT = KNOWN (POBJECT n_cache)',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.GENERATORRETURNRETAINED = [ptask_complete]',
            'S_one.DESTRUCTION.OPERATIONS = eps',
            '$heap_graph(S_one) = $heap_graph(S)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 1',
            '~(n_cache <- S_one.DESTRUCTION.CALLED)',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[DROP]),
            'S_done.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_done, ptask_complete)',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '~((HOBJECT n_cache) <- S_done.ALLOCATIONS)',
            'n_cache <- S_done.DESTRUCTION.CALLED',
            'n_return <- S_done.DESTRUCTION.CALLED',
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
