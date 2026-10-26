"""Reached captured-array COW and shared-DAG Throwable comparison steps."""
import base64
import json

PREFIX = r'''
dec $tac_stage(pstate) : bool
def $tac_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tac_stage(S) = false -- otherwise
dec $tac_seek(pstate, nat) : pstate
def $tac_seek(S, n) = S -- if $tac_stage(S) \/ n = 0
def $tac_seek(S, n) = $tac_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tac_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tac_seek(S, n) = S -- otherwise
dec $tac_event(pevent) : ptbytes
def $tac_event(OUTPUT ptbytes) = ptbytes
def $tac_event(pevent) = eps -- otherwise
dec $tac_output(pevent*) : ptbytes
def $tac_output(eps) = eps
def $tac_output(pevent :: pevent_tail*) = $tac_event(pevent) ++ $tac_output(pevent_tail*)
'''


def checks(program, path, name):
    source_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    common = [
        'S_initial = $php_run(' + program + ',0,' + source_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $tac_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tac_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$throwable_array_trace_pair(S,n_a,n_b)',
        '$throwable_field(S,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S,n_b,"trace") = PARRAY n_trace_b',
        '$entry_lookup(S.ARRAYS[n_trace_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_a))',
        '$entry_lookup(S.ARRAYS[n_trace_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_b))',
        '$entry_lookup(S.ARRAYS[n_frame_a].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_a))',
        '$entry_lookup(S.ARRAYS[n_frame_b].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_b))',
        '$entry_lookup(S.ARRAYS[n_args_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_saved_a))',
        '$entry_lookup(S.ARRAYS[n_args_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_saved_b))',
        r'$trace_array_graph(S,n_trace_a) /\ $trace_array_graph(S,n_trace_b)',
        r'$trace_array_arg_present(S,n_trace_a) /\ $trace_array_arg_present(S,n_trace_b)',
    ]
    if name == 'cow-and-tail':
        extra = [
            '$lookup(S.ENV,$ptascii("input")) = (n_inputcv)',
            'S.STORE[n_inputcv] = DEFINED (PARRAY n_input)',
            'n_input =/= n_saved_a',
            '$entry_lookup(S.ARRAYS[n_input].ITEMS,KINT 1) = (DIRECT (PARRAY n_input_child))',
            '$entry_lookup(S.ARRAYS[n_saved_a].ITEMS,KINT 1) = (DIRECT (PARRAY n_saved_child))',
            'n_input_child =/= n_saved_child',
            '$entry_lookup(S.ARRAYS[n_input_child].ITEMS,KSTRING $ptascii("k")) = (DIRECT (PINT 9))',
            '$entry_lookup(S.ARRAYS[n_saved_child].ITEMS,KSTRING $ptascii("k")) = (DIRECT (PINT 2))',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_saved_a) = 1',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_saved_child) = 1',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_input) = 1',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_input_child) = 1',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDER 0)',
            'PhpStep: S ~> S_raw',
            'S_raw.RESULT = KNOWN (PINT 0)',
            'S_raw.TODO = ptask*',
            r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
            r'S_raw.ARRAYS = S.ARRAYS /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
            '$aggregate_compare_seen(S_raw) = eps',
            '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
            '$drive_steps(S,1) = S_raw[.COMPLETION = BUDGET]',
            'S_done = $drive_steps(S_raw,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tac_output(S_done.EVENTS) = $ptascii("B|9:0|E:CAST|0|N:-1|")',
        ]
    else:
        assert name == 'shared-dag'
        extra = [
            'n_saved_a =/= n_saved_b',
            'S.ARRAYS[n_saved_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
            'S.ARRAYS[n_saved_b].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
            'S.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_child) = 5',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDER 0)',
            'PhpStep: S ~> S_raw',
            'S_raw.RESULT = KNOWN (PINT 0)',
            'S_raw.TODO = ptask*',
            r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
            r'S_raw.ARRAYS = S.ARRAYS /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
            '$aggregate_compare_seen(S_raw) = eps',
            '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
            '$drive_steps(S,1) = S_raw[.COMPLETION = BUDGET]',
            'S_done = $drive_steps(S_raw,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tac_output(S_done.EVENTS) = $ptascii("B|0|")',
        ]
    return common + extra
