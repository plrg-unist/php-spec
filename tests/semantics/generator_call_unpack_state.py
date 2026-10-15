#!/usr/bin/env python3
"""Reach native Generator sends, authenticated resumes and abrupt argument cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_unpack_cases.json')
REVIEW_CATALOG = Path(__file__).with_name('generator_call_unpack_review_cases.json')
INPUTS = [Path(__file__), CATALOG, REVIEW_CATALOG, Path(review.__file__)]
SOURCES = {row['id'].removeprefix('generator-call-unpack-'): row['source']
           for row in json.loads(CATALOG.read_bytes())}
REVIEW_SOURCES = {row['id']: row['source']
                  for row in json.loads(REVIEW_CATALOG.read_bytes())}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
DONE = ['S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
TEMP = ['n_data = pgeneratorunpack.OBJECT',
        'pgeneratorunpack.INPUT = KNOWN (POBJECT n_data)',
        '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "ready") = '
        '[HOBJECT n_data, HOBJECT n_data] ++ $unpack_call_roots(pgeneratorunpack.CALL)',
        '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
        'S.OBJECTS[n_data] = GENERATOR pgenerator',
        'pgenerator.PHASE = GENERATOR_PAUSED', 'pgenerator.FRAME = (pframe_saved)',
        '$generator_unpack_valid(S, pgeneratorunpack, "ready")']

CASES = {
    'reference-yield-send-freezes-value-before-borrowed-next-resume': {
        'source': SOURCES['reference-yield-snapshots-enter-byvalue-cells'],
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 0'),
        'checks': [
            *TEMP, 'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '~pgeneratorunpack.NAMED', 'pgenerator.FIRST',
            'pgenerator.REFCELL = (n_raw)', 'pgenerator.VALUE = eps',
            'pgenerator.KEY = (PINT 0)', 'n_raw <- S.REFCELLS',
            '$lookup(S.ENV, $ptascii("shared")) = (n_raw)',
            'S.STORE[n_raw] = DEFINED (PINT 11)',
            '$generator_cached_value(S, n_data, false) = PINT 11',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 3',
            '$unpack_origin(S, pgeneratorunpack.CALL) = (porigin_arg)',
            'S.ORIGIN = (porigin_arg)',
            '~$generator_unpack_valid(S, pgeneratorunpack[.COUNT = 1], "ready")',
            '~$generator_unpack_valid(S, pgeneratorunpack[.NAMED = true], "ready")',
            '~$generator_unpack_valid(S, pgeneratorunpack[.CALL.LINE = 0], "ready")',
            '~$generator_unpack_valid(S[.TODO = ptask_tail*], pgeneratorunpack, "ready")',
            '~$generator_unpack_valid(S[.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") '
            ':: S.TODO], pgeneratorunpack, "ready")',
            '~$generator_flat_tasks([AT porigin_arg (GENERATOR_UNPACK pgeneratorunpack "ready")])',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorunpack_next = pgeneratorunpack[.COUNT = 1]'
            '[.CALL.SENT = {SLOTS ([NAMED_SENT (KNOWN (PINT 11))]), NAMED eps}]',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HCELL n_raw) = 3', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]', '$drive(S, 2) = S_two_budget',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
            'S_two.FRAMES = [pframe_caller]',
            'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop) :: '
            '(GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pframe_caller.ORIGIN = (porigin_arg)',
            'pgeneratorop.STARTPACK', 'pgeneratorop.BORROWED',
            'pgeneratorop.OBJECT = n_data', 'pgeneratorop.NAME = "next"',
            'pgeneratorop.SITE = porigin_arg', 'pgeneratorop.LINE = 6',
            'pgeneratorop.LOOP = eps', 'pgeneratorop.ARGUMENTS = eps',
            '~pgeneratorop.ADVANCE', '$task_nodes(GENERATOR_RESUME pgeneratorop) = eps',
            '$generator_operation_site(S_two, pgeneratorop)',
            '$generator_resumption_valid(S_two, pgeneratorop)',
            '$generator_operation_trace(S_two, pgeneratorop) = eps',
            '~$generator_operation_site(S_two, pgeneratorop[.LINE = 0])',
            '~$generator_operation_site(S_two, pgeneratorop[.STARTPACK = false])',
            '~$generator_operation_site(S_two, pgeneratorop[.BORROWED = false])',
            'S_missing = S_two[.FRAMES = [pframe_caller[.TODO = '
            '(GENERATOR_RESUME pgeneratorop) :: ptask_tail*]]]',
            '~$generator_operation_site(S_missing, pgeneratorop)',
            '~$call_descriptors_valid(S_missing)',
            '$heap_owners($heap_graph(S_two), HOBJECT n_data) = 2',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
            'S_done = $drive(S_two, 4000)', *DONE,
            'S_done.STORE[n_raw] = DEFINED (PINT 22)',
            'S_done.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("D|"), '
            'OUTPUT $ptascii("11"), OUTPUT $ptascii("|"), OUTPUT $ptascii("22"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("M|"), OUTPUT $ptascii("22"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
        ],
    },
    'named-slot-send-reuses-key-errors-before-reference-boundary': {
        'source': SOURCES['named-fixed-slots-complete-before-target-body'],
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 1'),
        'checks': [
            *TEMP, 'pgeneratorunpack.NAMED',
            'pgeneratorunpack.CALL.SENT = {SLOTS ([NAMED_HOLE, '
            'NAMED_SENT (KNOWN (PINT 7))]), NAMED eps}',
            'pgenerator.KEY = (PSTRING $ptascii("first"))',
            'pgenerator.VALUE = (PINT 5)',
            '$target_function(S, pgeneratorunpack.CALL.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_first, psparam_second]',
            '~psparam_first.BYREF', '~psparam_second.BYREF',
            *ADMISSION, *ZERO,
            'S_duplicate = $generator_unpack_send($generator_set(S, n_data, '
            'pgenerator[.KEY = (PSTRING $ptascii("second"))]), pgeneratorunpack, ptask_tail*)',
            'S_duplicate.COMPLETION = THROWN "Error" '
            '($ptascii("Named parameter $second overwrites previous argument")) 5',
            'S_unknown = $generator_unpack_send($generator_set(S, n_data, '
            'pgenerator[.KEY = (PSTRING $ptascii("unknown"))]), pgeneratorunpack, ptask_tail*)',
            'S_unknown.COMPLETION = THROWN "Error" ($ptascii("Unknown named parameter $unknown")) 5',
            'S_key = $generator_unpack_send($generator_set(S, n_data, '
            'pgenerator[.KEY = (PBOOL true)]), pgeneratorunpack, ptask_tail*)',
            'S_key.COMPLETION = THROWN "Error" '
            '($ptascii("Keys must be of type int|string during argument unpacking")) 5',
            'pfunction_ref = pfunction[.SIGNATURE.PARAMETERS = '
            '[psparam_first[.BYREF = true], psparam_second]]',
            'S_ref = S[.FUNCTIONS = [pfunction_ref]]',
            'S_ref_send = $generator_unpack_send(S_ref, pgeneratorunpack, ptask_tail*)',
            'S_ref_send.COMPLETION = UNSUPPORTED "Generator unpack by-reference target"',
            'S_ref_unknown = $generator_unpack_send($generator_set(S_ref, n_data, '
            'pgenerator[.KEY = (PSTRING $ptascii("unknown"))]), pgeneratorunpack, ptask_tail*)',
            'S_ref_unknown.COMPLETION = S_unknown.COMPLETION', *ONE,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'pgeneratorunpack_next.COUNT = 2', 'pgeneratorunpack_next.NAMED',
            'pgeneratorunpack_next.CALL.SENT = {SLOTS ([NAMED_SENT (KNOWN (PINT 5)), '
            'NAMED_SENT (KNOWN (PINT 7))]), NAMED eps}',
            'S_one.STORE = S.STORE', 'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
            *POST, 'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
        ],
    },
    'body-throw-drops-borrowed-resumer-before-owning-unpack-marker': {
        'source': SOURCES['body-throw-retires-sent-payload-without-method-trace'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: (GENERATOR_RESUME pgeneratorop) :: '
                  '(GENERATOR_UNPACK pgeneratorunpack "next") :: ptask_tail*'),
        'checks': [
            'n_data = pgeneratorunpack.OBJECT', 'pgeneratorunpack.COUNT = 1',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT n_data)',
            'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_child))]',
            'pgeneratorunpack.CALL.SENT.NAMED = eps', '~pgeneratorunpack.NAMED',
            '$object_name(S, n_child) = $ptascii("GeneratorThrowChild09")',
            'S.OBJECTS[n_data] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_CLOSED', 'pgenerator.FRAME = eps',
            'pgenerator.VALUE = (POBJECT n_child)', 'pgenerator.REFCELL = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            '$task_nodes(GENERATOR_RESUME pgeneratorop) = eps',
            '$generator_operation_trace(S, pgeneratorop) = eps',
            '$generator_unpack_valid(S, pgeneratorunpack, "next")',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            'S.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("generatorThrow09")))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("args")) = '
            '(DIRECT (PARRAY n_args))', 'S.ARRAYS[n_args].ITEMS = eps',
            '$throwable_field(S, n_error, "code") = PINT 51',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(GENERATOR_UNPACK pgeneratorunpack "next") :: ptask_tail*',
            'S_one.STORE = S.STORE', 'S_one.OBJECTS = S.OBJECTS',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]', '$drive(S, 2) = S_two_budget',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_exit*',
            'pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "next"',
            'pdestructionoperation.PENDING = (n_error)',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_child)]',
            '$eager_operation_source_valid(S_two, pdestructionoperation)',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
            'S_done = $drive(S_two, 4000)', *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("A|"), OUTPUT $ptascii("T|"), '
            'OUTPUT $ptascii("51"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("generatorThrow09"), OUTPUT $ptascii("|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
            'n_child <- S_done.DESTRUCTION.CALLED',
            '$eager_operation_source_valid(S_done, pdestructionoperation)',
        ],
    },
    'temporary-order-error-keeps-marker-through-finally-and-cache-release': {
        'source': next(source for key, source in REVIEW_SOURCES.items() if 'temporary' in key),
        'stage': ('S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                  '-- if pgeneratorunpack.COUNT = 1'),
        'checks': [
            *TEMP, 'pgeneratorunpack.NAMED', 'pgenerator.KEY = (PINT 0)',
            'pgenerator.VALUE = (POBJECT n_current)',
            'pgeneratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_sent))]',
            'pgeneratorunpack.CALL.SENT.NAMED = eps',
            'n_current =/= n_sent',
            '$heap_owners($heap_graph(S), HOBJECT n_sent) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail*',
            '$throwable_field(S_one, n_error, "line") = PINT 6',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Cannot use positional argument after named argument during unpacking"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            'S_one.ARRAYS[n_trace].ITEMS = eps',
            'S_one.OBJECTS[n_data] = S.OBJECTS[n_data]',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]', '$drive(S, 2) = S_two_budget',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_exit*',
            'pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "ready"',
            'pdestructionoperation.PENDING = (n_error)',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_sent)]',
            '$eager_operation_source_valid(S_two, pdestructionoperation)',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
            'S_three_budget = $drive_steps(S_two, 1)', 'S_three_budget.COMPLETION = BUDGET',
            'S_three = S_three_budget[.COMPLETION = NORMAL]', '$drive(S_one, 2) = S_three_budget',
            'S_three.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_last) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_exit*',
            'pdestructionrelease_last.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_sent)]',
            '$heap_owners($heap_graph(S_three), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_three), HOBJECT n_current) = 1',
            '$heap_owners($heap_graph(S_three), HOBJECT n_sent) = 1',
            'S_three.EVENTS = S.EVENTS',
            'S_done = $drive(S_three, 4000)', *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("B|"), '
            'OUTPUT $ptascii("A|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("6"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("NOFRAME|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_sent) = 0',
            'n_current <- S_done.DESTRUCTION.CALLED', 'n_sent <- S_done.DESTRUCTION.CALLED',
            '$eager_operation_source_valid(S_done, pdestructionoperation)',
        ],
    },
    'receive-error-direct-trace-owns-array-after-generator-retirement': {
        'source': SOURCES['receive-error-trace-outlives-generator-retirement'],
        'stage': ('S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext)'),
        'checks': [
            '$receiving_function(S, porigin) = (pfunction)',
            'pcallcontext.FUNCTION = porigin', 'pcallcontext.ARGC = 1',
            'pcallcontext.CALLSITE = (porigin_call)', 'pcallcontext.LINE = 6',
            'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = eps',
            'pcallcontext.HOLES = eps',
            '$lookup(S.ENV, $ptascii("value")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            '$object_name(S, n_child) = $ptascii("GeneratorTypedChild09")',
            'n_data = 0', 'S.OBJECTS[n_data] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_CLOSED', 'pgenerator.FRAME = eps',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            'S.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("G|"), OUTPUT $ptascii("F|")]',
            'psparam = pfunction.SIGNATURE.PARAMETERS[0]', '~psparam.BYREF',
            '$typed_parameter_conversion(S, psparam, PARRAY n_array) = TYPEREJECT',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            '$throwable_field(S_one, n_error, "line") = PINT 4',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("generatorTypedTarget09(): Argument #1 ($value) must be of type '
            '?GeneratorTypedChild09, array given, called in ") ++ '
            '$call_sourcefile(S.FILES, porigin_call) ++ $ptascii(" on line 6"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            'S_one.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
            '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("generatorTypedTarget09")))',
            '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("args")) = '
            '(DIRECT (PARRAY n_args))',
            'S_one.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]',
            '$trace_graph_valid(S_one, n_trace)',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', *DONE,
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), OUTPUT $ptascii("4"), '
            'OUTPUT $ptascii("|HELD|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("U|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            'n_child <- S_done.DESTRUCTION.CALLED',
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
