"""Reached source-parent authority, inherited physical slots and live owners."""
import json
import re

from throwable_interface_protocol import field, front
from throwable_previous_graph_protocol import raw, trace
from throwable_trace_recursion_protocol import error_rows
from throwable_builtin_previous_protocol import PREFIX

EXPECTED = {
    'inherited-physical-slots-before-severity': 'B|-1:1|W|1:-1|P|1|M|-1|L|-1|S|1|T|-1:1|',
    'inherited-interface-alias-tables': 'B|-1:1|M|1:99:3|E|1:0|H|1:0|R|4:2:1|D|1|',
    'inherited-cycle-no-traps': 'B|-1:1|W|1:-1|C|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|I|0:1|R|-1:1|',
    'long-inherited-public-path': 'B|-1:1|W|1:-1|E|0|',
}


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def image():
    return [
        'S.OBJECTS[n_left] = INSTANCE porigin_leaf',
        'S.OBJECTS[n_right] = INSTANCE porigin_leaf',
        '$class_at(S.CLASSES,porigin_leaf) = (pclassdesc_leaf)',
        'pclassdesc_leaf.PARENT =/= eps',
        '$trace_visit_interfaces(S,pclassdesc_leaf)',
        '$trace_visit_parent_path(S,pclassdesc_leaf,eps)',
        '~$trace_visit_parent_path(S,pclassdesc_leaf,[porigin_leaf])',
        '~$trace_instance_class(S,n_left)',
        '$trace_visit_object_header(S,n_left)',
        '$trace_visit_object_header(S,n_right)',
        '$trace_visit_object_image(S,n_left)',
        '$trace_visit_object_image(S,n_right)',
        '$trace_visit_inline_pair(S,n_left,n_right)',
    ]


def chain():
    return [
        'pclassdesc_leaf.PARENT = ($ptascii("Middle157"))',
        '$class_link_at(S.LINKEDPARENTS,porigin_leaf) = (SOURCE_PARENT porigin_middle)',
        '$class_at(S.CLASSES,porigin_middle) = (pclassdesc_middle)',
        'pclassdesc_middle.PARENT = ($ptascii("Base157"))',
        '$class_link_at(S.LINKEDPARENTS,porigin_middle) = (SOURCE_PARENT porigin_base)',
        '$class_at(S.CLASSES,porigin_base) = (pclassdesc_base)',
        'pclassdesc_base.PARENT = eps',
        '$class_link_at(S.LINKEDPARENTS,porigin_base) = eps',
        '$pil_precedes(S.CLASSNAMES,porigin_base,porigin_middle)',
        '$pil_precedes(S.CLASSNAMES,porigin_middle,porigin_leaf)',
        '$trace_visit_parent_precedes(S.LINKEDPARENTS,porigin_middle,porigin_leaf)',
        '$trace_visit_parent_path(S,pclassdesc_middle,eps)',
        '$trace_visit_parent_path(S,pclassdesc_base,eps)',
    ]


def invalid_parents():
    return [
        'S.CLASSES = [pclassdesc_base,pclassdesc_middle,pclassdesc_leaf]',
        'S.LINKEDPARENTS = [CLASSLINK porigin_middle (SOURCE_PARENT porigin_base),CLASSLINK porigin_leaf (SOURCE_PARENT porigin_middle)]',
        'S_missing = S[.LINKEDPARENTS = eps]',
        '~$trace_visit_parent_path(S_missing,pclassdesc_leaf,eps)',
        '~$trace_visit_object_image(S_missing,n_left)',
        '$trace_visit_object_effect(S_missing,n_left,n_right,eps,z_S) = (S_missing,ORDERUNSUPPORTED "Throwable property comparison")',
        '$trace_visit_object_effect(S_missing,n_left,n_left,[HOBJECT n_left],z_S) = (S_missing,ORDER 0)',
        'S_wrong = S[.LINKEDPARENTS = [CLASSLINK porigin_middle (SOURCE_PARENT porigin_base),CLASSLINK porigin_leaf (SOURCE_PARENT porigin_base)]]',
        '~$trace_visit_parent_path(S_wrong,pclassdesc_leaf,eps)',
        'S_reordered = S[.LINKEDPARENTS = [CLASSLINK porigin_leaf (SOURCE_PARENT porigin_middle),CLASSLINK porigin_middle (SOURCE_PARENT porigin_base)]]',
        '~$trace_visit_parent_precedes(S_reordered.LINKEDPARENTS,porigin_middle,porigin_leaf)',
        '~$trace_visit_parent_path(S_reordered,pclassdesc_leaf,eps)',
        'S_names = S[.CLASSNAMES = [($ptlc(pclassdesc_leaf.NAME),porigin_leaf),($ptlc(pclassdesc_middle.NAME),porigin_middle),($ptlc(pclassdesc_base.NAME),porigin_base)]]',
        '~$trace_visit_parent_path(S_names,pclassdesc_leaf,eps)',
        'S_final = S[.CLASSES = [pclassdesc_base[.FINAL = true],pclassdesc_middle,pclassdesc_leaf]]',
        '~$trace_visit_parent_path(S_final,pclassdesc_leaf,eps)',
        'S_readonly = S[.CLASSES = [pclassdesc_base[.READONLY = true],pclassdesc_middle,pclassdesc_leaf]]',
        '~$trace_visit_parent_path(S_readonly,pclassdesc_leaf,eps)',
        'S_terminal = S[.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK porigin_base (SOURCE_PARENT porigin_leaf)]]',
        '~$trace_visit_parent_path(S_terminal,pclassdesc_leaf,eps)',
        'S_internal = S[.LINKEDPARENTS = [CLASSLINK porigin_middle (SOURCE_PARENT porigin_base),CLASSLINK porigin_leaf STDCLASS_PARENT]]',
        '~$trace_visit_parent_path(S_internal,pclassdesc_leaf,eps)',
        'pclassdesc_self = pclassdesc_leaf[.PARENT = (pclassdesc_leaf.NAME)]',
        'S_self = S[.CLASSES = [pclassdesc_base,pclassdesc_middle,pclassdesc_self]][.LINKEDPARENTS = [CLASSLINK porigin_middle (SOURCE_PARENT porigin_base),CLASSLINK porigin_leaf (SOURCE_PARENT porigin_leaf)]]',
        '~$trace_visit_parent_path(S_self,pclassdesc_self,eps)',
        '~$trace_visit_object_image(S_self,n_left)',
        '~$trace_visit_parent_precedes(S_self.LINKEDPARENTS,porigin_leaf,porigin_leaf)',
        'S_cycle = S[.CLASSES = [pclassdesc_base,pclassdesc_middle[.PARENT = (pclassdesc_leaf.NAME)],pclassdesc_leaf]][.LINKEDPARENTS = [CLASSLINK porigin_middle (SOURCE_PARENT porigin_leaf),CLASSLINK porigin_leaf (SOURCE_PARENT porigin_middle)]]',
        '~$trace_visit_parent_path(S_cycle,pclassdesc_leaf,eps)',
        '~$trace_visit_object_image(S_cycle,n_left)',
        'S_unrelated = S[.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK (PORIGIN 999 eps) STDCLASS_PARENT]]',
        '~$class_links_valid(S_unrelated)',
        '$trace_visit_parent_path(S_unrelated,pclassdesc_leaf,eps)',
        '$trace_visit_object_image(S_unrelated,n_left)',
    ]


def checks(program, path, name):
    rows = front(program, path)
    rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
    rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
    rows += image()
    if name != 'long-inherited-public-path':
        rows += chain()
    if name == 'inherited-physical-slots-before-severity':
        rows += invalid_parents()
        rows += [
            'pclassdesc_base.METHODS = [pmethoddesc_get]',
            'pmethoddesc_get.NAME = $ptascii("__get")',
            'pmethoddesc_get.FUNCTION.SIGNATURE.PARAMETERS = [psparam_get]',
            'psparam_get.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
            '$ppmethod_get_declaration_signature(pmethoddesc_get.FUNCTION.SIGNATURE)',
            '~$ppmethod_get_signature(pmethoddesc_get.FUNCTION.SIGNATURE)',
            '~$ppmethod_get_declaration_signature(pmethoddesc_get.FUNCTION.SIGNATURE[.PARAMETERS = [psparam_get[.BYREF = true]]])',
            '~$ppmethod_get_declaration_signature(pmethoddesc_get.FUNCTION.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]])',
            '$property_layout(S,porigin_leaf,|S.CLASSES|) = (ppropertydesc_first :: ppropertydesc_base_tail :: ppropertydesc_middle :: ppropertydesc_leaf :: eps)',
            'ppropertydesc_first.NAME = $ptascii("first")',
            'ppropertydesc_base_tail.NAME = $ptascii("baseTail")',
            'ppropertydesc_middle.NAME = $ptascii("middle")',
            'ppropertydesc_leaf.NAME = $ptascii("leaf")',
            '$property_declaring_name(S.CLASSES,ppropertydesc_first.ORIGIN) = $ptascii("Middle157")',
            '$property_declaring_name(S.CLASSES,ppropertydesc_base_tail.ORIGIN) = $ptascii("Base157")',
            '$property_info_layout(S,porigin_leaf,|S.CLASSES|) = (ppropertydesc_info :: ppropertydesc_info_tail*)',
            'ppropertydesc_info.NAME = $ptascii("leaf")',
            '$throwable_field(S,n_a,"severity") = PINT 9',
            '$throwable_field(S,n_b,"severity") = PINT 1',
        ]
        rows += field('S', 'n_left', 'first_left', 'DIRECT (PINT 1)', 'first')
        rows += ['ppropertyslot_first_left.DECL = (ppropertydesc_first.ORIGIN)']
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
            'S_parent = $tbp_seek(S_warm_raw,6000)[.COMPLETION = NORMAL]',
            '$value_order_effect(S_parent,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_parent,ORDER 1)',
            'S_middle = $tbp_next(S_parent)',
            '$value_order_effect(S_middle,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_middle,ORDER $(-1))',
            'S_leaf = $tbp_next(S_middle)',
            '$value_order_effect(S_leaf,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_leaf,ORDER $(-1))',
            'S_severity = $tbp_next(S_leaf)',
            '$value_order_effect(S_severity,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_severity,ORDER 1)',
            'S_tables = $tbp_next(S_severity)',
            '$object_table_at(S_tables.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_tables.OBJECTTABLES,n_right) = (n_table_right)',
            '$aggregate_hash_image(S_tables,n_left,n_table_left)',
            '$aggregate_hash_image(S_tables,n_right,n_table_right)',
            '~$trace_visit_inline_pair(S_tables,n_left,n_right)',
            '$entry_lookup(S_tables.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("first")) = (INDIRECT n_left ($ptascii("first")))',
        ]
        rows += raw('S_tables', -1)
        return rows + finish('S_tables_raw', name)
    if name == 'inherited-interface-alias-tables':
        rows += [
            'pclassdesc_leaf.INTERFACES = eps',
            'pclassdesc_base.INTERFACES = [$ptascii("Tag157")]',
            '$trace_visit_interfaces(S,pclassdesc_base)',
            'S_missing_interfaces = S[.LINKEDINTERFACES = eps]',
            '$trace_visit_interfaces(S_missing_interfaces,pclassdesc_leaf)',
            '~$trace_visit_parent_path(S_missing_interfaces,pclassdesc_leaf,eps)',
            '~$trace_visit_object_image(S_missing_interfaces,n_left)',
        ]
        rows += field('S', 'n_left', 'data_left', 'ALIAS n_live')
        rows += field('S', 'n_right', 'data_right', 'DIRECT (PARRAY n_right_data)')
        rows += [
            '$trace_visit_item_value(S,ALIAS n_live) = (PARRAY n_live_initial)',
            '$lookup(S.ENV,$ptascii("snapshot")) = (n_snapshotcv)',
            'S.STORE[n_snapshotcv] = DEFINED (PARRAY n_live_initial)',
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
            '$lookup(S_tables.ENV,$ptascii("left")) = (n_leftcv)',
            'S_tables.STORE[n_leftcv] = DEFINED PNULL',
            '(HOBJECT n_left) <- S_tables.ALLOCATIONS',
            '$object_table_at(S_tables.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_tables.OBJECTTABLES,n_right) = (n_table_right)',
            '$aggregate_hash_image(S_tables,n_left,n_table_left)',
            '$aggregate_hash_image(S_tables,n_right,n_table_right)',
            '$entry_lookup(S_tables.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("data")) = (INDIRECT n_left ($ptascii("data")))',
            '$object_table_item(S_tables,INDIRECT n_left ($ptascii("data"))) = ALIAS n_live',
            '$lookup(S_tables.ENV,$ptascii("viewLeft")) = (n_viewcv)',
            'S_tables.STORE[n_viewcv] = DEFINED (PARRAY n_view)',
            '$entry_lookup(S_tables.ARRAYS[n_view].ITEMS,KSTRING $ptascii("data")) = (ALIAS n_live)',
        ]
        rows += raw('S_tables', 0)
        rows += [
            'S_retarget = $tbp_seek(S_tables_raw,6000)[.COMPLETION = NORMAL]',
            '$trace_visit_item_value(S_retarget,ALIAS n_live) = (PARRAY n_live_retarget)',
            '$entry_lookup(S_retarget.ARRAYS[n_live_retarget].ITEMS,KINT 0) = (DIRECT (PINT 4))',
        ]
        rows += raw('S_retarget', 1)
        return rows + finish('S_retarget_raw', name) + ['~((HOBJECT n_left) <- S_done.ALLOCATIONS)']
    if name == 'inherited-cycle-no-traps':
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
        rows += [re.sub(r'\bS\b', 'S_cycle', re.sub(r'\bS_', 'S_cycle_', row)) for row in error_rows()]
        rows += ['S_cycle_error.ARRAYS[n_error_trace].ITEMS = eps']
        return rows + finish('S_cycle_one[.COMPLETION = NORMAL]', name)
    assert name == 'long-inherited-public-path'
    rows += [
        '|S.CLASSES| = 19',
        'pclassdesc_leaf.NAME = $ptascii("Parent157_18")',
        'pclassdesc_leaf.PROPERTIES = eps',
        '$property_layout(S,porigin_leaf,|S.CLASSES|) = [ppropertydesc_root]',
        '$property_declaring_name(S.CLASSES,ppropertydesc_root.ORIGIN) = $ptascii("Parent157_0")',
    ]
    rows += field('S', 'n_left', 'long_left', 'DIRECT (PINT 1)', 'value')
    rows += ['ppropertyslot_long_left.DECL = (ppropertydesc_root.ORIGIN)']
    rows += raw('S', -1)
    rows += [
        'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
        'S_warm = $tbp_next(S_reverse)',
        '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
        '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
        'preqbytes_warm =/= eps',
        'S_equal = $tbp_next(S_warm)',
    ]
    rows += raw('S_equal', 0)
    return rows + finish('S_equal_raw', name)
