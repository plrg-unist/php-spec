#!/usr/bin/env python3
"""Reach ancestor-unpack inherited-initialization close and mutable returned cells."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_owning_chain_unpack_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
COW = 'generator-owning-chain-unpack-review-return-cache-array-alias-cow'
CELL = 'generator-owning-chain-unpack-review-return-cell-rebind'
EVENTS = {
    COW: ['P|','O|','M|','C|','L|','H|','1','|','T|',
          'K|','10','|','NOPREV|','W|','1','|','1','|','EX|',
          'F|','OUT|','MID|','B|','ROW|','HELD|','E','A|'],
    CELL: ['P|','O|','M|','C|','L|','H|','1','|','T|',
           'K|','10','|','NOPREV|','EX|','F|','OUT|','MID|',
           'R|','WRITE|','UNSET|','E','CNEW|'],
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
    'ancestor-owning-array-alias-close-skips-inherited-initialization': {
        'source': ROWS[COW]['source'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
                  '-- if pgenclose.STAGE = CLOSE_QUEUED '
                  '-- if $trace_context_function(S, pgenclose.CONTEXT) = $ptascii("reviewChainMiddle30")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps', 'S.LITERALREFDEBTS = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'n_middle = pgenclose.OBJECT',
            'pgenclose.CALLER = eps', 'pgenclose.PENDING = eps',
            'pgenclose.SITE = porigin_site',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_CLOSING',
            'pgenerator_middle.FRAME = eps', 'pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.PARKED = eps',
            '~$generator_close_parked(S, pgenclose)',
            '$generator_close_pending_init(S, pgenclose)',
            '$generator_close_enter_valid(S, pgenclose)',
            'pgenclose.FRAME = (pframe_middle)',
            'pframe_middle.ORIGIN = (porigin_site)', 'pframe_middle.HELD = eps',
            'S.GENERATORRETURNRETAINED = [ptask_complete]',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_middle porigin_site n_child (PARRAY n_old_row)',
            '$generator_return_site(S, n_middle, porigin_site)',
            '$generator_return_receipt(S, n_middle, porigin_site, n_child, PARRAY n_old_row)',
            '$generator_return_retained_record(S, ptask_complete)',
            '$generator_return_retained_valid(S, S.GENERATORRETURNRETAINED)',
            '$task_nodes(ptask_complete) = [HARRAY n_old_row]',
            '$generator_input_tail(S, porigin_site, pframe_middle.TODO)',
            '$tasks_nodes(pframe_middle.TODO) = eps',
            '$generator_close_frame_nodes(S, pframe_middle) = eps',
            '~(ptask_complete <- pframe_middle.TODO)',
            '~$generator_return_waiting(S, n_middle)',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.SITE = porigin_site',
            'pgeneratorfrom.INPUT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.POSITION = 1', 'pgeneratorfrom.CURRENT = (REFERENCE n_row)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED', 'pgenerator_child.FRAME = eps',
            'pgenerator_child.RETURN = (PARRAY n_old_row)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_children(HOBJECT n_child, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("row")) = (n_row)',
            '$lookup(S_global.ENV, $ptascii("held")) = (n_held)',
            'S.STORE[n_held] = DEFINED (PARRAY n_old_row)',
            'S.STORE[n_row] = DEFINED (PARRAY n_live_row)',
            'n_row <- S.REFCELLS', '(HCELL n_row) <- S.ALLOCATIONS',
            'n_live_row =/= n_old_row',
            'S.ARRAYS[n_old_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
            'S.ARRAYS[n_live_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_live))]',
            '$object_name(S, n_old) = $ptascii("ReviewChainOld30")',
            '$object_name(S, n_live) = $ptascii("ReviewChainNew30")',
            '$node_children(S, HARRAY n_old_row) = [HOBJECT n_old]',
            '$node_children(S, HARRAY n_live_row) = [HOBJECT n_live]',
            '$node_children(S, HCELL n_row) = [HARRAY n_live_row]',
            '$heap_count(HARRAY n_old_row, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_old_row) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_live_row) = 1',
            '$heap_owners($heap_graph(S), HCELL n_row) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_live) = 1',
            '~(n_old <- S.DESTRUCTION.CALLED)', '~(n_live <- S.DESTRUCTION.CALLED)',
            '$lookup(S_global.ENV, $ptascii("error")) = eps',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '~$generator_return_retained_valid(S, [ptask_complete, ptask_complete])',
            'porigin_site = PORIGIN n_unit pcpath_site',
            'porigin_wrong = PORIGIN n_unit (pcpath_site ++ [PCFIELD 999])',
            'S_badsite = S[.GENERATORRETURNRETAINED = [GENERATOR_FROM_COMPLETE n_middle porigin_wrong n_child (PARRAY n_old_row)]]',
            '$heap_graph(S_badsite) = $heap_graph(S)',
            '~$generator_return_retained_record(S_badsite, GENERATOR_FROM_COMPLETE n_middle porigin_wrong n_child (PARRAY n_old_row))',
            '~$call_descriptors_valid(S_badsite)',
            'S.EVENTS = ' + outputs(EVENTS[COW][:21]),
            *VALID, *BUDGET,
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PHASE = GENERATOR_CLOSED][.PENDING_INIT = false][.PARKED = eps]',
            'S_one.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_one, ptask_complete)',
            'S_one.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_DONE pgenclose_done) :: ptask_tail*',
            'pgenrelease.JOBS = eps', 'pgenrelease.PENDING = eps',
            'pgenrelease.VALUE = S.RESULT', 'pgenrelease.BASE = S.BASE',
            'pgenclose_done = pgenclose[.FRAME = eps][.STAGE = CLOSE_FINISHED][.PENDING = eps]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.ENV = S.ENV',
            '$heap_owners($heap_graph(S_one), HARRAY n_old_row) = 2',
            '$heap_owners($heap_graph(S_one), HARRAY n_live_row) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_row) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_live) = 1',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[COW]),
            'S_done.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_done, ptask_complete)',
            '$heap_owners($heap_graph(S_done), HARRAY n_old_row) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 1',
            '(HARRAY n_old_row) <- S_done.ALLOCATIONS',
            '(HOBJECT n_old) <- S_done.ALLOCATIONS',
            'n_old <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HARRAY n_live_row) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_live) = 0',
            '~((HOBJECT n_live) <- S_done.ALLOCATIONS)',
            'n_live <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_middle) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        ],
    },
    'ancestor-owning-return-array-follows-the-late-shared-cell-write': {
        'source': ROWS[CELL]['source'],
        'stage': ('S.TODO = (WRITE_NAME n_name* z_write) :: ptask_tail* '
                  '-- if n_name* = $ptascii("slot") '
                  '-- if S.GENERATORRETURNRETAINED = [ptask_complete] '
                  '-- if S.RESULT = KNOWN (POBJECT n_new) '
                  '-- if $object_name(S, n_new) = $ptascii("ReviewChainCellNew30")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps', 'S.LITERALREFDEBTS = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'z_write = 12',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_middle porigin_site n_child (PARRAY n_array)',
            '$generator_return_site(S, n_middle, porigin_site)',
            '$generator_return_receipt(S, n_middle, porigin_site, n_child, PARRAY n_array)',
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
            '$object_name(S, n_old) = $ptascii("ReviewChainCellOld30")',
            '$node_children(S, HARRAY n_array) = [HCELL n_slot]',
            '$node_children(S, HCELL n_slot) = [HOBJECT n_old]',
            '$heap_owners($heap_graph(S), HCELL n_slot) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_new) = 1',
            '~(n_old <- S.DESTRUCTION.CALLED)', '~(n_new <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_middle.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_middle.FRAME = eps', 'pgenerator_child.FRAME = eps',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.PARKED = eps', 'pgenerator_child.PARKED = eps',
            'pgenerator_child.RETURN = (PARRAY n_array)',
            '~((HOBJECT n_middle) <- S.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_children(HOBJECT n_middle, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            '$heap_children(HOBJECT n_child, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            '$lookup(S_global.ENV, $ptascii("middle")) = eps',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$generator_return_retained_seen([ptask_complete], n_middle)',
            '~$generator_return_retained_valid(S, [ptask_complete, ptask_complete])',
            'porigin_site = PORIGIN n_unit pcpath_site',
            'porigin_wrong = PORIGIN n_unit (pcpath_site ++ [PCFIELD 999])',
            'S_badsite = S[.GENERATORRETURNRETAINED = [GENERATOR_FROM_COMPLETE n_middle porigin_wrong n_child (PARRAY n_array)]]',
            '$heap_graph(S_badsite) = $heap_graph(S)',
            '$heap_valid($heap_graph(S_badsite))',
            '~$generator_return_retained_valid(S_badsite, S_badsite.GENERATORRETURNRETAINED)',
            '~$call_descriptors_valid(S_badsite)',
            '~$generator_return_retained_record(S, GENERATOR_FROM_COMPLETE n_middle porigin_site n_middle (PARRAY n_array))',
            'S_unclaimed = $generator_set(S, n_middle, pgenerator_middle[.PHASE = GENERATOR_RUNNING])',
            '$heap_graph(S_unclaimed) = $heap_graph(S)',
            '~$generator_return_closing(S_unclaimed, n_middle)',
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
            '~((HOBJECT n_middle) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
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
