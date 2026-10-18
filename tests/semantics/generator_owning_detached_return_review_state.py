#!/usr/bin/env python3
"""Reach mutable retained-return cells and real cache-replacement callbacks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_owning_detached_return_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
CELL = 'generator-owning-detached-return-review-array-cell-rebind'
REPLACE = 'generator-owning-detached-return-review-temporary-cache-replacement'
EVENTS = {
    CELL: ['P|', 'G|', 'C|', 'L|', 'V|', 'HELD|', 'K|', '1', '|', 'M|',
           'T|', '11', '|', 'NOFRAME|', 'F|', 'A|', 'CLOSED|',
           'R|', 'WRITE|', 'UNSET|', 'E', 'CNEW|'],
    REPLACE: ['P|', 'G|', 'C|', 'L|', 'V|', 'HELD|', 'K|', '1', '|', 'M|',
              'TAKE|', 'F|', 'D|', 'CALLER|', 'REPLACED|', 'PREV|',
              'LINE|', '11', '|', 'E', 'R|'],
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
    'retained-return-array-follows-the-real-shared-cell-write': {
        'source': ROWS[CELL]['source'],
        'stage': ('S.TODO = (WRITE_NAME n_name* z_write) :: ptask_tail* '
                  '-- if n_name* = $ptascii("slot") '
                  '-- if S.GENERATORRETURNRETAINED = [ptask_complete] '
                  '-- if S.RESULT = KNOWN (POBJECT n_new) '
                  '-- if $object_name(S, n_new) = $ptascii("ReviewDetachedCellNew27")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_parent porigin_site n_child (PARRAY n_array)',
            '$generator_return_site(S, n_parent, porigin_site)',
            '$generator_return_receipt(S, n_parent, porigin_site, n_child, PARRAY n_array)',
            '$generator_return_retained_record(S, ptask_complete)',
            '$generator_return_retained_valid(S, S.GENERATORRETURNRETAINED)',
            '$task_nodes(ptask_complete) = [HARRAY n_array]',
            '$heap_count(HARRAY n_array, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_slot)]',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, n_name*) = (n_slot)',
            'n_slot <- S.REFCELLS', '(HCELL n_slot) <- S.ALLOCATIONS',
            'S.STORE[n_slot] = DEFINED (POBJECT n_old)',
            '$object_name(S, n_old) = $ptascii("ReviewDetachedCellOld27")',
            '$node_children(S, HARRAY n_array) = [HCELL n_slot]',
            '$node_children(S, HCELL n_slot) = [HOBJECT n_old]',
            '$heap_owners($heap_graph(S), HCELL n_slot) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_new) = 1',
            '~(n_old <- S.DESTRUCTION.CALLED)', '~(n_new <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_parent.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_parent.FRAME = eps', 'pgenerator_child.FRAME = eps',
            'pgenerator_parent.PARKED = eps', 'pgenerator_child.PARKED = eps',
            'pgenerator_child.RETURN = (PARRAY n_array)',
            '~((HOBJECT n_parent) <- S.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_parent) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_children(HOBJECT n_parent, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            '$heap_children(HOBJECT n_child, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            '$lookup(S_global.ENV, $ptascii("parent")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$generator_return_retained_seen([ptask_complete], n_parent)',
            '~$generator_return_retained_valid(S, [ptask_complete, ptask_complete])',
            'porigin_site = PORIGIN n_unit pcpath_site',
            'porigin_wrong = PORIGIN n_unit (pcpath_site ++ [PCFIELD 999])',
            'S_badsite = S[.GENERATORRETURNRETAINED = [GENERATOR_FROM_COMPLETE n_parent porigin_wrong n_child (PARRAY n_array)]]',
            '$heap_graph(S_badsite) = $heap_graph(S)',
            '$heap_valid($heap_graph(S_badsite))',
            '~$generator_return_retained_valid(S_badsite, S_badsite.GENERATORRETURNRETAINED)',
            '~$call_descriptors_valid(S_badsite)',
            '~$generator_return_retained_record(S, GENERATOR_FROM_COMPLETE n_parent porigin_site n_parent (PARRAY n_array))',
            'S_unclaimed = $generator_set(S, n_parent, pgenerator_parent[.PHASE = GENERATOR_RUNNING])',
            '$heap_graph(S_unclaimed) = $heap_graph(S)',
            '~$generator_return_closing(S_unclaimed, n_parent)',
            '~$generator_return_retained_record(S_unclaimed, ptask_complete)',
            '~$call_descriptors_valid(S_unclaimed)',
            'S.EVENTS = ' + outputs(EVENTS[CELL][:17]),
            *VALID, *BUDGET,
            'S_one.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_one, ptask_complete)',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.OBJECTS = S.OBJECTS',
            'S_expected = S[.STORE[n_slot] = DEFINED (POBJECT n_new)]',
            'S_one.STORE = S_expected.STORE', 'S_one.ENV = S.ENV',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]',
            'pdestructionrelease.USER', 'pdestructionrelease.CALLER = eps',
            'pdestructionoperation.SOURCE = WRITE_NAME n_name* z_write',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.COMPLETION = NORMAL', 'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.CLEANUP = eps', 'pdestructionoperation.NOGC = eps',
            '$node_children(S_one, HARRAY n_array) = [HCELL n_slot]',
            '$node_children(S_one, HCELL n_slot) = [HOBJECT n_new]',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_slot) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_new) = 1',
            '~(n_old <- S_one.DESTRUCTION.CALLED)',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[CELL]),
            'S_done.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_done, ptask_complete)',
            'S_done.ARRAYS[n_array].ITEMS = S.ARRAYS[n_array].ITEMS',
            'S_done.STORE[n_slot] = DEFINED (POBJECT n_new)',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HCELL n_slot) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_new) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 0',
            '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
            '(HOBJECT n_new) <- S_done.ALLOCATIONS',
            'n_old <- S_done.DESTRUCTION.CALLED', 'n_new <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        ],
    },
    'retained-return-survives-real-cache-replacement-callback': {
        'source': ROWS[REPLACE]['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) '
                  '-- if $object_name(S, n_cache) = $ptascii("ReviewDetachedTemporaryCache27") '
                  '-- if S.FRAMES = pframe_caller :: pframe_tail* '
                  '-- if pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_return* '
                  '-- if pdestructorcall.OPERATION = (pdestructionoperation)'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'S.GENERATORRETURNRETAINED = [ptask_complete]',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_parent porigin_site n_child (POBJECT n_return)',
            '$generator_return_site(S, n_parent, porigin_site)',
            '$generator_return_receipt(S, n_parent, porigin_site, n_child, POBJECT n_return)',
            '$generator_return_retained_record(S, ptask_complete)',
            '$generator_return_retained_valid(S, S.GENERATORRETURNRETAINED)',
            '$task_nodes(ptask_complete) = [HOBJECT n_return]',
            '$object_name(S, n_return) = $ptascii("ReviewDetachedTemporaryReturn27")',
            '$heap_count(HOBJECT n_return, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_return) = 1',
            '~(n_return <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_parent.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_parent.FRAME = eps', 'pgenerator_child.FRAME = eps',
            'pgenerator_parent.PARKED = eps', 'pgenerator_child.PARKED = eps',
            '[pgenstorage] = $generator_storage_tasks(S.TODO) ++ $generator_storage_frames(S.FRAMES)',
            'pgenstorage.OBJECT = n_parent', 'pgenstorage.NEXT = 2',
            'pgenstorage.USER', 'pgenstorage.CALLER = eps',
            '$generator_storage_for(S, n_parent) = (pgenstorage)',
            '$generator_storage_basic(S, pgenstorage)',
            '(HOBJECT n_parent) <- S.ALLOCATIONS',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_parent) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$node_children(S, HOBJECT n_parent) = eps',
            'n_parent <- S.DESTRUCTION.CALLED',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            'pcallcontext.INSTANCE = eps', 'pdestructorcall.OBJECT = n_cache',
            'pdestructorcall.CALLER = eps', 'pframe_caller.CONTEXT = eps',
            'pdestructionoperation.CALLER = eps',
            'pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "ready"',
            'pgeneratorunpack.OBJECT = n_parent', 'pgeneratorunpack.COUNT = 0',
            'pgeneratorunpack.CALL.LINE = 11',
            'pdestructionoperation.PENDING = (n_error)',
            'pdestructorcall.PENDING = (n_error)',
            'S.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
            '$throwable_field(S, n_error, "line") = PINT 11',
            '$throwable_field(S, n_error, "previous") = PNULL',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = eps', '$trace_graph_valid(S, n_trace)',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_error) = 2',
            'pdestructionoperation.NOGC = eps',
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) <- pframe_caller.TODO',
            '$destructor_operation_live(S, pdestructionoperation)',
            '~$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_call_live(S, pdestructorcall)',
            '$destructor_context_valid(S, pcallcontext)',
            '~$generator_return_retained_valid(S, [ptask_complete, ptask_complete])',
            'porigin_site = PORIGIN n_unit pcpath_site',
            'porigin_wrong = PORIGIN n_unit (pcpath_site ++ [PCFIELD 999])',
            'S_badsite = S[.GENERATORRETURNRETAINED = [GENERATOR_FROM_COMPLETE n_parent porigin_wrong n_child (POBJECT n_return)]]',
            '$heap_graph(S_badsite) = $heap_graph(S)',
            '~$generator_return_retained_valid(S_badsite, S_badsite.GENERATORRETURNRETAINED)',
            '~$call_descriptors_valid(S_badsite)',
            'S.EVENTS = ' + outputs(EVENTS[REPLACE][:12]),
            *VALID, *BUDGET,
            'S_one.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_one, ptask_complete)',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_error) = 2',
            '$generator_storage_for(S_one, n_parent) = (pgenstorage)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_parent) = 1',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[REPLACE]),
            'S_done.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_done, ptask_complete)',
            '$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1',
            '(HOBJECT n_return) <- S_done.ALLOCATIONS',
            'n_return <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
            '~((HOBJECT n_cache) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_error) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
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
