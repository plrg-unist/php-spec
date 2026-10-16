#!/usr/bin/env python3
"""Reach a pending shared SEND, close transfer and owning-slot overwrite."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_shared_send_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
OBJECT = 'generator-pending-shared-send-object-buffer-consumed-by-direct-child-next'
CLOSE = 'generator-pending-shared-send-sole-receiver-closes-buffer-before-finally'
OVERWRITE = 'generator-pending-shared-send-overwritten-owning-buffer-native-discriminator'
EVENTS = {
    OBJECT: ['P|','O|','M|','C|','H|','1','|','S|','1','|','N|','R|','1','|','A|','D|','K|','V|','13','|','L|','F|','Q|','23','|','J|','Z|','T|','G|','31','|','E'],
    CLOSE: ['P|','O|','M|','C|','H|','1','|','T|','D|','J|','F|','S|','1','|','K|','E','A|'],
    OVERWRITE: ['P|','O|','M|','C|','H|','S|','1','|','N|','R|','1','|','2','|','T|','J|','F|','E|','A|'],
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
    'pending-shared-send-installs-one-used-slot-owner-without-advancing': {
        'source': SOURCES[OBJECT]['source'],
        'stage': 'S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])) :: ptask_tail* -- if pgeneratorop.NAME = "send"',
        'checks': [
            'S.FRAMES = eps', 'S.CURRENT = eps', 'S.ACTIVEFIBER = eps',
            'S.ORIGIN = (pgeneratorop.SITE)', 'pgeneratorop.LINE = 8',
            'pgeneratorop.ARGUMENTS = eps', '~pgeneratorop.ADVANCE',
            'S.GENERATORINPUTS = eps', 'n_middle = pgeneratorop.OBJECT',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.PENDING_INIT', '~pgenerator_middle.FIRST',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = (POBJECT n_leaf)',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.CURRENT = eps',
            'S.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf',
            'pgenerator_leaf.PHASE = GENERATOR_PAUSED',
            '~pgenerator_leaf.PENDING_INIT', '~pgenerator_leaf.FIRST',
            'pgenerator_leaf.FRAME = (pframe_leaf)',
            'pframe_leaf.ORIGIN = (porigin_yield)',
            'pgenerator_leaf.VALUE = (POBJECT n_cache)',
            '$generator_input_site(S, n_leaf, porigin_yield)',
            '$generator_input_tail(S, porigin_yield, pframe_leaf.TODO)',
            '$generator_send_leaf(S, n_middle, |S.OBJECTS|) = (n_leaf)',
            '$generator_send_leaf(S, n_middle, 0) = eps',
            'pgeneratorop_send = pgeneratorop[.ARGUMENTS = [POBJECT n_argument]]',
            '$generator_operation_valid(S, pgeneratorop_send)',
            '$generator_pending_shared_send(S, pgeneratorop_send)',
            '~$generator_pending_shared_send(S, pgeneratorop)',
            '~$generator_pending_shared_send(S, pgeneratorop_send[.LINE = $(pgeneratorop_send.LINE + 1)])',
            '~$generator_pending_shared_send(S, pgeneratorop_send[.SITE = porigin_yield])',
            '~$generator_pending_shared_send(S, pgeneratorop_send[.ARGUMENTS = [PNULL, PNULL]])',
            '~$generator_pending_shared_send(S, pgeneratorop_send[.NAME = "throw"])',
            '~$generator_pending_shared_send(S, pgeneratorop_send[.ADVANCE = true])',
            'S_clear = $generator_set(S, n_middle, pgenerator_middle[.PENDING_INIT = false])',
            '$heap_graph(S_clear) = $heap_graph(S)',
            '~$generator_pending_shared_send(S_clear, pgeneratorop_send)',
            'n_missing = |S.OBJECTS|',
            'S_missing = S[.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_missing)])) :: ptask_tail*]',
            '~$heap_valid($heap_graph(S_missing))',
            '$object_name(S, n_argument) = $ptascii("SharedSendPayload18")',
            '$object_name(S, n_cache) = $ptascii("SharedSendCache18")',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_leaf) = 2',
            'S.EVENTS = ' + outputs(EVENTS[OBJECT][:7]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = [pgeneratorinput]',
            'pgeneratorinput.OBJECT = n_leaf', 'pgeneratorinput.SITE = porigin_yield',
            'pgeneratorinput.SOURCE = pgeneratorop_send', 'pgeneratorinput.LIVE',
            '$generator_inputs_nodes(S_one.GENERATORINPUTS) = [HOBJECT n_argument]',
            '$generator_input_count(S_one.GENERATORINPUTS, n_leaf) = 1',
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]',
            'S_one.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.FRAMES = S.FRAMES',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_middle)]',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])',
            'pdestructionoperation.VALUE = KNOWN (POBJECT n_cache)',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_middle) = 3',
            '$heap_count(HOBJECT n_argument, $node_children(S_one, HOBJECT n_leaf)) = 0',
            'S_wrong = S_one[.GENERATORINPUTS = [pgeneratorinput[.SOURCE = pgeneratorop_send[.LINE = $(pgeneratorop_send.LINE + 1)]]]]',
            '$heap_graph(S_wrong) = $heap_graph(S_one)',
            '~$generator_inputs_valid(S_wrong, S_wrong.GENERATORINPUTS)',
            '~$call_descriptors_valid(S_wrong)',
            'S_duplicate = S_one[.GENERATORINPUTS = [pgeneratorinput, pgeneratorinput]]',
            '$heap_valid($heap_graph(S_duplicate))',
            '~$generator_inputs_valid(S_duplicate, S_duplicate.GENERATORINPUTS)',
            '~$call_descriptors_valid(S_duplicate)',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[OBJECT]),
            'S_done.GENERATORINPUTS = eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_leaf) = 0',
        ],
    },
    'close-preserves-the-unconsumed-slot-count-through-real-finally': {
        'source': SOURCES[CLOSE]['source'],
        'stage': 'S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: ptask_tail* -- if pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_leaf)) :: pdestructionjob_tail* -- if S.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf -- if pgenerator_leaf.PHASE = GENERATOR_PAUSED -- if S.GENERATORINPUTS = [pgeneratorinput] -- if pgeneratorinput.OBJECT = n_leaf -- if pgeneratorinput.LIVE -- if $heap_owners($heap_graph(S[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease[.JOBS = pdestructionjob_tail*]) :: ptask_tail*]), HOBJECT n_leaf) = 0',
        'checks': [
            'pgenerator_leaf.FRAME = (pframe_leaf)',
            'pframe_leaf.ORIGIN = (pgeneratorinput.SITE)',
            'pgenerator_leaf.VALUE = (POBJECT n_cache)',
            'pgeneratorinput.SOURCE.ARGUMENTS = [POBJECT n_argument]',
            '$generator_input_source_valid(S, pgeneratorinput)',
            '$generator_input_live_valid(S, pgeneratorinput)',
            '$generator_input_tail(S, pgeneratorinput.SITE, pframe_leaf.TODO)',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_argument]',
            '$generator_input_count(S.GENERATORINPUTS, n_leaf) = 1',
            '$object_name(S, n_argument) = $ptascii("SharedSolePayload18")',
            '$object_name(S, n_cache) = $ptascii("SharedSoleCache18")',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            '~(n_argument <- S.DESTRUCTION.CALLED)',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("middle")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            'S.EVENTS = ' + outputs(EVENTS[CLOSE][:10]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]',
            '$generator_inputs_nodes(S_one.GENERATORINPUTS) = [HOBJECT n_argument]',
            '$generator_input_count(S_one.GENERATORINPUTS, n_leaf) = 0',
            'S_one.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf[.FRAME = eps][.PHASE = GENERATOR_CLOSING]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease_inner) :: (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_caller*',
            'pgenrelease_inner.JOBS = eps',
            'pgenclose.OBJECT = n_leaf', 'pgenclose.STAGE = CLOSE_QUEUED',
            'pgenclose.FRAME = (pframe_leaf)',
            '$generator_close_enter_valid(S_one, pgenclose)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            '~(n_argument <- S_one.DESTRUCTION.CALLED)',
            'S_wrong = S_one[.GENERATORINPUTS = [pgeneratorinput[.LIVE = false][.SOURCE = pgeneratorinput.SOURCE[.LINE = $(pgeneratorinput.SOURCE.LINE + 1)]]]]',
            '$heap_graph(S_wrong) = $heap_graph(S_one)',
            '~$call_descriptors_valid(S_wrong)',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[CLOSE]),
            'S_done.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 1',
            'n_argument <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
        ],
    },
    'ordinary-child-send-orphans-the-old-slot-before-advancing': {
        'source': SOURCES[OVERWRITE]['source'],
        'stage': 'S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (PINT 7)])) :: ptask_tail* -- if pgeneratorop.NAME = "send" -- if S.GENERATORINPUTS = [pgeneratorinput] -- if pgeneratorinput.LIVE',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'pgeneratorop.LINE = 7', 'pgeneratorop.ARGUMENTS = eps',
            'n_leaf = pgeneratorop.OBJECT', 'pgeneratorinput.OBJECT = n_leaf',
            'pgeneratorinput.SOURCE.ARGUMENTS = [POBJECT n_argument]',
            'S.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf',
            'pgenerator_leaf.PHASE = GENERATOR_PAUSED',
            '~pgenerator_leaf.PENDING_INIT', '~pgenerator_leaf.FIRST',
            'pgenerator_leaf.VALUE = (PINT 1)',
            'pgenerator_leaf.FRAME = (pframe_leaf)',
            'pframe_leaf.ORIGIN = (pgeneratorinput.SITE)',
            '$generator_input_tail(S, pgeneratorinput.SITE, pframe_leaf.TODO)',
            '$generator_input_count(S.GENERATORINPUTS, n_leaf) = 1',
            'pgeneratorop_send = pgeneratorop[.ARGUMENTS = [PINT 7]]',
            '$generator_operation_valid(S, pgeneratorop_send)',
            '~$generator_pending_shared_send(S, pgeneratorop_send)',
            '$object_name(S, n_argument) = $ptascii("SharedOverwritePayload18")',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 1',
            '~(n_argument <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = ' + outputs(EVENTS[OVERWRITE][:9]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]',
            '$generator_input_count(S_one.GENERATORINPUTS, n_leaf) = 0',
            '$generator_inputs_nodes(S_one.GENERATORINPUTS) = [HOBJECT n_argument]',
            'S_one.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf[.FRAME = eps][.PHASE = GENERATOR_RUNNING][.FIRST = false]',
            'S_one.TODO = pframe_leaf.TODO',
            'S_one.RESULT = KNOWN (PINT 7)',
            'S_one.FRAMES = pframe_resumer :: pframe_tail*',
            'pframe_tail* = S.FRAMES',
            'pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_send) :: ptask_tail*',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_argument) = 1',
            '~(n_argument <- S_one.DESTRUCTION.CALLED)',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[OVERWRITE]),
            'S_done.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 1',
            'n_argument <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
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
