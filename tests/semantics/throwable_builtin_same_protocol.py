"""Reached complete physical slot and finite trace comparisons."""
import base64
import json

PREFIX = r'''
dec $tbs_stage(pstate) : bool
def $tbs_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tbs_stage(S) = false -- otherwise
dec $tbs_seek(pstate, nat) : pstate
def $tbs_seek(S, n) = S -- if $tbs_stage(S) \/ n = 0
def $tbs_seek(S, n) = $tbs_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tbs_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tbs_seek(S, n) = S -- otherwise
dec $tbs_event(pevent) : ptbytes
def $tbs_event(OUTPUT ptbytes) = ptbytes
def $tbs_event(pevent) = eps -- otherwise
dec $tbs_output(pevent*) : ptbytes
def $tbs_output(eps) = eps
def $tbs_output(pevent :: pevent_tail*) = $tbs_event(pevent) ++ $tbs_output(pevent_tail*)
'''


def checks(program, path, name):
    encoded_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    if name == 'state-severity':
        return severity_checks(program, encoded_path)
    assert name == 'type-trace-arrays'
    return trace_checks(program, encoded_path)


def severity_checks(program, encoded_path):
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tbs_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tbs_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (BINARY_RIGHT SPACESHIP poperand_first z_first) :: ptask_first*',
        '$lookup(S_first.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_first.ENV,$ptascii("b")) = (n_bcv)',
        'S_first.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_first.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        'S_first.OBJECTS[n_a] = THROWABLE pthrowable_a',
        'S_first.OBJECTS[n_b] = THROWABLE pthrowable_b',
        'pthrowable_a.KIND = "ErrorException"',
        'pthrowable_b.KIND = "ErrorException"',
        '$throwable_object_image_valid(S_first,n_a)',
        '$throwable_object_image_valid(S_first,n_b)',
        '$throwable_field(S_first,n_a,"previous") = PNULL',
        '$throwable_field(S_first,n_b,"previous") = PNULL',
        '$throwable_field(S_first,n_a,"string") = PSTRING eps',
        '$throwable_field(S_first,n_b,"string") = PSTRING eps',
        '$throwable_field(S_first,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S_first,n_b,"trace") = PARRAY n_trace_b',
        'S_first.ARRAYS[n_trace_a].ITEMS = eps',
        'S_first.ARRAYS[n_trace_b].ITEMS = eps',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b,HARRAY n_trace_a,HARRAY n_trace_b],S_first.ALLOCATIONS)',
        '$objectprops_at(S_first.OBJECTPROPS,n_a) = (ppropertyslot_a*)',
        '$objectprops_at(S_first.OBJECTPROPS,n_b) = (ppropertyslot_b*)',
        '|ppropertyslot_a*| = 8',
        '|ppropertyslot_b*| = 8',
        '$property_order(S_first,ppropertyslot_a*[0:7],ppropertyslot_b*[0:7],[HOBJECT n_a]) = ORDER 0',
        '$throwable_field(S_first,n_a,"severity") = PINT 3',
        '$throwable_field(S_first,n_b,"severity") = PINT 4',
        '$throwable_builtin_same_pair(S_first,n_a,n_b,eps)',
        '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER $(-1))',
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT $(-1))',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.OBJECTS = S_first.OBJECTS /\ S_first_raw.OBJECTPROPS = S_first.OBJECTPROPS',
        r'S_first_raw.ARRAYS = S_first.ARRAYS /\ S_first_raw.OBJECTTABLES = S_first.OBJECTTABLES',
        r'S_first_raw.STORE = S_first.STORE /\ S_first_raw.ALLOCATIONS = S_first.ALLOCATIONS',
        'S_first_raw.EVENTS = S_first.EVENTS',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = $prune_allocations(S_first_raw)[.COMPLETION = BUDGET]',
        'S_warm_found = $tbs_seek(S_first_raw,1000)',
        '$tbs_stage(S_warm_found)',
        'S_warm = S_warm_found[.COMPLETION = NORMAL]',
        'S_warm.TODO = (BINARY_RIGHT SPACESHIP poperand_warm z_warm) :: ptask_warm*',
        '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_a',
        '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_b',
        'preqbytes_a = preqbytes_b',
        'preqbytes_a =/= eps',
        '$objectprops_at(S_warm.OBJECTPROPS,n_a) = (ppropertyslot_a_warm*)',
        '$objectprops_at(S_warm.OBJECTPROPS,n_b) = (ppropertyslot_b_warm*)',
        '$property_order(S_warm,ppropertyslot_a_warm*[0:7],ppropertyslot_b_warm*[0:7],[HOBJECT n_a]) = ORDER 0',
        '$throwable_builtin_same_pair(S_warm,n_a,n_b,eps)',
        '$value_order_effect(S_warm,POBJECT n_a,POBJECT n_b,eps,z_warm) = (S_warm,ORDER $(-1))',
        'PhpStep: S_warm ~> S_warm_raw',
        'S_warm_raw.RESULT = KNOWN (PINT $(-1))',
        'S_warm_raw.TODO = ptask_warm*',
        r'S_warm_raw.OBJECTS = S_warm.OBJECTS /\ S_warm_raw.OBJECTPROPS = S_warm.OBJECTPROPS',
        r'S_warm_raw.ARRAYS = S_warm.ARRAYS /\ S_warm_raw.OBJECTTABLES = S_warm.OBJECTTABLES',
        'S_warm_raw.EVENTS = S_warm.EVENTS',
        '$aggregate_compare_seen(S_warm_raw) = eps',
        '$drive_steps(S_warm,0) = S_warm[.COMPLETION = BUDGET]',
        '$drive_steps(S_warm,1) = $prune_allocations(S_warm_raw)[.COMPLETION = BUDGET]',
        'S_array_found = $tbs_seek(S_warm_raw,1000)',
        '$tbs_stage(S_array_found)',
        'S_array = S_array_found[.COMPLETION = NORMAL]',
        'S_array.TODO = (BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_left)) z_array) :: ptask_array*',
        'S_array.RESULT = KNOWN (PARRAY n_right)',
        '$entry_lookup(S_array.ARRAYS[n_left].ITEMS,KINT 0) = (DIRECT (PINT 0))',
        '$entry_lookup(S_array.ARRAYS[n_right].ITEMS,KINT 0) = (DIRECT (PINT 0))',
        '$entry_lookup(S_array.ARRAYS[n_left].ITEMS,KINT 1) = (DIRECT (POBJECT n_a))',
        '$entry_lookup(S_array.ARRAYS[n_right].ITEMS,KINT 1) = (DIRECT (POBJECT n_b))',
        '$entry_lookup(S_array.ARRAYS[n_left].ITEMS,KINT 2) = (DIRECT (POBJECT n_tail))',
        '$entry_lookup(S_array.ARRAYS[n_right].ITEMS,KINT 2) = (DIRECT pvalue_tail)',
        '$string_plain(pvalue_tail) = PSTRING $ptascii("x")',
        '$throwable_builtin_same_pair(S_array,n_a,n_b,[HARRAY n_left])',
        '$value_order_effect(S_array,PARRAY n_left,PARRAY n_right,eps,z_array) = (S_array,ORDER $(-1))',
        'PhpStep: S_array ~> S_array_raw',
        'S_array_raw.RESULT = KNOWN (PINT $(-1))',
        'S_array_raw.TODO = ptask_array*',
        r'S_array_raw.OBJECTS = S_array.OBJECTS /\ S_array_raw.OBJECTPROPS = S_array.OBJECTPROPS',
        r'S_array_raw.ARRAYS = S_array.ARRAYS /\ S_array_raw.OBJECTTABLES = S_array.OBJECTTABLES',
        'S_array_raw.EVENTS = S_array.EVENTS',
        '$aggregate_compare_seen(S_array_raw) = eps',
        '$drive_steps(S_array,0) = S_array[.COMPLETION = BUDGET]',
        '$drive_steps(S_array,1) = $literal_reference_debt_step(S_array,$sensitive_trace_freeze($source_exception_transition(S_array,$throwable_transition(S_array,S_array_raw))))[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_array_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbs_output(S_done.EVENTS) = $ptascii("B|-1|W|1:-1|A|-1|")',
    ]


def trace_checks(program, encoded_path):
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $tbs_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tbs_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        'S.OBJECTS[n_a] = THROWABLE pthrowable_a',
        'S.OBJECTS[n_b] = THROWABLE pthrowable_b',
        'pthrowable_a.KIND = "TypeError"',
        'pthrowable_b.KIND = "TypeError"',
        '$throwable_object_image_valid(S,n_a)',
        '$throwable_object_image_valid(S,n_b)',
        '$throwable_field(S,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S,n_b,"trace") = PARRAY n_trace_b',
        '$entry_lookup(S.ARRAYS[n_trace_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_a))',
        '$entry_lookup(S.ARRAYS[n_trace_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_b))',
        '$entry_lookup(S.ARRAYS[n_frame_a].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_a))',
        '$entry_lookup(S.ARRAYS[n_frame_b].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_b))',
        '$entry_lookup(S.ARRAYS[n_args_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_payload_a))',
        '$entry_lookup(S.ARRAYS[n_args_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_payload_b))',
        '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KINT 0) = (DIRECT (PINT 1))',
        '$entry_lookup(S.ARRAYS[n_payload_b].ITEMS,KINT 0) = (DIRECT (PINT 2))',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b,HARRAY n_trace_a,HARRAY n_trace_b,HARRAY n_frame_a,HARRAY n_frame_b,HARRAY n_args_a,HARRAY n_args_b,HARRAY n_payload_a,HARRAY n_payload_b],S.ALLOCATIONS)',
        '$trace_array_graph(S,n_trace_a)',
        '$trace_array_graph(S,n_trace_b)',
        '$throwable_field(S,n_a,"previous") = PNULL',
        '$throwable_field(S,n_b,"previous") = PNULL',
        '$throwable_field(S,n_a,"string") = PSTRING eps',
        '$throwable_field(S,n_b,"string") = PSTRING eps',
        '$throwable_builtin_same_pair(S,n_a,n_b,eps)',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDER $(-1))',
        'PhpStep: S ~> S_raw',
        'S_raw.RESULT = KNOWN (PINT $(-1))',
        'S_raw.TODO = ptask*',
        r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
        r'S_raw.ARRAYS = S.ARRAYS /\ S_raw.OBJECTTABLES = S.OBJECTTABLES',
        r'S_raw.STORE = S.STORE /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
        'S_raw.EVENTS = S.EVENTS',
        '$aggregate_compare_seen(S_raw) = eps',
        '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S,1) = $prune_allocations(S_raw)[.COMPLETION = BUDGET]',
    ]
