"""Reached inline zero, actual empty caches, dynamic folds and trace owners."""
import json
import re

from throwable_interface_protocol import front
from throwable_previous_graph_protocol import raw, trace
from throwable_trace_recursion_protocol import error_rows
from throwable_builtin_previous_protocol import PREFIX

EXPECTED = {
    'empty-inline-before-severity': 'B|0:1:0:0:1:0:1|W|1:0|N|0:-1|S|1:-1|',
    'empty-foreach-cast-caches': 'B|0|A|1:0|L|0:0|R|0|V|1:1:0|',
    'empty-dynamic-alias-count-cycle': 'B|0|C|1:-1|D|-1:1|M|3:99:1|E|0|X|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|K|1:-1|Q|1:1|',
    'empty-trace-owned-targets': 'B|0|H|1:0|T|1|D|1|K|1:1|',
}


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',10000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def start(program, path):
    return front(program, path) + trace('S', 'n_a', 'a', 'POBJECT n_left')[:4] + trace('S', 'n_b', 'b', 'POBJECT n_right')[:4] + [
        'S.OBJECTS[n_left] = INSTANCE porigin_empty',
        'S.OBJECTS[n_right] = INSTANCE porigin_empty',
        '$class_at(S.CLASSES,porigin_empty) = (pclassdesc_empty)',
        '$property_layout(S,porigin_empty,|S.CLASSES|) = eps',
        '$trace_visit_parent_path(S,pclassdesc_empty,eps)',
        '$trace_visit_interfaces(S,pclassdesc_empty)',
        '$objectprops_record_at(S.OBJECTPROPS,n_left) = (pobjectprops_left)',
        '$objectprops_record_at(S.OBJECTPROPS,n_right) = (pobjectprops_right)',
        r'pobjectprops_left.SLOTS = eps /\ pobjectprops_right.SLOTS = eps',
        '$object_table_at(S.OBJECTTABLES,n_left) = eps',
        '$object_table_at(S.OBJECTTABLES,n_right) = eps',
        '$object_table_ordinary(S,n_left)',
        '$trace_visit_object_image(S,n_left)',
        '$trace_visit_object_image(S,n_right)',
        '$trace_visit_inline_empty_pair(S,n_left,n_right)',
        '$trace_visit_object_effect(S,n_left,n_right,eps,z_S) = (S,ORDER 0)',
        # A derived supplied guard distinguishes Zend's zero-before-object-guard rule.
        '$trace_visit_object_effect(S,n_left,n_right,[HOBJECT n_left],z_S) = (S,ORDER 0)',
    ]


def cached(state):
    return [
        '$object_table_at(' + state + '.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(' + state + '.OBJECTTABLES,n_right) = (n_table_right)',
        '$aggregate_hash_image(' + state + ',n_left,n_table_left)',
        '$aggregate_hash_image(' + state + ',n_right,n_table_right)',
        '~$trace_visit_inline_pair(' + state + ',n_left,n_right)',
        '~$trace_visit_inline_empty_pair(' + state + ',n_left,n_right)',
    ]


def pair_raw(state, left, right, result, effect=None):
    return [row.replace('POBJECT n_a', 'POBJECT ' + left).replace('POBJECT n_b', 'POBJECT ' + right)
            for row in raw(state, result, effect)]


def checks(program, path, name):
    rows = start(program, path)
    rows += raw('S', 0)
    if name == 'empty-inline-before-severity':
        rows += [
            'pclassdesc_empty.PARENT =/= eps',
            'S_warm = $tbp_seek(S_raw,10000)[.COMPLETION = NORMAL]',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
            '$object_table_at(S_warm.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S_warm.OBJECTTABLES,n_right) = eps',
        ]
        rows += raw('S_warm', 0)
        rows += [
            'S_noise = $tbp_seek(S_warm_raw,10000)[.COMPLETION = NORMAL]',
            '$trace_visit_inline_empty_pair(S_noise,n_left,n_right)',
            '$value_order_effect(S_noise,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_noise,ORDER 0)',
            'S_array = $tbp_next(S_noise)',
            'S_severity = $tbp_next(S_array)',
            '$lookup(S_severity.ENV,$ptascii("c")) = (n_ccv)',
            '$lookup(S_severity.ENV,$ptascii("d")) = (n_dcv)',
            'S_severity.STORE[n_ccv] = DEFINED (POBJECT n_c)',
            'S_severity.STORE[n_dcv] = DEFINED (POBJECT n_d)',
            '$throwable_field(S_severity,n_c,"severity") = PINT 9',
            '$throwable_field(S_severity,n_d,"severity") = PINT 1',
        ]
        rows += pair_raw('S_severity', 'n_c', 'n_d', 1)
        return rows + finish('S_severity_raw', name)
    if name == 'empty-foreach-cast-caches':
        rows += [
            'S_cast = $tbp_seek(S_raw,10000)[.COMPLETION = NORMAL]',
            '$lookup(S_cast.ENV,$ptascii("cast")) = (n_castcv)',
            '$lookup(S_cast.ENV,$ptascii("copy")) = (n_copycv)',
            'S_cast.STORE[n_castcv] = DEFINED (PARRAY n_cast)',
            'S_cast.STORE[n_copycv] = DEFINED (PARRAY n_copy)',
            'n_cast =/= n_copy',
            'S_cast.ARRAYS[n_cast].ITEMS = eps',
            '$entry_lookup(S_cast.ARRAYS[n_copy].ITEMS,KSTRING $ptascii("x")) = (DIRECT (PINT 1))',
            '$object_table_at(S_cast.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S_cast.OBJECTTABLES,n_right) = eps',
            '$trace_visit_inline_empty_pair(S_cast,n_left,n_right)',
            'S_one = $tbp_next(S_cast)',
            '$object_table_at(S_one.OBJECTTABLES,n_left) = (n_left_before)',
            '$object_table_at(S_one.OBJECTTABLES,n_right) = eps',
            'S_one.ARRAYS[n_left_before].ITEMS = eps',
            '$aggregate_hash_image(S_one,n_left,n_left_before)',
            '~$trace_visit_inline_pair(S_one,n_left,n_right)',
            'n_right_new = |S_one.ARRAYS|',
            '$value_order_effect(S_one,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_effect,ORDER 0)',
            '$object_table_at(S_effect.OBJECTTABLES,n_left) = (n_left_before)',
            '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_right_new)',
            'S_effect.ARRAYS[n_right_new].ITEMS = eps',
            '|S_effect.ARRAYS| = $(|S_one.ARRAYS| + 1)',
            '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_right_new) = 1',
        ]
        rows += raw('S_one', 0, 'S_effect')
        rows += [
            'S_reverse = $tbp_seek(S_one_raw,10000)[.COMPLETION = NORMAL]',
            'S_both = $tbp_next(S_reverse)',
        ]
        rows += cached('S_both')
        rows += [
            'n_table_left =/= n_table_right',
            'S_both.ARRAYS[n_table_left].ITEMS = eps',
            'S_both.ARRAYS[n_table_right].ITEMS = eps',
            '$trace_visit_array_effect(S_both,n_table_left,n_table_right,[HARRAY n_table_left],z_S) = (S_both,ORDERRECURSIVE)',
        ]
        rows += raw('S_both', 0)
        return rows + finish('S_both_raw', name)
    if name == 'empty-trace-owned-targets':
        rows += [
            'S_held = $tbp_seek(S_raw,10000)[.COMPLETION = NORMAL]',
            '$lookup(S_held.ENV,$ptascii("left")) = (n_leftcv)',
            'S_held.STORE[n_leftcv] = DEFINED PNULL',
            '(HOBJECT n_left) <- S_held.ALLOCATIONS',
        ]
        rows += trace('S_held', 'n_a', 'held', 'POBJECT n_left')[:4]
        rows += raw('S_held', 0)
        rows += [
            'S_foreign = $tbp_seek(S_held_raw,10000)[.COMPLETION = NORMAL]',
            '~((HOBJECT n_left) <- S_foreign.ALLOCATIONS)',
            '$lookup(S_foreign.ENV,$ptascii("c")) = (n_ccv)',
            '$lookup(S_foreign.ENV,$ptascii("d")) = (n_dcv)',
            'S_foreign.STORE[n_ccv] = DEFINED (POBJECT n_c)',
            'S_foreign.STORE[n_dcv] = DEFINED (POBJECT n_d)',
            '$lookup(S_foreign.ENV,$ptascii("foreign")) = (n_foreigncv)',
            'S_foreign.STORE[n_foreigncv] = DEFINED (POBJECT n_foreign)',
            '$trace_visit_object_effect(S_foreign,n_right,n_foreign,eps,z_S) = (S_foreign,ORDER 1)',
        ]
        rows += pair_raw('S_foreign', 'n_c', 'n_d', 1)
        return rows + finish('S_foreign_raw', name)
    assert name == 'empty-dynamic-alias-count-cycle'
    rows += [
        'S_count = $tbp_seek(S_raw,10000)[.COMPLETION = NORMAL]',
        '$objectprops_record_at(S_count.OBJECTPROPS,n_left) = (pobjectprops_dynamic)',
        '$property_slot_at(pobjectprops_dynamic.SLOTS,$ptascii("data")) = (ppropertyslot_dynamic)',
        'ppropertyslot_dynamic.DECL = eps',
        'ppropertyslot_dynamic.STATE = PROP_VALUE (ALIAS n_live)',
        '$trace_visit_item_value(S_count,ALIAS n_live) = (PARRAY n_live_initial)',
        '$object_table_at(S_count.OBJECTTABLES,n_left) = (n_left_dynamic)',
        '$object_table_at(S_count.OBJECTTABLES,n_right) = eps',
        '$value_order_effect(S_count,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_count_effect,ORDER 1)',
        '$object_table_at(S_count_effect.OBJECTTABLES,n_right) = (n_right_empty)',
        'S_count_effect.ARRAYS[n_right_empty].ITEMS = eps',
    ]
    rows += raw('S_count', 1, 'S_count_effect')
    rows += [
        'S_reverse = $tbp_seek(S_count_raw,10000)[.COMPLETION = NORMAL]',
        'S_data = $tbp_next(S_reverse)',
    ]
    rows += cached('S_data')
    rows += [
        '$entry_lookup(S_data.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("data")) = (ALIAS n_live)',
        'S_data_reverse = $tbp_next(S_data)',
        'S_mutated = $tbp_next(S_data_reverse)',
        '$trace_visit_item_value(S_mutated,ALIAS n_live) = (PARRAY n_live_mutated)',
        '$entry_lookup(S_mutated.ARRAYS[n_live_mutated].ITEMS,KINT 0) = (DIRECT (PINT 3))',
        '$lookup(S_mutated.ENV,$ptascii("snapshot")) = (n_snapshotcv)',
        'S_mutated.STORE[n_snapshotcv] = DEFINED (PARRAY n_snapshot)',
        '$entry_lookup(S_mutated.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
        'n_snapshot =/= n_live_mutated',
        '$lookup(S_mutated.ENV,$ptascii("view")) = (n_viewcv)',
        'S_mutated.STORE[n_viewcv] = DEFINED (PARRAY n_view)',
        '$entry_lookup(S_mutated.ARRAYS[n_view].ITEMS,KSTRING $ptascii("data")) = (ALIAS n_live)',
        'S_equal = $tbp_next(S_mutated)',
        'S_cycle = $tbp_next(S_equal)',
        '$lookup(S_cycle.ENV,$ptascii("p")) = (n_pcv)',
        '$lookup(S_cycle.ENV,$ptascii("q")) = (n_qcv)',
        'S_cycle.STORE[n_pcv] = DEFINED (POBJECT n_p)',
        'S_cycle.STORE[n_qcv] = DEFINED (POBJECT n_q)',
        'S_cycle.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask_cycle*',
        '$value_order_effect(S_cycle,POBJECT n_p,POBJECT n_q,eps,z) = (S_cycle_effect,ORDERRECURSIVE)',
        'pbin = SPACESHIP',
    ]
    rows += [re.sub(r'\bS\b', 'S_cycle', re.sub(r'\bS_', 'S_cycle_', row)) for row in error_rows()]
    rows += ['S_cycle_error.ARRAYS[n_error_trace].ITEMS = eps']
    return rows + finish('S_cycle_one[.COMPLETION = NORMAL]', name)
