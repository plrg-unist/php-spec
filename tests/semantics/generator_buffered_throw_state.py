#!/usr/bin/env python3
"""Buffered THROW slot retirement and replacement-exception fronts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_buffered_throw_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
DIRECT = 'generator-buffered-throw-direct-child-releases-payload-before-catch'
REPLACE = 'generator-buffered-throw-payload-destructor-replaces-injected-exception'
EVENTS = {
    DIRECT: ['P|', 'O|', 'M|', 'C|', 'H|', '1', '|', 'S|', '5', '|', 'T|',
             'D|', 'CA|', 'SAME|', 'K|', '13', '|', 'TAIL|', 'F|', 'MR|',
             '17', '|', 'J|', 'OR|', '23', '|', 'Z|', 'Q|', '29', '|', 'E'],
    REPLACE: ['P|', 'O|', 'M|', 'C|', 'H|', '1', '|', 'S|', '7', '|', 'T|',
              'D|', 'CA|', 'REPLACED|', 'PREV|', 'END|', 'K|', '11', '|',
              'TAIL|', 'F|', 'MR|', '19', '|', 'J|', 'OR|', '31', '|',
              'Z|', 'Q|', '37', '|', 'E'],
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
    'direct-buffered-throw-moves-only-the-slot-owner-into-temp-release': {
        'source': ROWS[DIRECT]['source'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_exception)])) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "throw" -- if S.GENERATORINPUTS = [pgeneratorinput] '
                  '-- if pgeneratorinput.LIVE'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'pgeneratorop.LINE = 8', 'pgeneratorop.ARGUMENTS = eps',
            'n_child = pgeneratorop.OBJECT', 'pgeneratorinput.OBJECT = n_child',
            'pgeneratorinput.SOURCE.NAME = "send"', 'pgeneratorinput.SOURCE.LINE = 7',
            'pgeneratorinput.SOURCE.ARGUMENTS = [POBJECT n_payload]',
            '$object_name(S, n_payload) = $ptascii("BufferedThrowPayload20")',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_count(HOBJECT n_payload, $generator_inputs_nodes(S.GENERATORINPUTS)) = 1',
            '$heap_count(HOBJECT n_payload, $node_children(S, HOBJECT n_child)) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED', 'pgenerator_child.DELEGATE = eps',
            '~pgenerator_child.PENDING_INIT', '~pgenerator_child.FIRST',
            'pgenerator_child.VALUE = (PINT 5)', 'pgenerator_child.KEY = (PINT 0)',
            'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (pgeneratorinput.SITE)',
            'pframe_child.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_name* z_write) :: ptask_child*',
            '$generator_input_tail(S, pgeneratorinput.SITE, pframe_child.TODO)',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            'pgeneratorop_throw = pgeneratorop[.ARGUMENTS = [POBJECT n_exception]]',
            '$generator_operation_valid(S, pgeneratorop_throw)',
            '$generator_input_throw_ready(S, pgeneratorop_throw)',
            '~$generator_pending_resume(S, pgeneratorop_throw)',
            '~$generator_input_blocked(S, pgeneratorop_throw)',
            '$generator_input_throw_value(S, S.TODO[0]) = (POBJECT n_payload)',
            '~$generator_input_throw_ready(S, pgeneratorop)',
            '~$generator_input_throw_ready(S, pgeneratorop_throw[.NAME = "send"])',
            '~$generator_input_throw_ready(S, pgeneratorop_throw[.LINE = 0])',
            '~$generator_input_throw_ready(S, pgeneratorop_throw[.SITE = pgeneratorinput.SITE])',
            '~$generator_input_throw_ready(S, pgeneratorop_throw[.ADVANCE = true])',
            '~$generator_input_throw_ready(S, pgeneratorop_throw[.BORROWED = true])',
            '~$generator_input_throw_ready(S, pgeneratorop_throw[.STARTPACK = true])',
            '~$generator_input_throw_ready(S, pgeneratorop_throw[.ARGUMENTS = [PINT 1]])',
            '~$generator_input_throw_ready(S, pgeneratorop_throw[.ARGUMENTS = [POBJECT n_exception, PNULL]])',
            'S_pending = $generator_set(S, n_child, pgenerator_child[.PENDING_INIT = true])',
            '$heap_graph(S_pending) = $heap_graph(S)',
            '$generator_pending_resume(S_pending, pgeneratorop_throw)',
            '~$generator_input_throw_ready(S_pending, pgeneratorop_throw)',
            '$generator_input_blocked(S_pending, pgeneratorop_throw)',
            'S_orphan = S[.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]]',
            '$heap_graph(S_orphan) = $heap_graph(S)',
            '$generator_input_take(S_orphan.GENERATORINPUTS, n_child) = (eps, S_orphan.GENERATORINPUTS)',
            '~$generator_input_throw_ready(S_orphan, pgeneratorop_throw)',
            'S_bad = S[.GENERATORINPUTS = [pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = 0]]]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$generator_input_throw_ready(S_bad, pgeneratorop_throw)',
            '~$call_descriptors_valid(S_bad)',
            'S.EVENTS = ' + outputs(EVENTS[DIRECT][:11]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = eps', 'S_one.RESULT = KNOWN PNULL',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: pframe_child.TODO',
            'pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HOBJECT n_payload)]',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_exception)])',
            'pdestructionoperation.CALLER = S_one.CURRENT',
            'pdestructionoperation.ORIGIN = (pgeneratorinput.SITE)',
            'pdestructionoperation.PENDING = (n_exception)',
            'pdestructionoperation.VALUE = KNOWN PNULL', 'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.NOGC = ({OPERAND KNOWN (POBJECT n_payload), PENDING true})',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation)',
            '$generator_input_throw_receipt(S_one, pdestructionoperation)',
            'S_one.CURRENT = pframe_child.CONTEXT',
            'S_one.FRAMES = pframe_resumer :: S.FRAMES',
            'pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_throw) :: ptask_tail*',
            'pframe_resumer.CONTEXT = S.CURRENT',
            'S_expected = $generator_set(S, n_child, pgenerator_child[.FRAME = eps][.PHASE = GENERATOR_RUNNING])',
            'S_one.OBJECTS = S_expected.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.GC = S.GC',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 3',
            '$heap_count(HOBJECT n_payload, $task_nodes(DESTRUCTOR_RELEASE pdestructionrelease)) = 1',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[DIRECT]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            'n_payload <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'slot-destructor-replacement-is-pending-before-real-child-catch': {
        'source': ROWS[REPLACE]['source'],
        'stage': ('S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_original)]) '
                  '-- if pgeneratorop.NAME = "throw" -- if pdestructionoperation.PENDING = (n_replacement) '
                  '-- if n_replacement =/= n_original'),
        'checks': [
            'S.GENERATORINPUTS = eps', 'S.ACTIVEFIBER = eps',
            'pgeneratorop.LINE = 8', 'pgeneratorop.ARGUMENTS = eps',
            'n_child = pgeneratorop.OBJECT',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_RUNNING', 'pgenerator_child.FRAME = eps',
            '~pgenerator_child.PENDING_INIT', 'pgenerator_child.VALUE = (PINT 7)',
            'S.CURRENT = (pcallcontext)', 'pdestructionoperation.CALLER = (pcallcontext)',
            'pdestructionoperation.ORIGIN = S.ORIGIN', 'S.ORIGIN = (porigin_yield)',
            '$generator_input_site(S, n_child, porigin_yield)',
            '$generator_input_tail(S, porigin_yield, ptask_tail*)',
            'pdestructionoperation.COMPLETION = NORMAL', 'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.NOGC = ({OPERAND KNOWN (POBJECT n_payload), PENDING false})',
            '$object_name(S, n_payload) = $ptascii("BufferedThrowReplacementPayload20")',
            'n_payload <- S.DESTRUCTION.CALLED', '~((HOBJECT n_payload) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 0',
            '$throwable_field(S, n_replacement, "previous") = POBJECT n_original',
            '$throwable_field(S, n_original, "previous") = PNULL',
            '$string_bytes($throwable_field(S, n_original, "message")) = ($ptascii("injected20"))',
            '$string_bytes($throwable_field(S, n_replacement, "message")) = ($ptascii("replacement20"))',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_replacement) = 2',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$gc_operation_metadata_valid(S, pdestructionoperation)',
            '$generator_input_throw_receipt(S, pdestructionoperation)',
            'S.EVENTS = ' + outputs(EVENTS[REPLACE][:12]),
            *VALID, *BUDGET,
            'S_one.TODO = (THROW_SEARCH n_replacement) :: ptask_tail*',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.FRAMES = S.FRAMES',
            'S_one.CURRENT = S.CURRENT', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.GENERATORINPUTS = eps',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_replacement) = 2',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[REPLACE]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_original) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_replacement) = 0',
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
