"""Source-reached physical previous, severity, trace and skipped-leaf orders."""
import base64
import json

PREFIX = r'''
dec $tbp_stage(pstate) : bool
def $tbp_stage(S) = true -- if S.TODO = (BINARY_RIGHT SPACESHIP poperand z) :: ptask*
def $tbp_stage(S) = false -- otherwise
dec $tbp_seek(pstate, nat) : pstate
def $tbp_seek(S, n) = S -- if $tbp_stage(S) \/ n = 0
def $tbp_seek(S, n) = $tbp_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$tbp_stage(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tbp_seek(S, n) = S -- otherwise
dec $tbp_next(pstate) : pstate
def $tbp_next(S) = $tbp_seek($drive_steps(S[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]
dec $tbp_event(pevent) : ptbytes
def $tbp_event(OUTPUT ptbytes) = ptbytes
def $tbp_event(pevent) = eps -- otherwise
dec $tbp_output(pevent*) : ptbytes
def $tbp_output(eps) = eps
def $tbp_output(pevent :: pevent_tail*) = $tbp_event(pevent) ++ $tbp_output(pevent_tail*)
'''


def front(program, path, shared=False):
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
        'n_p = n_q' if shared else 'n_p =/= n_q',
        '$throwable_object_image_valid(S,n_a) /\\ $throwable_object_image_valid(S,n_b)',
        '$throwable_object_image_valid(S,n_p) /\\ $throwable_object_image_valid(S,n_q)',
        '$throwable_builtin_previous_chain_valid(S,n_a,eps)',
        '$throwable_builtin_previous_chain_valid(S,n_b,eps)',
        '$throwable_builtin_previous_pair(S,n_a,n_b,eps)',
        '~$throwable_builtin_same_pair(S,n_a,n_b,eps)',
        '~$throwable_previous_pair(S,n_a,n_b)',
        '~$throwable_warm_previous_pair(S,n_a,n_b)',
        '$objectprops_at(S.OBJECTPROPS,n_a) = (ppropertyslot_a*)',
        '$objectprops_at(S.OBJECTPROPS,n_b) = (ppropertyslot_b*)',
        '$property_order(S,ppropertyslot_a*[0:6],ppropertyslot_b*[0:6],[HOBJECT n_a]) = ORDER 0',
        '$heap_subset([HOBJECT n_a,HOBJECT n_b,HOBJECT n_p,HOBJECT n_q],S.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_p) = ' + ('3' if shared else '2'),
        '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_q) = ' + ('3' if shared else '2'),
    ]


def raw(state, result):
    value = str(result) if result >= 0 else '$(' + str(result) + ')'
    return [
        state + '.TODO = (BINARY_RIGHT SPACESHIP poperand_' + state + ' z_' + state + ') :: ptask_' + state + '*',
        '$value_order_effect(' + state + ',POBJECT n_a,POBJECT n_b,eps,z_' + state + ') = (' + state + ',ORDER ' + value + ')',
        'PhpStep: ' + state + ' ~> ' + state + '_raw',
        state + '_raw.RESULT = KNOWN (PINT ' + value + ')',
        state + '_raw.TODO = ptask_' + state + '*',
        state + '_raw.OBJECTS = ' + state + '.OBJECTS /\\ ' + state + '_raw.OBJECTPROPS = ' + state + '.OBJECTPROPS',
        state + '_raw.ARRAYS = ' + state + '.ARRAYS /\\ ' + state + '_raw.OBJECTTABLES = ' + state + '.OBJECTTABLES',
        state + '_raw.STORE = ' + state + '.STORE /\\ ' + state + '_raw.ALLOCATIONS = ' + state + '.ALLOCATIONS',
        state + '_raw.EVENTS = ' + state + '.EVENTS',
        '$aggregate_compare_seen(' + state + '_raw) = eps',
        '$drive_steps(' + state + ',0) = ' + state + '[.COMPLETION = BUDGET]',
        state + '_budget = $drive_steps(' + state + ',1)',
        state + '_budget.COMPLETION = BUDGET',
        state + '_budget.RESULT = ' + state + '_raw.RESULT /\\ ' + state + '_budget.TODO = ' + state + '_raw.TODO',
        state + '_budget.EVENTS = ' + state + '_raw.EVENTS',
    ]


def checks(program, path, name):
    conditions = front(program, path, name == 'shared-previous-all-root-kinds')
    if name == 'previous-before-severity':
        conditions += [
            '|ppropertyslot_a*| = 8 /\\ |ppropertyslot_b*| = 8',
            '$throwable_field(S,n_a,"severity") = PINT 3',
            '$throwable_field(S,n_b,"severity") = PINT 4',
            '$throwable_field(S,n_p,"code") = PINT 9',
            '$throwable_field(S,n_q,"code") = PINT 1',
            '$throwable_builtin_previous_order(S,n_p,n_q,[HOBJECT n_a]) = ORDER 1',
            '~$throwable_builtin_previous_pair(S[.COMPLETION = BUDGET],n_a,n_b,eps)',
            '~$throwable_builtin_previous_pair($objectprops_mark(S,n_p),n_a,n_b,eps)',
            '~$throwable_builtin_previous_chain_valid($throwable_set_previous_id(S,n_p,(n_a)),n_a,eps)',
            '~$throwable_builtin_previous_pair(S,n_a,n_b,[' + ','.join(['HOBJECT n_a'] * 16) + '])',
            '$throwable_builtin_previous_chain_valid(S,n_a,[' + ','.join(str(n) for n in range(100000, 100014)) + '])',
            '~$throwable_builtin_previous_chain_valid(S,n_a,[' + ','.join(str(n) for n in range(100000, 100015)) + '])',
        ]
        conditions += raw('S', 1)
        conditions += [
            'S_reverse = $tbp_seek(S_raw,1000)[.COMPLETION = NORMAL]',
            '$tbp_stage(S_reverse)',
            'S_warm = $tbp_next(S_reverse)',
            '$tbp_stage(S_warm)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
        ]
        conditions += raw('S_warm', 1)
    elif name == 'severity-after-equal-previous':
        conditions += [
            '|ppropertyslot_a*| = 8 /\\ |ppropertyslot_b*| = 8',
            '$throwable_field(S,n_a,"severity") = PINT 3',
            '$throwable_field(S,n_b,"severity") = PINT 4',
            '$throwable_builtin_previous_order(S,n_p,n_q,[HOBJECT n_a]) = ORDER 0',
            '$value_order(S,POBJECT n_p,POBJECT n_q,[HOBJECT n_a]) = ORDER 1',
        ]
        conditions += raw('S', -1)
        conditions += [
            'S_reverse = $tbp_seek(S_raw,1000)[.COMPLETION = NORMAL]',
            'S_equal = $tbp_next(S_reverse)',
            'S_warm = $tbp_next(S_equal)',
            '$tbp_stage(S_warm)',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
        ]
        conditions += raw('S_warm', -1)
        conditions += [
            'S_warm_equal = $tbp_seek(S_warm_raw,1000)[.COMPLETION = NORMAL]',
            'S_continue = $tbp_next(S_warm_equal)',
            'S_continue.TODO = (BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_left_continue)) z_continue) :: ptask_continue*',
            'S_continue.RESULT = KNOWN (PARRAY n_right_continue)',
            '$value_order_effect(S_continue,PARRAY n_left_continue,PARRAY n_right_continue,eps,z_continue) = (S_continue,ORDER $(-1))',
            'PhpStep: S_continue ~> S_continue_raw',
            'S_continue_raw.RESULT = KNOWN (PINT $(-1))',
            'S_skip = $tbp_seek(S_continue_raw,1000)[.COMPLETION = NORMAL]',
            'S_skip.TODO = (BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_left_skip)) z_skip) :: ptask_skip*',
            'S_skip.RESULT = KNOWN (PARRAY n_right_skip)',
            '$entry_lookup(S_skip.ARRAYS[n_left_skip].ITEMS,KINT 2) = (DIRECT (POBJECT n_tail))',
            '$value_order_effect(S_skip,PARRAY n_left_skip,PARRAY n_right_skip,eps,z_skip) = (S_skip,ORDER $(-1))',
            'PhpStep: S_skip ~> S_skip_raw',
            'S_skip_raw.RESULT = KNOWN (PINT $(-1))',
            'S_skip_raw.EVENTS = S_skip.EVENTS',
            '$aggregate_compare_seen(S_skip_raw) = eps',
            'S_done = $drive_steps(S_skip_raw,1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            '$tbp_output(S_done.EVENTS) = $ptascii("B|-1:1:0|W|1:1:-1:0|A|-1:-1|")',
        ]
    elif name == 'previous-trace-array':
        for child, leaf in [('p', 1), ('q', 2)]:
            conditions += [
                '$throwable_field(S,n_' + child + ',"trace") = PARRAY n_trace_' + child,
                '$entry_lookup(S.ARRAYS[n_trace_' + child + '].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_' + child + '))',
                '$entry_lookup(S.ARRAYS[n_frame_' + child + '].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_' + child + '))',
                '$entry_lookup(S.ARRAYS[n_args_' + child + '].ITEMS,KINT 0) = (DIRECT (PARRAY n_payload_' + child + '))',
                '$entry_lookup(S.ARRAYS[n_payload_' + child + '].ITEMS,KINT 0) = (DIRECT (PINT ' + str(leaf) + '))',
                '$trace_array_graph(S,n_trace_' + child + ')',
                '$heap_subset([HARRAY n_trace_' + child + ',HARRAY n_frame_' + child + ',HARRAY n_args_' + child + ',HARRAY n_payload_' + child + '],S.ALLOCATIONS)',
            ]
        conditions += raw('S', -1)
    elif name == 'mixed-previous-skips-cyclic-trace':
        conditions += [
            'S.OBJECTS[n_p] = THROWABLE pthrowable_p',
            'S.OBJECTS[n_q] = THROWABLE pthrowable_q',
            'pthrowable_p.KIND = "TypeError" /\\ pthrowable_q.KIND = "ValueError"',
            '$throwable_field(S,n_p,"trace") = PARRAY n_trace_p',
            '$throwable_field(S,n_q,"trace") = PARRAY n_trace_q',
            '~$trace_array_graph(S,n_trace_p) /\\ ~$trace_array_graph(S,n_trace_q)',
            '$throwable_builtin_previous_order(S,n_p,n_q,[HOBJECT n_a]) = ORDER 1',
            '$throwable_builtin_previous_order(S,n_q,n_p,[HOBJECT n_b]) = ORDER 1',
        ]
        conditions += raw('S', 1)
        conditions += [
            'S_done = $drive_steps(S_raw,1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            '$tbp_output(S_done.EVENTS) = $ptascii("B|010000:1:1|A|1|")',
        ]
    elif name == 'shared-previous-all-root-kinds':
        conditions += [
            '$throwable_field(S,n_p,"trace") = PARRAY n_trace_p',
            '~$trace_array_graph(S,n_trace_p)',
            '$throwable_builtin_previous_order(S,n_p,n_q,[HOBJECT n_a]) = ORDER 0',
        ]
        conditions += raw('S', 0)
    else:
        assert name == 'previous-object-trace-control'
        conditions += [
            '$throwable_field(S,n_p,"trace") = PARRAY n_trace_p',
            '~$trace_array_graph(S,n_trace_p)',
            '$throwable_builtin_previous_order(S,n_p,n_q,[HOBJECT n_a]) = ORDERUNSUPPORTED "Throwable property comparison"',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z) = (S,ORDERUNSUPPORTED "Throwable property comparison")',
            'PhpStep: S ~> S_raw',
            'S_raw.COMPLETION = UNSUPPORTED "Throwable property comparison"',
            'S_raw.OBJECTS = S.OBJECTS /\\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
            'S_raw.ARRAYS = S.ARRAYS /\\ S_raw.OBJECTTABLES = S.OBJECTTABLES',
            'S_raw.STORE = S.STORE /\\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
            'S_raw.EVENTS = S.EVENTS',
            '$tbp_output(S_raw.EVENTS) = $ptascii("B|")',
            '$aggregate_compare_seen(S_raw) = eps',
        ]
    return conditions
