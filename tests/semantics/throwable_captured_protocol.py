"""Reached captured builtin headers, physical slots, live owners and recurrence."""
import base64
import json

from throwable_trace_visited_protocol import PREFIX
from throwable_previous_graph_protocol import raw, tables, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'captured-cache-before-severity': 'B|-1:1|W|1:-1|C1|1:-1|C2|1:-1|',
    'captured-live-graph-cow': 'B|-1:1|W|1:-1|C|99:1:-1|M|1:-1|E|0|R|0:1:1|K|1:1|',
    'captured-identity-class-cache-skips': 'K|1:1|I|0:1|M|1:1|C|1:-1|A|1|',
    'captured-previous-active-before-prefix': 'B|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|I|0:1|',
}


def front(program, path):
    encoded = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $tbp_seek(S_initial[.COMPLETION = NORMAL],6000)',
        '$tbp_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (BINARY_RIGHT SPACESHIP poperand_S z_S) :: ptask_S*',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$string_compare_values(S,poperand_S,S.RESULT,z_S) = ((S_read,POBJECT n_a,POBJECT n_b))',
        'n_a =/= n_b',
        r'$throwable_builtin_previous_chain_valid(S,n_a,eps) /\ $throwable_builtin_previous_chain_valid(S,n_b,eps)',
        r'$throwable_field(S,n_a,"previous") = PNULL /\ $throwable_field(S,n_b,"previous") = PNULL',
        '$throwable_builtin_previous_order(S,n_a,n_b,eps) = ORDERUNSUPPORTED "Throwable property comparison"',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b],S.ALLOCATIONS)',
    ]


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def object_raw(state, result, effect=None, left='n_a', right='n_b'):
    return [row.replace('POBJECT n_a', 'POBJECT ' + left)
               .replace('POBJECT n_b', 'POBJECT ' + right)
            for row in raw(state, result, effect)]


def children(state='S'):
    return trace(state, 'n_a', 'a', 'POBJECT n_p')[:4] + trace(state, 'n_b', 'b', 'POBJECT n_q')[:4] + [
        'n_p =/= n_q',
        '$trace_visit_object_header(' + state + ',n_p)',
        '$trace_visit_object_header(' + state + ',n_q)',
        '~$trace_object_same_class(' + state + ',n_p,n_q)',
        '~$trace_visit_object_image(' + state + ',n_p)',
        '$heap_subset([HOBJECT n_p,HOBJECT n_q],' + state + '.ALLOCATIONS)',
    ]


def checks(program, path, name):
    rows = front(program, path)
    if name == 'captured-cache-before-severity':
        rows += children()
        rows += [
            '$trace_visit_captured_same_kind(S,n_p,n_q)',
            'S.OBJECTS[n_p] = THROWABLE pthrowable_p',
            'S.OBJECTS[n_q] = THROWABLE pthrowable_q',
            'pthrowable_p.KIND = "ErrorException"',
            'pthrowable_q.KIND = pthrowable_p.KIND',
            '$throwable_field(S,n_a,"severity") = PINT 9',
            '$throwable_field(S,n_b,"severity") = PINT 1',
            '$throwable_field(S,n_p,"severity") = PINT 1',
            '$throwable_field(S,n_q,"severity") = PINT 9',
            '$trace_visit_object_effect(S,n_p,n_q,[HOBJECT n_a],z_S) = (S,ORDER $(-1))',
            '$trace_visit_object_effect(S,n_p,n_q,[HOBJECT n_p],z_S) = (S,ORDERRECURSIVE)',
            '$trace_visit_object_effect(S,n_p,n_p,[HOBJECT n_p],z_S) = (S,ORDER 0)',
            'S_missing = S[.ALLOCATIONS = $tv_without(S.ALLOCATIONS,HOBJECT n_p)]',
            '~$trace_visit_object_header(S_missing,n_p)',
            '$trace_visit_object_effect(S_missing,n_p,n_p,eps,z_S) = (S_missing,ORDERUNSUPPORTED "Throwable property comparison")',
            'S_marked = $objectprops_mark(S,n_p)',
            '~$trace_visit_object_header(S_marked,n_p)',
            '$trace_visit_object_effect(S_marked,n_p,n_q,eps,z_S) = (S_marked,ORDERUNSUPPORTED "Throwable property comparison")',
        ]
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_outer',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_outer',
            'preqbytes_outer =/= eps',
            '$throwable_field(S_warm,n_p,"string") = PSTRING eps',
            '$throwable_field(S_warm,n_q,"string") = PSTRING eps',
        ]
        rows += raw('S_warm', -1)
        rows += [
            'S_child_warm = $tbp_seek(S_warm_raw,6000)[.COMPLETION = NORMAL]',
            '$throwable_field(S_child_warm,n_p,"string") = PSTRING preqbytes_inner',
            'preqbytes_inner =/= eps',
            '$throwable_field(S_child_warm,n_q,"string") = PSTRING eps',
            '$throwable_builtin_previous_effect(S_child_warm,n_p,n_q,[HOBJECT n_p],z_S) = (S_child_warm,ORDERRECURSIVE)',
        ]
        rows += raw('S_child_warm', 1)
        rows += [
            'S_child_reverse = $tbp_seek(S_child_warm_raw,6000)[.COMPLETION = NORMAL]',
            'S_equal_cache = $tbp_next(S_child_reverse)',
            '$throwable_field(S_equal_cache,n_p,"string") = PSTRING preqbytes_inner',
            '$throwable_field(S_equal_cache,n_q,"string") = PSTRING preqbytes_inner',
        ]
        rows += raw('S_equal_cache', -1)
        return rows + finish('S_equal_cache_raw', name)
    if name == 'captured-live-graph-cow':
        rows += trace('S', 'n_a', 'a', 'PARRAY n_payload_a')[:4]
        rows += trace('S', 'n_b', 'b', 'PARRAY n_payload_b')[:4]
        rows += [
            '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KINT 0) = (ALIAS n_live)',
            '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KINT 1) = (DIRECT (POBJECT n_p))',
            '$entry_lookup(S.ARRAYS[n_payload_b].ITEMS,KINT 0) = (DIRECT (POBJECT n_q))',
            '$entry_lookup(S.ARRAYS[n_payload_b].ITEMS,KINT 1) = (DIRECT (POBJECT n_p))',
            '$trace_visit_item_value(S,ALIAS n_live) = (POBJECT n_p)',
            'n_live <- S.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_live) = n_live_owners',
            '$(n_live_owners >= 2)',
            '$trace_visit_captured_same_kind(S,n_p,n_q)',
            '$throwable_field(S,n_p,"previous") = POBJECT n_previous',
            '$throwable_field(S,n_q,"previous") = POBJECT n_previous',
        ]
        rows += trace('S', 'n_p', 'p', 'POBJECT n_left')[:4]
        rows += trace('S', 'n_q', 'q', 'POBJECT n_right')[:4]
        rows += [
            '$entry_lookup($trace_object_current_entries(S,n_left),KSTRING $ptascii("data")) = (DIRECT (PARRAY n_data_left))',
            '$entry_lookup($trace_object_current_entries(S,n_right),KSTRING $ptascii("data")) = (DIRECT (PARRAY n_data_right))',
            '$entry_lookup(S.ARRAYS[n_data_left].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$entry_lookup(S.ARRAYS[n_data_right].ITEMS,KINT 0) = (DIRECT (PINT 2))',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_effect,ORDER $(-1))',
        ]
        rows += tables()
        rows += raw('S', -1, 'S_effect')
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            'S_cow = $tbp_next(S_warm)',
            '$lookup(S_cow.ENV,$ptascii("seed")) = (n_seedcv)',
            'S_cow.STORE[n_seedcv] = DEFINED (PARRAY n_seed_cow)',
            'n_seed_cow =/= n_data_left',
            '$entry_lookup(S_cow.ARRAYS[n_seed_cow].ITEMS,KINT 0) = (DIRECT (PINT 99))',
            '$entry_lookup(S_cow.ARRAYS[n_data_left].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$object_table_at(S_cow.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_cow.OBJECTTABLES,n_right) = (n_table_right)',
        ]
        rows += raw('S_cow', -1)
        rows += [
            'S_mutated = $tbp_seek(S_cow_raw,6000)[.COMPLETION = NORMAL]',
            '$entry_lookup($trace_object_current_entries(S_mutated,n_left),KSTRING $ptascii("data")) = (DIRECT (PARRAY n_data_mutated))',
            '$entry_lookup(S_mutated.ARRAYS[n_data_mutated].ITEMS,KINT 0) = (DIRECT (PINT 3))',
        ]
        rows += raw('S_mutated', 1)
        rows += [
            'S_mutated_reverse = $tbp_seek(S_mutated_raw,6000)[.COMPLETION = NORMAL]',
            'S_equal = $tbp_next(S_mutated_reverse)',
            'S_retarget = $tbp_next(S_equal)',
            '$trace_visit_item_value(S_retarget,ALIAS n_live) = (POBJECT n_q)',
            '$entry_lookup(S_retarget.ARRAYS[n_payload_a].ITEMS,KINT 1) = (DIRECT (POBJECT n_p))',
            '$object_table_at(S_retarget.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_retarget.OBJECTTABLES,n_right) = (n_table_right)',
        ]
        rows += raw('S_retarget', 0)
        return rows + finish('S_retarget_raw', name)
    if name == 'captured-identity-class-cache-skips':
        rows += children()
        rows += [
            '~$trace_visit_captured_same_kind(S,n_p,n_q)',
            'S.OBJECTS[n_p] = THROWABLE pthrowable_p',
            'S.OBJECTS[n_q] = THROWABLE pthrowable_q',
            'pthrowable_p.KIND = "RuntimeException"',
            'pthrowable_q.KIND = "ValueError"',
            '$throwable_field(S,n_p,"trace") = PARRAY n_child_trace',
            '~$trace_property_ref_graph(S,n_child_trace)',
            '$trace_visit_object_effect(S,n_p,n_q,[HOBJECT n_p],z_S) = (S,ORDER 1)',
            '$trace_visit_object_effect(S,n_p,n_p,[HOBJECT n_p],z_S) = (S,ORDER 0)',
            'S_cycle = $throwable_set_previous_id(S,n_p,(n_p))',
            '$throwable_builtin_previous_node_valid(S_cycle,n_p)',
            '~$trace_visit_object_header(S_cycle,n_p)',
            '$trace_visit_object_effect(S_cycle,n_p,n_q,eps,z_S) = (S_cycle,ORDERUNSUPPORTED "Throwable property comparison")',
            '$trace_visit_object_effect(S_cycle,n_p,n_p,eps,z_S) = (S_cycle,ORDERUNSUPPORTED "Throwable property comparison")',
        ]
        rows += trace('S', 'n_p', 'p', 'POBJECT n_method_left')[:4]
        rows += trace('S', 'n_q', 'q', 'POBJECT n_method_right')[:4]
        for side in ('left', 'right'):
            rows += [
                '$objectprops_record_at(S.OBJECTPROPS,n_method_' + side + ') = (pobjectprops_method_' + side + ')',
                '$property_slot_at(pobjectprops_method_' + side + '.SLOTS,$ptascii("next")) = (ppropertyslot_method_' + side + ')',
                'ppropertyslot_method_' + side + '.STATE = PROP_VALUE (DIRECT (POBJECT n_method_' + side + '))',
                '$object_table_at(S.OBJECTTABLES,n_method_' + side + ') = eps',
                '~$trace_visit_object_image(S,n_method_' + side + ')',
            ]
        rows += raw('S', 1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_identity = $tbp_next(S_reverse)',
            '$lookup(S_identity.ENV,$ptascii("c")) = (n_ccv)',
            '$lookup(S_identity.ENV,$ptascii("d")) = (n_dcv)',
            'S_identity.STORE[n_ccv] = DEFINED (POBJECT n_c)',
            'S_identity.STORE[n_dcv] = DEFINED (POBJECT n_d)',
        ]
        rows += trace('S_identity', 'n_c', 'c', 'POBJECT n_p')[:4]
        rows += trace('S_identity', 'n_d', 'd', 'POBJECT n_p')[:4]
        rows += object_raw('S_identity', 0, left='n_c', right='n_d')
        return rows + finish('S_identity_raw', name)
    assert name == 'captured-previous-active-before-prefix'
    rows += trace('S', 'n_a', 'a', 'PARRAY n_payload_a')[:4]
    rows += trace('S', 'n_b', 'b', 'PARRAY n_payload_b')[:4]
    rows += [
        '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KINT 0) = (ALIAS n_left_cell)',
        '$entry_lookup(S.ARRAYS[n_payload_b].ITEMS,KINT 0) = (ALIAS n_right_cell)',
        '$trace_visit_item_value(S,ALIAS n_left_cell) = (POBJECT n_bridge_left)',
        '$trace_visit_item_value(S,ALIAS n_right_cell) = (POBJECT n_bridge_right)',
        'n_bridge_left =/= n_bridge_right',
        '$trace_visit_captured_same_kind(S,n_bridge_left,n_bridge_right)',
        '$throwable_field(S,n_bridge_left,"previous") = POBJECT n_a',
        '$throwable_field(S,n_bridge_right,"previous") = POBJECT n_opposite',
        '$string_plain($throwable_field(S,n_a,"message")) = PSTRING ($ptascii("A"))',
        '$string_plain($throwable_field(S,n_opposite,"message")) = PSTRING ($ptascii("C"))',
        '$trace_visit_captured_same_kind(S,n_a,n_opposite)',
        r'$throwable_builtin_previous_chain_valid(S,n_bridge_left,eps) /\ $throwable_builtin_previous_chain_valid(S,n_bridge_right,eps)',
        '$heap_subset([HCELL n_left_cell,HCELL n_right_cell,HOBJECT n_bridge_left,HOBJECT n_bridge_right,HOBJECT n_opposite],S.ALLOCATIONS)',
        '$throwable_builtin_previous_effect(S,n_a,n_opposite,[HOBJECT n_a],z_S) = (S,ORDERRECURSIVE)',
        '$throwable_builtin_previous_effect(S,n_a,n_a,[HOBJECT n_a],z_S) = (S,ORDER 0)',
        '$throwable_builtin_previous_effect(S,n_a,n_bridge_right,[HOBJECT n_a],z_S) = (S,ORDER 1)',
        '$trace_visit_object_effect(S,n_bridge_left,n_bridge_right,[HOBJECT n_a],z_S) = (S,ORDERRECURSIVE)',
        'S_effect = S',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_effect,ORDERRECURSIVE)',
        'pbin = SPACESHIP',
        'z = z_S',
        '$lookup(S.ENV,$ptascii("hold")) = (n_hold)',
        'S.STORE[n_hold] = DEFINED pvalue_hold',
        '$string_plain(pvalue_hold) = PSTRING $ptascii("hold")',
    ]
    rows += error_rows()
    rows += ['S_error.ARRAYS[n_error_trace].ITEMS = eps']
    return rows + finish('S_one[.COMPLETION = NORMAL]', name)
