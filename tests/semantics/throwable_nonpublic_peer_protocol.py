"""Reached private keys, protected overrides, real caches and final owners."""
import json
import re

from throwable_empty_clone_protocol import PREFIX
from throwable_interface_protocol import front
from throwable_previous_graph_protocol import raw, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'private-same-name-cache-owners':
        'B|-1:1|W|1:-1|C|1|L|3:1|T|1:-1|E|0|H|1|D|1:3|',
    'protected-override-alias-recursion':
        'B|-1:1|C|99:3:1|E|1|Q|0|X|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|I|0:1|H|1|D|1|A|4:99|K|1:1|',
}

# Each row is a mutation of a reached image or an artificial active guard.
DERIVED = [
    'S_bad_key = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_base[.NAME = $ptascii("same")],ppropertyslot_child,ppropertyslot_tail])]',
    '~$trace_visit_object_image(S_bad_key,n_left)',
    'S_bad_decl = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_base[.DECL = (ppropertydesc_child.ORIGIN)],ppropertyslot_child,ppropertyslot_tail])]',
    '~$trace_visit_object_image(S_bad_decl,n_left)',
    'S_duplicate = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_base,ppropertyslot_child[.NAME = ppropertyslot_base.NAME],ppropertyslot_tail])]',
    '~$trace_visit_object_image(S_duplicate,n_left)',
    '$trace_visit_object_effect(S,n_left,n_right,[HOBJECT n_left],z_S) = (S,ORDERRECURSIVE)',
]


def value(state, name, label, item):
    return [
        '$lookup(' + state + '.ENV,$ptascii(' + json.dumps(name) + ')) = (n_cv_' + label + ')',
        state + '.STORE[n_cv_' + label + '] = DEFINED (' + item + ')',
    ]


def mark(state, label, output):
    return [
        label + ' = $tec_seek_output(' + state + ',10000,$ptascii(' + json.dumps(output) + '))',
        '$tbp_output(' + label + '.EVENTS) = $ptascii(' + json.dumps(output) + ')',
    ]


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',10000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def checks(program, path, name):
    rows = front(program, path)
    rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
    rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
    rows += [
        'S.OBJECTS[n_left] = INSTANCE porigin_leaf',
        'S.OBJECTS[n_right] = INSTANCE porigin_leaf',
        '$class_at(S.CLASSES,porigin_leaf) = (pclassdesc_leaf)',
        '$trace_visit_parent_path(S,pclassdesc_leaf,eps)',
        r'$trace_visit_object_image(S,n_left) /\ $trace_visit_object_image(S,n_right)',
        '~$trace_instance_class(S,n_left)',
        '$trace_visit_inline_pair(S,n_left,n_right)',
        '$objectprops_record_at(S.OBJECTPROPS,n_left) = (pobjectprops_left)',
    ]
    if name == 'private-same-name-cache-owners':
        rows += [
            '$property_layout(S,porigin_leaf,|S.CLASSES|) = [ppropertydesc_base,ppropertydesc_child,ppropertydesc_tail]',
            'ppropertydesc_base.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_child.VISIBILITY = PROPERTY_PRIVATE',
            r'ppropertydesc_base.NAME = $ptascii("same") /\ ppropertydesc_child.NAME = $ptascii("same")',
            'ppropertydesc_base.KEY = [0] ++ $ptascii("Base159") ++ [0] ++ $ptascii("same")',
            'ppropertydesc_child.KEY = [0] ++ $ptascii("Packet159") ++ [0] ++ $ptascii("same")',
            'ppropertydesc_base.KEY =/= ppropertydesc_child.KEY',
            '$property_declaring_name(S.CLASSES,ppropertydesc_base.ORIGIN) = $ptascii("Base159")',
            '$property_declaring_name(S.CLASSES,ppropertydesc_child.ORIGIN) = $ptascii("Packet159")',
            'pobjectprops_left.SLOTS = [ppropertyslot_base,ppropertyslot_child,ppropertyslot_tail]',
            'ppropertyslot_base.DECL = (ppropertydesc_base.ORIGIN)',
            'ppropertyslot_base.NAME = ppropertydesc_base.KEY',
            'ppropertyslot_base.STATE = PROP_VALUE (DIRECT (PINT 1))',
            'ppropertyslot_child.DECL = (ppropertydesc_child.ORIGIN)',
            'ppropertyslot_child.NAME = ppropertydesc_child.KEY',
            'ppropertyslot_child.STATE = PROP_VALUE (DIRECT (PINT 9))',
            'ppropertyslot_tail.NAME = ppropertydesc_tail.KEY',
        ]
        rows += DERIVED
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,10000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
            '$value_order_effect(S_warm,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_warm,ORDER $(-1))',
            'S_child = $tbp_next(S_warm)',
            '$value_order_effect(S_child,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_child,ORDER 1)',
            'S_one = $tbp_next(S_child)',
            '$object_table_at(S_one.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_one.OBJECTTABLES,n_right) = eps',
            'S_one.ARRAYS[n_table_left].ITEMS = [ENTRY (KSTRING ppropertydesc_base.KEY) (INDIRECT n_left ppropertydesc_base.KEY),ENTRY (KSTRING ppropertydesc_child.KEY) (INDIRECT n_left ppropertydesc_child.KEY),ENTRY (KSTRING ppropertydesc_tail.KEY) (INDIRECT n_left ppropertydesc_tail.KEY)]',
            '$object_table_item(S_one,INDIRECT n_left ppropertydesc_base.KEY) = DIRECT (PINT 2)',
            '$object_table_item(S_one,INDIRECT n_left ppropertydesc_child.KEY) = DIRECT (PINT 9)',
            '$value_order_effect(S_one,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_effect,ORDER 1)',
            'n_table_right = |S_one.ARRAYS|',
            '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_table_right)',
            'S_effect.ALLOCATIONS = S_one.ALLOCATIONS ++ [HARRAY n_table_right]',
            '$object_tables_valid(S_effect)',
        ]
        rows += value('S_one', 'view', 'view_one', 'PARRAY n_view')
        rows += value('S_one', 'snapshot', 'snapshot_one', 'PARRAY n_snapshot')
        rows += [
            'n_view =/= n_snapshot',
            '$entry_lookup(S_one.ARRAYS[n_view].ITEMS,KSTRING $ptascii("extra")) = (DIRECT (PINT 99))',
            '$entry_lookup(S_one.ARRAYS[n_snapshot].ITEMS,KSTRING $ptascii("extra")) = eps',
            '$entry_lookup(S_one.ARRAYS[n_snapshot].ITEMS,KSTRING ppropertydesc_base.KEY) = (DIRECT (PINT 2))',
            '$entry_lookup(S_one.ARRAYS[n_snapshot].ITEMS,KSTRING ppropertydesc_child.KEY) = (DIRECT (PINT 9))',
        ]
        rows += raw('S_one', 1, 'S_effect')
        rows += [
            'S_tables = $tbp_seek(S_one_raw,10000)[.COMPLETION = NORMAL]',
            '$object_table_at(S_tables.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_tables.OBJECTTABLES,n_right) = (n_table_right)',
            '$aggregate_hash_image(S_tables,n_left,n_table_left)',
            '$aggregate_hash_image(S_tables,n_right,n_table_right)',
            'S_tables_reverse = $tbp_next(S_tables)',
            'S_equal = $tbp_next(S_tables_reverse)',
            '$object_table_item(S_equal,INDIRECT n_right ppropertydesc_child.KEY) = DIRECT (PINT 9)',
        ]
        rows += raw('S_equal', 0)
        rows += mark('S_equal_raw', 'S_hold', 'B|-1:1|W|1:-1|C|1|L|3:1|T|1:-1|E|0|H|')
        rows += value('S_hold', 'left', 'left_hold', 'PNULL')
        rows += [
            '(HOBJECT n_left) <- S_hold.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_left) = 1',
        ]
        return rows + finish('S_hold', name) + [
            '~((HOBJECT n_left) <- S_done.ALLOCATIONS)',
            '$object_table_at(S_done.OBJECTTABLES,n_left) = eps',
            '(HARRAY n_snapshot) <- S_done.ALLOCATIONS',
            '$entry_lookup(S_done.ARRAYS[n_snapshot].ITEMS,KSTRING ppropertydesc_base.KEY) = (DIRECT (PINT 2))',
        ]
    assert name == 'protected-override-alias-recursion'
    rows += [
        '$property_layout(S,porigin_leaf,|S.CLASSES|) = [ppropertydesc_first,ppropertydesc_hidden,ppropertydesc_tail]',
        'ppropertydesc_first.VISIBILITY = PROPERTY_PROTECTED',
        'ppropertydesc_first.KEY = [0,42,0] ++ $ptascii("first")',
        '$property_declaring_name(S.CLASSES,ppropertydesc_first.ORIGIN) = $ptascii("Packet159")',
        '$property_declaring_name(S.CLASSES,ppropertydesc_hidden.ORIGIN) = $ptascii("Base159")',
        'pobjectprops_left.SLOTS = [ppropertyslot_first,ppropertyslot_hidden,ppropertyslot_tail]',
        'ppropertyslot_first.DECL = (ppropertydesc_first.ORIGIN)',
        'ppropertyslot_first.NAME = ppropertydesc_first.KEY',
        'ppropertyslot_first.STATE = PROP_VALUE (ALIAS n_live)',
        '$lookup(S.ENV,$ptascii("live")) = (n_live)',
        'S.STORE[n_live] = DEFINED (PARRAY n_initial)',
        '$entry_lookup(S.ARRAYS[n_initial].ITEMS,KINT 0) = (DIRECT (PINT 1))',
    ]
    rows += raw('S', -1)
    rows += [
        'S_reverse = $tbp_seek(S_raw,10000)[.COMPLETION = NORMAL]',
        'S_mutated = $tbp_next(S_reverse)',
        '$object_table_at(S_mutated.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(S_mutated.OBJECTTABLES,n_right) = (n_table_right)',
        '$entry_lookup(S_mutated.ARRAYS[n_table_left].ITEMS,KSTRING ppropertydesc_first.KEY) = (INDIRECT n_left ppropertydesc_first.KEY)',
        '$object_table_item(S_mutated,INDIRECT n_left ppropertydesc_first.KEY) = ALIAS n_live',
        'S_mutated.STORE[n_live] = DEFINED (PARRAY n_mutated)',
        '$entry_lookup(S_mutated.ARRAYS[n_mutated].ITEMS,KINT 0) = (DIRECT (PINT 3))',
        '$object_tables_valid(S_mutated)',
    ]
    rows += value('S_mutated', 'view', 'view_mutated', 'PARRAY n_view')
    rows += value('S_mutated', 'snapshot', 'snapshot_mutated', 'PARRAY n_snapshot')
    rows += [
        '$entry_lookup(S_mutated.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
        'n_snapshot =/= n_mutated',
        '$entry_lookup(S_mutated.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_first.KEY) = (ALIAS n_live)',
        '$($heap_owners($heap_prune($heap_graph(S_mutated)),HCELL n_live) >= 3)',
    ]
    rows += raw('S_mutated', 1)
    rows += [
        'S_equal_first = $tbp_seek(S_mutated_raw,10000)[.COMPLETION = NORMAL]',
        '$value_order_effect(S_equal_first,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_equal_first,ORDER 1)',
        'S_equal_tail = $tbp_next(S_equal_first)',
        '$value_order_effect(S_equal_tail,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_equal_tail,ORDER 0)',
        'S_cycle = $tbp_next(S_equal_tail)',
        'S_cycle.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask_cycle*',
        '$value_order_effect(S_cycle,POBJECT n_a,POBJECT n_b,eps,z) = (S_cycle,ORDERRECURSIVE)',
        'S_cycle_effect = S_cycle',
        'pbin = SPACESHIP',
    ]
    rows += [re.sub(r'\bS\b', 'S_cycle', re.sub(r'\bS_', 'S_cycle_', row)) for row in error_rows()]
    rows += [
        'S_cycle_error.ARRAYS[n_error_trace].ITEMS = eps',
        'S_identity = $tbp_seek(S_cycle_one[.COMPLETION = NORMAL],10000)[.COMPLETION = NORMAL]',
    ]
    rows += raw('S_identity', 0)
    hold = EXPECTED[name].split('H|')[0] + 'H|'
    rows += mark('S_identity_raw', 'S_hold', hold)
    rows += value('S_hold', 'left', 'left_hold', 'PNULL')
    rows += value('S_hold', 'a', 'a_hold', 'PNULL')
    rows += [
        '(HOBJECT n_left) <- S_hold.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_left) = 1',
    ]
    rows += mark('S_hold', 'S_drop', hold + '1|D|')
    rows += [
        '~((HOBJECT n_left) <- S_drop.ALLOCATIONS)',
        '$object_table_at(S_drop.OBJECTTABLES,n_left) = eps',
        '(HCELL n_live) <- S_drop.ALLOCATIONS',
        '$entry_lookup(S_drop.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_first.KEY) = (ALIAS n_live)',
        'S_foreign = $tbp_seek(S_drop,10000)[.COMPLETION = NORMAL]',
    ]
    rows += value('S_foreign', 'c', 'foreign_c', 'POBJECT n_c')
    rows += value('S_foreign', 'd', 'foreign_d', 'POBJECT n_d')
    rows += [
        '$value_order_effect(S_foreign,POBJECT n_c,POBJECT n_d,eps,z_S) = (S_foreign,ORDER 1)',
    ]
    rows += finish('S_foreign', name)
    rows += [
        'S_done.STORE[n_live] = DEFINED (PARRAY n_final)',
        '$entry_lookup(S_done.ARRAYS[n_final].ITEMS,KINT 0) = (DIRECT (PINT 4))',
        '$entry_lookup(S_done.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_first.KEY) = (ALIAS n_live)',
        '~((HOBJECT n_left) <- S_done.ALLOCATIONS)',
    ]
    return rows
