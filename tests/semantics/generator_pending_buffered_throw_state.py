#!/usr/bin/env python3
"""Pending buffered THROW preserves a live input through caller escape and close."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_buffered_throw_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
DIRECT = 'generator-pending-buffered-throw-keeps-input-through-caller-catch-and-parked-close'
REPLACE = 'generator-pending-buffered-throw-sole-receiver-cache-replacement-and-late-input'
EVENTS = {
    DIRECT: ['P|','O|','U|','L|','C|','H|','1','|','S|','5','|T|',
             'CALLER|','SAME|','NOPREV|','GET|','1','|','1','|','5','|','0','|',
             'Z|','J|','K|','CLOSED|','E','B|'],
    REPLACE: ['P|','O|','U|','L|','C|','S|T|','H|','Z|','DROP|','K|','J|',
              'D|','CALLER|','REPLACED|','PREV|','E','B|'],
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
    'pending-buffered-throw-parks-leaf-without-consuming-live-input': {
        'source': ROWS[DIRECT]['source'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_exception)])) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "throw" '
                  '-- if S.GENERATORINPUTS = [pgeneratorinput] -- if pgeneratorinput.LIVE'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.ORIGIN = (pgeneratorop.SITE)', 'pgeneratorop.LINE = 9',
            'pgeneratorop.ARGUMENTS = eps', '~pgeneratorop.ADVANCE',
            'pgeneratorop.LOOP = eps', '~pgeneratorop.STARTPACK', '~pgeneratorop.BORROWED',
            'n_upper = pgeneratorop.OBJECT',
            'S.OBJECTS[n_upper] = GENERATOR pgenerator_upper',
            'pgenerator_upper.PHASE = GENERATOR_DELEGATING',
            'pgenerator_upper.PENDING_INIT', 'pgenerator_upper.PARKED = eps',
            'pgenerator_upper.DELEGATE = (pgeneratorfrom_upper)',
            'pgeneratorfrom_upper.INPUT = (POBJECT n_lower)',
            'pgeneratorfrom_upper.ACQUISITION = eps', 'pgeneratorfrom_upper.CURRENT = eps',
            'S.OBJECTS[n_lower] = GENERATOR pgenerator_lower',
            'pgenerator_lower.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_lower.PENDING_INIT', 'pgenerator_lower.PARKED = eps',
            'pgenerator_lower.DELEGATE = (pgeneratorfrom_lower)',
            'pgeneratorfrom_lower.INPUT = (POBJECT n_child)',
            'pgeneratorfrom_lower.ACQUISITION = eps', 'pgeneratorfrom_lower.CURRENT = eps',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            '~pgenerator_child.PENDING_INIT', 'pgenerator_child.PARKED = eps',
            'pgenerator_child.DELEGATE = eps', 'pgenerator_child.VALUE = (PINT 5)',
            'pgenerator_child.KEY = (PINT 0)', 'pgenerator_child.REFCELL = eps',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (pgeneratorinput.SITE)',
            'pframe_child.HELD = eps', '$tasks_nodes(pframe_child.TODO) = eps',
            'pgeneratorinput.OBJECT = n_child',
            'pgeneratorinput.SOURCE.OBJECT = n_lower',
            'pgeneratorinput.SOURCE.NAME = "send"', 'pgeneratorinput.SOURCE.LINE = 8',
            'pgeneratorinput.SOURCE.ARGUMENTS = [POBJECT n_payload]',
            '$generator_input_source_valid(S, pgeneratorinput)',
            '$generator_input_live_valid(S, pgeneratorinput)',
            '$generator_input_site(S, n_child, pgeneratorinput.SITE)',
            '$generator_input_tail(S, pgeneratorinput.SITE, pframe_child.TODO)',
            '$generator_input_count(S.GENERATORINPUTS, n_child) = 1',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_payload]',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_send_leaf(S, n_upper, |S.OBJECTS|) = (n_child)',
            '$generator_pending_throw_leaf(S, n_upper, |S.OBJECTS|) = (n_child)',
            '$generator_pending_throw_leaf(S, n_upper, 0) = eps',
            'pgeneratorop_throw = pgeneratorop[.ARGUMENTS = [POBJECT n_exception]]',
            '$generator_operation_valid(S, pgeneratorop_throw)',
            '$generator_pending_throw_ready(S, pgeneratorop_throw)',
            '~$generator_input_throw_ready(S, pgeneratorop_throw)',
            '~$generator_input_blocked(S, pgeneratorop_throw)',
            '~$generator_pending_throw_ready(S, pgeneratorop)',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.LINE = 0])',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.ARGUMENTS = [PINT 1]])',
            '~$generator_pending_throw_ready(S, pgeneratorop_throw[.BORROWED = true])',
            'S_clear = $generator_set(S, n_upper, pgenerator_upper[.PENDING_INIT = false])',
            '$heap_graph(S_clear) = $heap_graph(S)',
            '~$generator_pending_throw_ready(S_clear, pgeneratorop_throw)',
            'S_wrong = S[.GENERATORINPUTS = [pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = 0]]]]',
            '$heap_graph(S_wrong) = $heap_graph(S)',
            '~$generator_pending_throw_ready(S_wrong, pgeneratorop_throw)',
            '~$call_descriptors_valid(S_wrong)',
            'S_held = $generator_set(S, n_child, pgenerator_child[.FRAME = (pframe_child[.HELD = [HOBJECT n_payload]])])',
            '$generator_pending_throw_leaf(S_held, n_child, 1) = eps',
            'S_duplicate = S[.GENERATORINPUTS = [pgeneratorinput, pgeneratorinput]]',
            '~$generator_pending_throw_ready(S_duplicate, pgeneratorop_throw)',
            '$object_name(S, n_payload) = $ptascii("PendingBufferedPayload22")',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_upper) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_lower) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            '~(n_payload <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = ' + outputs(EVENTS[DIRECT][:11]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = S.GENERATORINPUTS',
            'S_one.OBJECTS[n_upper] = GENERATOR pgenerator_upper[.PENDING_INIT = false]',
            'S_one.OBJECTS[n_lower] = S.OBJECTS[n_lower]',
            'S_one.OBJECTS[n_child] = GENERATOR pgenerator_child[.PARKED = (pgeneratorinput.SITE)]',
            '$generator_parked(S_one, n_upper, |S.OBJECTS|)',
            '$generator_input_live_valid(S_one, pgeneratorinput)',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (GENERATOR_PENDING_THROW pgeneratorpendingthrow) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_upper)]',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_exception)])',
            'pdestructionoperation.PENDING = (n_exception)',
            'pdestructionoperation.VALUE = KNOWN PNULL', 'pdestructionoperation.NOGC = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            'pgeneratorpendingthrow.SOURCE = pgeneratorop_throw',
            'pgeneratorpendingthrow.LEAF = n_child',
            'pgeneratorpendingthrow.SITE = pgeneratorinput.SITE',
            'pgeneratorpendingthrow.VALUE = PINT 5',
            '$task_nodes(GENERATOR_PENDING_THROW pgeneratorpendingthrow) = eps',
            '$call_task_valid(S_one, GENERATOR_PENDING_THROW pgeneratorpendingthrow)',
            '$generator_pending_throw_carried(S_one, pgeneratorpendingthrow, S_one.TODO)',
            'S_projected = $call_after_origin(S_one, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
            'S_projected.DESTRUCTION.OPERATIONS = eps',
            'S_projected.TODO = S_one.TODO',
            '$heap_graph(S_projected) = $heap_graph(S_one)',
            '$eager_operation_pending(S_projected) = eps',
            '$destructor_selected_pending(S_projected, eps) = eps',
            '$call_task_valid(S_projected, GENERATOR_PENDING_THROW pgeneratorpendingthrow)',
            '~$call_descriptors_valid(S_projected)',
            '~$generator_pending_throw_carried(S_projected, pgeneratorpendingthrow, [GENERATOR_PENDING_THROW pgeneratorpendingthrow])',
            '~$generator_pending_throw_carrier(S_projected, pgeneratorpendingthrow, DESTRUCTOR_OPERATION_EXIT pdestructionoperation[.PENDING = eps], (GENERATOR_PENDING_THROW pgeneratorpendingthrow) :: ptask_tail*)',
            '~$generator_pending_throw_carrier(S_projected, pgeneratorpendingthrow, DESTRUCTOR_OPERATION_EXIT pdestructionoperation[.ORIGIN = eps], (GENERATOR_PENDING_THROW pgeneratorpendingthrow) :: ptask_tail*)',
            '~$generator_pending_throw_carrier(S_projected, pgeneratorpendingthrow, DESTRUCTOR_OPERATION_EXIT pdestructionoperation[.SOURCE = GENERATOR_ARGS pgeneratorop[.LINE = 0] eps ([KNOWN (POBJECT n_exception)])], (GENERATOR_PENDING_THROW pgeneratorpendingthrow) :: ptask_tail*)',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.FRAMES = S.FRAMES',
            'S_one.GC = S.GC',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2',
            '~(n_payload <- S_one.DESTRUCTION.CALLED)',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[DIRECT]),
            'S_done.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 1',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HOBJECT n_upper) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_lower) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
        ],
    },
    'cache-replacement-callback-keeps-distinct-orphaned-input': {
        'source': ROWS[REPLACE]['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) '
                  '-- if $object_name(S, n_cache) = $ptascii("PendingBufferedCacheReplacement22") '
                  '-- if S.FRAMES = pframe_caller :: pframe_tail* '
                  '-- if pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_return* '
                  '-- if pdestructorcall.OPERATION = (pdestructionoperation) '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_PENDING_THROW pgeneratorpendingthrow'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.GENERATORINPUTS = [pgeneratorinput]',
            '~pgeneratorinput.LIVE', 'pgeneratorinput.OBJECT = pgeneratorpendingthrow.LEAF',
            'pgeneratorinput.SITE = pgeneratorpendingthrow.SITE',
            'pgeneratorinput.SOURCE.NAME = "send"', 'pgeneratorinput.SOURCE.LINE = 9',
            'pgeneratorinput.SOURCE.ARGUMENTS = [POBJECT n_payload]',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_payload]',
            '$object_name(S, n_payload) = $ptascii("PendingBufferedLateInput22")',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '~(n_payload <- S.DESTRUCTION.CALLED)',
            'pcallcontext.INSTANCE = eps', 'pdestructorcall.OBJECT = n_cache',
            'pgeneratorpendingthrow.VALUE = POBJECT n_cache',
            'pgeneratorop = pgeneratorpendingthrow.SOURCE',
            'pgeneratorop.ARGUMENTS = [POBJECT n_exception]',
            'pgeneratorop.NAME = "throw"', 'pgeneratorop.LINE = 10',
            'n_upper = pgeneratorop.OBJECT', 'n_child = pgeneratorpendingthrow.LEAF',
            'n_lower = pgeneratorinput.SOURCE.OBJECT',
            'S.OBJECTS[n_upper] = GENERATOR pgenerator_upper',
            'S.OBJECTS[n_lower] = GENERATOR pgenerator_lower',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_upper.PHASE = GENERATOR_CLOSED', 'pgenerator_upper.PARKED = eps',
            'pgenerator_lower.PHASE = GENERATOR_CLOSED', 'pgenerator_lower.PARKED = eps',
            'pgenerator_child.PHASE = GENERATOR_CLOSED', 'pgenerator_child.PARKED = eps',
            '~((HOBJECT n_upper) <- S.ALLOCATIONS)',
            '~((HOBJECT n_lower) <- S.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_upper) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_lower) = 0',
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
            'S.EVENTS = ' + outputs(EVENTS[REPLACE][:11]),
            *VALID, *BUDGET,
            '$generator_pending_throw_receipt(S_one, pdestructionoperation)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation)',
            'S_one.GENERATORINPUTS = S.GENERATORINPUTS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[REPLACE]),
            'S_done.GENERATORINPUTS = S.GENERATORINPUTS',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            'n_payload <- S_done.DESTRUCTION.CALLED',
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
