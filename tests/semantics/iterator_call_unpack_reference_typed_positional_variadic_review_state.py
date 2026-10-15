#!/usr/bin/env python3
"""Reach partial typed rest rejection and caught three-value trace ownership."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_reference_typed_positional_variadic_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'partial-typed-rest-rejection-keeps-alias-entry-and-owning-trace-values': {
        'source': SOURCES['iterator-reference-typed-positional-variadic-review-partial-rest-direct-trace-source-alias'],
        'stage': ('S.TODO = [VARIADIC_RECEIVE porigin 2] -- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("reviewTypedRestTrace08")'),
        'checks': [
            'pcallcontext.FUNCTION = porigin', 'pcallcontext.ARGC = 3',
            'pcallcontext.HOLES = eps', 'pcallcontext.NAMED = eps',
            'pcallcontext.LINE = 17', 'pcallcontext.CALLSITE = (porigin_call)',
            'pcallcontext.EXTRA = [REFERENCE n_good_cell, REFERENCE n_bad_cell]',
            '$receiving_function(S, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_head, psparam_rest]',
            r'~psparam_head.BYREF /\ ~psparam_head.VARIADIC /\ psparam_head.TYPE = eps',
            r'psparam_rest.BYREF /\ psparam_rest.VARIADIC',
            'psparam_rest.TYPE = [(PTBRANCH ([(PTCLASS $ptascii("ReviewTypedRestGood08"))])), '
            '(PTBRANCH ([PTBUILTIN "null"]))]',
            '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = [psparam_head]',
            '$default_parameter_line(S, porigin, 1) = 15',
            '$lookup(S.ENV, $ptascii("head")) = (n_head_cell)',
            'S.STORE[n_head_cell] = DEFINED (PARRAY n_head)',
            'S.ARRAYS[n_head].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_head_child))]',
            '$object_name(S, n_head_child) = $ptascii("ReviewTypedRestHead08")',
            '$lookup(S.ENV, $ptascii("items")) = (n_rest_cell)',
            'S.STORE[n_rest_cell] = DEFINED (PARRAY n_rest)',
            'S.ARRAYS[n_rest].ITEMS = [ENTRY (KINT 0) (ALIAS n_good_cell)]',
            'S.ARRAYS[n_rest].NEXT = 1',
            'n_good_cell =/= n_bad_cell', 'n_good_cell =/= n_rest_cell',
            'n_bad_cell =/= n_rest_cell',
            'n_good_cell <- S.REFCELLS', 'n_bad_cell <- S.REFCELLS',
            'S.STORE[n_good_cell] = DEFINED (POBJECT n_good)',
            '$object_name(S, n_good) = $ptascii("ReviewTypedRestGood08")',
            'S.STORE[n_bad_cell] = DEFINED (PARRAY n_bad)',
            'S.ARRAYS[n_bad].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_bad_child))]',
            '$object_name(S, n_bad_child) = $ptascii("ReviewTypedRestRejected08")',
            'n_head =/= n_bad', 'n_head =/= n_rest', 'n_bad =/= n_rest',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("alias")) = (n_raw)',
            'n_raw <- S.REFCELLS', 'n_raw =/= n_bad_cell', 'n_raw =/= n_good_cell',
            'S.STORE[n_raw] = DEFINED (PARRAY n_bad)',
            '~$typed_reference_cell_source(S, n_good_cell)',
            '~$typed_reference_cell_source(S, n_bad_cell)',
            '$parameter_backing_at(S.PARAMETERBACKINGS, n_good_cell) = eps',
            '$parameter_backing_at(S.PARAMETERBACKINGS, n_bad_cell) = eps',
            '$variadic_conversion(S, psparam_rest, REFERENCE n_good_cell) = TYPEVALUE (POBJECT n_good)',
            '$variadic_conversion(S, psparam_rest, REFERENCE n_bad_cell) = TYPEREJECT',
            '~$variadic_string_candidate(S)', '~$api_variadic_candidate(S)',
            '$node_children(S, HARRAY n_rest) = [HCELL n_good_cell]',
            '$node_children(S, HCELL n_bad_cell) = [HARRAY n_bad]',
            '$heap_owners($heap_graph(S), HCELL n_good_cell) = 2',
            '$heap_owners($heap_graph(S), HCELL n_bad_cell) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_good) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_head) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_bad) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_head_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_bad_child) = 1',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("ReviewTypedRestTrace08")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '$call_task_valid(S, VARIADIC_RECEIVE porigin 2)', *ADMISSION,
            '~$variadic_receive_valid(S[.TODO = [VARIADIC_RECEIVE porigin 1]], porigin, 1)',
            *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
            '$throwable_field(S_one, n_error, "line") = PINT 15',
            '$throwable_field(S_one, n_error, "code") = PINT 0',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("reviewTypedRestTrace08(): Argument #3 must be of type ?ReviewTypedRestGood08, '
            'array given, called in ") ++ $call_sourcefile(S.FILES, porigin_call) '
            '++ $ptascii(" on line 17"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            '$entry_lookup(S_one.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_trace_frame))',
            '$entry_lookup(S_one.ARRAYS[n_trace_frame].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("reviewTypedRestTrace08")))',
            '$entry_lookup(S_one.ARRAYS[n_trace_frame].ITEMS, KSTRING $ptascii("line")) = (DIRECT (PINT 17))',
            '$entry_lookup(S_one.ARRAYS[n_trace_frame].ITEMS, KSTRING $ptascii("args")) = '
            '(DIRECT (PARRAY n_trace_args))',
            'S_one.ARRAYS[n_trace_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_head)), '
            'ENTRY (KINT 1) (DIRECT (POBJECT n_good)), ENTRY (KINT 2) (DIRECT (PARRAY n_bad))]',
            '$node_children(S_one, HARRAY n_trace_args) = [HARRAY n_head, HOBJECT n_good, HARRAY n_bad]',
            '$trace_graph_valid(S_one, n_trace)',
            'S_one.ARRAYS[n_rest] = S.ARRAYS[n_rest]',
            '$heap_owners($heap_graph(S_one), HCELL n_good_cell) = 2',
            '$heap_owners($heap_graph(S_one), HCELL n_bad_cell) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_good) = 2',
            '$heap_owners($heap_graph(S_one), HARRAY n_head) = 2',
            '$heap_owners($heap_graph(S_one), HARRAY n_bad) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_head_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_bad_child) = 1',
            'S_one.STORE = S.STORE', 'S_one.CURRENT = S.CURRENT',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
        ],
    },
    'caught-partial-rest-error-keeps-direct-trace-and-independent-array-alias': {
        'source': SOURCES['iterator-reference-typed-positional-variadic-review-partial-rest-direct-trace-source-alias'],
        'stage': ('S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.CURRENT = eps '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("P|"))'),
        'checks': [
            'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            '$lookup(S.ENV, $ptascii("caught")) = (n_error_cell)',
            'S.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
            'S.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
            '$throwable_field(S, n_error, "line") = PINT 15',
            '$throwable_field(S, n_error, "code") = PINT 0',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            '$entry_lookup(S.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_frame))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("reviewTypedRestTrace08")))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("line")) = (DIRECT (PINT 17))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("args")) = '
            '(DIRECT (PARRAY n_args))',
            'S.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_head)), '
            'ENTRY (KINT 1) (DIRECT (POBJECT n_good)), ENTRY (KINT 2) (DIRECT (PARRAY n_bad))]',
            'S.ARRAYS[n_head].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_head_child))]',
            'S.ARRAYS[n_bad].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_bad_child))]',
            '$object_name(S, n_head_child) = $ptascii("ReviewTypedRestHead08")',
            '$object_name(S, n_good) = $ptascii("ReviewTypedRestGood08")',
            '$object_name(S, n_bad_child) = $ptascii("ReviewTypedRestRejected08")',
            '$lookup(S.ENV, $ptascii("alias")) = (n_raw)', 'n_raw <- S.REFCELLS',
            'n_raw =/= n_error_cell', 'S.STORE[n_raw] = DEFINED (PARRAY n_bad)',
            '$node_children(S, HCELL n_raw) = [HARRAY n_bad]',
            '$node_children(S, HARRAY n_args) = [HARRAY n_head, HOBJECT n_good, HARRAY n_bad]',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_head) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_head_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_good) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_bad) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_bad_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_error) = 1',
            'S.DESTRUCTION.CALLED = n_data :: n_called_tail*',
            '$object_name(S, n_data) = $ptascii("ReviewTypedRestTrace08")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '~(n_head_child <- S.DESTRUCTION.CALLED)',
            '~(n_good <- S.DESTRUCTION.CALLED)', '~(n_bad_child <- S.DESTRUCTION.CALLED)',
            '$trace_graph_valid(S, n_trace)', *ADMISSION,
            'S_alias_args = S[.ARRAYS[n_args] = S.ARRAYS[n_args]'
            '[.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_head)), '
            'ENTRY (KINT 1) (DIRECT (POBJECT n_good)), ENTRY (KINT 2) (ALIAS n_raw)]]]',
            '$heap_valid($heap_graph(S_alias_args))',
            '~$trace_graph_valid(S_alias_args, n_trace)', *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("P|")]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("P|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("B|"), OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_error_cell) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_head) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_bad) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_trace) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_frame) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_args) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_head_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_good) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_bad_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
            'n_head_child <- S_done.DESTRUCTION.CALLED',
            'n_good <- S_done.DESTRUCTION.CALLED', 'n_bad_child <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
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
