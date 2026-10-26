"""Reached nested object comparison, live writes and shared DAG owners."""
import base64
import json

PREFIX = r'''
dec $tog_stage(pstate) : bool
def $tog_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tog_stage(S) = false -- otherwise
dec $tog_seek(pstate, nat) : pstate
def $tog_seek(S, n) = S -- if $tog_stage(S) \/ n = 0
def $tog_seek(S, n) = $tog_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tog_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tog_seek(S, n) = S -- otherwise
dec $tog_event(pevent) : ptbytes
def $tog_event(OUTPUT ptbytes) = ptbytes
def $tog_event(pevent) = eps -- otherwise
dec $tog_output(pevent*) : ptbytes
def $tog_output(eps) = eps
def $tog_output(pevent :: pevent_tail*) = $tog_event(pevent) ++ $tog_output(pevent_tail*)
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
        fr'$trace_object_graph({state},n_trace_a) /\ $trace_object_graph({state},n_trace_b)',
        f'$trace_object_graph_pair({state},n_trace_a,n_trace_b)',
        f'$throwable_object_graph_pair({state},n_a,n_b)',
    ]


def child(state, label, dag):
    rows = [
        f'$objectprops_record_at({state}.OBJECTPROPS,n_left) = (pobjectprops_left_{label})',
        f'$objectprops_record_at({state}.OBJECTPROPS,n_right) = (pobjectprops_right_{label})',
        f'$property_slot_at(pobjectprops_left_{label}.SLOTS,$ptascii("{"first" if dag else "child"}")) = (ppropertyslot_left_{label})',
        f'$property_slot_at(pobjectprops_right_{label}.SLOTS,$ptascii("{"first" if dag else "child"}")) = (ppropertyslot_right_{label})',
        f'ppropertyslot_left_{label}.STATE = PROP_VALUE (DIRECT (POBJECT n_child_left))',
        f'ppropertyslot_right_{label}.STATE = PROP_VALUE (DIRECT (POBJECT n_child_right))',
        'n_child_left =/= n_child_right',
        f'{state}.OBJECTS[n_child_left] = STDINSTANCE',
        f'{state}.OBJECTS[n_child_right] = STDINSTANCE',
        f'$heap_subset([HOBJECT n_child_left,HOBJECT n_child_right],{state}.ALLOCATIONS)',
    ]
    if dag:
        rows += [
            f'$property_slot_at(pobjectprops_left_{label}.SLOTS,$ptascii("second")) = (ppropertyslot_second_left_{label})',
            f'$property_slot_at(pobjectprops_right_{label}.SLOTS,$ptascii("second")) = (ppropertyslot_second_right_{label})',
            f'ppropertyslot_second_left_{label}.STATE = PROP_VALUE (DIRECT (POBJECT n_child_left))',
            f'ppropertyslot_second_right_{label}.STATE = PROP_VALUE (DIRECT (POBJECT n_child_right))',
        ]
    return rows


def checks(program, path, name):
    assert name in ('live-child-value', 'shared-child-dag')
    dag = name == 'shared-child-dag'
    encoded_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    rows = [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tog_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tog_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        *front('S_first', 'first'),
        *child('S_first', 'first', dag),
        '$object_table_at(S_first.OBJECTTABLES,n_left) = eps',
        '$object_table_at(S_first.OBJECTTABLES,n_right) = eps',
        '$object_table_at(S_first.OBJECTTABLES,n_child_left) = eps',
        '$object_table_at(S_first.OBJECTTABLES,n_child_right) = eps',
        '$objectprops_record_at(S_first.OBJECTPROPS,n_child_left) = (pchildprops_left)',
        '$objectprops_record_at(S_first.OBJECTPROPS,n_child_right) = (pchildprops_right)',
        '$property_slot_at(pchildprops_left.SLOTS,$ptascii("x")) = (ppropertyslot_x_left)',
        '$property_slot_at(pchildprops_right.SLOTS,$ptascii("x")) = (ppropertyslot_x_right)',
        'ppropertyslot_x_left.STATE = PROP_VALUE (DIRECT (PINT 1))',
        'ppropertyslot_x_right.STATE = PROP_VALUE (DIRECT (PINT 1))' if dag else 'ppropertyslot_x_right.STATE = PROP_VALUE (DIRECT (PINT 2))',
        '$heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_child_left) = 3' if dag else '$heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_child_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_child_right) = 3' if dag else '$heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_child_right) = 2',
        f'(S_effect,ORDER {"0" if dag else "$(-1)"}) = $value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first)',
        'S_effect.COMPLETION = NORMAL',
        'n_root_table_left = |S_first.ARRAYS|',
        'n_root_table_right = $(n_root_table_left + 1)',
        'n_child_table_left = $(n_root_table_left + 2)',
        'n_child_table_right = $(n_root_table_left + 3)',
        '|S_effect.ARRAYS| = $(|S_first.ARRAYS| + 4)',
        'S_effect.ALLOCATIONS = S_first.ALLOCATIONS ++ [HARRAY n_root_table_left,HARRAY n_root_table_right,HARRAY n_child_table_left,HARRAY n_child_table_right]',
        '$object_table_at(S_effect.OBJECTTABLES,n_left) = (n_root_table_left)',
        '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_root_table_right)',
        '$object_table_at(S_effect.OBJECTTABLES,n_child_left) = (n_child_table_left)',
        '$object_table_at(S_effect.OBJECTTABLES,n_child_right) = (n_child_table_right)',
        '$aggregate_hash_image(S_effect,n_left,n_root_table_left)',
        '$aggregate_hash_image(S_effect,n_right,n_root_table_right)',
        '$aggregate_hash_image(S_effect,n_child_left,n_child_table_left)',
        '$aggregate_hash_image(S_effect,n_child_right,n_child_table_right)',
        'PhpStep: S_first ~> S_first_raw',
        f'S_first_raw.RESULT = KNOWN (PINT {"0" if dag else "$(-1)"})',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.ARRAYS = S_effect.ARRAYS /\ S_first_raw.OBJECTTABLES = S_effect.OBJECTTABLES',
        r'S_first_raw.OBJECTPROPS = S_effect.OBJECTPROPS /\ S_first_raw.ALLOCATIONS = S_effect.ALLOCATIONS',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = $prune_allocations(S_first_raw)[.COMPLETION = BUDGET]',
        'S_second_found = $tog_seek(S_first_raw,1000)',
        '$tog_stage(S_second_found)',
        'S_second = S_second_found[.COMPLETION = NORMAL]',
        *front('S_second', 'second'),
        *child('S_second', 'second', dag),
        '$objectprops_record_at(S_second.OBJECTPROPS,n_child_left) = (pchildprops_second_left)',
        '$objectprops_record_at(S_second.OBJECTPROPS,n_child_right) = (pchildprops_second_right)',
        '$property_slot_at(pchildprops_second_left.SLOTS,$ptascii("x")) = (ppropertyslot_x_second_left)',
        '$property_slot_at(pchildprops_second_right.SLOTS,$ptascii("x")) = (ppropertyslot_x_second_right)',
        'ppropertyslot_x_second_left.STATE = PROP_VALUE (DIRECT (PINT 2))' if dag else 'ppropertyslot_x_second_left.STATE = PROP_VALUE (DIRECT (PINT 3))',
        'ppropertyslot_x_second_right.STATE = PROP_VALUE (DIRECT (PINT 2))',
        '$object_table_at(S_second.OBJECTTABLES,n_left) = (n_root_table_left)',
        '$object_table_at(S_second.OBJECTTABLES,n_right) = (n_root_table_right)',
        '$object_table_at(S_second.OBJECTTABLES,n_child_left) = (n_child_table_left)',
        '$object_table_at(S_second.OBJECTTABLES,n_child_right) = (n_child_table_right)',
        f'$value_order_effect(S_second,POBJECT n_a,POBJECT n_b,eps,z_second) = (S_second,ORDER {"0" if dag else "1"})',
        'PhpStep: S_second ~> S_second_raw',
        f'S_second_raw.RESULT = KNOWN (PINT {"0" if dag else "1"})',
        'S_second_raw.TODO = ptask_second*',
        r'S_second_raw.ARRAYS = S_second.ARRAYS /\ S_second_raw.OBJECTTABLES = S_second.OBJECTTABLES',
        r'S_second_raw.OBJECTPROPS = S_second.OBJECTPROPS /\ S_second_raw.ALLOCATIONS = S_second.ALLOCATIONS',
        '$aggregate_compare_seen(S_second_raw) = eps',
        '$drive_steps(S_second,0) = S_second[.COMPLETION = BUDGET]',
        '$drive_steps(S_second,1) = $prune_allocations(S_second_raw)[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_second_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tog_output(S_done.EVENTS) = $ptascii(' + json.dumps('B|0|E|0|' if dag else 'B|-1|M|1:-1|E|0|') + ')',
    ]
    return rows
