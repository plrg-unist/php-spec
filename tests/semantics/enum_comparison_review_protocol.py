#!/usr/bin/env python3
"""Check pure and effectful ordering on source-reached enum/WeakMap objects."""
import base64
import json
from enum_core_review_protocol import PREFIX as CASE_PREFIX, term


PREFIX = CASE_PREFIX + r'''
dec $enumc_front(pstate) : bool
def $enumc_front(S) = true
  -- if $lookup(S.ENV,$ptascii("case")) = (n_cell_case)
  -- if S.STORE[n_cell_case] = DEFINED (POBJECT n_case)
  -- if $enum_case_object(S,n_case) =/= eps
  -- if $lookup(S.ENV,$ptascii("map")) = (n_cell_map)
  -- if S.STORE[n_cell_map] = DEFINED (POBJECT n_map)
  -- if $weakmap_at(S,n_map)
def $enumc_front(S) = false -- otherwise
dec $enumc_seek(pstate, nat) : pstate
def $enumc_seek(S, 0) = S
def $enumc_seek(S, n) = S
  -- if $(n > 0)
  -- if $enumc_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enumc_seek(S, n) = $enumc_seek($drive_steps($enumr_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enumc_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
'''


def assertions(case_id, main_fixture, source_path, expected_bytes):
    if case_id != 'enum-weakmap-order':
        raise ValueError(case_id)
    return ['S_initial = $php_run(' + main_fixture + ',0,' +
            json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_pair_found = $enumc_seek(S_initial,3000)',
        r'S_pair_found.COMPLETION = NORMAL \/ S_pair_found.COMPLETION = BUDGET',
        'S_pair = $enumr_running(S_pair_found)', '$enumc_front(S_pair)',
        '$call_descriptors_valid(S_pair)',
        '$lookup(S_pair.ENV,$ptascii("case")) = (n_cell_case)',
        'S_pair.STORE[n_cell_case] = DEFINED (POBJECT n_case)',
        '$lookup(S_pair.ENV,$ptascii("map")) = (n_cell_map)',
        'S_pair.STORE[n_cell_map] = DEFINED (POBJECT n_map)',
        '$enum_case_object(S_pair,n_case) = (pclassconstantdesc_case)',
        'S_pair.OBJECTS[n_map] = WEAKMAP eps', 'n_case =/= n_map',
        '(HOBJECT n_case) <- S_pair.ALLOCATIONS', '(HOBJECT n_map) <- S_pair.ALLOCATIONS',
        '$value_order(S_pair,POBJECT n_case,POBJECT n_map,eps) = ORDER 1',
        '$value_order(S_pair,POBJECT n_map,POBJECT n_case,eps) = ORDER 1',
        '$value_order_effect(S_pair,POBJECT n_case,POBJECT n_map,eps,6) = (S_pair,ORDER 1)',
        '$value_order_effect(S_pair,POBJECT n_map,POBJECT n_case,eps,6) = (S_pair,ORDER 1)',
        '$value_order(S_pair,POBJECT n_case,POBJECT n_case,eps) = ORDER 0',
        '$value_order(S_pair,POBJECT n_map,POBJECT n_map,eps) = ORDER 0',
        'S_zero = $drive_steps(S_pair,0)', 'S_zero = S_pair[.COMPLETION = BUDGET]',
        'S_finish = $drive_steps($enumr_running(S_zero),5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0', 'S_finish.TODO = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)']
