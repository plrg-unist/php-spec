#!/usr/bin/env python3
"""Pending THROW snapshot retirement and real cached-value destructor receipt."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_throw_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
DIRECT = 'generator-pending-throw-live-child-caller-catch-getters-and-close'
REPLACE = 'generator-pending-throw-sole-receiver-cache-destructor-replacement'
EVENTS = {
    DIRECT: ['P|', 'O|', 'M|', 'C|', 'H|', '1', '|', 'CALLER|', 'SAME|',
             'V|', '1', '|', '0', '|', 'LIVE|', 'SHARED|', 'Z|', 'J|',
             'CLOSED|', 'D|', 'END|', 'E'],
    REPLACE: ['P|', 'O|', 'M|', 'C|', 'T|', 'H|', 'Z|', 'DROP|', 'J|',
              'D|', 'CALLER|', 'OTHER|', 'REPLACED|', 'PREV|', 'SOME|', 'E'],
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
    'pending-throw-drops-only-copied-result-before-caller-search': {
        'source': ROWS[DIRECT]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_exception) :: (GENERATOR_PENDING_THROW pgeneratorpendingthrow) :: ptask_tail* '
                  '-- if pgeneratorpendingthrow.VALUE = POBJECT n_cache '
                  '-- if $object_name(S, n_cache) = $ptascii("PendingThrowCache21")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GENERATORINPUTS = eps', 'S.DESTRUCTION.OPERATIONS = eps',
            'S.RESULT = KNOWN PNULL', 'S.COMPLETION = NORMAL',
            'pgeneratorop = pgeneratorpendingthrow.SOURCE',
            'pgeneratorop.NAME = "throw"', 'pgeneratorop.LINE = 7',
            'pgeneratorop.ARGUMENTS = [POBJECT n_exception]',
            'pgeneratorop.LOOP = eps', '~pgeneratorop.ADVANCE',
            '~pgeneratorop.STARTPACK', '~pgeneratorop.BORROWED',
            'n_middle = pgeneratorop.OBJECT', 'n_child = pgeneratorpendingthrow.LEAF',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            'pgenerator_child.PARKED = (pgeneratorpendingthrow.SITE)',
            'pgenerator_child.DELEGATE = eps', '~pgenerator_child.PENDING_INIT',
            'pgenerator_child.VALUE = (POBJECT n_cache)',
            'pgenerator_child.KEY = (PINT 0)',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (pgeneratorpendingthrow.SITE)',
            '$generator_unused_send_tail(S, pgeneratorpendingthrow.SITE, pframe_child.TODO)',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_middle.PENDING_INIT', 'pgenerator_middle.PARKED = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.CURRENT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            '$generator_parked_valid(S, pgenerator_child)',
            '$generator_parked(S, n_middle, |S.OBJECTS|)',
            '$generator_parked(S, n_child, |S.OBJECTS|)',
            '~$generator_pending_throw_ready(S, pgeneratorop)',
            'S_unparked = $generator_set(S, n_child, pgenerator_child[.PARKED = eps])',
            '$heap_graph(S_unparked) = $heap_graph(S)',
            '$generator_pending_throw_leaf(S_unparked, n_child, |S.OBJECTS|) = (n_child)',
            'S_held = $generator_set(S_unparked, n_child, pgenerator_child[.PARKED = eps][.FRAME = (pframe_child[.HELD = [HOBJECT n_cache]])])',
            '$generator_pending_throw_leaf(S_held, n_child, |S.OBJECTS|) = eps',
            '$generator_pending_throw_valid(S, pgeneratorpendingthrow)',
            '$generator_pending_throw_discard(S, S.TODO[0]) = (pgeneratorpendingthrow)',
            '$call_task_valid(S, GENERATOR_PENDING_THROW pgeneratorpendingthrow)',
            '$task_nodes(GENERATOR_PENDING_THROW pgeneratorpendingthrow) = [HOBJECT n_cache]',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.SOURCE = pgeneratorop[.LINE = 0]])',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.SOURCE = pgeneratorop[.ARGUMENTS = [PINT 1]]])',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.SOURCE = pgeneratorop[.BORROWED = true]])',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.SITE = pgeneratorop.SITE])',
            '~$generator_pending_throw_valid(S, pgeneratorpendingthrow[.LEAF = n_middle])',
            'S_replay = S[.TODO = [GENERATOR_PENDING_THROW pgeneratorpendingthrow]]',
            '~$call_task_valid(S_replay, GENERATOR_PENDING_THROW pgeneratorpendingthrow)',
            'S_bad = $generator_set(S, n_child, pgenerator_child[.PARKED = (pgenerator_child.FUNCTION)])',
            '$heap_graph(S_bad) = $heap_graph(S)', '~$call_descriptors_valid(S_bad)',
            'S_stopped = $generator_resume(S, pgeneratorop[.NAME = "next"])',
            'S_stopped.COMPLETION = UNSUPPORTED "Generator resume after pending throw"',
            'S_stopped[.COMPLETION = NORMAL] = S',
            'S.EVENTS = ' + outputs(EVENTS[DIRECT][:7]),
            *VALID, *BUDGET,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HOBJECT n_cache)]',
            'pdestructionoperation.SOURCE = GENERATOR_PENDING_THROW pgeneratorpendingthrow',
            'pdestructionoperation.PENDING = (n_exception)',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.NOGC = ({OPERAND KNOWN (POBJECT n_cache), PENDING true})',
            '$generator_pending_throw_here(S_one, pdestructionoperation)',
            '$generator_pending_throw_receipt(S_one, pdestructionoperation)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation)',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.FRAMES = S.FRAMES',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.GC = S.GC',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2',
            'S_two_budget.COMPLETION = BUDGET',
            'S_two_budget.GC = S.GC',
            '$heap_owners($heap_graph(S_two_budget), HOBJECT n_cache) = 2',
            '~(n_cache <- S_two_budget.DESTRUCTION.CALLED)',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[DIRECT]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            'n_cache <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'pending-throw-copy-receipt-inside-cache-destructor-after-receiver-close': {
        'source': ROWS[REPLACE]['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) '
                  '-- if $object_name(S, n_cache) = $ptascii("PendingThrowReplacementCache21") '
                  '-- if S.FRAMES = pframe_caller :: pframe_tail* '
                  '-- if pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_return* '
                  '-- if pdestructorcall.OPERATION = (pdestructionoperation) '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_PENDING_THROW pgeneratorpendingthrow'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.GENERATORINPUTS = eps',
            'pcallcontext.INSTANCE = eps', 'pdestructorcall.OBJECT = n_cache',
            'pgeneratorpendingthrow.VALUE = POBJECT n_cache',
            'pgeneratorop = pgeneratorpendingthrow.SOURCE',
            'pgeneratorop.ARGUMENTS = [POBJECT n_exception]',
            'pgeneratorop.NAME = "throw"', 'pgeneratorop.LINE = 8',
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
            'S_caller = $constant_frame_scope(S, pframe_caller, pframe_tail*)',
            '$generator_pending_throw_here(S_caller, pdestructionoperation)',
            '$destructor_operation_live(S, pdestructionoperation)',
            '~$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_context_valid(S, pcallcontext)',
            '$gc_operation_metadata_valid(S, pdestructionoperation)',
            '~$generator_pending_throw_receipt(S, pdestructionoperation[.CALLER = S.CURRENT])',
            '~$gc_operation_metadata_valid(S, pdestructionoperation[.ORIGIN = eps])',
            '~$generator_pending_throw_receipt(S, pdestructionoperation[.SOURCE = GENERATOR_PENDING_THROW pgeneratorpendingthrow[.SOURCE = pgeneratorop[.LINE = 0]]])',
            '~$generator_pending_throw_receipt(S, pdestructionoperation[.SOURCE = GENERATOR_PENDING_THROW pgeneratorpendingthrow[.VALUE = PINT 0]])',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            'S.EVENTS = ' + outputs(EVENTS[REPLACE][:9]),
            *VALID, *BUDGET,
            '$generator_pending_throw_receipt(S_one, pdestructionoperation)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[REPLACE]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
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
