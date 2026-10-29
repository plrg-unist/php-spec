"""Source-reached lazy graph decisions and authentication at visited nodes."""
import base64
import json

from throwable_builtin_previous_protocol import PREFIX as SEEK_PREFIX
from throwable_previous_graph_protocol import raw, trace

PREFIX = SEEK_PREFIX + r'''
dec $tv_without(pnode*, pnode) : pnode*
def $tv_without(eps, pnode) = eps
def $tv_without(pnode :: pnode_tail*, pnode) = $tv_without(pnode_tail*, pnode)
def $tv_without(pnode_head :: pnode_tail*, pnode) = pnode_head :: $tv_without(pnode_tail*, pnode)
  -- if pnode_head =/= pnode
'''


def front(program, path):
    encoded = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $tbp_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tbp_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$throwable_field(S,n_a,"previous") = POBJECT n_p',
        '$throwable_field(S,n_b,"previous") = POBJECT n_q',
        'n_p =/= n_q',
        '$throwable_builtin_previous_pair(S,n_a,n_b,eps)',
        '~$throwable_builtin_previous_trace_pair(S,n_p,n_q)',
        '$throwable_builtin_previous_order(S,n_a,n_b,eps) = ORDERUNSUPPORTED "Throwable property comparison"',
    ]


def captured(node, label, value):
    # These graphs deliberately fail full authentication; trace()'s first four
    # rows bind only the reached canonical frame and direct argument.
    return trace('S', node, label, value)[:4] + [
        '~$trace_property_ref_graph(S,n_trace_' + label + ')',
    ]


def finish(state, output):
    return [
        'S_done = $drive_steps(' + state + ',1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(output) + ')',
    ]


def checks(program, path, name):
    rows = front(program, path)
    if name == 'array-count-skips-cycle':
        rows += captured('n_p', 'p', 'PARRAY n_payload_p')
        rows += captured('n_q', 'q', 'PARRAY n_payload_q')
        rows += [
            '|S.ARRAYS[n_payload_p].ITEMS| = 2',
            '|S.ARRAYS[n_payload_q].ITEMS| = 1',
            '$entry_lookup(S.ARRAYS[n_payload_p].ITEMS,KINT 0) = (DIRECT (PARRAY n_cycle))',
            '$entry_lookup(S.ARRAYS[n_cycle].ITEMS,KSTRING $ptascii("self")) = (ALIAS n_cycle_cell)',
            'S.STORE[n_cycle_cell] = DEFINED (PARRAY n_cycle)',
            '$heap_subset([HARRAY n_cycle,HCELL n_cycle_cell],S.ALLOCATIONS)',
            '$trace_visit_array_effect(S,n_payload_p,n_payload_q,[HARRAY n_payload_p],eps,z) = (S,ORDERUNSUPPORTED "Throwable property comparison")',
            '$trace_visit_array_effect(S,n_payload_p,n_payload_p,[HARRAY n_payload_p],eps,z) = (S,ORDER 0)',
            'S_bad = S[.ALLOCATIONS = $tv_without(S.ALLOCATIONS,HARRAY n_payload_p)]',
            '$trace_visit_array_effect(S_bad,n_payload_p,n_payload_p,eps,eps,z) = (S_bad,ORDERUNSUPPORTED "Throwable property comparison")',
            '$throwable_field(S,n_a,"severity") = PINT 1',
            '$throwable_field(S,n_b,"severity") = PINT 9',
        ]
        rows += raw('S', 1)
        rows += finish('S_raw', 'B|1:-1|W|1:1|')
    elif name == 'object-identity-skips-cycle':
        rows += captured('n_p', 'p', 'POBJECT n_shared')
        rows += captured('n_q', 'q', 'POBJECT n_shared')
        rows += [
            'S.OBJECTS[n_shared] = STDINSTANCE',
            '$objectprops_record_at(S.OBJECTPROPS,n_shared) = (pobjectprops_shared)',
            '$property_slot_at(pobjectprops_shared.SLOTS,$ptascii("self")) = (ppropertyslot_self)',
            'ppropertyslot_self.STATE = PROP_VALUE (DIRECT (POBJECT n_shared))',
            '$object_table_at(S.OBJECTTABLES,n_shared) = eps',
            '$trace_visit_object_effect(S,n_shared,n_shared,[HOBJECT n_shared],eps,z) = (S,ORDER 0)',
            'S_bad = S[.ALLOCATIONS = $tv_without(S.ALLOCATIONS,HOBJECT n_shared)]',
            '$trace_visit_object_effect(S_bad,n_shared,n_shared,eps,eps,z) = (S_bad,ORDERUNSUPPORTED "Throwable property comparison")',
        ]
        rows += raw('S', 0)
        rows += [
            '$object_table_at(S_raw.OBJECTTABLES,n_shared) = eps',
        ]
        rows += finish('S_raw', 'B|0|W|1:0|A|-1|')
    elif name == 'same-nan-cell-before-cycle':
        rows += captured('n_p', 'p', 'PARRAY n_payload_p')
        rows += captured('n_q', 'q', 'PARRAY n_payload_q')
        rows += [
            '$entry_lookup(S.ARRAYS[n_payload_p].ITEMS,KINT 0) = (ALIAS n_nan_cell)',
            '$entry_lookup(S.ARRAYS[n_payload_q].ITEMS,KINT 0) = (ALIAS n_nan_cell)',
            '$trace_visit_item_value(S,ALIAS n_nan_cell) = (PFLOAT n_nan)',
            '$float_decode(n_nan) = NOTNUMBER n_nan',
            'S_undefined = S[.STORE[n_nan_cell] = UNDEFINED]',
            '$trace_visit_item_value(S_undefined,ALIAS n_nan_cell) = eps',
            '$trace_visit_entries_effect(S_undefined,[ENTRY (KINT 0) (ALIAS n_nan_cell)],[ENTRY (KINT 0) (ALIAS n_nan_cell)],eps,eps,z) = (S_undefined,ORDERUNSUPPORTED "Throwable property comparison")',
            'S_unallocated = S[.ALLOCATIONS = $tv_without(S.ALLOCATIONS,HCELL n_nan_cell)]',
            '$trace_visit_item_value(S_unallocated,ALIAS n_nan_cell) = eps',
            '$trace_visit_entries_effect(S_unallocated,[ENTRY (KINT 0) (ALIAS n_nan_cell)],[ENTRY (KINT 0) (ALIAS n_nan_cell)],eps,eps,z) = (S_unallocated,ORDERUNSUPPORTED "Throwable property comparison")',
        ]
        rows += raw('S', 1)
        rows += finish('S_raw', 'B|01:1:1|')
    elif name == 'plain-inline-leaf-skips-cycle':
        rows += captured('n_p', 'p', 'POBJECT n_left')
        rows += captured('n_q', 'q', 'POBJECT n_right')
        rows += [
            'S.OBJECTS[n_left] = INSTANCE porigin_plain',
            'S.OBJECTS[n_right] = INSTANCE porigin_plain',
            '$class_at(S.CLASSES,porigin_plain) = (pclassdesc_plain)',
            '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_plain.NAME)) = (porigin_plain)',
            '$trace_visit_object_image(S,n_left)',
            '$trace_visit_object_image(S,n_right)',
            '$object_table_at(S.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S.OBJECTTABLES,n_right) = eps',
            'S_unpublished = S[.CLASSNAMES = eps]',
            '$trace_visit_object_effect(S_unpublished,n_left,n_left,eps,eps,z) = (S_unpublished,ORDERUNSUPPORTED "Throwable property comparison")',
            '$objectprops_record_at(S.OBJECTPROPS,n_left) = (pobjectprops_left)',
            '$property_slot_at(pobjectprops_left.SLOTS,$ptascii("next")) = (ppropertyslot_next)',
            'ppropertyslot_next.STATE = PROP_VALUE (DIRECT (POBJECT n_left))',
            '$throwable_field(S,n_a,"severity") = PINT 9',
            '$throwable_field(S,n_b,"severity") = PINT 1',
        ]
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,1000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
        ]
        rows += raw('S_warm', -1)
        rows += [
            'S_mutated = $tbp_seek(S_warm_raw,1000)[.COMPLETION = NORMAL]',
            '$object_table_at(S_mutated.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S_mutated.OBJECTTABLES,n_right) = eps',
            '$objectprops_record_at(S_mutated.OBJECTPROPS,n_left) = (pobjectprops_mutated)',
            '$property_slot_at(pobjectprops_mutated.SLOTS,$ptascii("first")) = (ppropertyslot_first)',
            'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (PINT 3))',
        ]
        rows += raw('S_mutated', 1)
        rows += finish('S_mutated_raw', 'B|-1:1|W|1:-1|M|1:-1|')
    else:
        assert name in ('visited-cell-cycle-control', 'active-cycle-before-count-control')
        rows += captured('n_p', 'p', 'POBJECT n_left')
        rows += captured('n_q', 'q', 'POBJECT n_right')
        rows += [
            '$object_table_at(S.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S.OBJECTTABLES,n_right) = eps',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S_effect,ORDERUNSUPPORTED "Throwable property comparison")',
            'S_effect.COMPLETION = NORMAL',
            'n_table_left = |S.ARRAYS|',
            'n_table_right = $(n_table_left + 1)',
            '$object_table_at(S_effect.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_table_right)',
            '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_table_left) = 1',
            '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_table_right) = 1',
        ]
        if name == 'active-cycle-before-count-control':
            rows += [
                '$lookup(S.ENV,$ptascii("other")) = (n_othercv)',
                'S.STORE[n_othercv] = DEFINED (POBJECT n_other)',
                '$object_table_at(S.OBJECTTABLES,n_other) = eps',
                'n_table_other = $(n_table_left + 2)',
                '$object_table_at(S_effect.OBJECTTABLES,n_other) = (n_table_other)',
                '$aggregate_table_count(S_effect.ARRAYS[n_table_left].ITEMS) = 1',
                '$aggregate_table_count(S_effect.ARRAYS[n_table_other].ITEMS) = 2',
                '$trace_visit_array_effect(S_effect,n_table_left,n_table_other,[HARRAY n_table_left],eps,z) = (S_effect,ORDERUNSUPPORTED "Throwable property comparison")',
                '|S_effect.ARRAYS| = $(|S.ARRAYS| + 3)',
            ]
        else:
            rows += [
                '|S_effect.ARRAYS| = $(|S.ARRAYS| + 2)',
                '$entry_lookup(S_effect.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("p")) = (ALIAS n_live_left)',
                '$entry_lookup(S_effect.ARRAYS[n_table_right].ITEMS,KSTRING $ptascii("p")) = (ALIAS n_live_right)',
                'S_effect.STORE[n_live_left] = DEFINED (POBJECT n_left)',
                'S_effect.STORE[n_live_right] = DEFINED (POBJECT n_right)',
            ]
        rows += [
            'PhpStep: S ~> S_raw',
            'S_raw.COMPLETION = UNSUPPORTED "Throwable property comparison"',
            r'S_raw.ARRAYS = S_effect.ARRAYS /\ S_raw.OBJECTTABLES = S_effect.OBJECTTABLES',
            r'S_raw.OBJECTPROPS = S_effect.OBJECTPROPS /\ S_raw.STORE = S_effect.STORE',
            'S_raw.ALLOCATIONS = S_effect.ALLOCATIONS',
            'S_raw.EVENTS = S.EVENTS',
            '$tbp_output(S_raw.EVENTS) = $ptascii("B|")',
            '$aggregate_compare_seen(S_raw) = eps',
            '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
            'S_one = $drive_steps(S,1)',
            'S_one.COMPLETION = UNSUPPORTED "Throwable property comparison"',
            'S_one.OBJECTTABLES = S_effect.OBJECTTABLES',
        ]
    return rows
