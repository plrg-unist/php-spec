"""Reached class-mismatch steps with cyclic trace arguments and skipped tail."""
import base64
import json

PREFIX = r'''
dec $tck_stage(pstate) : bool
def $tck_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tck_stage(S) = false -- otherwise
dec $tck_seek(pstate, nat) : pstate
def $tck_seek(S, n) = S -- if $tck_stage(S) \/ n = 0
def $tck_seek(S, n) = $tck_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tck_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tck_seek(S, n) = S -- otherwise
dec $tck_event(pevent) : ptbytes
def $tck_event(OUTPUT ptbytes) = ptbytes
def $tck_event(pevent) = eps -- otherwise
dec $tck_output(pevent*) : ptbytes
def $tck_output(eps) = eps
def $tck_output(pevent :: pevent_tail*) = $tck_event(pevent) ++ $tck_output(pevent_tail*)
'''


def checks(program, path, name):
    assert name == 'state-skip'
    encoded_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tck_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tck_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (BINARY_RIGHT SPACESHIP poperand_first z_first) :: ptask_first*',
        '$lookup(S_first.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_first.ENV,$ptascii("b")) = (n_bcv)',
        'S_first.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_first.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        'S_first.OBJECTS[n_a] = THROWABLE pthrowable_a',
        'S_first.OBJECTS[n_b] = THROWABLE pthrowable_b',
        'pthrowable_a.KIND = "Exception"',
        'pthrowable_b.KIND = "Error"',
        '$throwable_object_image_valid(S_first,n_a)',
        '$throwable_object_image_valid(S_first,n_b)',
        '$throwable_cross_kind_pair(S_first,n_a,n_b,eps)',
        '$throwable_field(S_first,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S_first,n_b,"trace") = PARRAY n_trace_b',
        '$entry_lookup(S_first.ARRAYS[n_trace_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_a))',
        '$entry_lookup(S_first.ARRAYS[n_trace_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_b))',
        '$entry_lookup(S_first.ARRAYS[n_frame_a].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_a))',
        '$entry_lookup(S_first.ARRAYS[n_frame_b].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_b))',
        '$entry_lookup(S_first.ARRAYS[n_args_a].ITEMS,KINT 0) = (DIRECT (POBJECT n_cycle_a))',
        '$entry_lookup(S_first.ARRAYS[n_args_b].ITEMS,KINT 0) = (DIRECT (POBJECT n_cycle_b))',
        'n_cycle_a =/= n_cycle_b',
        'S_first.OBJECTS[n_cycle_a] = STDINSTANCE',
        'S_first.OBJECTS[n_cycle_b] = STDINSTANCE',
        '$objectprops_record_at(S_first.OBJECTPROPS,n_cycle_a) = (pobjectprops_cycle_a)',
        '$objectprops_record_at(S_first.OBJECTPROPS,n_cycle_b) = (pobjectprops_cycle_b)',
        '$property_slot_at(pobjectprops_cycle_a.SLOTS,$ptascii("self")) = (ppropertyslot_cycle_a)',
        '$property_slot_at(pobjectprops_cycle_b.SLOTS,$ptascii("self")) = (ppropertyslot_cycle_b)',
        'ppropertyslot_cycle_a.STATE = PROP_VALUE (DIRECT (POBJECT n_cycle_a))',
        'ppropertyslot_cycle_b.STATE = PROP_VALUE (DIRECT (POBJECT n_cycle_b))',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b,HOBJECT n_cycle_a,HOBJECT n_cycle_b,HARRAY n_trace_a,HARRAY n_trace_b,HARRAY n_frame_a,HARRAY n_frame_b,HARRAY n_args_a,HARRAY n_args_b],S_first.ALLOCATIONS)',
        '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER 1)',
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT 1)',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.OBJECTS = S_first.OBJECTS /\ S_first_raw.OBJECTPROPS = S_first.OBJECTPROPS',
        r'S_first_raw.OBJECTTABLES = S_first.OBJECTTABLES /\ S_first_raw.ARRAYS = S_first.ARRAYS',
        r'S_first_raw.STORE = S_first.STORE /\ S_first_raw.ALLOCATIONS = S_first.ALLOCATIONS',
        'S_first_raw.EVENTS = S_first.EVENTS',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = $prune_allocations(S_first_raw)[.COMPLETION = BUDGET]',
        'S_second_found = $tck_seek(S_first_raw,1000)',
        '$tck_stage(S_second_found)',
        'S_second = S_second_found[.COMPLETION = NORMAL]',
        'S_second.TODO = (BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array_left)) z_second) :: ptask_second*',
        'S_second.RESULT = KNOWN (PARRAY n_array_right)',
        '$entry_lookup(S_second.ARRAYS[n_array_left].ITEMS,KINT 0) = (DIRECT (PINT 0))',
        '$entry_lookup(S_second.ARRAYS[n_array_right].ITEMS,KINT 0) = (DIRECT (PINT 0))',
        '$entry_lookup(S_second.ARRAYS[n_array_left].ITEMS,KINT 1) = (DIRECT (POBJECT n_a))',
        '$entry_lookup(S_second.ARRAYS[n_array_right].ITEMS,KINT 1) = (DIRECT (POBJECT n_b))',
        '$entry_lookup(S_second.ARRAYS[n_array_left].ITEMS,KINT 2) = (DIRECT (POBJECT n_tail))',
        '$entry_lookup(S_second.ARRAYS[n_array_right].ITEMS,KINT 2) = (DIRECT pvalue_tail_right)',
        '$string_plain(pvalue_tail_right) = PSTRING $ptascii("x")',
        '$throwable_cross_kind_pair(S_second,n_a,n_b,[HARRAY n_array_left])',
        '$value_order_effect(S_second,POBJECT n_a,POBJECT n_b,[HARRAY n_array_left],z_second) = (S_second,ORDER 1)',
        '$value_order_effect(S_second,PARRAY n_array_left,PARRAY n_array_right,eps,z_second) = (S_second,ORDER 1)',
        'PhpStep: S_second ~> S_second_raw',
        'S_second_raw.RESULT = KNOWN (PINT 1)',
        'S_second_raw.TODO = ptask_second*',
        r'S_second_raw.OBJECTS = S_second.OBJECTS /\ S_second_raw.OBJECTPROPS = S_second.OBJECTPROPS',
        r'S_second_raw.OBJECTTABLES = S_second.OBJECTTABLES /\ S_second_raw.ARRAYS = S_second.ARRAYS',
        r'S_second_raw.STORE = S_second.STORE /\ S_second_raw.ALLOCATIONS = S_second.ALLOCATIONS',
        'S_second_raw.EVENTS = S_second.EVENTS',
        '$aggregate_compare_seen(S_second_raw) = eps',
        '$drive_steps(S_second,0) = S_second[.COMPLETION = BUDGET]',
        '$drive_steps(S_second,1) = $prune_allocations(S_second_raw)[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_second_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tck_output(S_done.EVENTS) = $ptascii("B|1|A|1|")',
    ]
