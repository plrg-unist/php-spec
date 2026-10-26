"""Reached inline and materialized ordinary objects in Throwable traces."""
import base64
import json

PREFIX = r'''
dec $tic_stage(pstate) : bool
def $tic_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tic_stage(S) = false -- otherwise
dec $tic_seek(pstate, nat) : pstate
def $tic_seek(S, n) = S -- if $tic_stage(S) \/ n = 0
def $tic_seek(S, n) = $tic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tic_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tic_seek(S, n) = S -- otherwise
dec $tic_event(pevent) : ptbytes
def $tic_event(OUTPUT ptbytes) = ptbytes
def $tic_event(pevent) = eps -- otherwise
dec $tic_output(pevent*) : ptbytes
def $tic_output(eps) = eps
def $tic_output(pevent :: pevent_tail*) = $tic_event(pevent) ++ $tic_output(pevent_tail*)
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
        f'{state}.OBJECTS[n_left] = INSTANCE porigin',
        f'{state}.OBJECTS[n_right] = INSTANCE porigin',
        f'$class_at({state}.CLASSES,porigin) = (pclassdesc)',
        'pclassdesc.NAME = $ptascii("Plain139")',
        f'$heap_subset([HARRAY n_trace_a,HARRAY n_frame_a,HARRAY n_args_a,HARRAY n_trace_b,HARRAY n_frame_b,HARRAY n_args_b,HOBJECT n_left,HOBJECT n_right],{state}.ALLOCATIONS)',
        f'$trace_instance_graph_pair({state},n_trace_a,n_trace_b)',
        f'$throwable_instance_trace_pair({state},n_a,n_b)',
    ]


def checks(program, path, name):
    assert name in ('inline-declared-order', 'materialized-dynamic-array-cow')
    encoded_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    lines = [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tic_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tic_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        *front('S_first', 'first'),
        '$objectprops_record_at(S_first.OBJECTPROPS,n_left) = (pobjectprops_left)',
        '$objectprops_record_at(S_first.OBJECTPROPS,n_right) = (pobjectprops_right)',
        '$property_slot_at(pobjectprops_left.SLOTS,$ptascii("base")) = (ppropertyslot_base_left)' if name == 'materialized-dynamic-array-cow' else '$property_slot_at(pobjectprops_left.SLOTS,$ptascii("first")) = (ppropertyslot_first_left)',
        '$property_slot_at(pobjectprops_right.SLOTS,$ptascii("base")) = (ppropertyslot_base_right)' if name == 'materialized-dynamic-array-cow' else '$property_slot_at(pobjectprops_right.SLOTS,$ptascii("first")) = (ppropertyslot_first_right)',
    ]
    if name == 'inline-declared-order':
        lines += [
            '$object_table_at(S_first.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S_first.OBJECTTABLES,n_right) = eps',
            '~$objectprops_materialized(S_first.OBJECTPROPS,n_left)',
            '~$objectprops_materialized(S_first.OBJECTPROPS,n_right)',
            'pobjectprops_left.SLOTS = [ppropertyslot_first_left,ppropertyslot_second_left]',
            'pobjectprops_right.SLOTS = [ppropertyslot_first_right,ppropertyslot_second_right]',
            'ppropertyslot_first_left.STATE = PROP_VALUE (DIRECT (PINT 1))',
            'ppropertyslot_first_right.STATE = PROP_VALUE (DIRECT (PINT 1))',
            'ppropertyslot_second_left.STATE = PROP_VALUE (DIRECT (PINT 1))',
            'ppropertyslot_second_right.STATE = PROP_VALUE (DIRECT (PINT 2))',
            '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER $(-1))',
        ]
    else:
        lines += [
            'ppropertyslot_base_left.STATE = PROP_VALUE (DIRECT (PINT 1))',
            'ppropertyslot_base_right.STATE = PROP_VALUE (DIRECT (PINT 1))',
            '$property_slot_at(pobjectprops_left.SLOTS,$ptascii("payload")) = (ppropertyslot_payload_left)',
            '$property_slot_at(pobjectprops_right.SLOTS,$ptascii("payload")) = (ppropertyslot_payload_right)',
            'ppropertyslot_payload_left.STATE = PROP_VALUE (DIRECT (PARRAY n_saved))',
            'ppropertyslot_payload_right.STATE = PROP_VALUE (DIRECT (PARRAY n_other))',
            'S_first.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)),ENTRY (KINT 1) (DIRECT (PINT 2))]',
            'S_first.ARRAYS[n_other].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)),ENTRY (KINT 1) (DIRECT (PINT 3))]',
            '$lookup(S_first.ENV,$ptascii("source")) = (n_sourcecv)',
            'S_first.STORE[n_sourcecv] = DEFINED (PARRAY n_saved)',
            '$object_table_at(S_first.OBJECTTABLES,n_left) = (n_tableleft)',
            '$object_table_at(S_first.OBJECTTABLES,n_right) = (n_tableright)',
            '$heap_subset([HARRAY n_tableleft,HARRAY n_tableright,HARRAY n_saved,HARRAY n_other],S_first.ALLOCATIONS)',
            '$aggregate_hash_image(S_first,n_left,n_tableleft)',
            '$aggregate_hash_image(S_first,n_right,n_tableright)',
            '$object_table_ordinary(S_first,n_left) /\\ $object_table_ordinary(S_first,n_right)',
            '$aggregate_std_pair(S_first,n_left,n_right)',
            '$entry_lookup(S_first.ARRAYS[n_tableleft].ITEMS,KSTRING $ptascii("payload")) = (DIRECT (PARRAY n_saved))',
            '$entry_lookup(S_first.ARRAYS[n_tableright].ITEMS,KSTRING $ptascii("payload")) = (DIRECT (PARRAY n_other))',
            '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_tableleft) = 2',
            '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_tableright) = 2',
            '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER $(-1))',
        ]
    lines += [
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT $(-1))',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.OBJECTTABLES = S_first.OBJECTTABLES /\ S_first_raw.OBJECTPROPS = S_first.OBJECTPROPS',
        r'S_first_raw.ARRAYS = S_first.ARRAYS /\ S_first_raw.ALLOCATIONS = S_first.ALLOCATIONS',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = $prune_allocations(S_first_raw)[.COMPLETION = BUDGET]',
        'S_second_found = $tic_seek(S_first_raw,1000)',
        '$tic_stage(S_second_found)',
        'S_second = S_second_found[.COMPLETION = NORMAL]',
        *front('S_second', 'second'),
    ]
    if name == 'inline-declared-order':
        lines += [
            '$object_table_at(S_second.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S_second.OBJECTTABLES,n_right) = eps',
            '$objectprops_record_at(S_second.OBJECTPROPS,n_left) = (pobjectprops_second_left)',
            '$property_slot_at(pobjectprops_second_left.SLOTS,$ptascii("second")) = (ppropertyslot_second_now)',
            'ppropertyslot_second_now.STATE = PROP_VALUE (DIRECT (PINT 3))',
            '$value_order_effect(S_second,POBJECT n_a,POBJECT n_b,eps,z_second) = (S_second,ORDER 1)',
            'PhpStep: S_second ~> S_second_raw',
            'S_second_raw.RESULT = KNOWN (PINT 1)',
        ]
        expected = 'B|-1|S|1:-1|F|-1:1|'
    else:
        lines += [
            '$lookup(S_second.ENV,$ptascii("source")) = (n_sourcecv_second)',
            'S_second.STORE[n_sourcecv_second] = DEFINED (PARRAY n_mutated)',
            'n_mutated =/= n_saved',
            'S_second.ARRAYS[n_mutated].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)),ENTRY (KINT 1) (DIRECT (PINT 9))]',
            'S_second.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)),ENTRY (KINT 1) (DIRECT (PINT 2))]',
            '$object_table_at(S_second.OBJECTTABLES,n_left) = (n_tableleft)',
            '$object_table_at(S_second.OBJECTTABLES,n_right) = (n_tableright)',
            '$entry_lookup(S_second.ARRAYS[n_tableleft].ITEMS,KSTRING $ptascii("payload")) = (DIRECT (PARRAY n_saved))',
            '$trace_instance_object_pair(S_second,n_left,n_right)',
            '$value_order_effect(S_second,POBJECT n_a,POBJECT n_b,eps,z_second) = (S_second,ORDER $(-1))',
            'PhpStep: S_second ~> S_second_raw',
            'S_second_raw.RESULT = KNOWN (PINT $(-1))',
        ]
        expected = 'B|-1|C|9:2:-1|M|1:-1|'
    lines += [
        'S_second_raw.TODO = ptask_second*',
        r'S_second_raw.OBJECTTABLES = S_second.OBJECTTABLES /\ S_second_raw.OBJECTPROPS = S_second.OBJECTPROPS',
        r'S_second_raw.ARRAYS = S_second.ARRAYS /\ S_second_raw.ALLOCATIONS = S_second.ALLOCATIONS',
        '$aggregate_compare_seen(S_second_raw) = eps',
        '$drive_steps(S_second,0) = S_second[.COMPLETION = BUDGET]',
        '$drive_steps(S_second,1) = $prune_allocations(S_second_raw)[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_second_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tic_output(S_done.EVENTS) = $ptascii(' + json.dumps(expected) + ')',
    ]
    return lines
