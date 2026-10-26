"""Source-reached warmed Throwable slot and aggregate comparison steps."""
import base64
import json

PREFIX = r'''
dec $twc_stage(pstate) : bool
def $twc_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $twc_stage(S) = false -- otherwise
dec $twc_seek(pstate, nat) : pstate
def $twc_seek(S, n) = S -- if $twc_stage(S) \/ n = 0
def $twc_seek(S, n) = $twc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$twc_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $twc_seek(S, n) = S -- otherwise
dec $twc_event(pevent) : ptbytes
def $twc_event(OUTPUT ptbytes) = ptbytes
def $twc_event(pevent) = eps -- otherwise
dec $twc_output(pevent*) : ptbytes
def $twc_output(eps) = eps
def $twc_output(pevent :: pevent_tail*) = $twc_event(pevent) ++ $twc_output(pevent_tail*)
'''


def checks(program, path, name):
    source_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    common = [
        'S_initial = $php_run(' + program + ',0,' + source_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $twc_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$twc_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$throwable_field(S,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S,n_b,"trace") = PARRAY n_trace_b',
        'S.ARRAYS[n_trace_a].ITEMS = eps',
        'S.ARRAYS[n_trace_b].ITEMS = eps',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_trace_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_trace_b) = 1',
        '$throwable_field(S,n_a,"previous") = PNULL',
        '$throwable_field(S,n_b,"previous") = PNULL',
    ]
    if name == 'cache-before-line':
        # The first stage is cold; the second has both caches warm.
        return common + [
            '$throwable_cold_pair(S,n_a,n_b)',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDER $(-1))',
            'PhpStep: S ~> S_cold_raw',
            'S_cold_raw.RESULT = KNOWN (PINT $(-1))',
            'S_warm_found = $twc_seek(S_cold_raw,1000)',
            '$twc_stage(S_warm_found)',
            'S_warm = S_warm_found[.COMPLETION = NORMAL]',
            'S_warm.TODO = (BINARY_RIGHT SPACESHIP poperand_warm z_warm) :: ptask_warm*',
            '$throwable_field(S_warm,n_a,"line") = PINT 9',
            '$throwable_field(S_warm,n_b,"line") = PINT 10',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_a',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_b',
            'preqbytes_a = $throwable_chain_string(S_warm,n_a,[n_a])',
            'preqbytes_b = $throwable_chain_string(S_warm,n_b,[n_b])',
            'preqbytes_a =/= eps',
            'preqbytes_b =/= eps',
            '$throwable_warm_pair(S_warm,n_a,n_b)',
            '$value_order_effect(S_warm,POBJECT n_a,POBJECT n_b,eps,z_warm) = (S_warm,ORDER 1)',
            'PhpStep: S_warm ~> S_raw',
            'S_raw.RESULT = KNOWN (PINT 1)',
            'S_raw.TODO = ptask_warm*',
            r'S_raw.OBJECTS = S_warm.OBJECTS /\ S_raw.OBJECTPROPS = S_warm.OBJECTPROPS',
            r'S_raw.ARRAYS = S_warm.ARRAYS /\ S_raw.ALLOCATIONS = S_warm.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_raw)),HARRAY n_trace_a) = 1',
            '$heap_owners($heap_prune($heap_graph(S_raw)),HARRAY n_trace_b) = 1',
            '$aggregate_compare_seen(S_raw) = eps',
            '$drive_steps(S_warm,0) = S_warm[.COMPLETION = BUDGET]',
            '$drive_steps(S_warm,1) = S_raw[.COMPLETION = BUDGET]',
            'S_done = $drive_steps(S_raw,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$twc_output(S_done.EVENTS) = $ptascii("B|-1:1:-1|")',
        ]
    assert name == 'error-warm-tail'
    return common + [
        '$throwable_field(S,n_a,"string") = PSTRING preqbytes_a',
        'preqbytes_a = $throwable_chain_string(S,n_a,[n_a])',
        'preqbytes_a =/= eps',
        '$throwable_field(S,n_b,"string") = PSTRING eps',
        '$throwable_warm_pair(S,n_a,n_b)',
        '$lookup(S.ENV,$ptascii("later")) = (n_latercv)',
        'S.STORE[n_latercv] = DEFINED (POBJECT n_later)',
        '$lookup(S.ENV,$ptascii("x")) = eps',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDER 1)',
        'PhpStep: S ~> S_raw',
        'S_raw.RESULT = KNOWN (PINT 1)',
        'S_raw.TODO = ptask*',
        r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
        r'S_raw.ARRAYS = S.ARRAYS /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
        '$aggregate_compare_seen(S_raw) = eps',
        '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S,1) = S_raw[.COMPLETION = BUDGET]',
        'S_equal_found = $twc_seek(S_raw,1000)',
        '$twc_stage(S_equal_found)',
        'S_equal = S_equal_found[.COMPLETION = NORMAL]',
        'S_equal.TODO = (BINARY_RIGHT SPACESHIP poperand_equal z_equal) :: ptask_equal*',
        '$throwable_field(S_equal,n_a,"string") = PSTRING preqbytes_equal',
        '$throwable_field(S_equal,n_b,"string") = PSTRING preqbytes_equal',
        '$throwable_warm_pair(S_equal,n_a,n_b)',
        '$value_order_effect(S_equal,POBJECT n_a,POBJECT n_b,eps,z_equal) = (S_equal,ORDER 0)',
        'PhpStep: S_equal ~> S_equal_raw',
        'S_equal_raw.RESULT = KNOWN (PINT 0)',
        'S_equal_raw.TODO = ptask_equal*',
        r'S_equal_raw.OBJECTS = S_equal.OBJECTS /\ S_equal_raw.OBJECTPROPS = S_equal.OBJECTPROPS',
        r'S_equal_raw.ARRAYS = S_equal.ARRAYS /\ S_equal_raw.ALLOCATIONS = S_equal.ALLOCATIONS',
        '$aggregate_compare_seen(S_equal_raw) = eps',
        '$drive_steps(S_equal,0) = S_equal[.COMPLETION = BUDGET]',
        '$drive_steps(S_equal,1) = S_equal_raw[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_equal_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$twc_output(S_done.EVENTS) = $ptascii("N:1|E:0:0|T:CAST|0|")',
    ]
