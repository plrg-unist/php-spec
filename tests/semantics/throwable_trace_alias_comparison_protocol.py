"""Reached live reference cells inside captured Throwable trace arrays."""
import base64
import json

PREFIX = r'''
dec $tal_stage(pstate) : bool
def $tal_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tal_stage(S) = false -- otherwise
dec $tal_seek(pstate, nat) : pstate
def $tal_seek(S, n) = S -- if $tal_stage(S) \/ n = 0
def $tal_seek(S, n) = $tal_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tal_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tal_seek(S, n) = S -- otherwise
dec $tal_event(pevent) : ptbytes
def $tal_event(OUTPUT ptbytes) = ptbytes
def $tal_event(pevent) = eps -- otherwise
dec $tal_output(pevent*) : ptbytes
def $tal_output(eps) = eps
def $tal_output(pevent :: pevent_tail*) = $tal_event(pevent) ++ $tal_output(pevent_tail*)
'''


def trace_entries(state, name, suffix):
    return [
        f'$throwable_field({state},n_{name},"trace") = PARRAY n_trace_{suffix}',
        f'$entry_lookup({state}.ARRAYS[n_trace_{suffix}].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_{suffix}))',
        f'$entry_lookup({state}.ARRAYS[n_frame_{suffix}].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_{suffix}))',
        f'$entry_lookup({state}.ARRAYS[n_args_{suffix}].ITEMS,KINT 0) = (DIRECT (PARRAY n_saved_{suffix}))',
        f'$trace_alias_graph({state},n_trace_{suffix})',
    ]


def checks(program, path, name):
    source_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    common = [
        'S_initial = $php_run(' + program + ',0,' + source_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tal_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tal_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (BINARY_RIGHT SPACESHIP poperand_first z_first) :: ptask_first*',
        '$lookup(S_first.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_first.ENV,$ptascii("b")) = (n_bcv)',
        'S_first.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_first.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        'n_a =/= n_b',
        *trace_entries('S_first', 'a', 'a'),
        *trace_entries('S_first', 'b', 'b'),
        '$throwable_alias_trace_pair(S_first,n_a,n_b)',
    ]
    if name == 'alias-and-cow-sibling':
        return common + [
            '$lookup(S_first.ENV,$ptascii("v")) = (n_v)',
            'n_v <- S_first.REFCELLS',
            '(HCELL n_v) <- S_first.ALLOCATIONS',
            'S_first.STORE[n_v] = DEFINED (PINT 1)',
            '$entry_lookup(S_first.ARRAYS[n_saved_a].ITEMS,KINT 0) = (ALIAS n_v)',
            '$entry_lookup(S_first.ARRAYS[n_saved_a].ITEMS,KINT 1) = (DIRECT (PINT 1))',
            '$entry_lookup(S_first.ARRAYS[n_saved_b].ITEMS,KINT 0) = (DIRECT (PINT 2))',
            '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER $(-1))',
            'PhpStep: S_first ~> S_first_raw',
            'S_first_raw.RESULT = KNOWN (PINT $(-1))',
            'S_first_raw.TODO = ptask_first*',
            r'S_first_raw.STORE = S_first.STORE /\ S_first_raw.ARRAYS = S_first.ARRAYS',
            '$aggregate_compare_seen(S_first_raw) = eps',
            '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
            '$drive_steps(S_first,1) = S_first_raw[.COMPLETION = BUDGET]',
            'S_second_found = $tal_seek(S_first_raw,1000)',
            '$tal_stage(S_second_found)',
            'S = S_second_found[.COMPLETION = NORMAL]',
            'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
            '$lookup(S.ENV,$ptascii("a")) = (n_acv_second)',
            '$lookup(S.ENV,$ptascii("b")) = (n_bcv_second)',
            'S.STORE[n_acv_second] = DEFINED (POBJECT n_a)',
            'S.STORE[n_bcv_second] = DEFINED (POBJECT n_b)',
            '$lookup(S.ENV,$ptascii("source")) = (n_sourcecv)',
            'S.STORE[n_sourcecv] = DEFINED (PARRAY n_source)',
            'n_source =/= n_saved_a',
            'S.STORE[n_v] = DEFINED (PINT 2)',
            '$entry_lookup(S.ARRAYS[n_saved_a].ITEMS,KINT 0) = (ALIAS n_v)',
            '$entry_lookup(S.ARRAYS[n_saved_a].ITEMS,KINT 1) = (DIRECT (PINT 1))',
            '$entry_lookup(S.ARRAYS[n_source].ITEMS,KINT 0) = (ALIAS n_v)',
            '$entry_lookup(S.ARRAYS[n_source].ITEMS,KINT 1) = (DIRECT (PINT 9))',
            '$entry_lookup(S.ARRAYS[n_saved_b].ITEMS,KINT 0) = (DIRECT (PINT 2))',
            '$trace_alias_present(S,n_trace_a)',
            '$throwable_alias_trace_pair(S,n_a,n_b)',
            '$heap_count(HARRAY n_saved_a,$pools_nodes(S.POOLS)) = 0',
            '$heap_count(HARRAY n_source,$pools_nodes(S.POOLS)) = 0',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_saved_a) = 1',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_v) = 3',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDER 0)',
            'PhpStep: S ~> S_raw',
            'S_raw.RESULT = KNOWN (PINT 0)',
            'S_raw.TODO = ptask*',
            r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
            r'S_raw.STORE = S.STORE /\ S_raw.ARRAYS = S.ARRAYS',
            'S_raw.ALLOCATIONS = S.ALLOCATIONS',
            '$aggregate_compare_seen(S_raw) = eps',
            '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
            '$drive_steps(S,1) = S_raw[.COMPLETION = BUDGET]',
            'S_done = $drive_steps(S_raw,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tal_output(S_done.EVENTS) = $ptascii("B|-1|M|2:9:0|R|1:-1|")',
        ]
    assert name == 'shared-child-cell'
    return common + [
        'n_saved_a =/= n_saved_b',
        '$lookup(S_first.ENV,$ptascii("child")) = (n_childcv)',
        'S_first.STORE[n_childcv] = DEFINED (PARRAY n_child)',
        'S_first.ARRAYS[n_saved_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        'S_first.ARRAYS[n_saved_b].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        '$lookup(S_first.ENV,$ptascii("v")) = (n_v)',
        'S_first.STORE[n_v] = DEFINED (PINT 3)',
        'n_v <- S_first.REFCELLS',
        'S_first.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (ALIAS n_v)]',
        '$trace_alias_present(S_first,n_trace_a)',
        '$trace_alias_present(S_first,n_trace_b)',
        '$heap_count(HARRAY n_child,$pools_nodes(S_first.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_child) = 5',
        '$heap_owners($heap_prune($heap_graph(S_first)),HCELL n_v) = 2',
        '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER 0)',
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT 0)',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.STORE = S_first.STORE /\ S_first_raw.ARRAYS = S_first.ARRAYS',
        'S_first_raw.ALLOCATIONS = S_first.ALLOCATIONS',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = S_first_raw[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_first_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tal_output(S_done.EVENTS) = $ptascii("B|0|")',
    ]
