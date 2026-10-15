#!/usr/bin/env python3
"""Reach pending initialization close and a direct next that does not advance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_nested_detached_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
BUDGET = [
    'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
    'S_one = S_one_budget[.COMPLETION = NORMAL]',
    'S_one.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    'S_two_budget = $drive_steps(S_one, 1)',
    '$drive(S, 2) = S_two_budget',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
]
DONE = [
    'S_done = $drive(S_one, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
    'n_cache <- S_done.DESTRUCTION.CALLED',
]
CASES = {
    'inherited-init-detached-middle-close-skips-finally-with-real-cache-owner': {
        'source': SOURCES['generator-nested-detached-unpack-two-active-links-unowned-middle-close'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
                  '-- if $trace_context_function(S, pgenclose.CONTEXT) = $ptascii("nestedUnownedMiddle16")'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'n_middle = pgenclose.OBJECT',
            'pgenclose.STAGE = CLOSE_QUEUED', 'pgenclose.PENDING = eps',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_CLOSING',
            'pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.FRAME = eps',
            'pgenerator_middle.VALUE = eps', 'pgenerator_middle.REFCELL = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            'pgeneratorfrom.ACQUISITION = eps',
            '$object_name(S, n_cache) = $ptascii("NestedUnownedCache16")',
            '$generator_own_cache(pgenerator_middle)',
            '$generator_close_pending_init(S, pgenclose)',
            '$generator_close_enter_valid(S, pgenclose)',
            'pgenclose.FRAME = (pframe)',
            'pframe.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom.SITE n_child (PINT 23)) :: ptask_middle*',
            '~$generator_from_complete_valid(S, n_middle, pgeneratorfrom.SITE, n_child, PINT 23)',
            '$generator_close_drop_claim(S, pframe.TODO, n_middle, pgeneratorfrom.SITE) = ptask_middle*',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.RETURN = (PINT 23)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '$node_children(S, HOBJECT n_middle) = [HOBJECT n_cache]',
            'S_clear = $generator_set(S, n_middle, pgenerator_middle[.PENDING_INIT = false])',
            '$heap_graph(S_clear) = $heap_graph(S)',
            '~$generator_close_pending_init(S_clear, pgenclose)',
            'S_empty = $generator_set(S, n_middle, pgenerator_middle[.DELEGATE = (pgeneratorfrom[.CURRENT = eps])])',
            '~$generator_close_pending_init(S_empty, pgenclose)',
            'S_null = $generator_set(S, n_middle, pgenerator_middle[.DELEGATE = (pgeneratorfrom[.CURRENT = (KNOWN PNULL)])])',
            '$generator_close_pending_init(S_null, pgenclose)',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("12"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|")]',
            *VALID, *BUDGET,
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_closed',
            'pgenerator_closed.PHASE = GENERATOR_CLOSED',
            '~pgenerator_closed.PENDING_INIT',
            'pgenerator_closed.FRAME = eps',
            'pgenerator_closed.DELEGATE = pgenerator_middle.DELEGATE',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 1',
            'S_one.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_DONE pgenclose_done) :: ptask_tail*',
            'pgenrelease.JOBS = $destruction_values($generator_close_frame_nodes(S, pframe))',
            'pgenclose_done.OBJECT = n_middle',
            'pgenclose_done.STAGE = CLOSE_FINISHED',
            'pgenclose_done.FRAME = eps',
            '$generator_close_done_valid(S_one, pgenclose_done)',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("A|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("Z|"), OUTPUT $ptascii("E")]',
        ],
    },
    'direct-middle-next-consumes-init-without-return-or-tail-execution': {
        'source': SOURCES['generator-nested-detached-unpack-direct-next-clears-pending-init-without-advancing'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "next" '
                  '-- if $lookup(S.ENV, $ptascii("middle")) = (n_cell) '
                  '-- if S.STORE[n_cell] = DEFINED (POBJECT pgeneratorop.OBJECT)'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'n_middle = pgeneratorop.OBJECT',
            'pgeneratorop.LINE = 11',
            '~pgeneratorop.STARTPACK', '~pgeneratorop.BORROWED',
            '$generator_operation_valid(S, pgeneratorop)',
            '$generator_resume_root(S, pgeneratorop)',
            '$generator_pending_resume(S, pgeneratorop)',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            'pgeneratorfrom.ACQUISITION = eps',
            'pgenerator_middle.FRAME = (pframe)',
            'pframe.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom.SITE n_child (PINT 23)) :: ptask_middle*',
            '$generator_from_complete_valid(S, n_middle, pgeneratorfrom.SITE, n_child, PINT 23)',
            '$generator_own_cache(pgenerator_middle)',
            '$generator_cache_present(S, n_middle)',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            '$generator_pending_resume(S, pgeneratorop[.NAME = "send"])',
            'S_send = $generator_resume(S, pgeneratorop[.NAME = "send"])',
            'S_send.COMPLETION = UNSUPPORTED "Generator pending initialization send or throw"',
            'S_send[.COMPLETION = NORMAL] = S',
            'S_throw = $generator_resume(S, pgeneratorop[.NAME = "throw"])',
            'S_throw.COMPLETION = UNSUPPORTED "Generator pending initialization send or throw"',
            'S_throw[.COMPLETION = NORMAL] = S',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("O|"), OUTPUT $ptascii("H|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("L|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("HELD|")]',
            *VALID, *BUDGET,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_middle)]',
            'pdestructionrelease.CALLER = eps',
            'pdestructionrelease.USER',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps eps',
            'pdestructionoperation.PENDING = eps',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            'S_one.FRAMES = eps', 'S_one.CURRENT = eps',
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            '~$generator_pending_resume(S_one, pgeneratorop)',
            *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("Q|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("13"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("J|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("Z|"), OUTPUT $ptascii("E")]',
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
