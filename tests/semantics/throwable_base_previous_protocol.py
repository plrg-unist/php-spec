"""Reached linked-base slot order, finite path guards and physical effects."""
import base64
import json

from throwable_builtin_previous_protocol import PREFIX
from throwable_previous_graph_protocol import raw, tables, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'root-trace-before-link-code': 'L|0:1|B|-1:1|P|1|W|1:1|O|1:9|A|1|',
    'previous-before-child-severity': 'T|-1:1|P|1|W|1:1|S|1:-1|',
    'linked-array-error-before-previous': 'W|1|B|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|R|1:0:0|M|1:-1|',
    'equal-four-table-continuation': 'E|0:1|A|-1|M|-1:1|N|-1|W|1:-1|Q|0:-1|',
}


def object_raw(state, result, effect=None, left='n_a', right='n_b'):
    return [row.replace('POBJECT n_a', 'POBJECT ' + left)
               .replace('POBJECT n_b', 'POBJECT ' + right)
            for row in raw(state, result, effect)]


def front(program, path, name):
    encoded = json.dumps(base64.b64encode(str(path).encode()).decode())
    rows = [
        'S_initial = $php_run(' + program + ',0,' + encoded + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_first = $tbp_seek(S_initial[.COMPLETION = NORMAL],6000)',
        '$tbp_stage(S_first)',
    ]
    if name == 'root-trace-before-link-code':
        rows += [
            'S_legacy = S_first[.COMPLETION = NORMAL]',
            '$lookup(S_legacy.ENV,$ptascii("legacyA")) = (n_legacy_acv)',
            '$lookup(S_legacy.ENV,$ptascii("legacyB")) = (n_legacy_bcv)',
            'S_legacy.STORE[n_legacy_acv] = DEFINED (POBJECT n_legacy_a)',
            'S_legacy.STORE[n_legacy_bcv] = DEFINED (POBJECT n_legacy_b)',
            '$throwable_previous_pair(S_legacy,n_legacy_a,n_legacy_b)',
        ]
        rows += object_raw('S_legacy', 0, left='n_legacy_a', right='n_legacy_b')
        rows += ['S_found = $tbp_seek(S_legacy_raw,6000)']
    else:
        rows += ['S_found = S_first']
    kind = 'Exception' if name in ('root-trace-before-link-code', 'linked-array-error-before-previous') else 'Error'
    rows += [
        '$tbp_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (BINARY_RIGHT SPACESHIP poperand_S z_S) :: ptask_S*',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$string_compare_values(S,poperand_S,S.RESULT,z_S) = ((S_read,POBJECT n_a,POBJECT n_b))',
        'S.OBJECTS[n_a] = THROWABLE pthrowable_a',
        'S.OBJECTS[n_b] = THROWABLE pthrowable_b',
        'pthrowable_a.KIND = ' + json.dumps(kind),
        'pthrowable_b.KIND = pthrowable_a.KIND',
        '$throwable_field(S,n_a,"previous") = POBJECT n_p',
        '$throwable_field(S,n_b,"previous") = POBJECT n_q',
        'n_p =/= n_q',
        r'$throwable_builtin_previous_chain_valid(S,n_a,eps) /\ $throwable_builtin_previous_chain_valid(S,n_b,eps)',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b,HOBJECT n_p,HOBJECT n_q],S.ALLOCATIONS)',
        '~$throwable_builtin_previous_pair(S,n_a,n_b,eps)',
    ]
    return rows


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def checks(program, path, name):
    rows = front(program, path, name)
    if name == 'root-trace-before-link-code':
        rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
        rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
        rows += [
            '$throwable_field(S,n_p,"code") = PINT 9',
            '$throwable_field(S,n_q,"code") = PINT 1',
            '$entry_lookup($trace_object_current_entries(S,n_left),KSTRING $ptascii("value")) = (DIRECT (PINT 1))',
            '$entry_lookup($trace_object_current_entries(S,n_right),KSTRING $ptascii("value")) = (DIRECT (PINT 2))',
            'S_marked = $objectprops_mark(S,n_p)',
            '$throwable_builtin_previous_node_valid(S_marked,n_a)',
            '~$throwable_builtin_previous_chain_valid(S_marked,n_a,eps)',
            '$throwable_comparison_fallback_effect(S_marked,n_a,n_b,eps,z_S) = (S_marked[.COMPLETION = UNSUPPORTED "Throwable property comparison"],ORDER 0)',
            'S_cycle = $throwable_set_previous_id(S,n_p,(n_a))',
            r'$throwable_builtin_previous_node_valid(S_cycle,n_a) /\ $throwable_builtin_previous_node_valid(S_cycle,n_p)',
            '~$throwable_builtin_previous_chain_valid(S_cycle,n_a,eps)',
            '$throwable_comparison_fallback_effect(S_cycle,n_a,n_b,eps,z_S) = (S_cycle[.COMPLETION = UNSUPPORTED "Throwable property comparison"],ORDER 0)',
            '$throwable_comparison_fallback_effect(S,n_a,n_b,eps,z_S) = (S_effect,ORDER $(-1))',
        ]
        rows += tables()
        rows += object_raw('S', -1, 'S_effect')
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_previous = $tbp_next(S_reverse)',
            '$entry_lookup($trace_object_current_entries(S_previous,n_left),KSTRING $ptascii("value")) = (DIRECT (PINT 2))',
            '$entry_lookup($trace_object_current_entries(S_previous,n_right),KSTRING $ptascii("value")) = (DIRECT (PINT 2))',
        ]
        rows += object_raw('S_previous', 1)
        return rows + finish('S_previous_raw', name)
    if name == 'previous-before-child-severity':
        rows += trace('S', 'n_p', 'p', 'POBJECT n_left')[:4]
        rows += trace('S', 'n_q', 'q', 'POBJECT n_right')[:4]
        rows += [
            '$throwable_field(S,n_p,"severity") = PINT 1',
            '$throwable_field(S,n_q,"severity") = PINT 9',
            '$throwable_field(S,n_p,"previous") = POBJECT n_deep_left',
            '$throwable_field(S,n_q,"previous") = POBJECT n_deep_right',
            '$throwable_field(S,n_deep_left,"code") = PINT 9',
            '$throwable_field(S,n_deep_right,"code") = PINT 1',
            '$throwable_comparison_fallback_effect(S,n_a,n_b,eps,z_S) = (S_effect,ORDER $(-1))',
        ]
        rows += tables()
        rows += object_raw('S', -1, 'S_effect')
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_previous = $tbp_next(S_reverse)',
            '$entry_lookup($trace_object_current_entries(S_previous,n_left),KSTRING $ptascii("value")) = (DIRECT (PINT 2))',
            '$entry_lookup($trace_object_current_entries(S_previous,n_right),KSTRING $ptascii("value")) = (DIRECT (PINT 2))',
        ]
        rows += object_raw('S_previous', 1)
        rows += [
            'S_warm = $tbp_seek(S_previous_raw,6000)[.COMPLETION = NORMAL]',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
            'S_severity = $tbp_seek($drive_steps(S_warm,1)[.COMPLETION = NORMAL],6000)[.COMPLETION = NORMAL]',
            '$lookup(S_severity.ENV,$ptascii("c")) = (n_ccv)',
            '$lookup(S_severity.ENV,$ptascii("d")) = (n_dcv)',
            'S_severity.STORE[n_ccv] = DEFINED (POBJECT n_c)',
            'S_severity.STORE[n_dcv] = DEFINED (POBJECT n_d)',
            '$throwable_field(S_severity,n_c,"previous") = POBJECT n_u',
            '$throwable_field(S_severity,n_d,"previous") = POBJECT n_v',
            '$throwable_field(S_severity,n_u,"severity") = PINT 9',
            '$throwable_field(S_severity,n_v,"severity") = PINT 1',
            '$throwable_field(S_severity,n_u,"previous") = POBJECT n_deep_left',
            '$throwable_field(S_severity,n_v,"previous") = POBJECT n_deep_left',
            '$lookup(S_severity.ENV,$ptascii("shared")) = (n_sharedcv)',
            'S_severity.STORE[n_sharedcv] = DEFINED (POBJECT n_shared)',
            '$entry_lookup($trace_object_current_entries(S_severity,n_shared),KSTRING $ptascii("next")) = (DIRECT (POBJECT n_shared))',
            '$object_table_at(S_severity.OBJECTTABLES,n_shared) = eps',
        ]
        rows += trace('S_severity', 'n_u', 'u', 'POBJECT n_shared')[:4]
        rows += trace('S_severity', 'n_v', 'v', 'POBJECT n_shared')[:4]
        rows += object_raw('S_severity', 1, left='n_c', right='n_d')
        return rows + finish('S_severity_raw', name)
    if name == 'linked-array-error-before-previous':
        rows += trace('S', 'n_a', 'a', 'PARRAY n_payload_a')[:4]
        rows += trace('S', 'n_b', 'b', 'PARRAY n_payload_b')[:4]
        rows += [
            '$throwable_field(S,n_p,"code") = PINT 9',
            '$throwable_field(S,n_q,"code") = PINT 1',
            '$throwable_field(S,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
            '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KSTRING $ptascii("next")) = (ALIAS n_live_a)',
            '$entry_lookup(S.ARRAYS[n_payload_b].ITEMS,KSTRING $ptascii("next")) = (ALIAS n_live_b)',
            'S.STORE[n_live_a] = DEFINED (PARRAY n_payload_a)',
            'S.STORE[n_live_b] = DEFINED (PARRAY n_tail)',
            '|S.ARRAYS[n_payload_a].ITEMS| = 1',
            '|S.ARRAYS[n_tail].ITEMS| = 2',
            '$heap_subset([HCELL n_live_a,HCELL n_live_b,HARRAY n_payload_a,HARRAY n_payload_b,HARRAY n_tail],S.ALLOCATIONS)',
            '$trace_visit_array_effect(S,n_payload_a,n_tail,[HARRAY n_payload_a],z_S) = (S,ORDERRECURSIVE)',
            '$trace_visit_array_effect(S,n_tail,n_payload_a,eps,z_S) = (S,ORDER 1)',
            'S_effect = S',
            '$throwable_comparison_fallback_effect(S,n_a,n_b,eps,z_S) = (S_effect,ORDERRECURSIVE)',
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
    assert name == 'equal-four-table-continuation'
    pairs = [('n_a', 'root_left'), ('n_b', 'root_right'),
             ('n_p', 'child_left'), ('n_q', 'child_right')]
    for node, label in pairs:
        rows += trace('S', node, label, 'POBJECT n_' + label)[:4]
    rows += [
        '$heap_unique([HOBJECT n_root_left,HOBJECT n_root_right,HOBJECT n_child_left,HOBJECT n_child_right])',
        '$heap_subset([HOBJECT n_root_left,HOBJECT n_root_right,HOBJECT n_child_left,HOBJECT n_child_right],S.ALLOCATIONS)',
        '$throwable_comparison_fallback_effect(S,n_a,n_b,eps,z_S) = (S_effect,ORDER 0)',
        '|S_effect.ARRAYS| = $(|S.ARRAYS| + 4)',
        'n_table_root_left = |S.ARRAYS|',
        'n_table_root_right = $(n_table_root_left + 1)',
        'n_table_child_left = $(n_table_root_left + 2)',
        'n_table_child_right = $(n_table_root_left + 3)',
        'S_effect.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_table_root_left,HARRAY n_table_root_right,HARRAY n_table_child_left,HARRAY n_table_child_right]',
    ]
    for _, label in pairs:
        rows += [
            '$object_table_at(S.OBJECTTABLES,n_' + label + ') = eps',
            '$object_table_at(S_effect.OBJECTTABLES,n_' + label + ') = (n_table_' + label + ')',
            '$aggregate_hash_image(S_effect,n_' + label + ',n_table_' + label + ')',
            '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_table_' + label + ') = 1',
            '$entry_lookup($trace_object_current_entries(S,n_' + label + '),KSTRING $ptascii("value")) = (DIRECT (PINT ' + ('0' if label.startswith('root') else '1') + '))',
        ]
    rows += object_raw('S', 0, 'S_effect')
    return rows + finish('S_raw', name)
