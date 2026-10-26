"""Reached cache order and recursive previous-chain comparisons."""
import base64
import json

PREFIX = r'''
dec $twpc_stage(pstate) : bool
def $twpc_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $twpc_stage(S) = false -- otherwise
dec $twpc_seek(pstate, nat) : pstate
def $twpc_seek(S, n) = S -- if $twpc_stage(S) \/ n = 0
def $twpc_seek(S, n) = $twpc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$twpc_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $twpc_seek(S, n) = S -- otherwise
dec $twpc_event(pevent) : ptbytes
def $twpc_event(OUTPUT ptbytes) = ptbytes
def $twpc_event(pevent) = eps -- otherwise
dec $twpc_output(pevent*) : ptbytes
def $twpc_output(eps) = eps
def $twpc_output(pevent :: pevent_tail*) = $twpc_event(pevent) ++ $twpc_output(pevent_tail*)
'''


def checks(program, path, name):
    assert name in ('root-cache-collision', 'child-cache-collision')
    root_cache = name == 'root-cache-collision'
    source_path = json.dumps(base64.b64encode(str(path).encode()).decode())
    checks = [
        'S_initial = $php_run(' + program + ',0,' + source_path + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_cold_found = $twpc_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$twpc_stage(S_cold_found)',
        'S_cold = S_cold_found[.COMPLETION = NORMAL]',
        'S_cold.TODO = (BINARY_RIGHT SPACESHIP poperand_cold z_cold) :: ptask_cold*',
        '$lookup(S_cold.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S_cold.ENV,$ptascii("b")) = (n_bcv)',
        'S_cold.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S_cold.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$throwable_field(S_cold,n_a,"previous") = POBJECT n_pa',
        '$throwable_field(S_cold,n_b,"previous") = POBJECT n_pb',
        'n_pa =/= n_pb',
        '$throwable_field(S_cold,n_pa,"code") = PINT 1',
        '$throwable_field(S_cold,n_pb,"code") = PINT 2',
        '$throwable_field(S_cold,n_pa,"previous") = PNULL',
        '$throwable_field(S_cold,n_pb,"previous") = PNULL',
        '$throwable_previous_pair(S_cold,n_a,n_b)',
        '~$throwable_warm_previous_pair(S_cold,n_a,n_b)',
        '$throwable_field(S_cold,n_a,"trace") = PARRAY n_ta',
        '$throwable_field(S_cold,n_b,"trace") = PARRAY n_tb',
        '$throwable_field(S_cold,n_pa,"trace") = PARRAY n_tpa',
        '$throwable_field(S_cold,n_pb,"trace") = PARRAY n_tpb',
        '$heap_owners($heap_prune($heap_graph(S_cold)),HARRAY n_ta) = 1',
        '$heap_owners($heap_prune($heap_graph(S_cold)),HARRAY n_tb) = 1',
        '$heap_owners($heap_prune($heap_graph(S_cold)),HARRAY n_tpa) = 1',
        '$heap_owners($heap_prune($heap_graph(S_cold)),HARRAY n_tpb) = 1',
        '$heap_owners($heap_prune($heap_graph(S_cold)),HOBJECT n_pa) = ' + ('1' if root_cache else '2'),
        '$heap_owners($heap_prune($heap_graph(S_cold)),HOBJECT n_pb) = ' + ('1' if root_cache else '2'),
        '$value_order_effect(S_cold,POBJECT n_a,POBJECT n_b,eps,z_cold) = (S_cold,ORDER $(-1))',
        'PhpStep: S_cold ~> S_cold_raw',
        'S_cold_raw.RESULT = KNOWN (PINT $(-1))',
        'S_cold_raw.TODO = ptask_cold*',
        r'S_cold_raw.OBJECTS = S_cold.OBJECTS /\ S_cold_raw.OBJECTPROPS = S_cold.OBJECTPROPS',
        r'S_cold_raw.ARRAYS = S_cold.ARRAYS /\ S_cold_raw.ALLOCATIONS = S_cold.ALLOCATIONS',
        '$aggregate_compare_seen(S_cold_raw) = eps',
        'S_one_found = $twpc_seek(S_cold_raw,1000)',
        '$twpc_stage(S_one_found)',
        'S_one = S_one_found[.COMPLETION = NORMAL]',
        'S_one.TODO = (BINARY_RIGHT SPACESHIP poperand_one z_one) :: ptask_one*',
    ]
    warm_left = 'n_a' if root_cache else 'n_pa'
    warm_right = 'n_b' if root_cache else 'n_pb'
    checks += [
        f'$throwable_field(S_one,{warm_left},"string") = PSTRING preqbytes_one',
        f'preqbytes_one = $throwable_chain_string(S_one,{warm_left},[{warm_left}])',
        'preqbytes_one =/= eps',
        f'$throwable_field(S_one,{warm_right},"string") = PSTRING eps',
    ]
    if not root_cache:
        checks += [
            '$throwable_field(S_one,n_a,"string") = PSTRING eps',
            '$throwable_field(S_one,n_b,"string") = PSTRING eps',
        ]
    checks += [
        '$throwable_warm_previous_chain_valid(S_one,n_a,"Exception",eps)',
        '$throwable_warm_previous_chain_valid(S_one,n_b,"Exception",eps)',
        '$throwable_warm_previous_pair(S_one,n_a,n_b)',
        '~$throwable_previous_pair(S_one,n_a,n_b)',
        '$throwable_previous_cache_present(S_one,n_a)',
        '~$throwable_previous_cache_present(S_one,n_b)',
        '$objectprops_at(S_one.OBJECTPROPS,n_a) = (ppropertyslot_a_one*)',
        '$objectprops_at(S_one.OBJECTPROPS,n_b) = (ppropertyslot_b_one*)',
        '$property_order(S_one,ppropertyslot_a_one*[0:6],ppropertyslot_b_one*[0:6],[HOBJECT n_a]) = ORDER ' + ('1' if root_cache else '0'),
        '$throwable_previous_order(S_one,n_a,n_b,eps) = ORDER 1',
        '$value_order_effect(S_one,POBJECT n_a,POBJECT n_b,eps,z_one) = (S_one,ORDER 1)',
        'PhpStep: S_one ~> S_one_raw',
        'S_one_raw.RESULT = KNOWN (PINT 1)',
        'S_one_raw.TODO = ptask_one*',
        r'S_one_raw.OBJECTS = S_one.OBJECTS /\ S_one_raw.OBJECTPROPS = S_one.OBJECTPROPS',
        r'S_one_raw.ARRAYS = S_one.ARRAYS /\ S_one_raw.ALLOCATIONS = S_one.ALLOCATIONS',
        '$aggregate_compare_seen(S_one_raw) = eps',
        '$drive_steps(S_one,0) = S_one[.COMPLETION = BUDGET]',
        '$drive_steps(S_one,1) = S_one_raw[.COMPLETION = BUDGET]',
        'S_reverse_found = $twpc_seek(S_one_raw,1000)',
        '$twpc_stage(S_reverse_found)',
        'S_reverse = S_reverse_found[.COMPLETION = NORMAL]',
        'S_reverse.TODO = (BINARY_RIGHT SPACESHIP poperand_reverse z_reverse) :: ptask_reverse*',
        f'$throwable_field(S_reverse,{warm_left},"string") = PSTRING preqbytes_one',
        f'$throwable_field(S_reverse,{warm_right},"string") = PSTRING eps',
        '$throwable_warm_previous_pair(S_reverse,n_b,n_a)',
        '$value_order_effect(S_reverse,POBJECT n_b,POBJECT n_a,eps,z_reverse) = (S_reverse,ORDER $(-1))',
        'PhpStep: S_reverse ~> S_reverse_raw',
        'S_reverse_raw.RESULT = KNOWN (PINT $(-1))',
        'S_reverse_raw.TODO = ptask_reverse*',
        r'S_reverse_raw.OBJECTS = S_reverse.OBJECTS /\ S_reverse_raw.OBJECTPROPS = S_reverse.OBJECTPROPS',
        r'S_reverse_raw.ARRAYS = S_reverse.ARRAYS /\ S_reverse_raw.ALLOCATIONS = S_reverse.ALLOCATIONS',
        '$aggregate_compare_seen(S_reverse_raw) = eps',
        'S_equal_found = $twpc_seek(S_reverse_raw,1000)',
        '$twpc_stage(S_equal_found)',
        'S_equal = S_equal_found[.COMPLETION = NORMAL]',
        'S_equal.TODO = (BINARY_RIGHT SPACESHIP poperand_equal z_equal) :: ptask_equal*',
        f'$throwable_field(S_equal,{warm_left},"string") = PSTRING preqbytes_equal',
        f'$throwable_field(S_equal,{warm_right},"string") = PSTRING preqbytes_equal',
        'preqbytes_equal =/= eps',
    ]
    if not root_cache:
        checks += [
            '$throwable_field(S_equal,n_a,"string") = PSTRING eps',
            '$throwable_field(S_equal,n_b,"string") = PSTRING eps',
        ]
    checks += [
        '$throwable_warm_previous_pair(S_equal,n_a,n_b)',
        '$throwable_previous_cache_present(S_equal,n_a)',
        '$throwable_previous_cache_present(S_equal,n_b)',
        '$objectprops_at(S_equal.OBJECTPROPS,n_a) = (ppropertyslot_a_equal*)',
        '$objectprops_at(S_equal.OBJECTPROPS,n_b) = (ppropertyslot_b_equal*)',
        '$property_order(S_equal,ppropertyslot_a_equal*[0:6],ppropertyslot_b_equal*[0:6],[HOBJECT n_a]) = ORDER 0',
        '$objectprops_at(S_equal.OBJECTPROPS,n_pa) = (ppropertyslot_pa_equal*)',
        '$objectprops_at(S_equal.OBJECTPROPS,n_pb) = (ppropertyslot_pb_equal*)',
        '$property_order(S_equal,ppropertyslot_pa_equal*[0:6],ppropertyslot_pb_equal*[0:6],[HOBJECT n_pa,HOBJECT n_a]) = ORDER $(-1)',
        '$throwable_previous_order(S_equal,n_a,n_b,eps) = ORDER $(-1)',
        '$value_order_effect(S_equal,POBJECT n_a,POBJECT n_b,eps,z_equal) = (S_equal,ORDER $(-1))',
        'PhpStep: S_equal ~> S_equal_raw',
        'S_equal_raw.RESULT = KNOWN (PINT $(-1))',
        'S_equal_raw.TODO = ptask_equal*',
        r'S_equal_raw.OBJECTS = S_equal.OBJECTS /\ S_equal_raw.OBJECTPROPS = S_equal.OBJECTPROPS',
        r'S_equal_raw.ARRAYS = S_equal.ARRAYS /\ S_equal_raw.ALLOCATIONS = S_equal.ALLOCATIONS',
        '$aggregate_compare_seen(S_equal_raw) = eps',
        '$drive_steps(S_equal,0) = S_equal[.COMPLETION = BUDGET]',
        '$drive_steps(S_equal,1) = S_equal_raw[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_equal_raw,1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$twpc_output(S_done.EVENTS) = $ptascii("B|-1|W|1:-1|E|1:-1:1|")',
    ]
    return checks
