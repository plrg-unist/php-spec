#!/usr/bin/env python3
"""Independent typed private-cell writes and receive-error trace ownership."""
import argparse
import hashlib
import json
from pathlib import Path

import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_typed_reference_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']

CASES = {
    'typed-class-body-write-leaves-only-source-alias-payload-owner': {
        'source': SOURCES['iterator-typed-reference-review-class-alias-incompatible-body-write'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("reviewTypedClass03") '
                  '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("F"))'),
        'checks': [
            '$receiving_function(S, pcallcontext.FUNCTION) = (pfunction)',
            'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = [0]',
            'pcallcontext.LINE = 20', 'pcallcontext.NAMED = eps', 'pcallcontext.EXTRA = eps',
            'psparam = pfunction.SIGNATURE.PARAMETERS[1]',
            r'psparam.BYREF /\ ~psparam.VARIADIC',
            'psparam.TYPE = [(PTBRANCH ([(PTCLASS $ptascii("ReviewTypedPayload03"))])), '
            '(PTBRANCH ([PTBUILTIN "null"]))]',
            '$lookup(S.ENV, $ptascii("prefix")) = (n_prefix)',
            'S.STORE[n_prefix] = DEFINED (PINT 17)',
            '$lookup(S.ENV, $ptascii("item")) = (n_private)',
            'n_private <- S.REFCELLS', 'S.STORE[n_private] = DEFINED (PINT 19)',
            '~$typed_reference_cell_source(S, n_private)',
            '~$typed_parameter_source(S, psparam)',
            '$typed_parameter_conversion(S, psparam, PINT 19) = TYPEREJECT',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("alias")) = (n_raw)',
            'n_private =/= n_raw', 'n_raw <- S.REFCELLS',
            'S.STORE[n_raw] = DEFINED (POBJECT n_payload)',
            '$node_children(S, HCELL n_raw) = [HOBJECT n_payload]',
            '$object_name(S, n_payload) = $ptascii("ReviewTypedPayload03")',
            '$heap_owners($heap_graph(S), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("ReviewTypedIterator03")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '~(n_payload <- S.DESTRUCTION.CALLED)', *ADMISSION, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F")]',
            'S_one.STORE = S.STORE', 'S_one.CURRENT = S.CURRENT',
            'S_one.PROPREFS = S.PROPREFS', *POST,
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            '$drive(S, 4001) = S_done',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F"), '
            'OUTPUT $ptascii("19"), OUTPUT $ptascii("|"), OUTPUT $ptascii("HELD|"), '
            'OUTPUT $ptascii("O|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_private) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'array-receive-rejection-owns-direct-payload-trace-until-catch-release': {
        'source': SOURCES['iterator-typed-reference-review-object-rejected-by-array-trace'],
        'stage': ('S.TODO = [TYPE_RECEIVE porigin 1] '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("reviewTypedMismatch03")'),
        'checks': [
            '$receiving_function(S, porigin) = (pfunction)',
            'pcallcontext.FUNCTION = porigin', 'pcallcontext.ARGC = 2',
            'pcallcontext.HOLES = [0]', 'pcallcontext.LINE = 20',
            'pcallcontext.CALLSITE = (porigin_call)',
            'psparam = pfunction.SIGNATURE.PARAMETERS[1]',
            r'psparam.BYREF /\ ~psparam.VARIADIC',
            'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), '
            '(PTBRANCH ([PTBUILTIN "null"]))]',
            '$default_parameter_line(S, porigin, 1) = 14',
            '$lookup(S.ENV, $ptascii("prefix")) = (n_prefix)',
            'S.STORE[n_prefix] = DEFINED (PINT 17)',
            '$lookup(S.ENV, $ptascii("item")) = (n_private)',
            'n_private <- S.REFCELLS',
            'S.STORE[n_private] = DEFINED (POBJECT n_payload)',
            '$object_name(S, n_payload) = $ptascii("ReviewTypedPayload03")',
            '~$typed_reference_cell_source(S, n_private)',
            '~$typed_parameter_source(S, psparam)',
            '$typed_parameter_conversion(S, psparam, POBJECT n_payload) = TYPEREJECT',
            '$heap_owners($heap_graph(S), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("ReviewTypedIterator03")',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '$call_task_valid(S, TYPE_RECEIVE porigin 1)', *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
            '$throwable_field(S_one, n_error, "line") = PINT 14',
            '$throwable_field(S_one, n_error, "code") = PINT 0',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("reviewTypedMismatch03(): Argument #2 ($item) must be of type ?array, '
            'ReviewTypedPayload03 given, called in ") ++ $call_sourcefile(S.FILES, porigin_call) '
            '++ $ptascii(" on line 20"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            '$entry_lookup(S_one.ARRAYS[n_trace].ITEMS, KINT 0) = '
            '(DIRECT (PARRAY n_trace_frame))',
            '$entry_lookup(S_one.ARRAYS[n_trace_frame].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("reviewTypedMismatch03")))',
            '$entry_lookup(S_one.ARRAYS[n_trace_frame].ITEMS, KSTRING $ptascii("args")) = '
            '(DIRECT (PARRAY n_trace_args))',
            'S_one.ARRAYS[n_trace_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), '
            'ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]',
            '$node_children(S_one, HARRAY n_trace_args) = [HOBJECT n_payload]',
            '$trace_graph_valid(S_one, n_trace)',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
            'S_one.STORE = S.STORE', 'S_one.CURRENT = S.CURRENT',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            '$drive(S, 4001) = S_done',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("T|"), '
            'OUTPUT $ptascii("O|"), OUTPUT $ptascii("E")]',
            '$heap_owners($heap_graph(S_done), HCELL n_private) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
}


def run(selected):
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
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(independent_inputs={str(p): hashlib.sha256(b).hexdigest()
                                     for p, b in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, passed=passed and stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
