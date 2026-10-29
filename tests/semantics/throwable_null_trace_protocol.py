"""Reached standalone roots, live traces, skipped payloads and real Errors."""
import base64
import json

from throwable_builtin_previous_protocol import PREFIX
from throwable_previous_graph_protocol import raw, tables, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'object-trace-before-severity': 'B|-1:1|W|1:-1|M|1:-1|E|1|',
    'array-cell-retarget-snapshot': 'B|-1:1|W|1:-1|M|1|E|0:2:1|R|1:7:1|',
    'ordinary-cycle-finally-recovery': 'B|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|I|0|W|1:0|',
    'warm-cache-skips-callback-payload': 'B|1:-1|A|1|',
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
        r'$throwable_object_image_valid(S,n_a) /\ $throwable_object_image_valid(S,n_b)',
        r'$throwable_field(S,n_a,"previous") = PNULL /\ $throwable_field(S,n_b,"previous") = PNULL',
        '$throwable_builtin_previous_pair(S,n_a,n_b,eps)',
        '~$throwable_builtin_same_pair(S,n_a,n_b,eps)',
        '$throwable_builtin_previous_order(S,n_a,n_b,eps) = ORDERUNSUPPORTED "Throwable property comparison"',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b],S.ALLOCATIONS)',
        '~$throwable_builtin_previous_pair(S[.COMPLETION = BUDGET],n_a,n_b,eps)',
        '~$throwable_builtin_previous_pair($objectprops_mark(S,n_a),n_a,n_b,eps)',
    ]


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def checks(program, path, name):
    rows = front(program, path)
    if name == 'array-cell-retarget-snapshot':
        rows += trace('S', 'n_a', 'a', 'PARRAY n_payload_a')[:4]
        rows += trace('S', 'n_b', 'b', 'PARRAY n_payload_b')[:4]
        rows += [
            '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KINT 0) = (ALIAS n_live)',
            '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KINT 1) = (DIRECT (PARRAY n_snapshot))',
            'S.STORE[n_live] = DEFINED (PARRAY n_current)',
            '$entry_lookup(S.ARRAYS[n_current].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$entry_lookup(S.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$heap_subset([HCELL n_live,HARRAY n_current,HARRAY n_snapshot],S.ALLOCATIONS)',
        ]
        rows += raw('S', -1)
        return rows + finish('S_raw', name)
    rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
    rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
    if name == 'warm-cache-skips-callback-payload':
        rows += [
            '$throwable_field(S,n_a,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
            '$throwable_field(S,n_b,"string") = PSTRING eps',
            '~$trace_property_ref_graph(S,n_trace_a)',
            '~$trace_property_ref_graph(S,n_trace_b)',
            '$object_table_at(S.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S.OBJECTTABLES,n_right) = eps',
        ]
        rows += raw('S', 1)
        return rows + finish('S_raw', name)
    rows += [
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_effect,' + ('ORDERRECURSIVE' if name == 'ordinary-cycle-finally-recovery' else 'ORDER $(-1)') + ')',
    ]
    rows += tables()
    if name == 'object-trace-before-severity':
        rows += [
            '$throwable_field(S,n_a,"severity") = PINT 9',
            '$throwable_field(S,n_b,"severity") = PINT 1',
            '$entry_lookup($trace_object_current_entries(S,n_left),KSTRING $ptascii("value")) = (DIRECT (PINT 1))',
            '$entry_lookup($trace_object_current_entries(S,n_right),KSTRING $ptascii("value")) = (DIRECT (PINT 2))',
        ]
        rows += raw('S', -1, 'S_effect')
        return rows + finish('S_raw', name)
    assert name == 'ordinary-cycle-finally-recovery'
    rows += [
        'pbin = SPACESHIP',
        'z = z_S',
        '$entry_lookup($trace_object_current_entries(S,n_left),KSTRING $ptascii("next")) = (DIRECT (POBJECT n_left))',
        '$entry_lookup($trace_object_current_entries(S,n_right),KSTRING $ptascii("next")) = (DIRECT (POBJECT n_right))',
        '$lookup(S.ENV,$ptascii("hold")) = (n_hold)',
        'S.STORE[n_hold] = DEFINED pvalue_hold',
        '$string_plain(pvalue_hold) = PSTRING $ptascii("hold")',
    ]
    rows += error_rows()
    rows += ['S_error.ARRAYS[n_error_trace].ITEMS = eps']
    return rows + finish('S_one[.COMPLETION = NORMAL]', name)
