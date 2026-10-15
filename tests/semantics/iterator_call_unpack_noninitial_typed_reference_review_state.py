#!/usr/bin/env python3
"""Reach two typed private-array receives and caught multi-payload trace ownership."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_noninitial_typed_reference_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'repeated-raw-array-second-type-receive-keeps-source-free-private-cells': {
        'source': SOURCES['iterator-noninitial-typed-review-same-raw-array-two-typed-private-cells'],
        'stage': ('S.TODO = [TYPE_RECEIVE porigin 1] -- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("reviewTypedRepeated06")'),
        'checks': [
            'pcallcontext.FUNCTION = porigin', 'pcallcontext.ARGC = 2',
            'pcallcontext.HOLES = eps', 'pcallcontext.NAMED = eps',
            'pcallcontext.EXTRA = eps', 'pcallcontext.LINE = 16',
            '$receiving_function(S, porigin) = (pfunction)',
            'psparam_first = pfunction.SIGNATURE.PARAMETERS[0]',
            'psparam_second = pfunction.SIGNATURE.PARAMETERS[1]',
            'psparam_first.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), '
            '(PTBRANCH ([PTBUILTIN "null"]))]',
            'psparam_second.TYPE = psparam_first.TYPE',
            r'psparam_first.BYREF /\ ~psparam_first.VARIADIC',
            r'psparam_second.BYREF /\ ~psparam_second.VARIADIC',
            '$lookup(S.ENV, $ptascii("first")) = (n_first)',
            '$lookup(S.ENV, $ptascii("second")) = (n_second)',
            'n_first =/= n_second', 'n_first <- S.REFCELLS', 'n_second <- S.REFCELLS',
            'S.STORE[n_first] = DEFINED (PARRAY n_array)',
            'S.STORE[n_second] = DEFINED (PARRAY n_array)',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            '$object_name(S, n_child) = $ptascii("ReviewTypedShared06")',
            '$node_children(S, HCELL n_first) = [HARRAY n_array]',
            '$node_children(S, HCELL n_second) = [HARRAY n_array]',
            '$node_children(S, HARRAY n_array) = [HOBJECT n_child]',
            '$heap_owners($heap_graph(S), HCELL n_first) = 1',
            '$heap_owners($heap_graph(S), HCELL n_second) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$propref_at(S.PROPREFS, n_first) = eps',
            '$propref_at(S.PROPREFS, n_second) = eps',
            '$parameter_backing_at(S.PARAMETERBACKINGS, n_first) = eps',
            '$parameter_backing_at(S.PARAMETERBACKINGS, n_second) = eps',
            '~$typed_parameter_source(S, psparam_first)',
            '~$typed_parameter_source(S, psparam_second)',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("ReviewTypedRepeat06")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '$call_task_valid(S, TYPE_RECEIVE porigin 1)', *ADMISSION,
            '~$typed_receive_valid(S[.TODO = [TYPE_RECEIVE porigin 2]], porigin, 2)',
            *ZERO, *ONE,
            'S_one.TODO = $function_body_tasks(S_one, pfunction)',
            'S_one.CURRENT = S.CURRENT', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.EVENTS = S.EVENTS',
            '$propref_at(S_one.PROPREFS, n_first) = eps',
            '$propref_at(S_one.PROPREFS, n_second) = eps',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1', *POST,
            'S_two_budget = $drive_steps(S_one, 1)',
            '$drive(S, 2) = S_two_budget',
        ],
    },
    'caught-array-type-error-keeps-byvalue-array-and-current-source-alias': {
        'source': SOURCES['iterator-noninitial-typed-review-byvalue-array-and-current-alias-rejected-by-array'],
        'stage': ('S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.CURRENT = eps '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("P|"))'),
        'checks': [
            'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            '$lookup(S.ENV, $ptascii("caught")) = (n_error_cell)',
            'S.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
            'S.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
            '$throwable_field(S, n_error, "line") = PINT 16',
            '$throwable_field(S, n_error, "code") = PINT 0',
            '$throwable_field(S, n_error, "trace") = PARRAY n_trace',
            '$entry_lookup(S.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_frame))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("reviewTypedAliasFailure06")))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("line")) = (DIRECT (PINT 19))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("args")) = '
            '(DIRECT (PARRAY n_args))',
            'S.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_earlier)), '
            'ENTRY (KINT 1) (DIRECT (POBJECT n_current))]',
            'S.ARRAYS[n_earlier].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier_child))]',
            '$object_name(S, n_earlier_child) = $ptascii("ReviewTypedEarlier06")',
            '$object_name(S, n_current) = $ptascii("ReviewTypedCurrent06")',
            '$lookup(S.ENV, $ptascii("alias")) = (n_raw)', 'n_raw <- S.REFCELLS',
            'n_raw =/= n_error_cell', 'S.STORE[n_raw] = DEFINED (POBJECT n_current)',
            '$node_children(S, HCELL n_raw) = [HOBJECT n_current]',
            '$node_children(S, HARRAY n_args) = [HARRAY n_earlier, HOBJECT n_current]',
            '$node_children(S, HARRAY n_earlier) = [HOBJECT n_earlier_child]',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_earlier) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_error) = 1',
            'S.DESTRUCTION.CALLED = n_data :: n_called_tail*',
            '$object_name(S, n_data) = $ptascii("ReviewTypedIterator06")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '~(n_earlier_child <- S.DESTRUCTION.CALLED)',
            '~(n_current <- S.DESTRUCTION.CALLED)',
            '$trace_graph_valid(S, n_trace)', *ADMISSION,
            'S_alias_args = S[.ARRAYS[n_args] = S.ARRAYS[n_args]'
            '[.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_earlier)), '
            'ENTRY (KINT 1) (ALIAS n_raw)]]]',
            '$heap_valid($heap_graph(S_alias_args))',
            '~$trace_graph_valid(S_alias_args, n_trace)', *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("P|")]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)',
            '$drive(S, 2) = S_two_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("P|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("HELD|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_error_cell) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_earlier) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_trace) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_frame) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_args) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_earlier_child) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
            'n_earlier_child <- S_done.DESTRUCTION.CALLED',
            'n_current <- S_done.DESTRUCTION.CALLED',
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
