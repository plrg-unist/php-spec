#!/usr/bin/env python3
"""Reach buffered THROW retirement and the surviving aliased current owner."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_buffered_throw_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
ARRAY = 'generator-buffered-throw-review-forwarded-array-input-and-reference-cache'
ALIAS = 'generator-buffered-throw-review-buffer-alias-preserves-current-until-catch-yield'
EVENTS = {
    ARRAY: ['P|', 'O|', 'M|', 'C|', 'S|', 'OLD|', 'W|', 'A|', 'V|', 'LIVE|',
            'B|', 'CATCH|', '1', '|', 'LIVE|', '1', '|', 'THROW|', '13', '|',
            'T|', 'J|', 'I|', '23', '|', 'K|', 'F|', '29', '|', 'Z|',
            'RET|', '31', '|', 'CACHE|', 'E'],
    ALIAS: ['P|', 'O|', 'M|', 'C|', 'S|', '1', '|', 'W|', 'CATCH|', '1', '|',
            'A|', 'THROW|', '13', '|', 'T|', 'J|', 'I|', '23', '|', 'K|',
            'F|', '29', '|', 'Z|', 'RET|', '31', '|', 'E'],
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
    'forwarded-throw-moves-array-slot-into-child-pending-release': {
        'source': ROWS[ARRAY]['source'],
        'stage': ('S.TODO = (GENERATOR_FROM_NEXT n_middle porigin) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $trace_context_function(S, pcallcontext) = $ptascii("reviewBufferedMiddle20") '
                  '-- if S.GENERATORINPUTS = [pgeneratorinput] '
                  '-- if pgeneratorinput.LIVE '
                  '-- if $generator_from_operation(S, n_middle, porigin, pgeneratorinput.OBJECT).NAME = "throw"'),
        'checks': [
            'S.ACTIVEFIBER = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("cache")) = (n_cache_cell)',
            '$lookup(S_global.ENV, $ptascii("exception")) = (n_exception_cell)',
            'S.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
            '$lookup(S_global.ENV, $ptascii("row")) = eps',
            'S.STORE[n_cache_cell] = DEFINED (PARRAY n_cache_row)',
            'S.ARRAYS[n_cache_row].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_cache))]',
            '$object_name(S, n_cache) = $ptascii("ReviewBufferedNew20")',
            'pgeneratorinput.OBJECT = n_child',
            'pgeneratorinput.SOURCE.OBJECT = n_middle',
            'pgeneratorinput.SOURCE.NAME = "send"',
            'pgeneratorinput.SOURCE.LINE = 11',
            '~pgeneratorinput.SOURCE.ADVANCE',
            'pgeneratorinput.SOURCE.ARGUMENTS = [PARRAY n_buffer]',
            'S.ARRAYS[n_buffer].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]',
            '$object_name(S, n_payload) = $ptascii("ReviewBufferedPayload20")',
            'n_buffer =/= n_cache_row',
            '$generator_inputs_valid(S, S.GENERATORINPUTS)',
            '$generator_input_count(S.GENERATORINPUTS, n_child) = 1',
            '$generator_inputs_nodes(S.GENERATORINPUTS) = [HARRAY n_buffer]',
            '$heap_owners($heap_graph(S), HARRAY n_buffer) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_cache_row) = 1',
            '$heap_owners($heap_graph(S), HCELL n_cache_cell) = 3',
            '$heap_count(HARRAY n_buffer, $node_children(S, HOBJECT n_child)) = 0',
            'S.OBJECTS[n_middle] = GENERATOR pgenerator_middle',
            'pgenerator_middle.PHASE = GENERATOR_RUNNING',
            'pgenerator_middle.FRAME = eps',
            '~pgenerator_middle.PENDING_INIT',
            'pgenerator_middle.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.SITE = porigin',
            'pgeneratorfrom.INPUT = (POBJECT n_child)',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.CURRENT = eps',
            'pgeneratorfrom.POSITION = 1',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_PAUSED',
            'pgenerator_child.DELEGATE = eps',
            'pgenerator_child.FRAME = (pframe_child)',
            'pgenerator_child.VALUE = eps',
            'pgenerator_child.REFCELL = (n_cache_cell)',
            'pgenerator_child.KEY = (PINT 0)',
            '~pgenerator_child.FIRST', '~pgenerator_child.PENDING_INIT',
            'pframe_child.ORIGIN = (pgeneratorinput.SITE)',
            'pframe_child.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_name* z_write) :: ptask_child*',
            '$generator_input_tail(S, pgeneratorinput.SITE, pframe_child.TODO)',
            'pgeneratorop_forward = $generator_from_operation(S, n_middle, porigin, n_child)',
            '$generator_input_throw_forward(S, pgeneratorop_forward)',
            '$generator_input_throw_ready(S, pgeneratorop_forward)',
            '$generator_input_throw_value(S, GENERATOR_FROM_NEXT n_middle porigin) = (PARRAY n_buffer)',
            '~$generator_input_throw_forward(S, pgeneratorop_forward[.LINE = $(pgeneratorop_forward.LINE + 1)])',
            '~$generator_input_throw_ready(S, pgeneratorop_forward[.LINE = $(pgeneratorop_forward.LINE + 1)])',
            '~$generator_input_throw_forward(S, pgeneratorop_forward[.ARGUMENTS = [POBJECT n_payload]])',
            '~$generator_input_throw_ready(S, pgeneratorop_forward[.ARGUMENTS = [POBJECT n_payload]])',
            'S_wrong_tail = $generator_set(S, n_child, pgenerator_child[.FRAME = (pframe_child[.TODO = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME ($ptascii("wrong20")) z_write) :: ptask_child*])])',
            '$heap_graph(S_wrong_tail) = $heap_graph(S)',
            '$heap_valid($heap_graph(S_wrong_tail))',
            '~$generator_inputs_valid(S_wrong_tail, S_wrong_tail.GENERATORINPUTS)',
            '~$call_descriptors_valid(S_wrong_tail)',
            'pgeneratorinput_bad = pgeneratorinput[.SOURCE = pgeneratorinput.SOURCE[.LINE = $(pgeneratorinput.SOURCE.LINE + 1)]]',
            'S_bad = S[.GENERATORINPUTS = [pgeneratorinput_bad]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$call_descriptors_valid(S_bad)',
            'S.DESTRUCTION.CALLED = [n_old]',
            '$object_name(S, n_old) = $ptascii("ReviewBufferedOld20")',
            '~((HOBJECT n_old) <- S.ALLOCATIONS)',
            '~(n_payload <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = ' + outputs(EVENTS[ARRAY][:10]),
            *VALID, *BUDGET,
            'S_one.GENERATORINPUTS = eps',
            'S_one.RESULT = KNOWN PNULL',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: pframe_child.TODO',
            'pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HARRAY n_buffer)]',
            'pdestructionoperation.SOURCE = GENERATOR_FROM_NEXT n_middle porigin',
            'pdestructionoperation.PENDING = (n_exception)',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.CLEANUP = eps',
            'pdestructionoperation.NOGC = ({OPERAND KNOWN (PARRAY n_buffer), PENDING true})',
            'pdestructionoperation.CALLER = S_one.CURRENT',
            'pdestructionoperation.ORIGIN = (pgeneratorinput.SITE)',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation)',
            '~$gc_operation_metadata_valid(S_one, pdestructionoperation[.ORIGIN = eps])',
            '~$gc_operation_metadata_valid(S_one, pdestructionoperation[.NOGC = ({OPERAND KNOWN (PARRAY n_cache_row), PENDING true})])',
            'S_one_wrong_tail = S_one[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME ($ptascii("wrong20")) z_write) :: ptask_child*]',
            '$heap_graph(S_one_wrong_tail) = $heap_graph(S_one)',
            '$heap_valid($heap_graph(S_one_wrong_tail))',
            '~$generator_input_throw_receipt(S_one_wrong_tail, pdestructionoperation)',
            '~$gc_operation_metadata_valid(S_one_wrong_tail, pdestructionoperation)',
            '~$call_descriptors_valid(S_one_wrong_tail)',
            'S_one.CURRENT = (pcallcontext_child)',
            '$trace_context_function(S_one, pcallcontext_child) = $ptascii("reviewBufferedLeaf20")',
            'S_one.FRAMES = pframe_resumer :: S.FRAMES',
            'pframe_resumer.CONTEXT = S.CURRENT',
            'pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_middle porigin n_child) :: ptask_tail*',
            'pgeneratorop_child.OBJECT = n_child',
            'pgeneratorop_child.NAME = "throw"',
            'pgeneratorop_child.ARGUMENTS = [POBJECT n_exception]',
            'pgeneratorop_child.SITE = porigin',
            '~$generator_resume_root(S_one, pgeneratorop_child)',
            '$generator_from_operation_valid(S_one, pgeneratorop_child)',
            'S_expected = $generator_set(S, n_child, pgenerator_child[.FRAME = eps][.PHASE = GENERATOR_RUNNING])',
            'S_one.OBJECTS = S_expected.OBJECTS',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.GC = S.GC',
            '$heap_owners($heap_graph(S_one), HARRAY n_buffer) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_count(HARRAY n_buffer, $generator_inputs_nodes(S_one.GENERATORINPUTS)) = 0',
            '$heap_count(HARRAY n_buffer, $task_nodes(DESTRUCTOR_RELEASE pdestructionrelease)) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_cache_cell) = 3',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[ARRAY]),
            '$heap_owners($heap_graph(S_done), HARRAY n_buffer) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            'n_cache <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'buffer-alias-temp-release-keeps-current-and-does-not-buffer-gc-root': {
        'source': ROWS[ALIAS]['source'],
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HOBJECT n_payload)] '
                  '-- if pdestructionoperation.SOURCE = GENERATOR_FROM_NEXT n_middle porigin '
                  '-- if pdestructionoperation.PENDING = (n_exception) '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $trace_context_function(S, pcallcontext) = $ptascii("reviewBufferedAliasLeaf20")'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.GENERATORINPUTS = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("exception")) = (n_exception_cell)',
            'S.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
            '$lookup(S_global.ENV, $ptascii("child")) = (n_child_cell)',
            'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
            '$lookup(S_global.ENV, $ptascii("snapshot")) = eps',
            '$object_name(S, n_payload) = $ptascii("ReviewBufferedAlias20")',
            '$throwable_live(S, n_exception)',
            '$throwable_field(S, n_exception, "previous") = PNULL',
            '$string_bytes($throwable_field(S, n_exception, "message")) = ($ptascii("alias20"))',
            'pdestructionoperation.NOGC = ({OPERAND KNOWN (POBJECT n_payload), PENDING true})',
            'pdestructionoperation.CALLER = S.CURRENT',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.CLEANUP = eps',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'S.DESTRUCTION.RELEASES = pdestructionrelease :: pdestructionrelease_tail*',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_release_valid(S, pdestructionrelease)',
            '$gc_operation_metadata_valid(S, pdestructionoperation)',
            '$gc_temporary_pending((pdestructionrelease), {OPERAND KNOWN (POBJECT n_payload), PENDING true})',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_RUNNING',
            'pgenerator_child.FRAME = eps', 'pgenerator_child.DELEGATE = eps',
            'pgenerator_child.VALUE = (POBJECT n_payload)',
            'pgenerator_child.REFCELL = eps', 'pgenerator_child.KEY = (PINT 0)',
            '~pgenerator_child.PENDING_INIT',
            'S.ORIGIN = pdestructionoperation.ORIGIN',
            'S.ORIGIN = (porigin_yield)',
            '$generator_input_site(S, n_child, porigin_yield)',
            '$generator_input_tail(S, porigin_yield, ptask_tail*)',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2',
            '$heap_count(HOBJECT n_payload, $node_children(S, HOBJECT n_child)) = 1',
            '$heap_count(HOBJECT n_payload, $task_nodes(DESTRUCTOR_RELEASE pdestructionrelease)) = 1',
            '$heap_count(HOBJECT n_payload, $generator_inputs_nodes(S.GENERATORINPUTS)) = 0',
            '~(n_payload <- S.DESTRUCTION.CALLED)',
            '~$gc_operation_metadata_valid(S, pdestructionoperation[.ORIGIN = eps])',
            '~$gc_operation_metadata_valid(S, pdestructionoperation[.NOGC = ({OPERAND KNOWN (POBJECT n_exception), PENDING true})])',
            'S.EVENTS = ' + outputs(EVENTS[ALIAS][:8]),
            *VALID, *BUDGET,
            'pdestructionoperation_next = pdestructionoperation[.NOGC = ({OPERAND KNOWN (POBJECT n_payload), PENDING false})]',
            'pdestructionrelease_next = pdestructionrelease[.JOBS = eps]',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_next) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_next) :: ptask_tail*',
            'S_one.DESTRUCTION.OPERATIONS = pdestructionoperation_next :: pdestructionoperation_tail*',
            'S_one.DESTRUCTION.RELEASES = pdestructionrelease_next :: pdestructionrelease_tail*',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.FRAMES = S.FRAMES', 'S_one.CURRENT = S.CURRENT',
            'S_one.GENERATORINPUTS = eps', 'S_one.GC = S.GC',
            'S_one.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_count(HOBJECT n_payload, $node_children(S_one, HOBJECT n_child)) = 1',
            '$heap_count(HOBJECT n_payload, $machine_roots(S_one)) = 0',
            '$destructor_operation_valid(S_one, pdestructionoperation_next)',
            '$gc_operation_metadata_valid(S_one, pdestructionoperation_next)',
            *DONE,
            'S_done.EVENTS = ' + outputs(EVENTS[ALIAS]),
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0',
            'n_payload <- S_done.DESTRUCTION.CALLED',
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
