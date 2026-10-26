"""Reached cache-first and captured-array trace comparisons."""
import base64
import json

PREFIX = r'''
dec $twt_stage(pstate) : bool
def $twt_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $twt_stage(S) = false -- otherwise
dec $twt_seek(pstate, nat) : pstate
def $twt_seek(S, n) = S -- if $twt_stage(S) \/ n = 0
def $twt_seek(S, n) = $twt_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$twt_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $twt_seek(S, n) = S -- otherwise
dec $twt_event(pevent) : ptbytes
def $twt_event(OUTPUT ptbytes) = ptbytes
def $twt_event(pevent) = eps -- otherwise
dec $twt_output(pevent*) : ptbytes
def $twt_output(eps) = eps
def $twt_output(pevent :: pevent_tail*) = $twt_event(pevent) ++ $twt_output(pevent_tail*)
'''


def checks(program, path, name):
    source_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    common = [
        'S_initial = $php_run(' + program + ',0,' + source_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $twt_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$twt_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$throwable_field(S,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S,n_b,"trace") = PARRAY n_trace_b',
        r'$trace_array_graph(S,n_trace_a) /\ $trace_array_graph(S,n_trace_b)',
        '$entry_lookup(S.ARRAYS[n_trace_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_a))',
        '$entry_lookup(S.ARRAYS[n_trace_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_b))',
        '$entry_lookup(S.ARRAYS[n_frame_a].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_a))',
        '$entry_lookup(S.ARRAYS[n_frame_b].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_b))',
    ]
    if name == 'scalar-cache-order':
        return common + [
            '$entry_lookup(S.ARRAYS[n_args_a].ITEMS,KINT 0) = (DIRECT (PINT 9))',
            '$entry_lookup(S.ARRAYS[n_args_b].ITEMS,KINT 0) = (DIRECT (PINT 10))',
            '$throwable_scalar_trace_pair(S,n_a,n_b)',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDER $(-1))',
            'PhpStep: S ~> S_cold_raw',
            'S_cold_raw.RESULT = KNOWN (PINT $(-1))',
            'S_warm_found = $twt_seek(S_cold_raw,1000)',
            '$twt_stage(S_warm_found)',
            'S_warm = S_warm_found[.COMPLETION = NORMAL]',
            'S_warm.TODO = (BINARY_RIGHT SPACESHIP poperand_warm z_warm) :: ptask_warm*',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_a',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_b',
            'preqbytes_a = $throwable_chain_string(S_warm,n_a,[n_a])',
            'preqbytes_b = $throwable_chain_string(S_warm,n_b,[n_b])',
            'preqbytes_a =/= eps',
            'preqbytes_b =/= eps',
            '$trace_array_graph(S_warm,n_trace_a)',
            '$trace_array_graph(S_warm,n_trace_b)',
            '$value_order_effect(S_warm,PARRAY n_trace_a,PARRAY n_trace_b,[HOBJECT n_a],z_warm) = (S_warm,ORDER $(-1))',
            '$throwable_warm_trace_pair(S_warm,n_a,n_b)',
            '$value_order_effect(S_warm,POBJECT n_a,POBJECT n_b,eps,z_warm) = (S_warm,ORDER 1)',
            'PhpStep: S_warm ~> S_raw',
            'S_raw.RESULT = KNOWN (PINT 1)',
            'S_raw.TODO = ptask_warm*',
            r'S_raw.OBJECTS = S_warm.OBJECTS /\ S_raw.OBJECTPROPS = S_warm.OBJECTPROPS',
            r'S_raw.ARRAYS = S_warm.ARRAYS /\ S_raw.ALLOCATIONS = S_warm.ALLOCATIONS',
            '$aggregate_compare_seen(S_raw) = eps',
            '$drive_steps(S_warm,0) = S_warm[.COMPLETION = BUDGET]',
            '$drive_steps(S_warm,1) = S_raw[.COMPLETION = BUDGET]',
            'S_done = $drive_steps(S_raw,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$twt_output(S_done.EVENTS) = $ptascii("B|-1:1:-1|")',
        ]
    assert name == 'array-cache-cow-tail'
    return common + [
        '$lookup(S.ENV,$ptascii("c")) = (n_ccv)',
        'S.STORE[n_ccv] = DEFINED (POBJECT n_c)',
        '$lookup(S.ENV,$ptascii("source")) = (n_sourcecv)',
        'S.STORE[n_sourcecv] = DEFINED (PARRAY n_source)',
        '$throwable_field(S,n_c,"trace") = PARRAY n_trace_c',
        '$trace_array_graph(S,n_trace_c)',
        '$entry_lookup(S.ARRAYS[n_trace_c].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_c))',
        '$entry_lookup(S.ARRAYS[n_frame_c].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_c))',
        '$entry_lookup(S.ARRAYS[n_args_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_saved_a))',
        '$entry_lookup(S.ARRAYS[n_args_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_saved_b))',
        '$entry_lookup(S.ARRAYS[n_args_c].ITEMS,KINT 0) = (DIRECT (PARRAY n_saved_c))',
        '$entry_lookup(S.ARRAYS[n_saved_a].ITEMS,KINT 1) = (DIRECT (PARRAY n_saved_child))',
        '$entry_lookup(S.ARRAYS[n_saved_b].ITEMS,KINT 1) = (DIRECT (PARRAY n_equal_child))',
        '$entry_lookup(S.ARRAYS[n_saved_c].ITEMS,KINT 1) = (DIRECT (PARRAY n_diff_child))',
        '$entry_lookup(S.ARRAYS[n_source].ITEMS,KINT 1) = (DIRECT (PARRAY n_source_child))',
        'n_source =/= n_saved_a',
        'n_source_child =/= n_saved_child',
        '$entry_lookup(S.ARRAYS[n_source_child].ITEMS,KSTRING $ptascii("k")) = (DIRECT (PINT 9))',
        '$entry_lookup(S.ARRAYS[n_saved_child].ITEMS,KSTRING $ptascii("k")) = (DIRECT (PINT 2))',
        '$entry_lookup(S.ARRAYS[n_equal_child].ITEMS,KSTRING $ptascii("k")) = (DIRECT (PINT 2))',
        '$entry_lookup(S.ARRAYS[n_diff_child].ITEMS,KSTRING $ptascii("k")) = (DIRECT (PINT 3))',
        '$heap_count(HARRAY n_saved_a,$pools_nodes(S.POOLS)) = 1',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_saved_a) = 2',
        '$heap_count(HARRAY n_source,$pools_nodes(S.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_source) = 1',
        '$throwable_field(S,n_a,"string") = PSTRING preqbytes_a',
        'preqbytes_a = $throwable_chain_string(S,n_a,[n_a])',
        'preqbytes_a =/= eps',
        '$throwable_field(S,n_c,"string") = PSTRING eps',
        '$throwable_warm_trace_pair(S,n_a,n_c)',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_c,eps,z) = (S,ORDER 1)',
        'PhpStep: S ~> S_one_raw',
        'S_one_raw.RESULT = KNOWN (PINT 1)',
        r'S_one_raw.OBJECTS = S.OBJECTS /\ S_one_raw.OBJECTPROPS = S.OBJECTPROPS',
        r'S_one_raw.ARRAYS = S.ARRAYS /\ S_one_raw.ALLOCATIONS = S.ALLOCATIONS',
        '$aggregate_compare_seen(S_one_raw) = eps',
        'S_equal_found = $twt_seek(S_one_raw,1000)',
        '$twt_stage(S_equal_found)',
        'S_equal = S_equal_found[.COMPLETION = NORMAL]',
        'S_equal.TODO = (BINARY_RIGHT SPACESHIP poperand_equal z_equal) :: ptask_equal*',
        '$throwable_field(S_equal,n_a,"string") = PSTRING preqbytes_equal',
        '$throwable_field(S_equal,n_b,"string") = PSTRING preqbytes_equal',
        '$throwable_field(S_equal,n_c,"string") = PSTRING preqbytes_equal',
        'preqbytes_equal =/= eps',
        '$throwable_warm_trace_pair(S_equal,n_a,n_b)',
        '$value_order_effect(S_equal,POBJECT n_a,POBJECT n_b,eps,z_equal) = (S_equal,ORDER 0)',
        'PhpStep: S_equal ~> S_equal_raw',
        'S_equal_raw.RESULT = KNOWN (PINT 0)',
        r'S_equal_raw.OBJECTS = S_equal.OBJECTS /\ S_equal_raw.OBJECTPROPS = S_equal.OBJECTPROPS',
        r'S_equal_raw.ARRAYS = S_equal.ARRAYS /\ S_equal_raw.ALLOCATIONS = S_equal.ALLOCATIONS',
        '$aggregate_compare_seen(S_equal_raw) = eps',
        'S_diff_found = $twt_seek(S_equal_raw,1000)',
        '$twt_stage(S_diff_found)',
        'S_diff = S_diff_found[.COMPLETION = NORMAL]',
        'S_diff.TODO = (BINARY_RIGHT SPACESHIP poperand_diff z_diff) :: ptask_diff*',
        '$throwable_warm_trace_pair(S_diff,n_a,n_c)',
        '$value_order_effect(S_diff,POBJECT n_a,POBJECT n_c,eps,z_diff) = (S_diff,ORDER $(-1))',
        'PhpStep: S_diff ~> S_diff_raw',
        'S_diff_raw.RESULT = KNOWN (PINT $(-1))',
        'S_diff_raw.TODO = ptask_diff*',
        r'S_diff_raw.OBJECTS = S_diff.OBJECTS /\ S_diff_raw.OBJECTPROPS = S_diff.OBJECTPROPS',
        r'S_diff_raw.ARRAYS = S_diff.ARRAYS /\ S_diff_raw.ALLOCATIONS = S_diff.ALLOCATIONS',
        '$aggregate_compare_seen(S_diff_raw) = eps',
        '$drive_steps(S_diff,0) = S_diff[.COMPLETION = BUDGET]',
        '$drive_steps(S_diff,1) = S_diff_raw[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_diff_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$twt_output(S_done.EVENTS) = $ptascii("W|1|C|9:0:-1:1|E:CAST|0|N:-1|")',
    ]
