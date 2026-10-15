#!/usr/bin/env python3
"""A borrowed array CV can disappear before fixed cast delivery."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import array_string_cast_review_cases as cases
import array_string_cast_protocol as shared

REVIEW_HELPERS = r'''
dec $array_string_cast_review_warning_item(pevent) : nat
def $array_string_cast_review_warning_item(DIAGNOSTIC "Warning" n* z) = 1
def $array_string_cast_review_warning_item(pevent) = 0 -- otherwise
dec $array_string_cast_review_warnings(pevent*) : nat
def $array_string_cast_review_warnings(eps) = 0
def $array_string_cast_review_warnings(pevent :: pevent_tail*) = $($array_string_cast_review_warning_item(pevent) + $array_string_cast_review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $array_string_cast_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S, 1)',
        'S.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand 11 0) :: ptask_tail*',
        'poperand = VARIABLE ($ptascii("input")) 11',
        '$lookup(S.ENV, $ptascii("input")) = (n_input)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        'S.STORE[n_input] = DEFINED (PARRAY n_array)',
        'S.STORE[n_v] = DEFINED pvalue_pending',
        '$string_bytes(pvalue_pending) = ($ptascii("pending"))',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)), ENTRY (KINT 1) (DIRECT (PINT 2))]',
        '~(n_input <- S.REFCELLS)', '~(n_array <- S.GC.IMMUTABLE)',
        'S.RESULT = KNOWN PNULL', 'S.BASE = BASE_VALUE (KNOWN PNULL)',
        '$array_string_cast_source(S, porigin, poperand, 11)',
        '$array_string_cast_snapshot(S, poperand)',
        '$array_string_cast_warning_valid(S, porigin, poperand, 11, 0)',
        '$task_nodes(ARRAY_STRING_CAST_WARNING porigin poperand 11 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_input) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$array_string_cast_review_warnings(S.EVENTS) = 0',
        'S_line_bad = S[.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand 10 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        'S_flavor_bad = S[.TODO = (ARRAY_STRING_CAST_WARNING porigin (KNOWN (PARRAY n_array)) 11 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_flavor_bad))', '~$call_descriptors_valid(S_flavor_bad)',
        'S_ref_bad = $reference_cell(S, n_input)',
        '$heap_valid($heap_graph(S_ref_bad))', '~$array_string_cast_snapshot(S_ref_bad, poperand)',
        '~$call_descriptors_valid(S_ref_bad)',
        'S_scalar_bad = S[.STORE = $set_cell(S.STORE, n_input, DEFINED (PINT 99))]',
        '$heap_valid($heap_graph(S_scalar_bad))', '~$array_string_cast_snapshot(S_scalar_bad, poperand)',
        '~$call_descriptors_valid(S_scalar_bad)',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARRAY_STRING_CAST_WARNING porigin poperand 11 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_bad = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Warning" eps 11]',
        '~$error_call_valid(S_dispatch, perrorcall_bad)',
        'S_message_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_message_bad))', '~$call_descriptors_valid(S_message_bad)',
        'S_return_found = $array_string_cast_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S_return, 4)',
        'S_return.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand 11 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("input")) = eps',
        '$integer_pointer_select(S_return, poperand) = eps',
        'S_return.STORE[n_v] = DEFINED pvalue_pending',
        '$array_string_cast_source(S_return, porigin, poperand, 11)',
        '~$array_string_cast_snapshot(S_return, poperand)',
        '$array_string_cast_warning_valid(S_return, porigin, poperand, 11, 1)',
        '~$array_string_cast_warning_valid(S_return, porigin, poperand, 11, 0)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_input) = 0',
        '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '$array_string_cast_review_warnings(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Warning" ($ptascii("Array to string conversion")) 11) <- S_return.EVENTS',
        'S_fresh_bad = S_return[.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand 11 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_fresh_bad))', '~$call_descriptors_valid(S_fresh_bad)',
        'S_fresh_ehi_bad = S_return[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_fresh_ehi_bad))', '~$error_call_valid(S_fresh_ehi_bad, perrorcall)',
        '~$call_descriptors_valid(S_fresh_ehi_bad)',
        'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result.TODO = ptask_tail*',
        'S_result.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))',
        'S_result.BASE = BASE_VALUE (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array"))))',
        'S_result.ENV = S_return.ENV', 'S_result.STORE = S_return.STORE',
        'S_result.ARRAYS = S_return.ARRAYS', 'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.OBJECTS = S_return.OBJECTS', 'S_result.EVENTS = S_return.EVENTS',
        '$lookup(S_result.ENV, $ptascii("input")) = eps',
        'S_result.STORE[n_v] = DEFINED pvalue_pending',
        '$heap_owners($heap_prune($heap_graph(S_result)), HARRAY n_array) = 0',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))',
        '$lookup(S_done.ENV, $ptascii("input")) = (n_after)',
        'S_done.STORE[n_after] = DEFINED pvalue_after',
        '$string_bytes(pvalue_after) = ($ptascii("after"))',
        '$array_string_cast_review_warnings(S_done.EVENTS) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done',
    ]


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(shared.__file__), Path(cases.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.conditions = cases, tuple(cases.CASES), conditions
    shared.HELPERS += REVIEW_HELPERS
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['review_inputs'] = before
    report['review_scope'] = 'Removed borrowed CV, zero array owner, historical fixed interned result and one default warning; production steps only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
