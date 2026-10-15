#!/usr/bin/env python3
"""Reach delegated-array sends, temporary abort cleanup and real receive traces."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_array_delegation_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}

CASES = {
    'delegated-array-ready-send-and-borrowed-next-preserve-caller': {
        'source': SOURCES['generator-array-unpack-nested-caller-finishes-delegation-and-direct-tail'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* -- if pgeneratorunpack.COUNT = 0',
        'checks': ['n_data = pgeneratorunpack.OBJECT',
         'S.CURRENT = (pcallcontext)',
         'pcallcontext.NAME = $ptascii("generatorArrayCaller10")',
         'pgeneratorunpack.INPUT = VARIABLE ptbytes z',
         'ptbytes = $ptascii("generator")',
         '$lookup(S.ENV, ptbytes) = (n_cell)',
         'S.STORE[n_cell] = DEFINED (POBJECT n_data)',
         'pgeneratorunpack.COUNT = 0',
         '~pgeneratorunpack.NAMED',
         'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
         'S.OBJECTS[n_data] = GENERATOR pgenerator',
         'pgenerator.PHASE = GENERATOR_DELEGATING',
         'pgenerator.FIRST',
         'pgenerator.FRAME = (pframe_saved)',
         'pgenerator.VALUE = eps',
         'pgenerator.REFCELL = eps',
         'pgenerator.KEY = (PINT 0)',
         'pgenerator.BORROWED = eps',
         'pgenerator.DELEGATE = (pgeneratorfrom)',
         'pgeneratorfrom.INPUT = (PARRAY n_table)',
         'pgeneratorfrom.CURRENT = (KNOWN (PINT 7))',
         'pgeneratorfrom.ACQUISITION = eps',
         'pgeneratorfrom.POSITION = 1',
         '$generator_from_record_valid(S, n_data, pgenerator)',
         '$generator_unpack_array_delegate(S, n_data)',
         '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
         'S_required = S[.COMPLETION = UNSUPPORTED "Generator unpack delegated producer"]',
         '~$generator_unpack_delegated_blocked(S_required)',
         'S.ARRAYS[n_table].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PINT 11))]',
         '$generator_cached_value(S, n_data, false) = PINT 7',
         '$generator_cached_value(S, n_data, true) = PINT 0',
         '$node_children(S, HOBJECT n_data) = [HARRAY n_table]',
         '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
         '$heap_owners($heap_graph(S), HARRAY n_table) = 1',
         '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = [HOBJECT n_data]',
         'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|")]',
         'S_missing = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.CURRENT = eps])])',
         '~$generator_unpack_array_delegate(S_missing, n_data)',
         '~$generator_unpack_valid(S_missing, pgeneratorunpack, "ready")',
         'S_position = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.POSITION = 0])])',
         '~$generator_unpack_array_delegate(S_position, n_data)',
         'pgeneratorunpack.CALL.CALLSITE = (porigin_call)',
         'S_source = $generator_set(S, n_data, pgenerator[.DELEGATE = (pgeneratorfrom[.SITE = porigin_call])])',
         '~$generator_unpack_array_delegate(S_source, n_data)',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_zero = $drive(S, 0)',
         'S_zero.COMPLETION = BUDGET',
         'S_zero[.COMPLETION = NORMAL] = S',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
         'pgeneratorunpack_next = pgeneratorunpack[.COUNT = 1][.CALL.SENT = {SLOTS ([NAMED_SENT (KNOWN (PINT '
         '7))]), NAMED eps}]',
         'S_one.STORE = S.STORE',
         'S_one.ARRAYS = S.ARRAYS',
         'S_one.OBJECTS = S.OBJECTS',
         'S_one.EVENTS = S.EVENTS',
         '$heap_owners($heap_graph(S_one), HARRAY n_table) = 1',
         '$call_descriptors_valid(S_one)',
         '$heap_valid($heap_graph(S_one))',
         'S_two_budget = $drive_steps(S_one, 1)',
         'S_two_budget.COMPLETION = BUDGET',
         'S_two = S_two_budget[.COMPLETION = NORMAL]',
         '$drive(S, 2) = S_two_budget',
         '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
         'S_two.FRAMES = pframe_caller :: S.FRAMES',
         'pframe_caller.CONTEXT = S.CURRENT',
         'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop) :: (GENERATOR_UNPACK pgeneratorunpack_next '
         '"next") :: ptask_tail*',
         'pgeneratorop.OBJECT = n_data',
         'pgeneratorop.STARTPACK',
         'pgeneratorop.BORROWED',
         'pgeneratorop.NAME = "next"',
         '~pgeneratorop.ADVANCE',
         '$task_nodes(GENERATOR_RESUME pgeneratorop) = eps',
         '$generator_operation_site(S_two, pgeneratorop)',
         '$generator_resumption_valid(S_two, pgeneratorop)',
         '$generator_operation_trace(S_two, pgeneratorop) = eps',
         '$call_descriptors_valid(S_two)',
         '$heap_valid($heap_graph(S_two))',
         'S_done = $drive(S_two, 4000)',
         'S_done.COMPLETION = NORMAL',
         'S_done.TODO = eps',
         'S_done.FRAMES = eps',
         'S_done.CURRENT = eps',
         'S_done.HELD = eps',
         '$call_descriptors_valid(S_done)',
         '$heap_valid($heap_graph(S_done))',
         'S_done.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("N|"), OUTPUT '
         '$ptascii("F|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("7"), OUTPUT $ptascii("|"), OUTPUT '
         '$ptascii("11"), OUTPUT $ptascii("|"), OUTPUT $ptascii("13"), OUTPUT $ptascii("|"), OUTPUT '
         '$ptascii("R|"), OUTPUT $ptascii("23"), OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
         '$heap_owners($heap_graph(S_done), HARRAY n_table) = 0',
         '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0'],
    },
    'temporary-error-retires-array-before-finally-cache-and-sent': {
        'source': SOURCES['generator-array-unpack-temporary-key-error-closes-before-sent-release'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* -- if pgeneratorunpack.COUNT = 1',
        'checks': ['$destructor_operational(S)',
         '$generator_storage_release(S, eps) = $destructor_release_begin(S, eps)',
         'n_data = pgeneratorunpack.OBJECT',
         'pgeneratorunpack.INPUT = KNOWN (POBJECT n_data)',
         '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = [HOBJECT n_data, HOBJECT n_data] ++ '
         '$unpack_call_roots(pgeneratorunpack.CALL)',
         '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
         'S.OBJECTS[n_data] = GENERATOR pgenerator',
         'pgenerator.PHASE = GENERATOR_DELEGATING',
         'pgenerator.FRAME = (pframe_saved)',
         'pgenerator.DELEGATE = (pgeneratorfrom)',
         'pgeneratorfrom.INPUT = (PARRAY n_table)',
         'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_current))',
         'pgeneratorfrom.ACQUISITION = eps',
         'pgeneratorfrom.POSITION = 2',
         '$generator_unpack_array_delegate(S, n_data)',
         '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
         'pgeneratorunpack.NAMED',
         'pgenerator.KEY = (PINT 0)',
         'pgenerator.VALUE = eps',
         'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_sent))]',
         'pgeneratorunpack.CALL.SENT.NAMED = eps',
         'n_current =/= n_sent',
         'S.ARRAYS[n_table].ITEMS = [ENTRY (KSTRING $ptascii("alpha")) (DIRECT (POBJECT n_sent)), ENTRY (KINT '
         '0) (DIRECT (POBJECT n_current))]',
         '$heap_owners($heap_graph(S), HARRAY n_table) = 1',
         '$node_children(S, HARRAY n_table) = [HOBJECT n_sent, HOBJECT n_current]',
         '$heap_owners($heap_graph(S), HOBJECT n_sent) = 2',
         '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_zero = $drive(S, 0)',
         'S_zero.COMPLETION = BUDGET',
         'S_zero[.COMPLETION = NORMAL] = S',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (THROW_SEARCH n_error) :: (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail*',
         '$throwable_field(S_one, n_error, "line") = PINT 7',
         '$string_bytes($throwable_field(S_one, n_error, "message")) = ($ptascii("Cannot use positional '
         'argument after named argument during unpacking"))',
         '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
         'S_one.ARRAYS[n_trace].ITEMS = eps',
         'S_one.OBJECTS[n_data] = S.OBJECTS[n_data]',
         'S_one.EVENTS = S.EVENTS',
         '$call_descriptors_valid(S_one)',
         '$heap_valid($heap_graph(S_one))',
         'S_two_budget = $drive_steps(S_one, 1)',
         'S_two_budget.COMPLETION = BUDGET',
         'S_two = S_two_budget[.COMPLETION = NORMAL]',
         '$drive(S, 2) = S_two_budget',
         'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT '
         'pdestructionoperation) :: ptask_exit*',
         'pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "ready"',
         'pdestructionoperation.PENDING = (n_error)',
         'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), '
         'DESTRUCTION_VALUE (HOBJECT n_sent)]',
         '$eager_operation_source_valid(S_two, pdestructionoperation)',
         '$call_descriptors_valid(S_two)',
         '$heap_valid($heap_graph(S_two))',
         'S_three_budget = $drive_steps(S_two, 1)',
         'S_three_budget.COMPLETION = BUDGET',
         'S_three = S_three_budget[.COMPLETION = NORMAL]',
         '$drive(S_one, 2) = S_three_budget',
         'S_three.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_last) :: (DESTRUCTOR_OPERATION_EXIT '
         'pdestructionoperation) :: ptask_exit*',
         'pdestructionrelease_last.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT '
         'n_sent)]',
         '$heap_owners($heap_graph(S_three), HOBJECT n_data) = 1',
         '$heap_owners($heap_graph(S_three), HOBJECT n_current) = 2',
         '$heap_owners($heap_graph(S_three), HOBJECT n_sent) = 2',
         'S_three.EVENTS = S.EVENTS',
         'S_done = $drive(S_three, 4000)',
         'S_done.COMPLETION = NORMAL',
         'S_done.TODO = eps',
         'S_done.FRAMES = eps',
         'S_done.CURRENT = eps',
         'S_done.HELD = eps',
         '$call_descriptors_valid(S_done)',
         '$heap_valid($heap_graph(S_done))',
         'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("A|"), '
         'OUTPUT $ptascii("T|"), OUTPUT $ptascii("7"), OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), '
         'OUTPUT $ptascii("E")]',
         '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
         '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
         '$heap_owners($heap_graph(S_done), HOBJECT n_sent) = 0',
         'n_current <- S_done.DESTRUCTION.CALLED',
         'n_sent <- S_done.DESTRUCTION.CALLED',
         '$eager_operation_source_valid(S_done, pdestructionoperation)',
         '$heap_owners($heap_graph(S_done), HARRAY n_table) = 0',
         '$eager_operation_source_valid(S_done[.ARRAYS = eps], pdestructionoperation)'],
    },
    'receive-error-owns-nested-value-after-delegated-table-retirement': {
        'source': SOURCES['generator-array-unpack-receive-trace-owns-child-after-table-and-cache'],
        'stage': 'S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail* -- if S.CURRENT = (pcallcontext)',
        'checks': ['$receiving_function(S, porigin) = (pfunction)',
         'pcallcontext.FUNCTION = porigin',
         'pcallcontext.ARGC = 1',
         'pcallcontext.CALLSITE = (porigin_call)',
         'pcallcontext.LINE = 6',
         'pcallcontext.EXTRA = eps',
         'pcallcontext.NAMED = eps',
         'pcallcontext.HOLES = eps',
         '$lookup(S.ENV, $ptascii("value")) = (n_cell)',
         'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
         'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
         '$object_name(S, n_child) = $ptascii("GeneratorArrayReceiveChild10")',
         'n_data = 0',
         'S.OBJECTS[n_data] = GENERATOR pgenerator',
         'pgenerator.PHASE = GENERATOR_CLOSED',
         'pgenerator.FRAME = eps',
         '~((HOBJECT n_data) <- S.ALLOCATIONS)',
         '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
         '~$generator_unpack_array_delegate(S, n_data)',
         '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
         '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
         'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("F|")]',
         'psparam = pfunction.SIGNATURE.PARAMETERS[0]',
         '~psparam.BYREF',
         '$typed_parameter_conversion(S, psparam, PARRAY n_array) = TYPEREJECT',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_zero = $drive(S, 0)',
         'S_zero.COMPLETION = BUDGET',
         'S_zero[.COMPLETION = NORMAL] = S',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
         '$throwable_field(S_one, n_error, "line") = PINT 4',
         '$string_bytes($throwable_field(S_one, n_error, "message")) = '
         '($ptascii("generatorArrayReceiveTarget10(): Argument #1 ($value) must be of type '
         '?GeneratorArrayReceiveChild10, array given, called in ") ++ $call_sourcefile(S.FILES, porigin_call) '
         '++ $ptascii(" on line 6"))',
         '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
         'S_one.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
         '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING '
         '$ptascii("generatorArrayReceiveTarget10")))',
         '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args))',
         'S_one.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]',
         '$trace_graph_valid(S_one, n_trace)',
         '$heap_owners($heap_graph(S_one), HARRAY n_array) = 2',
         '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
         'S_one.EVENTS = S.EVENTS',
         '$call_descriptors_valid(S_one)',
         '$heap_valid($heap_graph(S_one))',
         'S_two_budget = $drive_steps(S_one, 1)',
         '$drive(S, 2) = S_two_budget',
         'S_done = $drive(S_one, 4000)',
         'S_done.COMPLETION = NORMAL',
         'S_done.TODO = eps',
         'S_done.FRAMES = eps',
         'S_done.CURRENT = eps',
         'S_done.HELD = eps',
         '$call_descriptors_valid(S_done)',
         '$heap_valid($heap_graph(S_done))',
         'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), OUTPUT $ptascii("4"), OUTPUT $ptascii("|HELD|"), '
         'OUTPUT $ptascii("A|"), OUTPUT $ptascii("U|"), OUTPUT $ptascii("E")]',
         '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0',
         '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
         'n_child <- S_done.DESTRUCTION.CALLED'],
    },
}


assert all(case['source'] in SOURCES.values() for case in CASES.values())


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
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                                     cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs=before, author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
