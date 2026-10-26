"""Reached cold Throwable pair and equal-prefix array comparison steps."""
import base64
import json

PREFIX = r'''
dec $tc_stage(pstate) : bool
def $tc_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tc_stage(S) = false -- otherwise
dec $tc_seek(pstate, nat) : pstate
def $tc_seek(S, n) = S -- if $tc_stage(S) \/ n = 0
def $tc_seek(S, n) = $tc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tc_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tc_seek(S, n) = S -- otherwise
dec $tc_event(pevent) : ptbytes
def $tc_event(OUTPUT ptbytes) = ptbytes
def $tc_event(pevent) = eps -- otherwise
dec $tc_output(pevent*) : ptbytes
def $tc_output(eps) = eps
def $tc_output(pevent :: pevent_tail*) = $tc_event(pevent) ++ $tc_output(pevent_tail*)
'''


def checks(program, path, name):
    assert name == 'state-direct-array'
    source_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + source_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tc_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tc_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (BINARY_RIGHT SPACESHIP poperand_first z_first) :: ptask_first*',
        '$lookup(S_first.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_first.ENV,$ptascii("b")) = (n_bcv)',
        'S_first.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_first.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$throwable_cold_pair(S_first,n_a,n_b)',
        '$throwable_field(S_first,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S_first,n_b,"trace") = PARRAY n_trace_b',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_trace_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_trace_b) = 1',
        '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER 0)',
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT 0)',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.OBJECTS = S_first.OBJECTS /\ S_first_raw.OBJECTPROPS = S_first.OBJECTPROPS',
        r'S_first_raw.ARRAYS = S_first.ARRAYS /\ S_first_raw.ALLOCATIONS = S_first.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_first_raw)),HARRAY n_trace_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_raw)),HARRAY n_trace_b) = 1',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = S_first_raw[.COMPLETION = BUDGET]',
        'S_second_found = $tc_seek(S_first_raw,1000)',
        '$tc_stage(S_second_found)',
        'S_second = S_second_found[.COMPLETION = NORMAL]',
        'S_second.TODO = (BINARY_RIGHT SPACESHIP poperand_second z_second) :: ptask_second*',
        '$lookup(S_second.ENV,$ptascii("x")) = (n_xcv)',
        '$lookup(S_second.ENV,$ptascii("y")) = (n_ycv)',
        'S_second.STORE[n_xcv] = DEFINED (PARRAY n_x)',
        'S_second.STORE[n_ycv] = DEFINED (PARRAY n_y)',
        'S_second.ARRAYS[n_x].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_a)),ENTRY (KINT 1) (DIRECT (PINT 1))]',
        'S_second.ARRAYS[n_y].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_b)),ENTRY (KINT 1) (DIRECT (PINT 3))]',
        '$value_order_effect(S_second,POBJECT n_a,POBJECT n_b,[HARRAY n_x],z_second) = (S_second,ORDER 0)',
        '$value_order_effect(S_second,PARRAY n_x,PARRAY n_y,eps,z_second) = (S_second,ORDER $(-1))',
        'PhpStep: S_second ~> S_second_raw',
        'S_second_raw.RESULT = KNOWN (PINT $(-1))',
        'S_second_raw.TODO = ptask_second*',
        r'S_second_raw.OBJECTS = S_second.OBJECTS /\ S_second_raw.OBJECTPROPS = S_second.OBJECTPROPS',
        r'S_second_raw.ARRAYS = S_second.ARRAYS /\ S_second_raw.ALLOCATIONS = S_second.ALLOCATIONS',
        '$aggregate_compare_seen(S_second_raw) = eps',
        '$drive_steps(S_second,0) = S_second[.COMPLETION = BUDGET]',
        '$drive_steps(S_second,1) = S_second_raw[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_second_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tc_output(S_done.EVENTS) = $ptascii("B|0|-1|")',
    ]
