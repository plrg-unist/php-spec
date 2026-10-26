"""Reached scalar-trace Throwable pair and equal-prefix array comparison steps."""
import base64
import json

PREFIX = r'''
dec $ttc_stage(pstate) : bool
def $ttc_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $ttc_stage(S) = false -- otherwise
dec $ttc_seek(pstate, nat) : pstate
def $ttc_seek(S, n) = S -- if $ttc_stage(S) \/ n = 0
def $ttc_seek(S, n) = $ttc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$ttc_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ttc_seek(S, n) = S -- otherwise
dec $ttc_event(pevent) : ptbytes
def $ttc_event(OUTPUT ptbytes) = ptbytes
def $ttc_event(pevent) = eps -- otherwise
dec $ttc_output(pevent*) : ptbytes
def $ttc_output(eps) = eps
def $ttc_output(pevent :: pevent_tail*) = $ttc_event(pevent) ++ $ttc_output(pevent_tail*)
'''


def checks(program, path, name):
    source_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    if name == 'state-string-carrier':
        return [
            'S_initial = $php_run(' + program + ',0,' + source_path + ')',
            'S_initial.COMPLETION = BUDGET',
            'S_found = $ttc_seek(S_initial[.COMPLETION = NORMAL],1000)',
            '$ttc_stage(S_found)',
            'S = S_found[.COMPLETION = NORMAL]',
            'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
            '$lookup(S.ENV,$ptascii("d")) = (n_dcv)',
            '$lookup(S.ENV,$ptascii("e")) = (n_ecv)',
            'S.STORE[n_dcv] = DEFINED (POBJECT n_d)',
            'S.STORE[n_ecv] = DEFINED (POBJECT n_e)',
            '$throwable_scalar_trace_pair(S,n_d,n_e)',
            '$throwable_field(S,n_e,"trace") = PARRAY n_trace',
            '$entry_lookup(S.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
            '$entry_lookup(S.ARRAYS[n_frame].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args))',
            '$entry_lookup(S.ARRAYS[n_args].ITEMS,KINT 0) = (DIRECT (PSTRING_CARRIER pstringidentity_e ($ptascii("x"))))',
            '$string_carrier_valid(S,PSTRING_CARRIER pstringidentity_e ($ptascii("x")))',
            '$trace_compare_graph(S,n_trace)',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_trace) = 1',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_frame) = 1',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_args) = 1',
            '$value_order_effect(S,POBJECT n_d,POBJECT n_e,eps,z) = (S,ORDER $(-1))',
            'PhpStep: S ~> S_raw',
            'S_raw.RESULT = KNOWN (PINT $(-1))',
            'S_raw.TODO = ptask*',
            r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
            r'S_raw.ARRAYS = S.ARRAYS /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
            '$aggregate_compare_seen(S_raw) = eps',
            '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
            '$drive_steps(S,1) = S_raw[.COMPLETION = BUDGET]',
            'S_done = $drive_steps(S_raw,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$ttc_output(S_done.EVENTS) = $ptascii("B|-1|")',
        ]
    assert name == 'state-direct-array'
    return [
        'S_initial = $php_run(' + program + ',0,' + source_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $ttc_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$ttc_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (BINARY_RIGHT SPACESHIP poperand_first z_first) :: ptask_first*',
        '$lookup(S_first.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_first.ENV,$ptascii("b")) = (n_bcv)',
        'S_first.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_first.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$throwable_scalar_trace_pair(S_first,n_a,n_b)',
        '$throwable_field(S_first,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S_first,n_b,"trace") = PARRAY n_trace_b',
        'S_first.ARRAYS[n_trace_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_a))]',
        'S_first.ARRAYS[n_trace_b].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_b))]',
        'S_first.ARRAYS[n_frame_a].ITEMS = [ENTRY (KSTRING $ptascii("file")) (DIRECT (PSTRING preqbytes_file_a)),ENTRY (KSTRING $ptascii("line")) (DIRECT (PINT 3)),ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING $ptascii("trace130"))),ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_args_a))]',
        'S_first.ARRAYS[n_frame_b].ITEMS = [ENTRY (KSTRING $ptascii("file")) (DIRECT (PSTRING preqbytes_file_b)),ENTRY (KSTRING $ptascii("line")) (DIRECT (PINT 3)),ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING $ptascii("trace130"))),ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_args_b))]',
        'S_first.ARRAYS[n_args_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_first.ARRAYS[n_args_b].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        r'$trace_compare_graph(S_first,n_trace_a) /\ $trace_compare_graph(S_first,n_trace_b)',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_trace_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_trace_b) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_frame_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_frame_b) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_args_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_args_b) = 1',
        '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER 0)',
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT 0)',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.OBJECTS = S_first.OBJECTS /\ S_first_raw.OBJECTPROPS = S_first.OBJECTPROPS',
        r'S_first_raw.ARRAYS = S_first.ARRAYS /\ S_first_raw.ALLOCATIONS = S_first.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_first_raw)),HARRAY n_trace_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_raw)),HARRAY n_trace_b) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_raw)),HARRAY n_frame_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_raw)),HARRAY n_frame_b) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_raw)),HARRAY n_args_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_raw)),HARRAY n_args_b) = 1',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = S_first_raw[.COMPLETION = BUDGET]',
        'S_second_found = $ttc_seek(S_first_raw,1000)',
        '$ttc_stage(S_second_found)',
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
        '$ttc_output(S_done.EVENTS) = $ptascii("B|0|-1|")',
    ]
