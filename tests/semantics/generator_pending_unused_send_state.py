#!/usr/bin/env python3
"""Pending unused SEND owner retirement and sole-receiver close fronts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_unused_send_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
SCALAR = 'generator-pending-unused-send-scalar-cache-and-forwarded-next'
CLOSE = 'generator-pending-unused-send-sole-receiver-cache-snapshot-and-close'
EVENTS = {
    SCALAR: ['P|','O|','M|','C|','H|','1','|','A|','S|','5','|','N|','R|','V|','13','|','L|','F|','Q|','23','|','J|','Z|','T|','G|','31','|','E'],
    CLOSE: ['P|','O|','M|','C|','H|','1','|','T|','D|','A|','J|','F|','S|','1','|','K|','E'],
}
assert all(''.join(parts) == SOURCES[name]['native_stdout'] for name, parts in EVENTS.items())


def outputs(parts):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
BUDGET = [
    'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
    'S_one = S_one_budget[.COMPLETION = NORMAL]',
    'S_one.EVENTS = S.EVENTS',
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
    'pending-unused-send-retires-argument-without-buffering-or-advancing': {
        'source': SOURCES[SCALAR]['source'],
        'stage': 'S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])) :: ptask_tail* -- if pgeneratorop.NAME = "send"',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'pgeneratorop.LINE = 7', 'pgeneratorop.ARGUMENTS = eps',
            'S.ORIGIN = (pgeneratorop.SITE)', 'S.GENERATORINPUTS = eps',
            'n_middle = pgeneratorop.OBJECT',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.PENDING_INIT', '~pgenerator_middle.FIRST',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_leaf)',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.CURRENT = eps',
            'S.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf',
            'pgenerator_leaf.PHASE = GENERATOR_PAUSED',
            '~pgenerator_leaf.PENDING_INIT', '~pgenerator_leaf.FIRST',
            'pgenerator_leaf.VALUE = (PINT 5)',
            'pgenerator_leaf.FRAME = (pframe_leaf)',
            'pframe_leaf.ORIGIN = (porigin_yield)',
            'pframe_leaf.TODO = (ORIGIN_RETURN (porigin_statement)) :: DISCARD :: ptask_after*',
            '$generator_unused_send_tail(S, porigin_yield, pframe_leaf.TODO)',
            '~$generator_send_target(pframe_leaf.TODO)',
            '$generator_unused_send_leaf(S, n_middle, |S.OBJECTS|) = (n_leaf)',
            '$generator_unused_send_leaf(S, n_middle, 0) = eps',
            '$generator_send_leaf(S, n_middle, |S.OBJECTS|) = eps',
            'pgeneratorop_send = pgeneratorop[.ARGUMENTS = [POBJECT n_argument]]',
            '$generator_operation_valid(S, pgeneratorop_send)',
            '$generator_pending_unused_send(S, pgeneratorop_send)',
            '~$generator_pending_shared_send(S, pgeneratorop_send)',
            '~$generator_pending_detached_send(S, pgeneratorop_send)',
            '~$generator_pending_unused_send(S, pgeneratorop)',
            '~$generator_pending_unused_send(S, pgeneratorop_send[.LINE = $(pgeneratorop_send.LINE + 1)])',
            '~$generator_pending_unused_send(S, pgeneratorop_send[.SITE = porigin_yield])',
            '~$generator_pending_unused_send(S, pgeneratorop_send[.ARGUMENTS = [PNULL, PNULL]])',
            '~$generator_pending_unused_send(S, pgeneratorop_send[.NAME = "throw"])',
            '~$generator_pending_unused_send(S, pgeneratorop_send[.ADVANCE = true])',
            'S_clear = $generator_set(S, n_middle, pgenerator_middle[.PENDING_INIT = false])',
            '$heap_graph(S_clear) = $heap_graph(S)',
            '~$generator_pending_unused_send(S_clear, pgeneratorop_send)',
            'pframe_wrong = pframe_leaf[.TODO = DISCARD :: ptask_after*]',
            'S_wrong = $generator_set(S, n_leaf, pgenerator_leaf[.FRAME = (pframe_wrong)])',
            '$heap_graph(S_wrong) = $heap_graph(S)',
            '~$generator_unused_send_tail(S_wrong, porigin_yield, pframe_wrong.TODO)',
            '$generator_unused_send_leaf(S_wrong, n_middle, |S.OBJECTS|) = eps',
            '~$generator_pending_unused_send(S_wrong, pgeneratorop_send)',
            'n_missing = |S.OBJECTS|',
            'S_missing = S[.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_missing)])) :: ptask_tail*]',
            '~$heap_valid($heap_graph(S_missing))',
            '$object_name(S, n_argument) = $ptascii("UnusedSendPayload19")',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_leaf) = 2',
            'S.EVENTS = ' + outputs(EVENTS[SCALAR][:7]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = S.GENERATORINPUTS',
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]',
            'S_one.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.FRAMES = S.FRAMES',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HOBJECT n_middle)]',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])',
            'pdestructionoperation.VALUE = KNOWN (PINT 5)',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_middle) = 3',
            '$heap_count(HOBJECT n_argument, $node_children(S_one, HOBJECT n_leaf)) = 0',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[SCALAR]),
            'S_done.GENERATORINPUTS = eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_leaf) = 0',
        ],
    },
    'ignored-argument-is-gone-before-sole-middle-finally': {
        'source': SOURCES[CLOSE]['source'],
        'stage': 'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* -- if pgenclose.STAGE = CLOSE_QUEUED -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail* -- if pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)]) -- if pgenclose.OBJECT = pgeneratorop.OBJECT',
        'checks': [
            'n_middle = pgenclose.OBJECT',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_CLOSING',
            '~pgenerator_middle.PENDING_INIT', 'pgenerator_middle.FRAME = eps',
            'pgenclose.FRAME = (pframe_middle)', 'pgenclose.PENDING = eps',
            '$generator_close_enter_valid(S, pgenclose)',
            '~$generator_close_pending_init(S, pgenclose)',
            'pgeneratorop.NAME = "send"', 'pgeneratorop.LINE = 9',
            'pdestructionoperation.VALUE = KNOWN (POBJECT n_cache)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$object_name(S, n_argument) = $ptascii("UnusedSolePayload19")',
            '$object_name(S, n_cache) = $ptascii("UnusedSoleCache19")',
            '~((HOBJECT n_argument) <- S.ALLOCATIONS)',
            'n_argument <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            'S.GENERATORINPUTS = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("middle")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '~$generator_pending_unused_send(S, pgeneratorop[.ARGUMENTS = [POBJECT n_argument]])',
            'S.EVENTS = ' + outputs(EVENTS[CLOSE][:10]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = eps',
            '$heap_owners($heap_graph(S_one), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            'n_argument <- S_one.DESTRUCTION.CALLED',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[CLOSE]),
            'S_done.GENERATORINPUTS = eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
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
