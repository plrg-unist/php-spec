"""Reached stdClass trace leaves and their lazy live property tables."""
import base64
import json

PREFIX = r'''
dec $tsc_stage(pstate) : bool
def $tsc_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tsc_stage(S) = false -- otherwise
dec $tsc_seek(pstate, nat) : pstate
def $tsc_seek(S, n) = S -- if $tsc_stage(S) \/ n = 0
def $tsc_seek(S, n) = $tsc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tsc_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tsc_seek(S, n) = S -- otherwise
dec $tsc_event(pevent) : ptbytes
def $tsc_event(OUTPUT ptbytes) = ptbytes
def $tsc_event(pevent) = eps -- otherwise
dec $tsc_output(pevent*) : ptbytes
def $tsc_output(eps) = eps
def $tsc_output(pevent :: pevent_tail*) = $tsc_event(pevent) ++ $tsc_output(pevent_tail*)
'''


def checks(program, path, name):
    assert name == 'array-property-cow'
    encoded_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tsc_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tsc_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (BINARY_RIGHT SPACESHIP poperand_first z_first) :: ptask_first*',
        '$lookup(S_first.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_first.ENV,$ptascii("b")) = (n_bcv)',
        'S_first.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_first.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        'n_a =/= n_b',
        '$throwable_field(S_first,n_a,"trace") = PARRAY n_trace_a',
        '$throwable_field(S_first,n_b,"trace") = PARRAY n_trace_b',
        '$entry_lookup(S_first.ARRAYS[n_trace_a].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_a))',
        '$entry_lookup(S_first.ARRAYS[n_trace_b].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_b))',
        '$entry_lookup(S_first.ARRAYS[n_frame_a].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_a))',
        '$entry_lookup(S_first.ARRAYS[n_frame_b].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_b))',
        '$entry_lookup(S_first.ARRAYS[n_args_a].ITEMS,KINT 0) = (DIRECT (POBJECT n_left))',
        '$entry_lookup(S_first.ARRAYS[n_args_b].ITEMS,KINT 0) = (DIRECT (POBJECT n_right))',
        'n_left =/= n_right',
        '$heap_subset([HARRAY n_trace_a,HARRAY n_frame_a,HARRAY n_args_a,HARRAY n_trace_b,HARRAY n_frame_b,HARRAY n_args_b,HOBJECT n_left,HOBJECT n_right],S_first.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_right) = 2',
        '$trace_std_graph_pair(S_first,n_trace_a,n_trace_b)',
        '$throwable_std_trace_pair(S_first,n_a,n_b)',
        '$object_table_at(S_first.OBJECTTABLES,n_left) = eps',
        '$object_table_at(S_first.OBJECTTABLES,n_right) = eps',
        '$objectprops_at(S_first.OBJECTPROPS,n_left) = (ppropertyslot_left*)',
        '$objectprops_at(S_first.OBJECTPROPS,n_right) = (ppropertyslot_right*)',
        '$property_slot_at(ppropertyslot_left*,$ptascii("p")) = (ppropertyslot_left)',
        '$property_slot_at(ppropertyslot_right*,$ptascii("p")) = (ppropertyslot_right)',
        'ppropertyslot_left.STATE = PROP_VALUE (DIRECT (PARRAY n_saved))',
        'ppropertyslot_right.STATE = PROP_VALUE (DIRECT (PARRAY n_other))',
        'S_first.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)),ENTRY (KINT 1) (DIRECT (PINT 2))]',
        'S_first.ARRAYS[n_other].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)),ENTRY (KINT 1) (DIRECT (PINT 3))]',
        '$lookup(S_first.ENV,$ptascii("source")) = (n_sourcecv)',
        'S_first.STORE[n_sourcecv] = DEFINED (PARRAY n_saved)',
        '(S_effect,ORDER $(-1)) = $value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first)',
        'S_effect.COMPLETION = NORMAL',
        'n_tableleft = |S_first.ARRAYS|',
        'n_tableright = $(n_tableleft + 1)',
        '|S_effect.ARRAYS| = $(|S_first.ARRAYS| + 2)',
        'S_effect.ALLOCATIONS = S_first.ALLOCATIONS ++ [HARRAY n_tableleft,HARRAY n_tableright]',
        '$object_table_at(S_effect.OBJECTTABLES,n_left) = (n_tableleft)',
        '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_tableright)',
        '$aggregate_hash_image(S_effect,n_left,n_tableleft)',
        '$aggregate_hash_image(S_effect,n_right,n_tableright)',
        '$entry_lookup(S_effect.ARRAYS[n_tableleft].ITEMS,KSTRING $ptascii("p")) = (DIRECT (PARRAY n_saved))',
        '$entry_lookup(S_effect.ARRAYS[n_tableright].ITEMS,KSTRING $ptascii("p")) = (DIRECT (PARRAY n_other))',
        '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_tableleft) = 1',
        '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_tableright) = 1',
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT $(-1))',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.ARRAYS = S_effect.ARRAYS /\ S_first_raw.OBJECTTABLES = S_effect.OBJECTTABLES',
        r'S_first_raw.OBJECTPROPS = S_effect.OBJECTPROPS /\ S_first_raw.ALLOCATIONS = S_effect.ALLOCATIONS',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = $prune_allocations(S_first_raw)[.COMPLETION = BUDGET]',
        'S_second_found = $tsc_seek(S_first_raw,1000)',
        '$tsc_stage(S_second_found)',
        'S_second = S_second_found[.COMPLETION = NORMAL]',
        'S_second.TODO = (BINARY_RIGHT SPACESHIP poperand_second z_second) :: ptask_second*',
        '$lookup(S_second.ENV,$ptascii("a")) = (n_acv_second)',
        '$lookup(S_second.ENV,$ptascii("b")) = (n_bcv_second)',
        'S_second.STORE[n_acv_second] = DEFINED (POBJECT n_a)',
        'S_second.STORE[n_bcv_second] = DEFINED (POBJECT n_b)',
        '$lookup(S_second.ENV,$ptascii("source")) = (n_sourcecv_second)',
        'S_second.STORE[n_sourcecv_second] = DEFINED (PARRAY n_mutated)',
        'n_mutated =/= n_saved',
        'S_second.ARRAYS[n_mutated].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)),ENTRY (KINT 1) (DIRECT (PINT 9))]',
        'S_second.ARRAYS[n_saved].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)),ENTRY (KINT 1) (DIRECT (PINT 2))]',
        '$object_table_at(S_second.OBJECTTABLES,n_left) = (n_tableleft)',
        '$object_table_at(S_second.OBJECTTABLES,n_right) = (n_tableright)',
        '$entry_lookup(S_second.ARRAYS[n_tableleft].ITEMS,KSTRING $ptascii("p")) = (DIRECT (PARRAY n_saved))',
        '$throwable_std_trace_pair(S_second,n_a,n_b)',
        '$value_order_effect(S_second,POBJECT n_a,POBJECT n_b,eps,z_second) = (S_second,ORDER $(-1))',
        'PhpStep: S_second ~> S_second_raw',
        'S_second_raw.RESULT = KNOWN (PINT $(-1))',
        'S_second_raw.TODO = ptask_second*',
        r'S_second_raw.ARRAYS = S_second.ARRAYS /\ S_second_raw.OBJECTTABLES = S_second.OBJECTTABLES',
        'S_second_raw.ALLOCATIONS = S_second.ALLOCATIONS',
        '$aggregate_compare_seen(S_second_raw) = eps',
        '$drive_steps(S_second,0) = S_second[.COMPLETION = BUDGET]',
        '$drive_steps(S_second,1) = $prune_allocations(S_second_raw)[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_second_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tsc_output(S_done.EVENTS) = $ptascii("B|-1|S|9:2:-1|M|1:-1|")',
    ]
