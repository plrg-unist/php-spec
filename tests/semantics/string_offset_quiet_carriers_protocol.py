#!/usr/bin/env python3
"""Reached quiet string carriers, unchanged storage, and bounded admissions."""
import base64
import json
from pathlib import Path

import string_offset_quiet_carriers_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = true
  -- if S.TODO = (ISSET_RESULT false z) :: ptask_tail*
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ISSET_RESULT true z) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (COALESCE_QUIET expression z_left z_right) :: ptask_tail*
'''


def conditions(name, program, path, stdout):
    string_key = name.endswith('-key')
    key = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))' if string_key else 'PINT 0'
    base = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("a0"))'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        'S.TODO = (ISSET_RESULT false 2) :: ptask_after*',
        'S.BASE = BASE_DIM pbase poperand 2',
        '$lookup(S.ENV, $ptascii("s")) = (n_s)',
        'S.STORE[n_s] = DEFINED (' + base + ')',
        '~(n_s <- S.REFCELLS)', '$heap_owners($heap_graph(S), HCELL n_s) = 1',
        'S_base = $quiet_base(S, pbase, 2)', 'S_base.RESULT = KNOWN (' + base + ')',
        'S_key = $quiet_operand(S_base, poperand)', 'S_key.RESULT = KNOWN (' + key + ')',
        '$string_carrier_valid(S, ' + base + ')', '$value_nodes(' + base + ') = eps',
        '$quiet_dimension_value(S, ' + base + ', ' + key + ', 2) = S[.RESULT = KNOWN (PSTRING ($ptascii("a")))]',
        '$isset_dimension_value(S, ' + base + ', ' + key + ', false, 2) = S[.RESULT = KNOWN (PBOOL true)]',
        '$isset_dimension_value(S, ' + base + ', ' + key + ', true, 2) = S[.RESULT = KNOWN (PBOOL false)]',
        '$quiet_dimension_value(S, ' + base + ', ' + key + ', 2) = $quiet_dimension_value(S, PSTRING ($ptascii("a0")), PINT 0, 2)',
        '$isset_dimension_value(S, ' + base + ', ' + key + ', false, 2) = $isset_dimension_value(S, PSTRING ($ptascii("a0")), PINT 0, false, 2)',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
        'PhpStep: S ~> S_test',
        'S_test.RESULT = KNOWN (PBOOL true)', 'S_test.TODO = ptask_after*',
        'S_test.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_test.STORE = S.STORE', 'S_test.ENV = S.ENV', 'S_test.STRINGDATA = S.STRINGDATA',
        'S_test.ALLOCATIONS = S.ALLOCATIONS', 'S_test.HELD = S.HELD',
    ] + driven('S', 'S_test', 'S_test_driven')
    if string_key:
        checks += [
            '$lookup(S.ENV, $ptascii("key")) = (n_key)',
            'S.STORE[n_key] = DEFINED (' + key + ')', '~(n_key <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_key) = 1',
            '$quiet_string(S, $ptascii("a0"), ' + key + ', 2) = $quiet_string(S, $ptascii("a0"), PSTRING ($ptascii("0")), 2)',
            '$isset_string(S, $ptascii("a0"), ' + key + ', true, 2) = $isset_string(S, $ptascii("a0"), PSTRING ($ptascii("0")), true, 2)',
        ]
    checks += seek('S_test_driven', 11, 'S_empty') + [
        'S_empty.TODO = (ISSET_RESULT true 2) :: ptask_empty*',
        'PhpStep: S_empty ~> S_empty_test',
        'S_empty_test.RESULT = KNOWN (PBOOL false)', 'S_empty_test.TODO = ptask_empty*',
        'S_empty_test.STORE = S_empty.STORE', 'S_empty_test.STRINGDATA = S_empty.STRINGDATA',
    ] + driven('S_empty', 'S_empty_test', 'S_empty_driven')
    checks += seek('S_empty_driven', 12, 'S_coalesce') + [
        'S_coalesce.TODO = (COALESCE_QUIET expression_right 2 2) :: ptask_coalesce*',
        'PhpStep: S_coalesce ~> S_coalesced',
        'S_coalesced.RESULT = KNOWN (PSTRING ($ptascii("a")))',
        'S_coalesced.TODO = ptask_coalesce*', 'S_coalesced.STORE = S_coalesce.STORE',
        'S_coalesced.STRINGDATA = S_coalesce.STRINGDATA',
    ] + driven('S_coalesce', 'S_coalesced', 'S_coalesce_driven')
    checks += [
        'S_done = $drive_steps(S_coalesce_driven, 1000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.POOLS = S.POOLS', 'S_done.CODE = S.CODE',
        'S_done.STORE[n_s] = DEFINED (' + base + ')',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 1000) = S_done',
    ]
    for bad in ('PSTRING_CARRIER INTERNED_STRING [97,0]',
                'PSTRING_CARRIER INTERNED_STRING [256]'):
        checks += [
            '$quiet_dimension_value(S, ' + bad + ', PINT 0, 2) = S[.RESULT = KNOWN PNULL]',
            '$isset_dimension_value(S, ' + bad + ', PINT 0, false, 2) = S[.RESULT = KNOWN (PBOOL false)]',
        ]
    checks += [
        'S_request = S[.STRINGDATA = S.STRINGDATA ++ [($ptascii("a0"))]]',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("a0"))',
        '$string_carrier_valid(S_request, pvalue_request)',
        '$quiet_dimension_value(S_request, pvalue_request, PINT 0, 2) = S_request[.RESULT = KNOWN PNULL]',
        '$isset_dimension_value(S_request, pvalue_request, PINT 0, false, 2) = S_request[.RESULT = KNOWN (PBOOL false)]',
        '$isset_string(S_request, $ptascii("a0"), pvalue_request, false, 2) = S_request[.RESULT = KNOWN (PBOOL false)]',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, extra_inputs=(Path(__file__),)) else 1)
