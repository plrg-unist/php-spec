#!/usr/bin/env python3
"""Reach no-copy NEXT with one LIVE input and its physical cache destructor."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_parked_pending_buffered_next_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
NEXT = 'generator-parked-pending-buffered-next-top-void-then-held-close'
DROP = 'generator-parked-pending-buffered-next-temporary-top-cache-cleanup'
EVENTS = {
    NEXT: ['P|', 'O|', 'TOP|', 'U|', 'L|', 'C|', 'S|', '1', '|', 'DROP|',
           'T|', 'CATCH|', '1', '|', '1', '|', 'N|', 'RET|', '1', '|', '1', '|',
           '1', '|', 'HELD|', '1', '|', 'EX|', 'OF|', 'OUT|', 'TF|', 'TOP-DROP|',
           'UF|', 'UP|', 'LF|', 'LOW|', 'CHILD|', 'A|', 'DROPPED|', 'E', 'B|'],
    DROP: ['P|', 'O|', 'TOP|', 'U|', 'L|', 'C|', 'S|', 'T|', 'CATCH|', '1', '|',
           '1', '|', 'N|', 'TAKE|', 'OF|', 'CLEARED|', 'D|', 'LF|', 'UF|', 'TF|',
           'CALLER|', '1', '|', '1', '|', '1', '|', 'E', 'B|'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def outputs(parts):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


BUDGET = [
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
    'S_one = S_one_budget[.COMPLETION = NORMAL]', 'S_one.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    'S_two_budget = $drive_steps(S_one, 1)',
    '$drive(S, 2) = S_two_budget',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
]
DONE = [
    'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
    'S_done.HELD = eps', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
]

CASES = {
    'parked-buffered-next-keeps-object-input-and-does-not-copy-cache': {
        'source': ROWS[NEXT]['source'],
        'stage': 'S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* -- if pgeneratorop.NAME = "next" -- if pgeneratorop.LINE = 12',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps', 'S.HELD = eps',
            'S.GENERATORRETURNRETAINED = eps', 'S.GENERATORLOOPRETAINED = eps',
            'S.RESULT = KNOWN PNULL', 'S.ORIGIN = (pgeneratorop.SITE)',
            'pgeneratorop.ARGUMENTS = eps', 'pgeneratorop.LOOP = eps',
            '~pgeneratorop.ADVANCE', '~pgeneratorop.BORROWED', '~pgeneratorop.STARTPACK',
            'n_top = pgeneratorop.OBJECT',
            'S.OBJECTS[n_top] = GENERATOR pgenerator_top',
            'pgenerator_top.PHASE = GENERATOR_DELEGATING',
            'pgenerator_top.PENDING_INIT', 'pgenerator_top.PARKED = eps',
            'pgenerator_top.DELEGATE = (pgeneratorfrom_top)',
            'pgeneratorfrom_top.INPUT = (POBJECT n_upper)',
            'pgeneratorfrom_top.CURRENT = eps', 'pgeneratorfrom_top.ACQUISITION = eps',
            '$generator_from_record_valid(S, n_top, pgenerator_top)',
            'pgenerator_top.FRAME = (pframe_top)', 'pframe_top.HELD = eps',
            '$tasks_nodes(pframe_top.TODO) = eps',
            'S.OBJECTS[n_upper] = GENERATOR pgenerator_upper',
            'pgenerator_upper.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_upper.PENDING_INIT', 'pgenerator_upper.PARKED = eps',
            'pgenerator_upper.DELEGATE = (pgeneratorfrom_upper)',
            'pgeneratorfrom_upper.INPUT = (POBJECT n_lower)',
            '$generator_from_record_valid(S, n_upper, pgenerator_upper)',
            'S.OBJECTS[n_lower] = GENERATOR pgenerator_lower',
            'pgenerator_lower.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_lower.PENDING_INIT', 'pgenerator_lower.PARKED = eps',
            'pgenerator_lower.DELEGATE = (pgeneratorfrom_lower)',
            'pgeneratorfrom_lower.INPUT = (POBJECT n_child)',
            '$generator_from_record_valid(S, n_lower, pgenerator_lower)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            '~pgenerator_child.PENDING_INIT', 'pgenerator_child.DELEGATE = eps',
            'pgenerator_child.PARKED = (porigin_yield)',
            'pgenerator_child.VALUE = (POBJECT n_cache)',
            'pgenerator_child.REFCELL = eps', 'pgenerator_child.KEY = (PINT 0)',
            'pgenerator_child.RETURN = eps', 'pgenerator_child.FRAME = (pframe_child)',
            'pframe_child.ORIGIN = (porigin_yield)', 'pframe_child.HELD = eps',
            '$tasks_nodes(pframe_child.TODO) = eps',
            'pframe_child.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_target* z_target) :: ptask_child*',
            '$generator_input_site(S, n_child, porigin_yield)',
            '$generator_input_tail(S, porigin_yield, pframe_child.TODO)',
            '$generator_parked_valid(S, pgenerator_child)',
            'S.GENERATORINPUTS = [pgeneratorinput]', 'pgeneratorinput.LIVE',
            'pgeneratorinput.OBJECT = n_child', 'pgeneratorinput.SITE = porigin_yield',
            'pgeneratorinput.SOURCE.OBJECT = n_lower', 'pgeneratorinput.SOURCE.NAME = "send"',
            'pgeneratorinput.SOURCE.LINE = 10',
            'pgeneratorinput.SOURCE.ARGUMENTS = [POBJECT n_payload]',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_input_count(S.GENERATORINPUTS, n_child) = 1',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_payload]',
            '$object_name(S, n_payload) = $ptascii("ParkedBufferedNextInput36")',
            '$object_name(S, n_cache) = $ptascii("ParkedBufferedNextCache36")',
            '$node_children(S, HOBJECT n_child) = [HOBJECT n_cache]',
            '$heap_count(HOBJECT n_payload, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_top) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_upper) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_lower) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = (n_outer_cell)',
            'S.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)',
            'S.OBJECTS[n_outer] = GENERATOR pgenerator_outer',
            '~pgenerator_outer.PENDING_INIT',
            '$heap_owners($heap_graph(S), HOBJECT n_outer) = 1',
            '$lookup(S_global.ENV, $ptascii("injected")) = (n_injected_cell)',
            '$lookup(S_global.ENV, $ptascii("caught")) = (n_caught_cell)',
            'S.STORE[n_injected_cell] = DEFINED (POBJECT n_exception)',
            'S.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
            '$string_bytes($throwable_field(S, n_exception, "message")) = ($ptascii("park36"))',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '$generator_operation_valid(S, pgeneratorop)',
            '$generator_pending_resume(S, pgeneratorop)',
            '$generator_pending_parked_next(S, pgeneratorop)',
            '~$generator_pending_parked_send(S, pgeneratorop)',
            '$generator_from_leaf(S, n_top, $(|S.OBJECTS| + 1)) = n_child',
            '$generator_buffered_next_leaf(S, n_top, $(|S.OBJECTS| + 1)) = eps',
            'S_view = $generator_set(S, n_child, pgenerator_child[.PARKED = eps])',
            '$heap_graph(S_view) = $heap_graph(S)',
            '$generator_buffered_next_leaf(S_view, n_top, 0) = eps',
            '$generator_buffered_next_leaf(S_view, n_top, 3) = eps',
            '$generator_buffered_next_leaf(S_view, n_top, 4) = (n_child)',
            '$generator_buffered_next_leaf(S_view, n_outer, 5) = (n_child)',
            '~$generator_pending_parked_next(S, pgeneratorop[.LINE = 0])',
            '~$generator_pending_parked_next(S, pgeneratorop[.ARGUMENTS = [PNULL]])',
            '~$generator_pending_parked_next(S, pgeneratorop[.NAME = "send"])',
            '~$generator_pending_parked_next(S, pgeneratorop[.ADVANCE = true])',
            '~$generator_pending_parked_next(S, pgeneratorop[.BORROWED = true])',
            '~$generator_pending_parked_next(S, pgeneratorop[.STARTPACK = true])',
            'S_clear = $generator_set(S, n_top, pgenerator_top[.PENDING_INIT = false])',
            '$heap_graph(S_clear) = $heap_graph(S)',
            '~$generator_pending_parked_next(S_clear, pgeneratorop)',
            'S_blocked = $generator_resume(S_clear, pgeneratorop)',
            'S_blocked.COMPLETION = UNSUPPORTED "Generator resume after pending throw"',
            'S_badinput = S[.GENERATORINPUTS = [pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = 0]]]]',
            '$heap_graph(S_badinput) = $heap_graph(S)',
            '~$generator_pending_parked_next(S_badinput, pgeneratorop)',
            'S_orphan = S[.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]]',
            '$heap_graph(S_orphan) = $heap_graph(S)',
            '~$generator_pending_parked_next(S_orphan, pgeneratorop)',
            'S_duplicate = S[.GENERATORINPUTS = [pgeneratorinput, pgeneratorinput]]',
            '~$generator_pending_parked_next(S_duplicate, pgeneratorop)',
            'S_scalar = S[.GENERATORINPUTS = [pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.ARGUMENTS = [PINT 9]]]]]',
            '$generator_inputs_valid(S_scalar, S_scalar.GENERATORINPUTS)',
            '~$generator_pending_parked_next(S_scalar, pgeneratorop)',
            'pframe_wrong = pframe_child[.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME $ptascii("wrong36") z_target) :: ptask_child*]',
            'S_wrong = $generator_set(S, n_child, pgenerator_child[.FRAME = (pframe_wrong)])',
            '$heap_graph(S_wrong) = $heap_graph(S)',
            '~$generator_pending_parked_next(S_wrong, pgeneratorop)',
            'S_held = $generator_set(S, n_top, pgenerator_top[.FRAME = (pframe_top[.HELD = [HOBJECT n_payload]])])',
            '~$generator_pending_parked_next(S_held, pgeneratorop)',
            'S.EVENTS = ' + outputs(EVENTS[NEXT][:17]),
            *BUDGET,
            'S_expected = $generator_set(S, n_top, pgenerator_top[.PENDING_INIT = false])',
            'S_one.OBJECTS = S_expected.OBJECTS',
            'S_one.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'S_one.GENERATORINPUTS = S.GENERATORINPUTS',
            '$generator_input_live_valid(S_one, pgeneratorinput)',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.CURRENT = S.CURRENT',
            'S_one.FRAMES = S.FRAMES', '$heap_graph(S_one) = $heap_graph(S)',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_top)]',
            'pdestructionrelease.USER', 'pdestructionrelease.CALLER = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps eps',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.PENDING = eps', 'pdestructionoperation.COMPLETION = NORMAL',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
            '~$generator_pending_parked_next(S_one, pgeneratorop)',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[NEXT]),
            'S_done.GENERATORINPUTS = [pgeneratorinput[.LIVE = false]]',
            '$generator_inputs_valid(S_done, S_done.GENERATORINPUTS)',
            'S_done.GENERATORRETURNRETAINED = eps', 'S_done.GENERATORLOOPRETAINED = eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_lower) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_upper) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_top) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_outer) <- S_done.ALLOCATIONS)',
            'n_cache <- S_done.DESTRUCTION.CALLED', 'n_payload <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'parked-buffered-next-cache-destructor-precedes-ancestor-finalizers': {
        'source': ROWS[DROP]['source'],
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) -- if $object_name(S, n_cache) = $ptascii("ParkedBufferedNextReplaceCache36") -- if S.FRAMES = pframe_caller :: pframe_tail* -- if pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_return* -- if pdestructorcall.OPERATION = (pdestructionoperation)',
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps',
            'S.GENERATORRETURNRETAINED = eps', 'S.GENERATORLOOPRETAINED = eps',
            'S.GENERATORINPUTS = [pgeneratorinput]', '~pgeneratorinput.LIVE',
            'n_child = pgeneratorinput.OBJECT', 'n_lower = pgeneratorinput.SOURCE.OBJECT',
            'pgeneratorinput.SOURCE.NAME = "send"', 'pgeneratorinput.SOURCE.LINE = 11',
            'pgeneratorinput.SOURCE.ARGUMENTS = [POBJECT n_payload]',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_input_count(S.GENERATORINPUTS, n_child) = 0',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HOBJECT n_payload]',
            '$object_name(S, n_payload) = $ptascii("ParkedBufferedNextLate36")',
            '$heap_count(HOBJECT n_payload, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '~(n_payload <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED', 'pgenerator_child.FRAME = eps',
            'pgenerator_child.PARKED = eps', 'pgenerator_child.DELEGATE = eps',
            'pgenerator_child.VALUE = (POBJECT n_cache)',
            '[pgenstorage] = $generator_storage_tasks(S.TODO) ++ $generator_storage_frames(S.FRAMES)',
            'pgenstorage.OBJECT = n_child', 'pgenstorage.NEXT = 2',
            'pgenstorage.USER', 'pgenstorage.CALLER = eps',
            '$generator_storage_for(S, n_child) = (pgenstorage)',
            '$generator_storage_basic(S, pgenstorage)',
            '(HOBJECT n_child) <- S.ALLOCATIONS',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$node_children(S, HOBJECT n_child) = eps',
            'n_child <- S.DESTRUCTION.CALLED',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps eps',
            'n_top = pgeneratorop.OBJECT', 'pgeneratorop.NAME = "next"',
            'pgeneratorop.LINE = 13', 'pgeneratorop.ARGUMENTS = eps',
            'pgeneratorop.LOOP = eps', '~pgeneratorop.ADVANCE',
            '~pgeneratorop.STARTPACK', '~pgeneratorop.BORROWED',
            '$getter_arguments(S, pgeneratorop.SITE) = PCALLARGUMENTS eps 2',
            'S.OBJECTS[n_top] = GENERATOR pgenerator_top',
            'pgenerator_top.PHASE = GENERATOR_CLOSING', 'pgenerator_top.FRAME = eps',
            'S.OBJECTS[n_lower] = GENERATOR pgenerator_lower',
            'pgenerator_lower.PHASE = GENERATOR_CLOSING', 'pgenerator_lower.FRAME = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_top) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_lower) = 1',
            'nat_claims* = $generator_close_claims(S.TODO) ++ $generator_close_frame_claims(S.FRAMES)',
            '$generator_id_count(nat_claims*, n_top) = 1',
            '$generator_id_count(nat_claims*, n_lower) = 1',
            'pcallcontext.INSTANCE = eps', 'pdestructorcall.OBJECT = n_cache',
            'pdestructorcall.CALLER = eps', 'pdestructorcall.PENDING = eps',
            'pframe_caller.CONTEXT = eps', 'pdestructionoperation.CALLER = eps',
            'pdestructionoperation.VALUE = KNOWN PNULL', 'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.COMPLETION = NORMAL', 'pdestructionoperation.NOGC = eps',
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) <- pframe_caller.TODO',
            '$destructor_operation_live(S, pdestructionoperation)',
            '~$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_call_live(S, pdestructorcall)',
            '$destructor_context_valid(S, pcallcontext)',
            'S_caller = $constant_frame_scope(S, pframe_caller, pframe_tail*)',
            '$generator_storage_tail(pframe_caller.TODO, pgenstorage) = (ptask_storage_tail*)',
            '$generator_storage_parent(S_caller, pgenstorage, ptask_storage_tail*)',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("outer")) = eps',
            '$lookup(S_global.ENV, $ptascii("top")) = eps',
            '$lookup(S_global.ENV, $ptascii("upper")) = eps',
            '$lookup(S_global.ENV, $ptascii("lower")) = eps',
            '$lookup(S_global.ENV, $ptascii("child")) = eps',
            '$lookup(S_global.ENV, $ptascii("injected")) = (n_injected_cell)',
            '$lookup(S_global.ENV, $ptascii("caught")) = (n_caught_cell)',
            'S.STORE[n_injected_cell] = DEFINED (POBJECT n_old_exception)',
            'S.STORE[n_caught_cell] = DEFINED (POBJECT n_old_exception)',
            '$string_bytes($throwable_field(S, n_old_exception, "message")) = ($ptascii("old36"))',
            '$throwable_field(S, n_old_exception, "previous") = PNULL',
            '$heap_owners($heap_graph(S), HOBJECT n_old_exception) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            'S_badsource = S[.GENERATORINPUTS = [pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = 0]]]]',
            '$heap_graph(S_badsource) = $heap_graph(S)',
            '~$generator_inputs_valid(S_badsource, S_badsource.GENERATORINPUTS)',
            '~$call_descriptors_valid(S_badsource)',
            'S_revived = S[.GENERATORINPUTS = [pgeneratorinput[.LIVE = true]]]',
            '$heap_graph(S_revived) = $heap_graph(S)',
            '~$generator_inputs_valid(S_revived, S_revived.GENERATORINPUTS)',
            '~$call_descriptors_valid(S_revived)',
            'S.EVENTS = ' + outputs(EVENTS[DROP][:17]),
            *BUDGET,
            'S_one.GENERATORINPUTS = S.GENERATORINPUTS',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$generator_storage_for(S_one, n_child) = (pgenstorage)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_old_exception) = 2',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[DROP]),
            'S_done.GENERATORINPUTS = S.GENERATORINPUTS',
            '$generator_inputs_valid(S_done, S_done.GENERATORINPUTS)',
            'S_done.GENERATORRETURNRETAINED = eps', 'S_done.GENERATORLOOPRETAINED = eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old_exception) = 0',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_lower) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_top) <- S_done.ALLOCATIONS)',
            'n_cache <- S_done.DESTRUCTION.CALLED', 'n_payload <- S_done.DESTRUCTION.CALLED',
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
