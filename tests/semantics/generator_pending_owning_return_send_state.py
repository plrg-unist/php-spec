#!/usr/bin/env python3
"""Reach pending owning-return SEND and actual replacement-cache cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_pending_owning_return_send_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
CONSUME = 'generator-pending-owning-return-send-object-next-consumption'
REPLACE = 'generator-pending-owning-return-send-sole-receiver-replacement'
EVENTS = {
    CONSUME: ['P|','O|','M|','C|','L|','H|','1','|','T|','S|','V|','1','|K|','1','|',
              'BODY|','1','|','R|','DROP|','N|','31','|','TAIL|','J|','OUTER|','29','|',
              'F|','DONE|','1','|','GONE|','A|','E'],
    REPLACE: ['P|','O|','M|','C|','L|','H|','1','|','T|','F|','DROP|','S|','J|','D|',
              'CALLER|','1','|','1','|','E','R|'],
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
    'pending-send-preserves-the-owning-complete-until-real-next': {
        'source': ROWS[CONSUME]['source'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "send"'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GC.ACTIVE = eps', 'S.GENERATORRETURNRETAINED = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'S.ORIGIN = (pgeneratorop.SITE)', 'S.RESULT = KNOWN PNULL',
            'pgeneratorop.LINE = 10', 'pgeneratorop.ARGUMENTS = eps',
            'pgeneratorop.LOOP = eps', '~pgeneratorop.BORROWED',
            '~pgeneratorop.STARTPACK', '~pgeneratorop.ADVANCE',
            'n_middle = pgeneratorop.OBJECT',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_DELEGATING',
            'pgenerator_middle.PENDING_INIT', '~pgenerator_middle.FIRST',
            'pgenerator_middle.PARKED = eps',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            'pgeneratorfrom.POSITION = 1', 'pgenerator_middle.FRAME = (pframe_middle)',
            'pframe_middle.HELD = eps', 'pframe_middle.ORIGIN = (pgeneratorfrom.SITE)',
            'pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom.SITE n_child (POBJECT n_return)) :: ptask_used_tail*',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom.SITE n_child (POBJECT n_return)',
            '$generator_input_tail(S, pgeneratorfrom.SITE, ptask_used_tail*)',
            '$tasks_nodes(ptask_used_tail*) = eps',
            '$generator_from_complete_valid(S, n_middle, pgeneratorfrom.SITE, n_child, POBJECT n_return)',
            '$generator_return_receipt(S, n_middle, pgeneratorfrom.SITE, n_child, POBJECT n_return)',
            '$generator_return_waiting(S, n_middle)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.RETURN = (POBJECT n_return)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$object_name(S, n_return) = $ptascii("PendingOwningReturn28")',
            '$object_name(S, n_cache) = $ptascii("PendingOwningCache28")',
            '$object_name(S, n_argument) = $ptascii("PendingOwningArgument28")',
            '$heap_owners($heap_graph(S), HOBJECT n_return) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 3',
            '$heap_count(HOBJECT n_return, $node_children(S, HOBJECT n_middle)) = 1',
            '$heap_count(HOBJECT n_argument, $node_children(S, HOBJECT n_middle)) = 0',
            'pgeneratorop_send = pgeneratorop[.ARGUMENTS = [POBJECT n_argument]]',
            '$generator_operation_valid(S, pgeneratorop_send)',
            '$generator_pending_resume(S, pgeneratorop_send)',
            '$generator_pending_detached_send(S, pgeneratorop_send)',
            '~$generator_unpack_detached(S, n_middle)',
            '~$generator_unpack_chain(S, n_middle, |S.OBJECTS|)',
            '~$generator_pending_shared_send(S, pgeneratorop_send)',
            '~$generator_pending_unused_send(S, pgeneratorop_send)',
            '~$generator_pending_detached_send(S, pgeneratorop)',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.LINE = 0])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.SITE = pgeneratorfrom.SITE])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.NAME = "throw"])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.ADVANCE = true])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.BORROWED = true])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.STARTPACK = true])',
            '~$generator_pending_detached_send(S, pgeneratorop_send[.ARGUMENTS = [PNULL, PNULL]])',
            'S_clear = $generator_set(S, n_middle, pgenerator_middle[.PENDING_INIT = false])',
            '$heap_graph(S_clear) = $heap_graph(S)',
            '~$generator_pending_detached_send(S_clear, pgeneratorop_send)',
            'ptask_used_tail* = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_target* z_target) :: ptask_after*',
            'pframe_wrong = pframe_middle[.TODO = ptask_complete :: (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME $ptascii("wrong28") z_target) :: ptask_after*]',
            'S_wrong = $generator_set(S, n_middle, pgenerator_middle[.FRAME = (pframe_wrong)])',
            '$heap_graph(S_wrong) = $heap_graph(S)',
            '~$generator_return_waiting(S_wrong, n_middle)',
            '~$generator_pending_detached_send(S_wrong, pgeneratorop_send)',
            'S_held = $generator_set(S, n_middle, pgenerator_middle[.FRAME = (pframe_middle[.HELD = [HOBJECT n_return]])])',
            '~$generator_pending_detached_send(S_held, pgeneratorop_send)',
            'S_double = $generator_set(S, n_middle, pgenerator_middle[.FRAME = (pframe_middle[.TODO = pframe_middle.TODO ++ [ptask_complete]])])',
            '~$generator_pending_detached_send(S_double, pgeneratorop_send)',
            'S.EVENTS = ' + outputs(EVENTS[CONSUME][:9]),
            *VALID, *BUDGET,
            'S_one.OBJECTS[n_middle] = GENERATOR pgenerator_middle[.PENDING_INIT = false]',
            'S_one.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'S_one.GENERATORRETURNRETAINED = eps', 'S_one.GENERATORINPUTS = eps',
            'S_one.GENERATORLOOPRETAINED = eps',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.FRAMES = S.FRAMES',
            'S_one.CURRENT = S.CURRENT', 'S_one.GC = S.GC',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HOBJECT n_middle)]',
            'pdestructionrelease.USER', 'pdestructionrelease.CALLER = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'pdestructionoperation.SOURCE = GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_argument)])',
            'pdestructionoperation.VALUE = KNOWN (POBJECT n_cache)',
            'pdestructionoperation.PENDING = eps',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_middle) = 3',
            '~$generator_pending_resume(S_one, pgeneratorop_send)',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[CONSUME]),
            'S_done.GENERATORRETURNRETAINED = eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n_return) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_middle) = 0',
            'n_return <- S_done.DESTRUCTION.CALLED',
            'n_cache <- S_done.DESTRUCTION.CALLED',
            'n_argument <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'owning-return-remains-independent-in-real-send-cache-replacement': {
        'source': ROWS[REPLACE]['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) '
                  '-- if $object_name(S, n_cache) = $ptascii("PendingOwningReplaceCache28") '
                  '-- if S.FRAMES = pframe_caller :: pframe_tail* '
                  '-- if pframe_caller.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_return* '
                  '-- if pdestructorcall.OPERATION = eps'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.COMPLETION = NORMAL', 'S.GC.ACTIVE = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'S.GENERATORRETURNRETAINED = [ptask_complete]',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_middle porigin_site n_child (PARRAY n_array)',
            '$generator_return_retained_record(S, ptask_complete)',
            '$generator_return_retained_valid(S, S.GENERATORRETURNRETAINED)',
            '$task_nodes(ptask_complete) = [HARRAY n_array]',
            '$heap_count(HARRAY n_array, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_return))]',
            '$object_name(S, n_return) = $ptascii("PendingOwningLate28")',
            '$heap_owners($heap_graph(S), HOBJECT n_return) = 1',
            '~(n_return <- S.DESTRUCTION.CALLED)',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_middle.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_middle.FRAME = eps', 'pgenerator_child.FRAME = eps',
            '~pgenerator_middle.PENDING_INIT', 'pgenerator_middle.PARKED = eps',
            '$generator_storage_for(S, n_middle) = eps',
            '~((HOBJECT n_middle) <- S.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_children(HOBJECT n_middle, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            '$heap_children(HOBJECT n_child, $allocation_edges(S, S.ALLOCATIONS)) = eps',
            'n_middle <- S.DESTRUCTION.CALLED',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            'pcallcontext.INSTANCE = eps', 'pdestructorcall.OBJECT = n_cache',
            'pdestructorcall.CALLER = eps', 'pframe_caller.CONTEXT = eps',
            'pdestructorcall.FRAME = eps',
            'S.DESTRUCTION.OPERATIONS = eps',
            'S.DESTRUCTION.CALLS = [pdestructorcall]',
            'pdestructorcall.PENDING = (n_exception)',
            'ptask_return* = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_exception) :: ptask_send_tail*',
            'pdestructionrelease.JOBS = eps',
            '$destructor_call_pending_tail(S, pdestructorcall) = (ptask_return*)',
            '$destructor_tail_pending(ptask_return*) = (n_exception)',
            '$destructor_call_pending_valid(S, pdestructorcall)',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("injected")) = (n_injected)',
            'S.STORE[n_injected] = DEFINED (POBJECT n_exception)',
            'S.OBJECTS[n_exception] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            '$string_bytes($throwable_field(S, n_exception, "message")) = ($ptascii("argument28"))',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '$destructor_call_live(S, pdestructorcall)',
            '$destructor_context_valid(S, pcallcontext)',
            'pdestructorcall_wrong = pdestructorcall[.PENDING = eps]',
            'S_badpending = S[.FRAMES = pframe_caller[.TODO = (DESTRUCTOR_RESULT pdestructorcall_wrong) :: ptask_return*] :: pframe_tail*][.DESTRUCTION.CALLS = [pdestructorcall_wrong]]',
            '$heap_graph(S_badpending) = $heap_graph(S)',
            '$destructor_call_pending_tail(S_badpending, pdestructorcall_wrong) = (ptask_return*)',
            '~$destructor_call_pending_valid(S_badpending, pdestructorcall_wrong)',
            '~$destructor_context_valid(S_badpending, pcallcontext)',
            '~$call_descriptors_valid(S_badpending)',
            '~$generator_return_retained_valid(S, [ptask_complete, ptask_complete])',
            'porigin_site = PORIGIN n_unit pcpath_site',
            'porigin_wrong = PORIGIN n_unit (pcpath_site ++ [PCFIELD 999])',
            'S_badsite = S[.GENERATORRETURNRETAINED = [GENERATOR_FROM_COMPLETE n_middle porigin_wrong n_child (PARRAY n_array)]]',
            '$heap_graph(S_badsite) = $heap_graph(S)',
            '~$generator_return_retained_valid(S_badsite, S_badsite.GENERATORRETURNRETAINED)',
            '~$call_descriptors_valid(S_badsite)',
            'S.EVENTS = ' + outputs(EVENTS[REPLACE][:13]),
            *VALID, *BUDGET,
            'S_one.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_one, ptask_complete)',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_exception) = 2',
            '$destructor_call_pending_valid(S_one, pdestructorcall)',
            '$generator_storage_for(S_one, n_middle) = eps',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[REPLACE]),
            'S_done.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_done, ptask_complete)',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1',
            '(HOBJECT n_return) <- S_done.ALLOCATIONS',
            'n_return <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            '~((HOBJECT n_middle) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_cache) <- S_done.ALLOCATIONS)',
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
