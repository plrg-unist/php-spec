"""Reached local interface authority, physical fields and skipped callbacks."""
import base64
import json

from throwable_builtin_previous_protocol import PREFIX
from throwable_previous_graph_protocol import raw, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'stringable-fields-before-severity': 'B|-1:1|W|1:-1|C|99:1:-1|M|1:-1|E|1|',
    'source-interface-alias-tables': 'B|-1:1|M|1:99:3|E|1:0|T|0|R|4:2:1|',
    'stringable-cycle-no-cast': 'B|-1:1|W|1:-1|C|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|I|0:1|R|-1:1|',
    'interface-count-key-class-skips': 'C|1:-1|K|1:1|W|1:1|A|1|D|1:1|E|0:-1|',
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
        r'$throwable_builtin_previous_chain_valid(S,n_a,eps) /\ $throwable_builtin_previous_chain_valid(S,n_b,eps)',
        '$throwable_builtin_previous_order(S,n_a,n_b,eps) = ORDERUNSUPPORTED "Throwable property comparison"',
    ]


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def interface_pair(state='S'):
    return [
        state + '.OBJECTS[n_left] = INSTANCE porigin_class',
        state + '.OBJECTS[n_right] = INSTANCE porigin_class',
        '$class_at(' + state + '.CLASSES,porigin_class) = (pclassdesc_interface_owner)',
        'pclassdesc_interface_owner.INTERFACES =/= eps',
        'pclassdesc_interface_owner.PARENT = eps',
        '$pil_at(' + state + '.LINKEDINTERFACES,porigin_class) = (PILTARGETS pilref_targets*)',
        '$pil_unique_names(pclassdesc_interface_owner.INTERFACES,eps)',
        '$pil_targets_valid(' + state + ',pclassdesc_interface_owner.INTERFACES,pilref_targets*)',
        '$pil_targets_ordered(' + state + ',porigin_class,pilref_targets*)',
        '$trace_visit_interfaces(' + state + ',pclassdesc_interface_owner)',
        '~$trace_instance_class(' + state + ',n_left)',
        '$trace_visit_object_header(' + state + ',n_left)',
        '$trace_visit_object_header(' + state + ',n_right)',
        '$trace_visit_object_image(' + state + ',n_left)',
        '$trace_visit_object_image(' + state + ',n_right)',
    ]


def field(state, node, label, item, name='data'):
    return [
        '$objectprops_record_at(' + state + '.OBJECTPROPS,' + node + ') = (pobjectprops_' + label + ')',
        '$property_slot_at(pobjectprops_' + label + '.SLOTS,$ptascii(' + json.dumps(name) + ')) = (ppropertyslot_' + label + ')',
        'ppropertyslot_' + label + '.STATE = PROP_VALUE (' + item + ')',
    ]


def checks(program, path, name):
    rows = front(program, path)
    if name == 'source-interface-alias-tables':
        rows += trace('S', 'n_a', 'a', 'POBJECT n_p')[:4]
        rows += trace('S', 'n_b', 'b', 'POBJECT n_q')[:4]
        rows += trace('S', 'n_p', 'p', 'POBJECT n_left')[:4]
        rows += trace('S', 'n_q', 'q', 'POBJECT n_right')[:4]
    else:
        rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
        rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
    rows += interface_pair()
    if name in ('stringable-fields-before-severity', 'stringable-cycle-no-cast'):
        rows += ['pilref_targets* = [PILBUILTIN $ptascii("Stringable")]']
    else:
        target = 'Tag156' if name == 'source-interface-alias-tables' else 'Marker156'
        rows += [
            'pilref_targets* = [PILSOURCE ($ptascii("' + target + '")) porigin_interface]',
            '$class_at(S.CLASSES,porigin_interface) = (pclassdesc_interface)',
            'pclassdesc_interface.KIND = "interface"',
            '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_interface.NAME)) = (porigin_interface)',
        ]
    if name == 'stringable-fields-before-severity':
        rows += [
            'S_missing = S[.LINKEDINTERFACES = eps]',
            '~$trace_visit_interfaces(S_missing,pclassdesc_interface_owner)',
            '$trace_visit_object_header(S_missing,n_left)',
            '~$trace_visit_object_image(S_missing,n_left)',
            '$trace_visit_object_effect(S_missing,n_left,n_right,eps,z_S) = (S_missing,ORDERUNSUPPORTED "Throwable property comparison")',
            '$trace_visit_object_effect(S_missing,n_left,n_left,[HOBJECT n_left],z_S) = (S_missing,ORDER 0)',
        ]
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
    if name == 'source-interface-alias-tables':
        rows += [
            'S_wrong = S[.LINKEDINTERFACES = [{OWNER porigin_class, TARGETS [PILBUILTIN $ptascii("Stringable")]}]]',
            '~$trace_visit_interfaces(S_wrong,pclassdesc_interface_owner)',
            'S_reordered = S[.CLASSNAMES = [($ptlc(pclassdesc_interface_owner.NAME),porigin_class),($ptlc(pclassdesc_interface.NAME),porigin_interface)]]',
            '$trace_visit_object_header(S_reordered,n_left)',
            '~$pil_targets_ordered(S_reordered,porigin_class,pilref_targets*)',
            '~$trace_visit_interfaces(S_reordered,pclassdesc_interface_owner)',
            '$trace_visit_object_effect(S_reordered,n_left,n_right,eps,z_S) = (S_reordered,ORDERUNSUPPORTED "Throwable property comparison")',
        ]
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
    if name == 'stringable-cycle-no-cast':
        rows += field('S', 'n_left', 'value_left', 'DIRECT (PINT 1)', 'value')
        rows += field('S', 'n_right', 'value_right', 'DIRECT (PINT 2)', 'value')
        rows += field('S', 'n_left', 'next_left', 'DIRECT (POBJECT n_left)', 'next')
        rows += field('S', 'n_right', 'next_right', 'DIRECT (POBJECT n_right)', 'next')
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
        ]
        rows += raw('S_warm', -1)
        rows += [
            'S_cycle = $tbp_seek(S_warm_raw,6000)[.COMPLETION = NORMAL]',
            '$trace_visit_object_effect(S_cycle,n_left,n_right,[HOBJECT n_left],z_S) = (S_cycle,ORDERRECURSIVE)',
            '$trace_visit_object_effect(S_cycle,n_left,n_left,[HOBJECT n_left],z_S) = (S_cycle,ORDER 0)',
            'S_cycle_effect = S_cycle',
            '$value_order_effect(S_cycle,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_cycle_effect,ORDERRECURSIVE)',
            'pbin = SPACESHIP',
            'S_cycle.TODO = (BINARY_RIGHT pbin poperand z) :: ptask_cycle*',
            '$lookup(S_cycle.ENV,$ptascii("hold")) = (n_hold)',
            'S_cycle.STORE[n_hold] = DEFINED pvalue_hold',
            '$string_plain(pvalue_hold) = PSTRING $ptascii("hold")',
        ]
        import re
        rows += [re.sub(r'\bS\b', 'S_cycle', re.sub(r'\bS_', 'S_cycle_', row)) for row in error_rows()]
        rows += ['S_cycle_error.ARRAYS[n_error_trace].ITEMS = eps']
        return rows + finish('S_cycle_one[.COMPLETION = NORMAL]', name)
    assert name == 'interface-count-key-class-skips'
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
        '$object_table_at(S_keys.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(S_keys.OBJECTTABLES,n_right) = (n_table_right)',
        '$aggregate_hash_image(S_keys,n_left,n_table_left)',
        '$aggregate_hash_image(S_keys,n_right,n_table_right)',
    ]
    rows += raw('S_keys', 1)
    rows += [
        'S_keys_reverse = $tbp_seek(S_keys_raw,6000)[.COMPLETION = NORMAL]',
        'S_warm = $tbp_next(S_keys_reverse)',
        'S_array = $tbp_next(S_warm)',
        'S_different = $tbp_next(S_array)',
        '$lookup(S_different.ENV,$ptascii("foreign")) = (n_foreigncv)',
        'S_different.STORE[n_foreigncv] = DEFINED (POBJECT n_foreign)',
        '~$trace_object_same_class(S_different,n_left,n_foreign)',
        'S_different_bad = S_different[.LINKEDINTERFACES = eps]',
        '$trace_visit_object_header(S_different_bad,n_left)',
        '$trace_visit_object_header(S_different_bad,n_foreign)',
        '$trace_visit_object_effect(S_different_bad,n_left,n_foreign,[HOBJECT n_left],z_S) = (S_different_bad,ORDER 1)',
    ]
    return rows + finish('S_different', name)
