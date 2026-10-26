"""Source-reached live property cells and comparison continuation."""
import base64
import json

PREFIX = r'''
dec $tpa_stage(pstate) : bool
def $tpa_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tpa_stage(S) = false -- otherwise
dec $tpa_seek(pstate, nat) : pstate
def $tpa_seek(S, n) = S -- if $tpa_stage(S) \/ n = 0
def $tpa_seek(S, n) = $tpa_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tpa_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tpa_seek(S, n) = S -- otherwise
dec $tpa_event(pevent) : ptbytes
def $tpa_event(OUTPUT ptbytes) = ptbytes
def $tpa_event(pevent) = eps -- otherwise
dec $tpa_output(pevent*) : ptbytes
def $tpa_output(eps) = eps
def $tpa_output(pevent :: pevent_tail*) = $tpa_event(pevent) ++ $tpa_output(pevent_tail*)
'''


def front(state, label):
    return [
        f'{state}.TODO = (BINARY_RIGHT SPACESHIP poperand_{label} z_{label}) :: ptask_{label}*',
        f'$lookup({state}.ENV,$ptascii("a")) = (n_acv_{label})',
        f'$lookup({state}.ENV,$ptascii("b")) = (n_bcv_{label})',
        f'{state}.STORE[n_acv_{label}] = DEFINED (POBJECT n_a)',
        f'{state}.STORE[n_bcv_{label}] = DEFINED (POBJECT n_b)',
        'n_a =/= n_b',
        f'$throwable_field({state},n_a,"trace") = PARRAY n_trace_a',
        f'$throwable_field({state},n_b,"trace") = PARRAY n_trace_b',
        f'$entry_lookup({state}.ARRAYS[n_trace_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_a))',
        f'$entry_lookup({state}.ARRAYS[n_trace_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_b))',
        f'$entry_lookup({state}.ARRAYS[n_frame_a].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_a))',
        f'$entry_lookup({state}.ARRAYS[n_frame_b].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_b))',
        f'$entry_lookup({state}.ARRAYS[n_args_a].ITEMS,KINT 0) = (DIRECT (POBJECT n_left))',
        f'$entry_lookup({state}.ARRAYS[n_args_b].ITEMS,KINT 0) = (DIRECT (POBJECT n_right))',
        'n_left =/= n_right',
        f'{state}.OBJECTS[n_left] = STDINSTANCE',
        f'{state}.OBJECTS[n_right] = STDINSTANCE',
        f'$heap_subset([HARRAY n_trace_a,HARRAY n_frame_a,HARRAY n_args_a,HARRAY n_trace_b,HARRAY n_frame_b,HARRAY n_args_b,HOBJECT n_left,HOBJECT n_right],{state}.ALLOCATIONS)',
        f'$trace_property_ref_graph({state},n_trace_a)',
        f'$trace_property_ref_graph({state},n_trace_b)',
        f'$trace_object_graph_pair({state},n_trace_a,n_trace_b)',
        f'$throwable_property_ref_pair({state},n_a,n_b)',
        f'$objectprops_record_at({state}.OBJECTPROPS,n_left) = (pobjectprops_left_{label})',
        f'$objectprops_record_at({state}.OBJECTPROPS,n_right) = (pobjectprops_right_{label})',
    ]


def checks(program, path, name):
    assert name in ('cell-type-retarget', 'shared-cell-dag')
    dag = name == 'shared-cell-dag'
    first_key = 'first' if dag else 'p'
    encoded_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    rows = [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tpa_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tpa_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        *front('S_first', 'first'),
        f'$property_slot_at(pobjectprops_left_first.SLOTS,$ptascii("{first_key}")) = (ppropertyslot_left_first)',
        f'$property_slot_at(pobjectprops_right_first.SLOTS,$ptascii("{first_key}")) = (ppropertyslot_right_first)',
        'ppropertyslot_left_first.STATE = PROP_VALUE (ALIAS n_cell)',
        'ppropertyslot_right_first.STATE = PROP_VALUE (DIRECT (PINT 1))',
        'n_cell <- S_first.REFCELLS',
        '(HCELL n_cell) <- S_first.ALLOCATIONS',
        'S_first.STORE[n_cell] = DEFINED (PINT 1)',
        '$object_table_at(S_first.OBJECTTABLES,n_left) = eps',
        '$object_table_at(S_first.OBJECTTABLES,n_right) = eps',
        '$heap_owners($heap_prune($heap_graph(S_first)),HCELL n_cell) = n_cell_owners_first',
        '$(n_cell_owners_first >= 2)',
    ]
    if dag:
        rows += [
            '$property_slot_at(pobjectprops_left_first.SLOTS,$ptascii("second")) = (ppropertyslot_second_left_first)',
            'ppropertyslot_second_left_first.STATE = PROP_VALUE (ALIAS n_cell)',
            '$(n_cell_owners_first >= 3)',
            '$property_slot_at(pobjectprops_right_first.SLOTS,$ptascii("second")) = (ppropertyslot_second_right_first)',
            'ppropertyslot_second_right_first.STATE = PROP_VALUE (DIRECT (PINT 1))',
        ]
    rows += [
        '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_effect,ORDER 0)',
        'S_effect.COMPLETION = NORMAL',
        'n_table_left = |S_first.ARRAYS|',
        'n_table_right = $(n_table_left + 1)',
        '|S_effect.ARRAYS| = $(|S_first.ARRAYS| + 2)',
        '$object_table_at(S_effect.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_table_right)',
        '$aggregate_hash_image(S_effect,n_left,n_table_left)',
        '$aggregate_hash_image(S_effect,n_right,n_table_right)',
        '$entry_lookup(S_effect.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("' + first_key + '")) = (pitem_effect_left)',
        '$object_table_item(S_effect,pitem_effect_left) = ALIAS n_cell',
        'S_effect.STORE[n_cell] = DEFINED (PINT 1)',
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT 0)',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.ARRAYS = S_effect.ARRAYS /\ S_first_raw.OBJECTTABLES = S_effect.OBJECTTABLES',
        r'S_first_raw.OBJECTPROPS = S_effect.OBJECTPROPS /\ S_first_raw.STORE = S_effect.STORE',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = $prune_allocations(S_first_raw)[.COMPLETION = BUDGET]',
        'S_second_found = $tpa_seek(S_first_raw,1000)',
        '$tpa_stage(S_second_found)',
        'S_second = S_second_found[.COMPLETION = NORMAL]',
        *front('S_second', 'second'),
        '$object_table_at(S_second.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(S_second.OBJECTTABLES,n_right) = (n_table_second_right)',
        '$aggregate_hash_image(S_second,n_left,n_table_left)',
        '$aggregate_hash_image(S_second,n_right,n_table_second_right)',
        f'$property_slot_at(pobjectprops_left_second.SLOTS,$ptascii("{first_key}")) = (ppropertyslot_left_second)',
        'ppropertyslot_left_second.STATE = PROP_VALUE (ALIAS n_cell)',
        '(HCELL n_cell) <- S_second.ALLOCATIONS',
        'n_cell <- S_second.REFCELLS',
        '$entry_lookup(S_second.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("' + first_key + '")) = (pitem_second_left)',
        '$object_table_item(S_second,pitem_second_left) = ALIAS n_cell',
    ]
    if dag:
        rows += [
            'S_second.STORE[n_cell] = DEFINED (PINT 2)',
            '$property_slot_at(pobjectprops_left_second.SLOTS,$ptascii("second")) = (ppropertyslot_second_left_second)',
            'ppropertyslot_second_left_second.STATE = PROP_VALUE (ALIAS n_cell)',
            '$heap_owners($heap_prune($heap_graph(S_second)),HCELL n_cell) = n_cell_owners_second',
            '$(n_cell_owners_second >= 3)',
            '$object_table_at(S_second.OBJECTTABLES,n_right) = (n_table_right)',
        ]
    else:
        rows += [
            'S_second.STORE[n_cell] = DEFINED (PARRAY n_live)',
            '$entry_lookup(S_second.ARRAYS[n_live].ITEMS,KINT 1) = (DIRECT (PINT 2))',
            '$property_slot_at(pobjectprops_right_second.SLOTS,$ptascii("p")) = (ppropertyslot_right_second)',
            'ppropertyslot_right_second.STATE = PROP_VALUE (DIRECT (PARRAY n_direct))',
            '$entry_lookup(S_second.ARRAYS[n_direct].ITEMS,KINT 1) = (DIRECT (PINT 3))',
            '$lookup(S_second.ENV,$ptascii("source")) = (n_source_cv)',
            'S_second.STORE[n_source_cv] = DEFINED (PARRAY n_source)',
            'n_source =/= n_direct',
            '$entry_lookup(S_second.ARRAYS[n_source].ITEMS,KINT 1) = (DIRECT (PINT 9))',
        ]
    second_result = '1' if dag else '$(-1)'
    rows += [
        f'$value_order_effect(S_second,POBJECT n_a,POBJECT n_b,eps,z_second) = (S_second_effect,ORDER {second_result})',
        'S_second_effect.COMPLETION = NORMAL',
        'PhpStep: S_second ~> S_second_raw',
        f'S_second_raw.RESULT = KNOWN (PINT {second_result})',
        'S_second_raw.TODO = ptask_second*',
        r'S_second_raw.ARRAYS = S_second_effect.ARRAYS /\ S_second_raw.OBJECTTABLES = S_second_effect.OBJECTTABLES',
        r'S_second_raw.OBJECTPROPS = S_second_effect.OBJECTPROPS /\ S_second_raw.STORE = S_second_effect.STORE',
        '$aggregate_compare_seen(S_second_raw) = eps',
        '$drive_steps(S_second,0) = S_second[.COMPLETION = BUDGET]',
        '$drive_steps(S_second,1) = $prune_allocations(S_second_raw)[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_second_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tpa_output(S_done.EVENTS) = $ptascii(' + json.dumps('B|0|M|1|' if dag else 'B|0|A|-1:1|M|1:-1|') + ')',
    ]
    return rows
