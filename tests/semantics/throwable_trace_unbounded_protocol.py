"""Reached deep paths, shared DAGs, live cells and real recurrence errors."""
import json

from throwable_builtin_previous_protocol import PREFIX as PREVIOUS_PREFIX
from throwable_previous_graph_protocol import front, raw, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'deep-inline-live-leaf': 'B|-1:1|W|1:-1|M|1:-1|E|1|',
    'deep-cycle-before-count-and-identity': 'B|1:E|Nesting level too deep - recursive dependency?|I|1|',
    'deep-shared-dag-and-tail-skip': 'B|0|W|1:0|M|1:-1|A|1|',
    'deep-cell-array-retarget': 'B|-1:1|W|1:-1|M|1:-1|R|-1|',
}

PREFIX = PREVIOUS_PREFIX + r'''
dec $tub_objects(pstate, nat, nat) : (pnode*, nat)
def $tub_objects(S, n, 0) = ([HOBJECT n],n)
def $tub_objects(S, n, n_left) = ((HOBJECT n) :: pnode_tail*,n_leaf)
  -- if $(n_left > 0)
  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,$ptascii("next")) = (ppropertyslot_next)
  -- if ppropertyslot_next.STATE = PROP_VALUE (DIRECT (POBJECT n_next))
  -- if (pnode_tail*,n_leaf) = $tub_objects(S,n_next,$nabs($(n_left - 1)))
dec $tub_refs(pstate, pvalue, nat) : (pnode*, pvalue)
def $tub_refs(S, pvalue, 0) = (eps,pvalue)
def $tub_refs(S, PARRAY n, n_left) = ([HARRAY n,HCELL n_cell] ++ pnode_tail*,pvalue_leaf)
  -- if $(n_left > 0)
  -- if $entry_lookup(S.ARRAYS[n].ITEMS,KINT 0) = (ALIAS n_cell)
  -- if S.STORE[n_cell] = DEFINED pvalue_next
  -- if (pnode_tail*,pvalue_leaf) = $tub_refs(S,pvalue_next,$nabs($(n_left - 1)))
dec $tub_tables(pstate, pnode*) : pnode*
def $tub_tables(S, eps) = eps
def $tub_tables(S, (HOBJECT n) :: pnode_tail*) = (HARRAY n_table) :: $tub_tables(S,pnode_tail*)
  -- if $object_table_at(S.OBJECTTABLES,n) = (n_table)
'''


def captured(node, label, value):
    return trace('S', node, label, value)[:4] + [
        '~$trace_property_ref_graph(S,n_trace_' + label + ')',
    ]


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def checks(program, path, name):
    rows = [row.replace('$tbp_seek(S_initial[.COMPLETION = NORMAL],1000)',
                        '$tbp_seek(S_initial[.COMPLETION = NORMAL],6000)')
            for row in front(program, path)]
    rows += ['S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask_tail*']
    if name == 'deep-cell-array-retarget':
        rows += captured('n_p', 'p', 'PARRAY n_payload_p')
        rows += captured('n_q', 'q', 'PARRAY n_payload_q')
        rows += [
            '(pnode_left*,PINT 1) = $tub_refs(S,PARRAY n_payload_p,24)',
            '(pnode_right*,PINT 2) = $tub_refs(S,PARRAY n_payload_q,24)',
            r'|pnode_left*| = 48 /\ |pnode_right*| = 48',
            '$heap_unique(pnode_left* ++ pnode_right*)',
            '$heap_subset(pnode_left* ++ pnode_right*,S.ALLOCATIONS)',
            '$lookup(S.ENV,$ptascii("left0")) = (n_left0)',
            'S.STORE[n_left0] = DEFINED (PINT 1)',
        ]
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            'S_mutated = $tbp_next(S_warm)',
            'S_mutated_reverse = $tbp_next(S_mutated)',
            'S_retarget = $tbp_next(S_mutated_reverse)',
            '$lookup(S_retarget.ENV,$ptascii("left12")) = (n_left12)',
            '$lookup(S_retarget.ENV,$ptascii("right12")) = (n_right12)',
            'S_retarget.STORE[n_left12] = DEFINED (PARRAY n_retarget_left)',
            'S_retarget.STORE[n_right12] = DEFINED (PARRAY n_retarget_right)',
            '$entry_lookup(S_retarget.ARRAYS[n_retarget_left].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$entry_lookup(S_retarget.ARRAYS[n_retarget_right].ITEMS,KINT 0) = (DIRECT (PINT 9))',
            'S_retarget.STORE[n_left0] = DEFINED (PINT 99)',
        ]
        rows += raw('S_retarget', -1)
        rows += finish('S_retarget_raw', name)
        return rows
    rows += captured('n_p', 'p', 'POBJECT n_left')
    rows += captured('n_q', 'q', 'POBJECT n_right')
    if name == 'deep-shared-dag-and-tail-skip':
        rows += [
            '$lookup(S.ENV,$ptascii("lc")) = (n_lccv)',
            '$lookup(S.ENV,$ptascii("rc")) = (n_rccv)',
            'S.STORE[n_lccv] = DEFINED (POBJECT n_lc)',
            'S.STORE[n_rccv] = DEFINED (POBJECT n_rc)',
            '(pnode_chain_left*,n_leaf_left) = $tub_objects(S,n_lc,24)',
            '(pnode_chain_right*,n_leaf_right) = $tub_objects(S,n_rc,24)',
            'pnode_left* = (HOBJECT n_left) :: pnode_chain_left*',
            'pnode_right* = (HOBJECT n_right) :: pnode_chain_right*',
            '$objectprops_at(S.OBJECTPROPS,n_left) = (ppropertyslot_left*)',
            '$property_slot_at(ppropertyslot_left*,$ptascii("first")) = (ppropertyslot_first)',
            '$property_slot_at(ppropertyslot_left*,$ptascii("second")) = (ppropertyslot_second)',
            r'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_lc)) /\ ppropertyslot_second.STATE = PROP_VALUE (DIRECT (POBJECT n_lc))',
            '$objectprops_at(S.OBJECTPROPS,n_right) = (ppropertyslot_right*)',
            '$property_slot_at(ppropertyslot_right*,$ptascii("first")) = (ppropertyslot_first_right)',
            '$property_slot_at(ppropertyslot_right*,$ptascii("second")) = (ppropertyslot_second_right)',
            r'ppropertyslot_first_right.STATE = PROP_VALUE (DIRECT (POBJECT n_rc)) /\ ppropertyslot_second_right.STATE = PROP_VALUE (DIRECT (POBJECT n_rc))',
        ]
        order = 0
    else:
        rows += [
            '(pnode_left*,n_leaf_left) = $tub_objects(S,n_left,24)',
            '(pnode_right*,n_leaf_right) = $tub_objects(S,n_right,24)',
            r'|pnode_left*| = 25 /\ |pnode_right*| = 25',
        ]
        order = -1
    rows += [
        '$heap_unique(pnode_left* ++ pnode_right*)',
        '$heap_subset(pnode_left* ++ pnode_right*,S.ALLOCATIONS)',
        '$lookup(S.ENV,$ptascii("lp")) = (n_lpcv)',
        '$lookup(S.ENV,$ptascii("rp")) = (n_rpcv)',
        r'S.STORE[n_lpcv] = DEFINED (POBJECT n_leaf_left) /\ S.STORE[n_rpcv] = DEFINED (POBJECT n_leaf_right)',
    ]
    if name == 'deep-cycle-before-count-and-identity':
        rows += [
            '$lookup(S.ENV,$ptascii("other")) = (n_othercv)',
            'S.STORE[n_othercv] = DEFINED (POBJECT n_other)',
            '$objectprops_at(S.OBJECTPROPS,n_leaf_left) = (ppropertyslot_leaf_left*)',
            '$property_slot_at(ppropertyslot_leaf_left*,$ptascii("next")) = (ppropertyslot_backedge)',
            'ppropertyslot_backedge.STATE = PROP_VALUE (DIRECT (POBJECT n_left))',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S_effect,ORDERRECURSIVE)',
            'pnode_tables* = $tub_tables(S_effect,pnode_left* ++ pnode_right* ++ [HOBJECT n_other])',
            '|pnode_tables*| = 51',
            '$heap_unique(pnode_tables*)',
            '$heap_subset(pnode_tables*,S_effect.ALLOCATIONS)',
            '|S_effect.ARRAYS| = $(|S.ARRAYS| + 51)',
            '$object_table_at(S_effect.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_effect.OBJECTTABLES,n_other) = (n_table_other)',
            '$aggregate_table_count(S_effect.ARRAYS[n_table_left].ITEMS) = 1',
            '$aggregate_table_count(S_effect.ARRAYS[n_table_other].ITEMS) = 2',
            '$trace_visit_array_effect(S_effect,n_table_left,n_table_other,[HARRAY n_table_left],z) = (S_effect,ORDERRECURSIVE)',
        ]
        rows += error_rows()
        rows += finish('S_one[.COMPLETION = NORMAL]', name)
        return rows
    rows += [
        '$objectprops_at(S.OBJECTPROPS,n_leaf_left) = (ppropertyslot_leaf*)',
        '$property_slot_at(ppropertyslot_leaf*,$ptascii("value")) = (ppropertyslot_value)',
        'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 1))',
    ]
    if name == 'deep-inline-live-leaf':
        rows += [
            'S.OBJECTS[n_left] = INSTANCE porigin_plain',
            '$objectprops_at(S.OBJECTPROPS,n_leaf_right) = (ppropertyslot_right*)',
            '$property_slot_at(ppropertyslot_right*,$ptascii("value")) = (ppropertyslot_value_right)',
            'ppropertyslot_value_right.STATE = PROP_VALUE (DIRECT (PINT 2))',
            '$throwable_field(S,n_a,"severity") = PINT 9',
            '$throwable_field(S,n_b,"severity") = PINT 1',
            '$object_table_at(S.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S.OBJECTTABLES,n_leaf_left) = eps',
        ]
        rows += raw('S', order)
        rows += [
            'S_raw.OBJECTTABLES = S.OBJECTTABLES',
            'S_raw.ARRAYS = S.ARRAYS',
        ]
    else:
        rows += [
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S_effect,ORDER 0)',
            'pnode_tables* = $tub_tables(S_effect,pnode_left* ++ pnode_right*)',
            '|pnode_tables*| = 52',
            '$heap_unique(pnode_tables*)',
            '$heap_subset(pnode_tables*,S_effect.ALLOCATIONS)',
            '|S_effect.ARRAYS| = $(|S.ARRAYS| + 52)',
        ]
        rows += raw('S', order, 'S_effect')
    rows += finish('S_raw', name)
    return rows
