"""Reached legacy/fallback dispatch, live cells, early skips and real Error."""
import base64
import json

from throwable_builtin_previous_protocol import PREFIX
from throwable_previous_graph_protocol import raw, tables, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'warm-array-cell-snapshot': 'C|-1:1|W|1:-1|M|9:1|E|0:2:1|R|1:7:1|',
    'prefix-cache-skips-methods': 'B|-1:1|W|1:-1|A|1|',
    'count-key-skips-cycles': 'C|-1:1|K|1:1|W|1:1|A|1|',
    'array-cycle-before-count': 'W|1|B|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|R|1:0:0|M|0:1|',
}


def front(program, path, kind):
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
        'S.OBJECTS[n_a] = THROWABLE pthrowable_a',
        'S.OBJECTS[n_b] = THROWABLE pthrowable_b',
        'pthrowable_a.KIND = ' + json.dumps(kind),
        'pthrowable_b.KIND = pthrowable_a.KIND',
        r'$throwable_builtin_previous_node_valid(S,n_a) /\ $throwable_builtin_previous_node_valid(S,n_b)',
        r'$throwable_field(S,n_a,"previous") = PNULL /\ $throwable_field(S,n_b,"previous") = PNULL',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b],S.ALLOCATIONS)',
        '~$throwable_builtin_previous_pair(S,n_a,n_b,eps)',
    ]


def fallback(state, order, effect=None):
    effect = effect or state
    older = ('cold', 'warm', 'warm_trace', 'scalar_trace', 'array_trace',
             'alias_trace', 'array_cell_trace', 'std_trace', 'instance_trace',
             'object_graph', 'property_ref', 'previous', 'warm_previous')
    rows = [f'{state}.TODO = (BINARY_RIGHT SPACESHIP poperand_{state} z_{state}) :: ptask_{state}*']
    rows += [f'~$throwable_{name}_pair({state},n_a,n_b)' for name in older]
    rows += [f'~$throwable_{name}_pair({state},n_a,n_b,eps)'
             for name in ('cross_kind', 'builtin_kind', 'builtin_same', 'builtin_previous')]
    rows += [
        f'~$weakmap_standard_mismatch({state},n_a,n_b)',
        f'$throwable_comparison_fallback_effect({state},n_a,n_b,eps,z_{state}) = ({effect},{order})',
        f'{effect}.COMPLETION = NORMAL',
        f'$throwable_comparison_fallback_effect({state}[.COMPLETION = BUDGET],n_a,n_b,eps,z_{state}) = ({state}[.COMPLETION = UNSUPPORTED "Throwable property comparison"],ORDER 0)',
        f'$throwable_comparison_fallback_effect({state}[.COMPLETION = THROWING n_a],n_a,n_b,eps,z_{state}) = ({state}[.COMPLETION = UNSUPPORTED "Throwable property comparison"],ORDER 0)',
        f'S_materialized = $objectprops_mark({state},n_a)',
        '~$throwable_builtin_previous_node_valid(S_materialized,n_a)',
        f'$throwable_comparison_fallback_effect(S_materialized,n_a,n_b,eps,z_{state}) = (S_materialized[.COMPLETION = UNSUPPORTED "Throwable property comparison"],ORDER 0)',
    ]
    return rows


def finish(state, name):
    return [
        'S_done = $drive_steps(' + state + ',6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]


def checks(program, path, name):
    kind = 'Exception' if name in ('warm-array-cell-snapshot', 'count-key-skips-cycles') else 'Error'
    rows = front(program, path, kind)
    if name == 'warm-array-cell-snapshot':
        rows += trace('S', 'n_a', 'a', 'PARRAY n_payload_a')[:4]
        rows += trace('S', 'n_b', 'b', 'PARRAY n_payload_b')[:4]
        rows += [
            '$throwable_array_cell_trace_pair(S,n_a,n_b)',
            '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KINT 0) = (ALIAS n_live)',
            '$entry_lookup(S.ARRAYS[n_payload_a].ITEMS,KINT 1) = (DIRECT (PARRAY n_snapshot))',
            'S.STORE[n_live] = DEFINED (PARRAY n_current)',
            '$entry_lookup(S.ARRAYS[n_current].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$entry_lookup(S.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 1))',
            '$heap_subset([HCELL n_live,HARRAY n_current,HARRAY n_snapshot],S.ALLOCATIONS)',
        ]
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
            '$entry_lookup(S_warm.ARRAYS[n_payload_a].ITEMS,KINT 0) = (ALIAS n_live)',
        ]
        rows += fallback('S_warm', 'ORDER $(-1)')
        rows += raw('S_warm', -1)
        return rows + finish('S_warm_raw', name)
    if name == 'array-cycle-before-count':
        rows += trace('S', 'n_a', 'a', 'PARRAY n_payload_a')[:4]
        rows += trace('S', 'n_b', 'b', 'PARRAY n_payload_b')[:4]
        rows += [
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
        ]
        rows += fallback('S', 'ORDERRECURSIVE')
        rows += [
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
    rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
    rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
    if name == 'prefix-cache-skips-methods':
        rows += [
            '$string_plain($throwable_field(S,n_a,"message")) = PSTRING $ptascii("a")',
            '$string_plain($throwable_field(S,n_b,"message")) = PSTRING $ptascii("b")',
            '~$trace_property_ref_graph(S,n_trace_a)',
            '~$trace_property_ref_graph(S,n_trace_b)',
            '$object_table_at(S.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S.OBJECTTABLES,n_right) = eps',
        ]
        rows += fallback('S', 'ORDER $(-1)')
        rows += raw('S', -1)
        return rows + finish('S_raw', name)
    assert name == 'count-key-skips-cycles'
    rows += [
        '|$trace_object_current_entries(S,n_left)| = 2',
        '|$trace_object_current_entries(S,n_right)| = 3',
        '$entry_lookup($trace_object_current_entries(S,n_left),KSTRING $ptascii("next")) = (DIRECT (POBJECT n_left))',
        '$entry_lookup($trace_object_current_entries(S,n_right),KSTRING $ptascii("next")) = (DIRECT (POBJECT n_right))',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_effect,ORDER $(-1))',
    ]
    rows += tables()
    rows += fallback('S', 'ORDER $(-1)', 'S_effect')
    rows += raw('S', -1, 'S_effect')
    return rows + finish('S_raw', name)
