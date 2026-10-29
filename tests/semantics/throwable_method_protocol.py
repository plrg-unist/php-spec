"""Reached ordinary-method images, current field owners and standard recursion."""
import base64
import json

from throwable_builtin_previous_protocol import PREFIX
from throwable_previous_graph_protocol import raw, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'method-fields-before-severity': 'B|-1:1|W|1:-1|C|99:1:-1|M|1:-1|E|1|',
    'method-foreach-cached-tables': 'B|-1:1|M|1:99:3|E|1:0|T|0|R|4:2:1|',
    'method-cycle-before-earlier-field': 'B|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|I|0:1|M|-1:1|W|1:-1|',
    'method-table-count-key-tail': 'C|1:-1|K|1:1|W|1:1|A|1|E|0:-1|',
}
CONTROLS = ('implicit-stringable-control', 'private-layout-control')


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
        r'$throwable_builtin_previous_chain_valid(S,n_a,eps) /\ $throwable_builtin_previous_chain_valid(S,n_b,eps)',
        '$throwable_builtin_previous_order(S,n_a,n_b,eps) = ORDERUNSUPPORTED "Throwable property comparison"',
    ]


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def method_pair(state='S', normal=True):
    rows = [
        state + '.OBJECTS[n_left] = INSTANCE porigin_class',
        state + '.OBJECTS[n_right] = INSTANCE porigin_class',
        '$class_at(' + state + '.CLASSES,porigin_class) = (pclassdesc_method)',
        'pclassdesc_method.METHODS =/= eps',
        '$trace_visit_object_header(' + state + ',n_left)',
        '$trace_visit_object_header(' + state + ',n_right)',
        '~$trace_instance_class(' + state + ',n_left)',
    ]
    if normal:
        rows += [
            'pclassdesc_method.INTERFACES = eps',
            'pclassdesc_method.PARENT = eps',
            '$trace_visit_object_class(' + state + ',n_left)',
            '$trace_visit_object_class(' + state + ',n_right)',
            '$trace_visit_object_image(' + state + ',n_left)',
            '$trace_visit_object_image(' + state + ',n_right)',
        ]
    return rows


def field(state, node, label, item, name='data'):
    return [
        '$objectprops_record_at(' + state + '.OBJECTPROPS,' + node + ') = (pobjectprops_' + label + ')',
        '$property_slot_at(pobjectprops_' + label + '.SLOTS,$ptascii(' + json.dumps(name) + ')) = (ppropertyslot_' + label + ')',
        'ppropertyslot_' + label + '.STATE = PROP_VALUE (' + item + ')',
    ]


def checks(program, path, name):
    rows = front(program, path)
    if name == 'method-foreach-cached-tables':
        rows += trace('S', 'n_a', 'a', 'POBJECT n_p')[:4]
        rows += trace('S', 'n_b', 'b', 'POBJECT n_q')[:4]
        rows += trace('S', 'n_p', 'p', 'POBJECT n_left')[:4]
        rows += trace('S', 'n_q', 'q', 'POBJECT n_right')[:4]
    else:
        rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
        rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
    rows += method_pair(normal=name not in CONTROLS)
    if name == 'implicit-stringable-control':
        rows += [
            'pclassdesc_method.INTERFACES = [$ptascii("Stringable")]',
            '$pil_at(S.LINKEDINTERFACES,porigin_class) = (PILTARGETS pilref_implicit*)',
            'pilref_implicit* = [PILBUILTIN $ptascii("Stringable")]',
            '$pil_targets_valid(S,pclassdesc_method.INTERFACES,pilref_implicit*)',
            '$pil_targets_ordered(S,porigin_class,pilref_implicit*)',
            '$trace_visit_interfaces(S,pclassdesc_method)',
            '$trace_visit_object_class(S,n_left)',
            '$trace_visit_object_image(S,n_left)',
            '$trace_visit_object_image(S,n_right)',
        ]
        rows += raw('S', -1)
        return rows + [
            'S_done = $drive_steps(S_raw,6000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tbp_output(S_done.EVENTS) = $ptascii("B|-1|")',
        ]
    if name == 'private-layout-control':
        return rows + [
            '~$trace_visit_object_class(S,n_left)',
            '~$trace_visit_object_image(S,n_left)',
            '$property_layout(S,porigin_class,|S.CLASSES|) = (ppropertydesc_first :: ppropertydesc_tail*)',
            'pclassdesc_method.INTERFACES = eps',
            'ppropertydesc_first.VISIBILITY = PROPERTY_PRIVATE',
            '~$trace_instance_public(ppropertydesc_first :: ppropertydesc_tail*)',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z_S) = (S,ORDERUNSUPPORTED "Throwable property comparison")',
            'PhpStep: S ~> S_raw',
            'S_raw.COMPLETION = UNSUPPORTED "Throwable property comparison"',
            'S_raw.TODO = ptask_S*',
            r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
            r'S_raw.ARRAYS = S.ARRAYS /\ S_raw.OBJECTTABLES = S.OBJECTTABLES',
            r'S_raw.STORE = S.STORE /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
            'S_raw.EVENTS = S.EVENTS',
            '$tbp_output(S_raw.EVENTS) = $ptascii("B|")',
        ]
    if name == 'method-fields-before-severity':
        rows += field('S', 'n_left', 'data_left', 'DIRECT (PARRAY n_data_left)')
        rows += field('S', 'n_right', 'data_right', 'DIRECT (PARRAY n_data_right)')
        rows += [
            '$trace_visit_inline_pair(S,n_left,n_right)',
            '$throwable_field(S,n_a,"severity") = PINT 9',
            '$throwable_field(S,n_b,"severity") = PINT 1',
            '$entry_lookup(S.ARRAYS[n_data_left].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$entry_lookup(S.ARRAYS[n_data_right].ITEMS,KINT 0) = (DIRECT (PINT 2))',
            '$object_table_at(S.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S.OBJECTTABLES,n_right) = eps',
            '$trace_visit_object_effect(S,n_left,n_right,eps,z_S) = (S,ORDER $(-1))',
        ]
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
            'S_cow = $tbp_next(S_warm)',
            '$lookup(S_cow.ENV,$ptascii("source")) = (n_sourcecv)',
            'S_cow.STORE[n_sourcecv] = DEFINED (PARRAY n_source_cow)',
            'n_source_cow =/= n_data_left',
            '$entry_lookup(S_cow.ARRAYS[n_source_cow].ITEMS,KINT 0) = (DIRECT (PINT 99))',
            '$entry_lookup(S_cow.ARRAYS[n_data_left].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            'S_mutated = $tbp_next(S_cow)',
        ]
        rows += field('S_cow', 'n_left', 'cow_left', 'DIRECT (PARRAY n_data_left)')
        rows += raw('S_mutated', 1)
        rows += ['S_mutated_reverse = $tbp_seek(S_mutated_raw,6000)[.COMPLETION = NORMAL]',
                 'S_equal = $tbp_next(S_mutated_reverse)']
        rows += raw('S_equal', 1)
        return rows + finish('S_equal_raw', name)
    if name == 'method-foreach-cached-tables':
        rows += field('S', 'n_left', 'data_left', 'ALIAS n_live')
        rows += field('S', 'n_right', 'data_right', 'DIRECT (PARRAY n_right_data)')
        rows += [
            '$trace_visit_item_value(S,ALIAS n_live) = (PARRAY n_live_initial)',
            '$lookup(S.ENV,$ptascii("snapshot")) = (n_snapshotcv)',
            'S.STORE[n_snapshotcv] = DEFINED (PARRAY n_live_initial)',
            '$entry_lookup(S.ARRAYS[n_live_initial].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$entry_lookup(S.ARRAYS[n_right_data].ITEMS,KINT 0) = (DIRECT (PINT 2))',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_live) = n_live_owners',
            '$(n_live_owners >= 2)',
        ]
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_mutated = $tbp_next(S_reverse)',
            '$trace_visit_item_value(S_mutated,ALIAS n_live) = (PARRAY n_live_mutated)',
            '$entry_lookup(S_mutated.ARRAYS[n_live_mutated].ITEMS,KINT 0) = (DIRECT (PINT 3))',
            '$lookup(S_mutated.ENV,$ptascii("snapshot")) = (n_snapshotcv_mutated)',
            'S_mutated.STORE[n_snapshotcv_mutated] = DEFINED (PARRAY n_snapshot_mutated)',
            'n_snapshot_mutated =/= n_live_mutated',
            '$entry_lookup(S_mutated.ARRAYS[n_snapshot_mutated].ITEMS,KINT 0) = (DIRECT (PINT 99))',
            'S_equal = $tbp_next(S_mutated)',
            'S_tables = $tbp_next(S_equal)',
            '$object_table_at(S_tables.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_tables.OBJECTTABLES,n_right) = (n_table_right)',
            'n_table_left =/= n_table_right',
            '$aggregate_hash_image(S_tables,n_left,n_table_left)',
            '$aggregate_hash_image(S_tables,n_right,n_table_right)',
            '$object_table_ordinary(S_tables,n_left)',
            '$object_table_ordinary(S_tables,n_right)',
            '$heap_owners($heap_prune($heap_graph(S_tables)),HARRAY n_table_left) = 1',
            '$heap_owners($heap_prune($heap_graph(S_tables)),HARRAY n_table_right) = 1',
            '~$trace_visit_inline_pair(S_tables,n_left,n_right)',
            '$trace_visit_object_image(S_tables,n_left)',
            '$entry_lookup(S_tables.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("data")) = (INDIRECT n_left ($ptascii("data")))',
            '$object_table_item(S_tables,INDIRECT n_left ($ptascii("data"))) = ALIAS n_live',
            '$lookup(S_tables.ENV,$ptascii("viewLeft")) = (n_view_leftcv)',
            'S_tables.STORE[n_view_leftcv] = DEFINED (PARRAY n_view_left)',
            '$entry_lookup(S_tables.ARRAYS[n_view_left].ITEMS,KSTRING $ptascii("data")) = (ALIAS n_live)',
        ]
        rows += raw('S_tables', 0)
        rows += [
            'S_retarget = $tbp_seek(S_tables_raw,6000)[.COMPLETION = NORMAL]',
            '$trace_visit_item_value(S_retarget,ALIAS n_live) = (PARRAY n_live_retarget)',
            '$entry_lookup(S_retarget.ARRAYS[n_live_retarget].ITEMS,KINT 0) = (DIRECT (PINT 4))',
            '$object_table_at(S_retarget.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_retarget.OBJECTTABLES,n_right) = (n_table_right)',
        ]
        rows += raw('S_retarget', 1)
        return rows + finish('S_retarget_raw', name)
    if name == 'method-cycle-before-earlier-field':
        rows += [
            '$effective_method(S,porigin_class,$ptascii("__isset"),|S.CLASSES|) = (pmethoddesc_isset)',
            'pmethoddesc_isset.FUNCTION.SIGNATURE.PARAMETERS = [psparam_isset]',
            'psparam_isset.TYPE = eps',
            '$ppmethod_isset_signature(pmethoddesc_isset.FUNCTION.SIGNATURE)',
            '~$property_magic_method_source(S,pmethoddesc_isset,"__isset")',
            '~$property_empty_isset_source(S,pmethoddesc_isset)',
        ]
        rows += field('S', 'n_left', 'value_left', 'DIRECT (PINT 0)', 'value')
        rows += field('S', 'n_right', 'value_right', 'DIRECT (PINT 0)', 'value')
        rows += field('S', 'n_left', 'next_left', 'DIRECT (POBJECT n_left)', 'next')
        rows += field('S', 'n_right', 'next_right', 'DIRECT (POBJECT n_tail)', 'next')
        rows += field('S', 'n_tail', 'value_tail', 'DIRECT (PINT 1)', 'value')
        rows += [
            'S.OBJECTS[n_tail] = INSTANCE porigin_class',
            '$trace_visit_inline_pair(S,n_left,n_tail)',
            '$trace_visit_object_effect(S,n_left,n_tail,[HOBJECT n_left],z_S) = (S,ORDERRECURSIVE)',
            '$trace_visit_object_effect(S,n_left,n_left,[HOBJECT n_left],z_S) = (S,ORDER 0)',
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
    assert name == 'method-table-count-key-tail'
    rows += field('S', 'n_left', 'data_left', 'DIRECT (PARRAY n_data_left)')
    rows += field('S', 'n_right', 'data_right', 'DIRECT (PARRAY n_data_right)')
    rows += [
        '|S.ARRAYS[n_data_left].ITEMS| = 2',
        '|S.ARRAYS[n_data_right].ITEMS| = 1',
        '$entry_lookup(S.ARRAYS[n_data_left].ITEMS,KSTRING $ptascii("cycle")) = (DIRECT (POBJECT n_left))',
        '$entry_lookup(S.ARRAYS[n_data_right].ITEMS,KSTRING $ptascii("cycle")) = (DIRECT (POBJECT n_right))',
    ]
    rows += raw('S', 1)
    rows += ['S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
             'S_keys = $tbp_next(S_reverse)']
    rows += field('S_keys', 'n_right', 'keys_right', 'DIRECT (PARRAY n_data_keys)')
    rows += [
        '|S_keys.ARRAYS[n_data_keys].ITEMS| = 2',
        '$entry_lookup(S_keys.ARRAYS[n_data_keys].ITEMS,KSTRING $ptascii("cycle")) = eps',
        '$entry_lookup(S_keys.ARRAYS[n_data_keys].ITEMS,KSTRING $ptascii("other")) = (DIRECT (POBJECT n_right))',
        '$object_table_at(S_keys.OBJECTTABLES,n_left) = eps',
        '$object_table_at(S_keys.OBJECTTABLES,n_right) = eps',
        '$trace_visit_inline_pair(S_keys,n_left,n_right)',
        '$trace_visit_object_image(S_keys,n_left)',
    ]
    rows += raw('S_keys', 1)
    return rows + finish('S_keys_raw', name)
