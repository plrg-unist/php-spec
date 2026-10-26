"""Reached builtin-kind mismatch with severity and cyclic tail skip."""
import base64
import json

PREFIX = r'''
dec $tbk_stage(pstate) : bool
def $tbk_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tbk_stage(S) = false -- otherwise
dec $tbk_seek(pstate, nat) : pstate
def $tbk_seek(S, n) = S -- if $tbk_stage(S) \/ n = 0
def $tbk_seek(S, n) = $tbk_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tbk_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tbk_seek(S, n) = S -- otherwise
dec $tbk_event(pevent) : ptbytes
def $tbk_event(OUTPUT ptbytes) = ptbytes
def $tbk_event(pevent) = eps -- otherwise
dec $tbk_output(pevent*) : ptbytes
def $tbk_output(eps) = eps
def $tbk_output(pevent :: pevent_tail*) = $tbk_event(pevent) ++ $tbk_output(pevent_tail*)
'''


def checks(program, path, name):
    if name == 'severity-warm-previous':
        return severity_checks(program, path)
    assert name == 'cyclic-tail-skip'
    encoded_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tbk_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tbk_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (BINARY_RIGHT SPACESHIP poperand_first z_first) :: ptask_first*',
        '$lookup(S_first.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_first.ENV,$ptascii("b")) = (n_bcv)',
        'S_first.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_first.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        'S_first.OBJECTS[n_a] = THROWABLE pthrowable_a',
        'S_first.OBJECTS[n_b] = THROWABLE pthrowable_b',
        'pthrowable_a.KIND = "ParseError"',
        'pthrowable_b.KIND = "CompileError"',
        '$throwable_object_image_valid(S_first,n_a)',
        '$throwable_object_image_valid(S_first,n_b)',
        '$throwable_builtin_kind_pair(S_first,n_a,n_b,eps)',
        '$throwable_field(S_first,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S_first,n_b,"trace") = PARRAY n_trace_b',
        '$entry_lookup(S_first.ARRAYS[n_trace_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_a))',
        '$entry_lookup(S_first.ARRAYS[n_trace_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_b))',
        '$entry_lookup(S_first.ARRAYS[n_frame_a].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_a))',
        '$entry_lookup(S_first.ARRAYS[n_frame_b].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_b))',
        '$entry_lookup(S_first.ARRAYS[n_args_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_capture_a))',
        '$entry_lookup(S_first.ARRAYS[n_capture_a].ITEMS,KINT 0) = (DIRECT (POBJECT n_cycle_a))',
        '$entry_lookup(S_first.ARRAYS[n_args_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_capture_b))',
        '$entry_lookup(S_first.ARRAYS[n_capture_b].ITEMS,KINT 0) = (DIRECT (POBJECT n_cycle_b))',
        'n_cycle_a =/= n_cycle_b',
        'S_first.OBJECTS[n_cycle_a] = STDINSTANCE',
        'S_first.OBJECTS[n_cycle_b] = STDINSTANCE',
        '$objectprops_record_at(S_first.OBJECTPROPS,n_cycle_a) = (pobjectprops_cycle_a)',
        '$objectprops_record_at(S_first.OBJECTPROPS,n_cycle_b) = (pobjectprops_cycle_b)',
        '$property_slot_at(pobjectprops_cycle_a.SLOTS,$ptascii("self")) = (ppropertyslot_cycle_a)',
        '$property_slot_at(pobjectprops_cycle_b.SLOTS,$ptascii("self")) = (ppropertyslot_cycle_b)',
        'ppropertyslot_cycle_a.STATE = PROP_VALUE (DIRECT (POBJECT n_cycle_a))',
        'ppropertyslot_cycle_b.STATE = PROP_VALUE (DIRECT (POBJECT n_cycle_b))',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b,HOBJECT n_cycle_a,HOBJECT n_cycle_b,HARRAY n_trace_a,HARRAY n_trace_b,HARRAY n_frame_a,HARRAY n_frame_b,HARRAY n_args_a,HARRAY n_args_b,HARRAY n_capture_a,HARRAY n_capture_b],S_first.ALLOCATIONS)',
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
        'S_reverse_found = $tbk_seek(S_first_raw,1000)',
        '$tbk_stage(S_reverse_found)',
        'S_reverse = S_reverse_found[.COMPLETION = NORMAL]',
        'S_reverse.TODO = (BINARY_RIGHT SPACESHIP poperand_reverse z_reverse) :: ptask_reverse*',
        '$throwable_builtin_kind_pair(S_reverse,n_b,n_a,eps)',
        '$value_order_effect(S_reverse,POBJECT n_b,POBJECT n_a,eps,z_reverse) = (S_reverse,ORDER 1)',
        'PhpStep: S_reverse ~> S_reverse_raw',
        'S_reverse_raw.RESULT = KNOWN (PINT 1)',
        'S_reverse_raw.TODO = ptask_reverse*',
        '$aggregate_compare_seen(S_reverse_raw) = eps',
        'S_second_found = $tbk_seek(S_reverse_raw,1000)',
        '$tbk_stage(S_second_found)',
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
        '$throwable_builtin_kind_pair(S_second,n_a,n_b,[HARRAY n_array_left])',
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
        '$drive_steps(S_second,1) = $literal_reference_debt_step(S_second,$sensitive_trace_freeze($source_exception_transition(S_second,$throwable_transition(S_second,S_second_raw))))[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_second_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbk_output(S_done.EVENTS) = $ptascii("B|1:1|A|1|")',
    ]


def severity_checks(program, path):
    encoded_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $tbk_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tbk_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        'S.OBJECTS[n_a] = THROWABLE pthrowable_a',
        'S.OBJECTS[n_b] = THROWABLE pthrowable_b',
        'pthrowable_a.KIND = "ErrorException"',
        'pthrowable_b.KIND = "RuntimeException"',
        '$throwable_object_image_valid(S,n_a)',
        '$throwable_object_image_valid(S,n_b)',
        '$objectprops_record_at(S.OBJECTPROPS,n_a) = (pobjectprops_a)',
        '$property_slot_at(pobjectprops_a.SLOTS,$throwable_key("ErrorException","severity")) = (ppropertyslot_severity)',
        'ppropertyslot_severity.STATE = PROP_VALUE (DIRECT (PINT 8))',
        '$throwable_field(S,n_a,"file") = PSTRING $ptascii("custom.php")',
        '$throwable_field(S,n_a,"line") = PINT $(-2)',
        '$throwable_field(S,n_a,"previous") = POBJECT n_previous',
        '$throwable_object_image_valid(S,n_previous)',
        '$throwable_builtin_kind_pair(S,n_a,n_b,eps)',
        '~$throwable_cross_kind_pair(S,n_a,n_b,eps)',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDER 1)',
        'PhpStep: S ~> S_raw',
        'S_raw.RESULT = KNOWN (PINT 1)',
        'S_raw.TODO = ptask*',
        r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
        r'S_raw.OBJECTTABLES = S.OBJECTTABLES /\ S_raw.ARRAYS = S.ARRAYS',
        r'S_raw.STORE = S.STORE /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
        'S_raw.EVENTS = S.EVENTS',
        '$aggregate_compare_seen(S_raw) = eps',
        '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S,1) = $prune_allocations(S_raw)[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbk_output(S_done.EVENTS) = $ptascii("B|1:1:8|W|1:1|")',
    ]
