#!/usr/bin/env python3
"""A second array warning keeps the first converted string across callback writes."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import concat_array_warning_review_cases as cases
import concat_array_warning_protocol as shared

REVIEW_HELPERS = r'''
dec $concat_array_review_warning_item(pevent) : nat
def $concat_array_review_warning_item(DIAGNOSTIC "Warning" n* z) = 1
def $concat_array_review_warning_item(pevent) = 0 -- otherwise
dec $concat_array_review_warnings(pevent*) : nat
def $concat_array_review_warnings(eps) = 0
def $concat_array_review_warnings(pevent :: pevent_tail*) = $($concat_array_review_warning_item(pevent) + $concat_array_review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $concat_array_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$concat_array_frontier(S, 1)',
        'S.TODO = (CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 0) :: (CONCAT_AFTER_RIGHT porigin pvalue_left 14) :: ptask_tail*',
        'poperand_left = VARIABLE ($ptascii("left")) 12',
        'poperand_right = VARIABLE ($ptascii("right")) 14',
        'pvalue_left = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("before"))',
        'S.STRINGDATA[n_string] = ($ptascii("before"))',
        '$lookup(S.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        'S.STORE[n_left] = DEFINED pvalue_left',
        'S.STORE[n_right] = DEFINED (PARRAY n_array)',
        'S.STORE[n_v] = DEFINED (PINT 100)',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        '~(n_left <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        'S.RESULT = KNOWN PNULL', 'S.BASE = BASE_VALUE (KNOWN PNULL)',
        'S.ORIGIN = $origin_child((porigin), [PCFIELD 1])',
        '$concat_array_source(S, porigin, poperand_left, poperand_right, 14)',
        '$concat_array_right_fresh(S, poperand_left, poperand_right, pvalue_left)',
        '$concat_array_right_valid(S, porigin, poperand_left, poperand_right, 14, 0)',
        '$task_nodes(CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 0) = eps',
        '$task_nodes(CONCAT_AFTER_RIGHT porigin pvalue_left 14) = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$concat_array_review_warnings(S.EVENTS) = 0',
        'pvalue_forged = PSTRING_CARRIER INTERNED_STRING ($ptascii("forged"))',
        'S_cache_bad = S[.TODO = (CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 0) :: (CONCAT_AFTER_RIGHT porigin pvalue_forged 14) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_cache_bad))',
        '~$concat_array_right_valid(S_cache_bad, porigin, poperand_left, poperand_right, 14, 0)',
        '~$call_descriptors_valid(S_cache_bad)',
        'S_carrier_bad = S[.TODO = (CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 0) :: (CONCAT_AFTER_RIGHT porigin (PSTRING_CARRIER INTERNED_STRING ($ptascii("before"))) 14) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_carrier_bad))',
        '~$concat_array_right_valid(S_carrier_bad, porigin, poperand_left, poperand_right, 14, 0)',
        '~$call_descriptors_valid(S_carrier_bad)',
        'S_consumer_bad = S[.TODO = (CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 0) :: (CONCAT_AFTER_LEFT porigin poperand_right false 14) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_consumer_bad))',
        '~$concat_array_right_valid(S_consumer_bad, porigin, poperand_left, poperand_right, 14, 0)',
        '~$call_descriptors_valid(S_consumer_bad)',
        'S_stage_bad = S[.TODO = (CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 2) :: (CONCAT_AFTER_RIGHT porigin pvalue_left 14) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_stage_bad))', '~$call_descriptors_valid(S_stage_bad)',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: (CONCAT_AFTER_RIGHT porigin pvalue_left 14) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_ehi_cache_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: (CONCAT_AFTER_RIGHT porigin pvalue_forged 14) :: ptask_tail*]',
        '$concat_array_right_valid(S_ehi_cache_bad, porigin, poperand_left, poperand_right, 14, 1)',
        '~$error_call_valid(S_ehi_cache_bad, perrorcall)',
        '$heap_valid($heap_graph(S_ehi_cache_bad))', '~$call_descriptors_valid(S_ehi_cache_bad)',
        'perrorcall_bad = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Warning" eps 14]',
        '~$error_call_valid(S_dispatch, perrorcall_bad)',
        'S_message_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: (CONCAT_AFTER_RIGHT porigin pvalue_left 14) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_message_bad))', '~$call_descriptors_valid(S_message_bad)',
        'S_return_found = $concat_array_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$concat_array_frontier(S_return, 4)',
        'S_return.TODO = (CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 1) :: (CONCAT_AFTER_RIGHT porigin pvalue_left 14) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_left)',
        'S_return.STORE[n_left] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("after"))',
        '$lookup(S_return.ENV, $ptascii("right")) = eps',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$concat_array_right_valid(S_return, porigin, poperand_left, poperand_right, 14, 1)',
        '~$concat_array_right_valid(S_return, porigin, poperand_left, poperand_right, 14, 0)',
        '~$concat_array_right_fresh(S_return, poperand_left, poperand_right, pvalue_left)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 0',
        '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '$concat_array_review_warnings(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Warning" ($ptascii("Array to string conversion")) 14) <- S_return.EVENTS',
        'S_fresh_bad = S_return[.TODO = (CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right 14 0) :: (CONCAT_AFTER_RIGHT porigin pvalue_left 14) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_fresh_bad))', '~$call_descriptors_valid(S_fresh_bad)',
        'S_fixed_budget = $drive_steps(S_return, 1)', 'S_fixed_budget.COMPLETION = BUDGET',
        'S_fixed = S_fixed_budget[.COMPLETION = NORMAL]', '$concat_array_frontier(S_fixed, 5)',
        'S_fixed.TODO = (CONCAT_AFTER_RIGHT porigin pvalue_left 14) :: ptask_tail*',
        'S_fixed.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))',
        'S_fixed.BASE = BASE_VALUE (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array"))))',
        'S_fixed.ENV = S_return.ENV', 'S_fixed.STORE = S_return.STORE',
        'S_fixed.ARRAYS = S_return.ARRAYS', 'S_fixed.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_fixed.EVENTS = S_return.EVENTS', '~$concat_array_tasks(S_fixed.TODO)',
        '$call_descriptors_valid(S_fixed)', '$heap_valid($heap_graph(S_fixed))',
        'S_result_budget = $drive_steps(S_fixed, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result.TODO = ptask_tail*', 'S_result.ORIGIN = (porigin)',
        'S_result.RESULT = KNOWN pvalue_result',
        'pvalue_result = PSTRING_CARRIER (REQUEST_STRING n_result) ($ptascii("beforeArray"))',
        'S_result.STRINGDATA[n_result] = ($ptascii("beforeArray"))',
        'S_result.STORE = S_return.STORE', 'S_result.ARRAYS = S_return.ARRAYS',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS', 'S_result.OBJECTS = S_return.OBJECTS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STORE[n_v] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED pvalue_result',
        'S_done.STORE[n_left] = DEFINED pvalue_changed',
        '$lookup(S_done.ENV, $ptascii("right")) = eps',
        '$concat_array_review_warnings(S_done.EVENTS) = 1',
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
    report['review_scope'] = 'Initial RIGHT array, cached first request string, missing borrowed CV, default warning and legacy finish; production steps only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
