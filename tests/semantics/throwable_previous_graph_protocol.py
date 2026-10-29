"""Reached live graph effects, reference retargets and nested slot priority."""
import base64
import json

from throwable_builtin_previous_protocol import PREFIX


def front(program, path):
    encoded = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $tbp_seek(S_initial[.COMPLETION = NORMAL],1000)',
        '$tbp_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
        '$lookup(S.ENV,$ptascii("a")) = (n_acv)',
        '$lookup(S.ENV,$ptascii("b")) = (n_bcv)',
        'S.STORE[n_acv] = DEFINED (POBJECT n_a)',
        'S.STORE[n_bcv] = DEFINED (POBJECT n_b)',
        '$throwable_field(S,n_a,"previous") = POBJECT n_p',
        '$throwable_field(S,n_b,"previous") = POBJECT n_q',
        'n_p =/= n_q',
        r'$throwable_object_image_valid(S,n_a) /\ $throwable_object_image_valid(S,n_b)',
        r'$throwable_object_image_valid(S,n_p) /\ $throwable_object_image_valid(S,n_q)',
        '$throwable_builtin_previous_pair(S,n_a,n_b,eps)',
        '$throwable_builtin_previous_order(S,n_a,n_b,eps) = ORDERUNSUPPORTED "Throwable property comparison"',
    ]


def trace(state, node, label, value):
    return [
        f'$throwable_field({state},{node},"trace") = PARRAY n_trace_{label}',
        f'$entry_lookup({state}.ARRAYS[n_trace_{label}].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_{label}))',
        f'$entry_lookup({state}.ARRAYS[n_frame_{label}].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_{label}))',
        f'$entry_lookup({state}.ARRAYS[n_args_{label}].ITEMS,KINT 0) = (DIRECT ({value}))',
        f'$trace_property_ref_graph({state},n_trace_{label})',
        f'$heap_subset([HARRAY n_trace_{label},HARRAY n_frame_{label},HARRAY n_args_{label}],{state}.ALLOCATIONS)',
    ]


def raw(state, result, effect=None):
    effect = effect or state
    value = str(result) if result >= 0 else '$(' + str(result) + ')'
    return [
        f'{state}.TODO = (BINARY_RIGHT SPACESHIP poperand_{state} z_{state}) :: ptask_{state}*',
        f'$value_order_effect({state},POBJECT n_a,POBJECT n_b,eps,z_{state}) = ({effect},ORDER {value})',
        f'{effect}.COMPLETION = NORMAL',
        f'PhpStep: {state} ~> {state}_raw',
        f'{state}_raw.RESULT = KNOWN (PINT {value})',
        f'{state}_raw.TODO = ptask_{state}*',
        fr'{state}_raw.ARRAYS = {effect}.ARRAYS /\ {state}_raw.OBJECTTABLES = {effect}.OBJECTTABLES',
        fr'{state}_raw.OBJECTPROPS = {effect}.OBJECTPROPS /\ {state}_raw.STORE = {effect}.STORE',
        f'{state}_raw.ALLOCATIONS = {effect}.ALLOCATIONS',
        f'{state}_raw.OBJECTS = {state}.OBJECTS',
        f'{state}_raw.EVENTS = {state}.EVENTS',
        f'$aggregate_compare_seen({state}_raw) = eps',
        f'$drive_steps({state},0) = {state}[.COMPLETION = BUDGET]',
        f'{state}_budget = $drive_steps({state},1)',
        f'{state}_budget.COMPLETION = BUDGET',
        fr'{state}_budget.RESULT = {state}_raw.RESULT /\ {state}_budget.TODO = {state}_raw.TODO',
        f'{state}_budget.OBJECTTABLES = {state}_raw.OBJECTTABLES',
    ]


def tables():
    return [
        '$object_table_at(S.OBJECTTABLES,n_left) = eps',
        '$object_table_at(S.OBJECTTABLES,n_right) = eps',
        'n_table_left = |S.ARRAYS|',
        'n_table_right = $(n_table_left + 1)',
        '|S_effect.ARRAYS| = $(|S.ARRAYS| + 2)',
        'S_effect.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_table_left,HARRAY n_table_right]',
        '$object_table_at(S_effect.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_table_right)',
        '$aggregate_hash_image(S_effect,n_left,n_table_left)',
        '$aggregate_hash_image(S_effect,n_right,n_table_right)',
        '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_table_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_effect)),HARRAY n_table_right) = 1',
    ]


def checks(program, path, name):
    rows = front(program, path)
    if name == 'array-cell-retarget':
        rows += trace('S', 'n_p', 'p', 'PARRAY n_payload_p')
        rows += trace('S', 'n_q', 'q', 'PARRAY n_payload_q')
        rows += [
            '$entry_lookup(S.ARRAYS[n_payload_p].ITEMS,KINT 0) = (ALIAS n_cell)',
            '$entry_lookup(S.ARRAYS[n_payload_p].ITEMS,KINT 1) = (DIRECT (PARRAY n_copy))',
            'n_cell <- S.REFCELLS',
            '(HCELL n_cell) <- S.ALLOCATIONS',
            'S.STORE[n_cell] = DEFINED (PARRAY n_live)',
            '$entry_lookup(S.ARRAYS[n_live].ITEMS,KINT 1) = (DIRECT (PINT 2))',
            '$entry_lookup(S.ARRAYS[n_copy].ITEMS,KINT 1) = (DIRECT (PINT 2))',
            '$lookup(S.ENV,$ptascii("snapshot")) = (n_snapshotcv)',
            'S.STORE[n_snapshotcv] = DEFINED (PARRAY n_copy)',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_cell) = n_cell_owners',
            '$(n_cell_owners >= 2)',
            'S_cycle = S[.STORE[n_cell] = DEFINED (PARRAY n_payload_p)]',
            '~$trace_property_ref_graph(S_cycle,n_trace_p)',
            '$value_order_effect(S_cycle,POBJECT n_a,POBJECT n_b,eps,1) = (S_cycle,ORDERUNSUPPORTED "Throwable property comparison")',
        ]
        rows += raw('S', -1)
        rows += [
            'S_reverse = $tbp_seek(S_raw,1000)[.COMPLETION = NORMAL]',
            'S_mutated = $tbp_next(S_reverse)',
            'S_mutated.STORE[n_cell] = DEFINED (PARRAY n_live_mutated)',
            '$entry_lookup(S_mutated.ARRAYS[n_live_mutated].ITEMS,KINT 1) = (DIRECT (PINT 4))',
            '$lookup(S_mutated.ENV,$ptascii("snapshot")) = (n_snapshotcv_mutated)',
            'S_mutated.STORE[n_snapshotcv_mutated] = DEFINED (PARRAY n_snapshot_mutated)',
            'n_snapshot_mutated =/= n_copy',
            '$entry_lookup(S_mutated.ARRAYS[n_snapshot_mutated].ITEMS,KINT 1) = (DIRECT (PINT 99))',
            '$entry_lookup(S_mutated.ARRAYS[n_copy].ITEMS,KINT 1) = (DIRECT (PINT 2))',
            '$entry_lookup(S_mutated.ARRAYS[n_payload_p].ITEMS,KINT 0) = (ALIAS n_cell)',
        ]
        rows += raw('S_mutated', 1)
        rows += [
            'S_mutated_reverse = $tbp_seek(S_mutated_raw,1000)[.COMPLETION = NORMAL]',
            'S_retarget = $tbp_next(S_mutated_reverse)',
            'S_retarget.STORE[n_cell] = DEFINED (PARRAY n_retarget)',
            '$entry_lookup(S_retarget.ARRAYS[n_retarget].ITEMS,KINT 1) = (DIRECT (PINT 3))',
            '$entry_lookup(S_retarget.ARRAYS[n_copy].ITEMS,KINT 1) = (DIRECT (PINT 2))',
            '$entry_lookup(S_retarget.ARRAYS[n_payload_p].ITEMS,KINT 0) = (ALIAS n_cell)',
        ]
        rows += raw('S_retarget', 0)
        expected = 'B|-1:1|M|99:1:-1|R|0:1|'
        last = 'S_retarget_raw'
    else:
        assert name in ('std-live-cow-warm-tail', 'trace-before-link-and-severity')
        rows += trace('S', 'n_p', 'p', 'POBJECT n_left')
        rows += trace('S', 'n_q', 'q', 'POBJECT n_right')
        rows += [
            '$trace_object_graph_pair(S,n_trace_p,n_trace_q)',
            '$throwable_builtin_previous_trace_pair(S,n_p,n_q)',
            '~$trace_array_graph(S,n_trace_p)',
            'S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S_effect,ORDER $(-1))',
        ]
        rows += tables()
        rows += raw('S', -1, 'S_effect')
        rows += [
            'S_reverse = $tbp_seek(S_raw,1000)[.COMPLETION = NORMAL]',
            'S_warm = $tbp_next(S_reverse)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
            '$object_table_at(S_warm.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_warm.OBJECTTABLES,n_right) = (n_table_right)',
        ]
        rows += raw('S_warm', -1)
        rows += [
            'S_mutated = $tbp_seek(S_warm_raw,1000)[.COMPLETION = NORMAL]',
            '$object_table_at(S_mutated.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_mutated.OBJECTTABLES,n_right) = (n_table_right)',
        ]
        if name == 'std-live-cow-warm-tail':
            rows += [
                '$throwable_field(S,n_a,"severity") = PINT 9',
                '$throwable_field(S,n_b,"severity") = PINT 1',
                '$entry_lookup(S_effect.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("data")) = (DIRECT (PARRAY n_saved))',
                '$entry_lookup(S_effect.ARRAYS[n_table_right].ITEMS,KSTRING $ptascii("data")) = (DIRECT (PARRAY n_other))',
                '$lookup(S.ENV,$ptascii("source")) = (n_sourcecv)',
                'S.STORE[n_sourcecv] = DEFINED (PARRAY n_saved)',
                '$lookup(S_mutated.ENV,$ptascii("source")) = (n_sourcecv_mutated)',
                'S_mutated.STORE[n_sourcecv_mutated] = DEFINED (PARRAY n_source_mutated)',
                'n_source_mutated =/= n_saved',
                '$entry_lookup(S_mutated.ARRAYS[n_source_mutated].ITEMS,KINT 1) = (DIRECT (PINT 99))',
                '$entry_lookup(S_mutated.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("data")) = (DIRECT (PARRAY n_left_mutated))',
                'n_source_mutated =/= n_left_mutated',
                '$entry_lookup(S_mutated.ARRAYS[n_left_mutated].ITEMS,KINT 1) = (DIRECT (PINT 4))',
                '$entry_lookup(S_mutated.ARRAYS[n_other].ITEMS,KINT 1) = (DIRECT (PINT 3))',
            ]
            rows += raw('S_mutated', 1)
            rows += [
                'S_mutated_reverse = $tbp_seek(S_mutated_raw,1000)[.COMPLETION = NORMAL]',
                'S_severity = $tbp_next(S_mutated_reverse)',
                '$value_order_effect(S_severity,POBJECT n_a,POBJECT n_b,eps,1) = (S_severity,ORDER 1)',
                'S_equal = $tbp_next(S_severity)',
                'S_array = $tbp_next(S_equal)',
                'S_array.TODO = (BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array_left)) z_array) :: ptask_array*',
                'S_array.RESULT = KNOWN (PARRAY n_array_right)',
                '$value_order_effect(S_array,PARRAY n_array_left,PARRAY n_array_right,eps,z_array) = (S_array,ORDER $(-1))',
                'PhpStep: S_array ~> S_array_raw',
                'S_array_raw.RESULT = KNOWN (PINT $(-1))',
            ]
            expected = 'B|-1:1|W|1:-1|M|99:1:-1|E|1:0|A|-1:1|'
            last = 'S_array_raw'
        else:
            rows += [
                '$throwable_field(S,n_a,"severity") = PINT 1',
                '$throwable_field(S,n_b,"severity") = PINT 9',
                '$throwable_field(S,n_p,"severity") = PINT 1',
                '$throwable_field(S,n_q,"severity") = PINT 9',
                '$throwable_field(S,n_p,"previous") = POBJECT n_deep_left',
                '$throwable_field(S,n_q,"previous") = POBJECT n_deep_right',
                '$throwable_field(S,n_deep_left,"code") = PINT 9',
                '$throwable_field(S,n_deep_right,"code") = PINT 1',
                '$entry_lookup(S_effect.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("x")) = (DIRECT (PINT 1))',
                '$entry_lookup(S_mutated.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("x")) = (DIRECT (PINT 2))',
                '$entry_lookup(S_mutated.ARRAYS[n_table_right].ITEMS,KSTRING $ptascii("x")) = (DIRECT (PINT 2))',
                'S_mutated.TODO = (BINARY_RIGHT SPACESHIP poperand_mutated z_mutated) :: ptask_mutated*',
                '$throwable_builtin_previous_effect(S_mutated,n_p,n_q,[HOBJECT n_a],z_mutated) = (S_mutated,ORDER 1)',
            ]
            rows += raw('S_mutated', 1)
            expected = 'B|-1:1|W|1:-1|P|1:-1|'
            last = 'S_mutated_raw'
    rows += [
        f'S_done = $drive_steps({last},1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(expected) + ')',
    ]
    return rows
