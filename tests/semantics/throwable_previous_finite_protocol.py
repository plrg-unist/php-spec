"""Reached canonical previous paths and real deep aggregate root contexts."""
import base64
import json

from throwable_builtin_previous_protocol import PREFIX as PREVIOUS_PREFIX
from throwable_previous_graph_protocol import raw, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'long-cold-exception': 'B|-1:1|A|-1|',
    'long-warm-error': 'B|1:-1:1|A|-1|',
    'long-captured-cycle-recovery': 'B|-1:1|W|1:-1|C|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|I|1|',
    'deep-base-class-skip': 'B|1:1:0:0|',
}

PREFIX = PREVIOUS_PREFIX + r'''
dec $tpf_previous(pstate, nat, nat) : (pnode*, nat)
def $tpf_previous(S, n, 0) = ([HOBJECT n],n)
def $tpf_previous(S, n, n_left) = ((HOBJECT n) :: pnode_tail*,n_leaf)
  -- if $(n_left > 0)
  -- if $throwable_field(S,n,"previous") = POBJECT n_previous
  -- if (pnode_tail*,n_leaf) = $tpf_previous(S,n_previous,$nabs($(n_left - 1)))
dec $tpf_arrays(pstate, nat, nat) : (pnode*, nat)
def $tpf_arrays(S, n, 0) = ([HARRAY n],n)
def $tpf_arrays(S, n, n_left) = ((HARRAY n) :: pnode_tail*,n_leaf)
  -- if $(n_left > 0)
  -- if S.ARRAYS[n].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_next))]
  -- if (pnode_tail*,n_leaf) = $tpf_arrays(S,n_next,$nabs($(n_left - 1)))
'''


def front(program, path, state='S'):
    encoded = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $tbp_seek(S_initial[.COMPLETION = NORMAL],6000)',
        '$tbp_stage(S_found)',
        state + ' = S_found[.COMPLETION = NORMAL]',
        state + '.TODO = (BINARY_RIGHT SPACESHIP poperand_' + state + ' z_' + state + ') :: ptask_' + state + '*',
        '$lookup(' + state + '.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(' + state + '.ENV,$ptascii("b")) = (n_bcv)',
        state + '.STORE[n_acv] = DEFINED (POBJECT n_a)',
        state + '.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        r'$throwable_object_image_valid(' + state + r',n_a) /\ $throwable_object_image_valid(' + state + ',n_b)',
    ]


def paths(state):
    return [
        '(pnode_left*,n_leaf_left) = $tpf_previous(' + state + ',n_a,24)',
        '(pnode_right*,n_leaf_right) = $tpf_previous(' + state + ',n_b,24)',
        r'|pnode_left*| = 25 /\ |pnode_right*| = 25',
        '$heap_unique(pnode_left* ++ pnode_right*)',
        '$heap_subset(pnode_left* ++ pnode_right*,' + state + '.ALLOCATIONS)',
        '$throwable_field(' + state + ',n_leaf_left,"previous") = PNULL',
        '$throwable_field(' + state + ',n_leaf_right,"previous") = PNULL',
        '$throwable_field(' + state + ',n_a,"previous") = POBJECT n_previous_left',
        '$throwable_field(' + state + ',n_b,"previous") = POBJECT n_previous_right',
        '$heap_owners($heap_prune($heap_graph(' + state + ')),HOBJECT n_previous_left) = 1',
        '$heap_owners($heap_prune($heap_graph(' + state + ')),HOBJECT n_previous_right) = 1',
        '$heap_owners($heap_prune($heap_graph(' + state + ')),HOBJECT n_leaf_left) = 1',
        '$heap_owners($heap_prune($heap_graph(' + state + ')),HOBJECT n_leaf_right) = 1',
    ]


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def deep_root(program, path, name):
    rows = front(program, path)
    rows += [
        '$string_compare_values(S,poperand_S,S.RESULT,z_S) = ((S_read,PARRAY n_outer_left,PARRAY n_outer_right))',
        '(pnode_left*,n_inner_left) = $tpf_arrays(S,n_outer_left,24)',
        '(pnode_right*,n_inner_right) = $tpf_arrays(S,n_outer_right,24)',
        r'|pnode_left*| = 25 /\ |pnode_right*| = 25',
        '$heap_unique(pnode_left* ++ pnode_right*)',
        '$heap_subset(pnode_left* ++ pnode_right*,S.ALLOCATIONS)',
        'S.ARRAYS[n_inner_left].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_a)),ENTRY (KINT 1) (DIRECT (POBJECT n_tail))]',
        'S.ARRAYS[n_inner_right].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_b)),ENTRY (KINT 1) (DIRECT pvalue_tail)]',
        '$string_plain(pvalue_tail) = PSTRING $ptascii("tail")',
        'S.OBJECTS[n_a] = THROWABLE pthrowable_a',
        'S.OBJECTS[n_b] = THROWABLE pthrowable_b',
        r'pthrowable_a.KIND = "Exception" /\ pthrowable_b.KIND = "Error"',
        '$throwable_cross_kind_pair(S,n_a,n_b,pnode_left*)',
    ]
    rows += trace('S', 'n_a', 'a', 'POBJECT n_cycle_left')[:4]
    rows += trace('S', 'n_b', 'b', 'POBJECT n_cycle_right')[:4]
    rows += [
        '$objectprops_at(S.OBJECTPROPS,n_cycle_left) = (ppropertyslot_left*)',
        '$objectprops_at(S.OBJECTPROPS,n_cycle_right) = (ppropertyslot_right*)',
        '$property_slot_at(ppropertyslot_left*,$ptascii("next")) = (ppropertyslot_backedge_left)',
        '$property_slot_at(ppropertyslot_right*,$ptascii("next")) = (ppropertyslot_backedge_right)',
        'ppropertyslot_backedge_left.STATE = PROP_VALUE (DIRECT (POBJECT n_cycle_left))',
        'ppropertyslot_backedge_right.STATE = PROP_VALUE (DIRECT (POBJECT n_cycle_right))',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b,HOBJECT n_tail,HOBJECT n_cycle_left,HOBJECT n_cycle_right],S.ALLOCATIONS)',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,pnode_left*,z_S) = (S,ORDER 1)',
        '$value_order_effect(S,PARRAY n_outer_left,PARRAY n_outer_right,eps,z_S) = (S,ORDER 1)',
        'PhpStep: S ~> S_raw',
        'S_raw.RESULT = KNOWN (PINT 1)',
        'S_raw.TODO = ptask_S*',
        r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
        r'S_raw.ARRAYS = S.ARRAYS /\ S_raw.OBJECTTABLES = S.OBJECTTABLES',
        r'S_raw.STORE = S.STORE /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
        'S_raw.EVENTS = S.EVENTS',
        '$aggregate_compare_seen(S_raw) = eps',
        '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.RESULT = S_raw.RESULT',
        'S_one.EVENTS = S.EVENTS',
    ]
    return rows + finish('S_raw', name)


def captured_cycle(program, path, name):
    rows = front(program, path, 'S_first') + paths('S_first')
    rows += [
        '$string_compare_values(S_first,poperand_S_first,S_first.RESULT,z_S_first) = ((S_first_read,POBJECT n_a,POBJECT n_b))',
        '$throwable_builtin_previous_pair(S_first,n_a,n_b,eps)',
        '~$throwable_builtin_previous_chain_valid(S_first,n_a,[n_leaf_left])',
        '~$throwable_builtin_previous_chain_valid($throwable_set_previous_id(S_first,n_leaf_left,(n_a)),n_a,eps)',
        '$throwable_field(S_first,n_a,"severity") = PINT 9',
        '$throwable_field(S_first,n_b,"severity") = PINT 1',
    ]
    rows += trace('S_first', 'n_leaf_left', 'left', 'POBJECT n_left')[:4]
    rows += trace('S_first', 'n_leaf_right', 'right', 'POBJECT n_right')[:4]
    rows += [
        '$entry_lookup($trace_object_current_entries(S_first,n_left),KSTRING $ptascii("value")) = (DIRECT (PINT 1))',
        '$entry_lookup($trace_object_current_entries(S_first,n_right),KSTRING $ptascii("value")) = (DIRECT (PINT 2))',
        '$value_order_effect(S_first,POBJECT n_a,POBJECT n_b,eps,z_S_first) = (S_first_effect,ORDER $(-1))',
        '$object_table_at(S_first.OBJECTTABLES,n_left) = eps',
        '$object_table_at(S_first.OBJECTTABLES,n_right) = eps',
        '$object_table_at(S_first_effect.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(S_first_effect.OBJECTTABLES,n_right) = (n_table_right)',
        '|S_first_effect.ARRAYS| = $(|S_first.ARRAYS| + 2)',
        '$heap_owners($heap_prune($heap_graph(S_first_effect)),HARRAY n_table_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_effect)),HARRAY n_table_right) = 1',
    ]
    rows += raw('S_first', -1, 'S_first_effect')
    rows += [
        'S_reverse = $tbp_seek(S_first_raw,6000)[.COMPLETION = NORMAL]',
        '$tbp_stage(S_reverse)',
        'S_warm = $tbp_next(S_reverse)',
        '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
        '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
        'preqbytes_warm =/= eps',
        'S = $tbp_next(S_warm)',
        'S.TODO = (BINARY_RIGHT pbin poperand z) :: ptask_tail*',
        'pbin = SPACESHIP',
        '$lookup(S.ENV,$ptascii("hold")) = (n_hold)',
        'S.STORE[n_hold] = DEFINED pvalue_hold',
        '$string_plain(pvalue_hold) = PSTRING $ptascii("hold")',
        '$objectprops_at(S.OBJECTPROPS,n_left) = (ppropertyslot_left*)',
        '$objectprops_at(S.OBJECTPROPS,n_right) = (ppropertyslot_right*)',
        '$property_slot_at(ppropertyslot_left*,$ptascii("next")) = (ppropertyslot_backedge_left)',
        '$property_slot_at(ppropertyslot_right*,$ptascii("next")) = (ppropertyslot_backedge_right)',
        'ppropertyslot_backedge_left.STATE = PROP_VALUE (DIRECT (POBJECT n_left))',
        'ppropertyslot_backedge_right.STATE = PROP_VALUE (DIRECT (POBJECT n_right))',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S_effect,ORDERRECURSIVE)',
        r'S_effect.ARRAYS = S.ARRAYS /\ S_effect.OBJECTTABLES = S.OBJECTTABLES',
    ]
    rows += error_rows()
    rows += [
        'S_error.ARRAYS[n_error_trace].ITEMS = eps',
        'S_recovered = $tbp_seek(S_one[.COMPLETION = NORMAL],6000)[.COMPLETION = NORMAL]',
        '$tbp_stage(S_recovered)',
        '$objectprops_at(S_recovered.OBJECTPROPS,n_right) = (ppropertyslot_recovered*)',
        '$property_slot_at(ppropertyslot_recovered*,$ptascii("next")) = (ppropertyslot_shared)',
        'ppropertyslot_shared.STATE = PROP_VALUE (DIRECT (POBJECT n_left))',
    ]
    rows += raw('S_recovered', 1)
    return rows + finish('S_recovered_raw', name)


def checks(program, path, name):
    if name == 'deep-base-class-skip':
        return deep_root(program, path, name)
    if name == 'long-captured-cycle-recovery':
        return captured_cycle(program, path, name)
    rows = front(program, path) + paths('S')
    rows += [
        '$string_compare_values(S,poperand_S,S.RESULT,z_S) = ((S_read,POBJECT n_a,POBJECT n_b))',
    ]
    kind = 'Exception' if name == 'long-cold-exception' else 'Error'
    validator = 'throwable_previous_chain_valid' if kind == 'Exception' else 'throwable_warm_previous_chain_valid'
    pair = 'throwable_previous_pair' if kind == 'Exception' else 'throwable_warm_previous_pair'
    rows += [
        '$' + validator + '(S,n_a,"' + kind + '",eps)',
        '$' + validator + '(S,n_b,"' + kind + '",eps)',
        '~$' + validator + '(S,n_a,"' + kind + '",[n_leaf_left])',
        '~$' + validator + '($throwable_set_previous_id(S,n_leaf_left,(n_a)),n_a,"' + kind + '",eps)',
        '$' + pair + '(S,n_a,n_b)',
        '~$' + pair + '($throwable_set_previous_id(S,n_leaf_left,(n_a)),n_a,n_b)',
        '$throwable_field(S,n_leaf_left,"code") = PINT 1',
        '$throwable_field(S,n_leaf_right,"code") = PINT 2',
        '$objectprops_at(S.OBJECTPROPS,n_a) = (ppropertyslot_left*)',
        '$objectprops_at(S.OBJECTPROPS,n_b) = (ppropertyslot_right*)',
        '$property_order(S,ppropertyslot_left*[0:6],ppropertyslot_right*[0:6],[HOBJECT n_a]) = ORDER 0',
        '$throwable_previous_order(S,n_a,n_b,eps) = ORDER $(-1)',
    ]
    if kind == 'Error':
        rows += [
            '~$throwable_previous_pair(S,n_a,n_b)',
            '$throwable_field(S,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
        ]
    rows += raw('S', -1)
    return rows + finish('S_raw', name)
