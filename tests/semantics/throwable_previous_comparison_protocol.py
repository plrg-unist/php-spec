"""Reached finite previous-chain comparison and equal array prefix."""
import base64
import json

PREFIX = r'''
dec $tpc_stage(pstate) : bool
def $tpc_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tpc_stage(S) = false -- otherwise
dec $tpc_seek(pstate, nat) : pstate
def $tpc_seek(S, n) = S -- if $tpc_stage(S) \/ n = 0
def $tpc_seek(S, n) = $tpc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tpc_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tpc_seek(S, n) = S -- otherwise
dec $tpc_event(pevent) : ptbytes
def $tpc_event(OUTPUT ptbytes) = ptbytes
def $tpc_event(pevent) = eps -- otherwise
dec $tpc_output(pevent*) : ptbytes
def $tpc_output(eps) = eps
def $tpc_output(pevent :: pevent_tail*) = $tpc_event(pevent) ++ $tpc_output(pevent_tail*)
'''


def checks(program, path, name):
    assert name == 'state-direct-array'
    source_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + source_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first_found = $tpc_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tpc_stage(S_first_found)',
        'S_first = S_first_found[.COMPLETION = NORMAL]',
        'S_first.TODO = (BINARY_RIGHT SPACESHIP poperand_first z_first) :: ptask_first*',
        '$lookup(S_first.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_first.ENV,$ptascii("b")) = (n_bcv)',
        'S_first.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_first.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        'n_a =/= n_b',
        '$throwable_field(S_first,n_a,"previous") = POBJECT n_pa',
        '$throwable_field(S_first,n_b,"previous") = POBJECT n_pb',
        'n_pa =/= n_pb',
        '$throwable_field(S_first,n_pa,"previous") = PNULL',
        '$throwable_field(S_first,n_pb,"previous") = PNULL',
        '$throwable_previous_chain_valid(S_first,n_a,"Exception",eps)',
        '$throwable_previous_chain_valid(S_first,n_b,"Exception",eps)',
        '$throwable_previous_pair(S_first,n_a,n_b)',
        '~$throwable_cold_pair(S_first,n_a,n_b)',
        '$throwable_field(S_first,n_a,"trace") = PARRAY n_ta',
        '$throwable_field(S_first,n_b,"trace") = PARRAY n_tb',
        '$throwable_field(S_first,n_pa,"trace") = PARRAY n_tpa',
        '$throwable_field(S_first,n_pb,"trace") = PARRAY n_tpb',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_ta) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_tb) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_tpa) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HARRAY n_tpb) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_pa) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_pb) = 1',
        '$objectprops_at(S_first.OBJECTPROPS,n_a) = (ppropertyslot_a*)',
        '$objectprops_at(S_first.OBJECTPROPS,n_b) = (ppropertyslot_b*)',
        '$property_order(S_first,ppropertyslot_a*[0:6],ppropertyslot_b*[0:6],[HOBJECT n_a]) = ORDER 0',
        '$value_order(S_first,POBJECT n_pa,POBJECT n_pb,eps) = ORDER 1',
        '$throwable_previous_order(S_first,n_a,n_b,eps) = ORDER 0',
        '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_first) = (S_first,ORDER 0)',
        'PhpStep: S_first ~> S_first_raw',
        'S_first_raw.RESULT = KNOWN (PINT 0)',
        'S_first_raw.TODO = ptask_first*',
        r'S_first_raw.OBJECTS = S_first.OBJECTS /\ S_first_raw.OBJECTPROPS = S_first.OBJECTPROPS',
        r'S_first_raw.ARRAYS = S_first.ARRAYS /\ S_first_raw.ALLOCATIONS = S_first.ALLOCATIONS',
        '$aggregate_compare_seen(S_first_raw) = eps',
        '$drive_steps(S_first,0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_first,1) = S_first_raw[.COMPLETION = BUDGET]',
        'S_second_found = $tpc_seek(S_first_raw,1000)',
        '$tpc_stage(S_second_found)',
        'S_second = S_second_found[.COMPLETION = NORMAL]',
        'S_second.TODO = (BINARY_RIGHT SPACESHIP poperand_second z_second) :: ptask_second*',
        '$lookup(S_second.ENV,$ptascii("x")) = (n_xcv)',
        '$lookup(S_second.ENV,$ptascii("y")) = (n_ycv)',
        'S_second.STORE[n_xcv] = DEFINED (PARRAY n_x)',
        'S_second.STORE[n_ycv] = DEFINED (PARRAY n_y)',
        'S_second.ARRAYS[n_x].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_a)),ENTRY (KINT 1) (DIRECT (PINT 1))]',
        'S_second.ARRAYS[n_y].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_b)),ENTRY (KINT 1) (DIRECT (PINT 3))]',
        '$throwable_previous_pair(S_second,n_a,n_b)',
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
        '$tpc_output(S_done.EVENTS) = $ptascii("B|0|-1|")',
    ]
