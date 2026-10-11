"""Explicit constructor invoke buffer, two trace arguments and original cleanup."""
from from_callable_construct_fiber_review import render as constructor_render
from from_callable_throw_fiber_review import lines


def render(program, filename, expected):
    text, prior, genuine_count, _ = constructor_render(program, filename, expected)
    replacements = {
        'S_received.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]':
            'S_received.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame)), ENTRY (KINT 1) (DIRECT (PARRAY n_frame_invoke))]',
        '$node_children(S_received, HARRAY n_trace) = [HARRAY n_frame]':
            '$node_children(S_received, HARRAY n_trace) = [HARRAY n_frame, HARRAY n_frame_invoke]',
        '$heap_owners($heap_graph(S_received), HOBJECT n_capture) = 1':
            '$heap_owners($heap_graph(S_received), HOBJECT n_capture) = 2',
        '$heap_owners($heap_graph(S_received), HOBJECT n_fresh) = 2':
            '$heap_owners($heap_graph(S_received), HOBJECT n_fresh) = 4',
        '$node_children(S_retired, HARRAY n_trace) = [HARRAY n_frame]':
            '$node_children(S_retired, HARRAY n_trace) = [HARRAY n_frame, HARRAY n_frame_invoke]',
    }
    for state in ['S_rejected', 'S_retired', 'S_before_catch', 'S_caught', 'S_clear_before']:
        replacements[f'$heap_owners($heap_graph({state}), HOBJECT n_fresh) = 1'] = (
            f'$heap_owners($heap_graph({state}), HOBJECT n_fresh) = 2')
    assert all(prior[:genuine_count].count(check) == 1 for check in replacements)
    additions = {
        '$call_current_valid(S_invoke)': lines(r'''
pconfigcall_construct.INDEX = 1
$exit_method_site(S_invoke, pconfigcall_construct.SITE)
'''),
        '$trace_argument_array_valid(S_received, n_args)': lines(r'''
S_received.ARRAYS[n_frame_invoke].ITEMS = [ENTRY (KSTRING $ptascii("file")) (DIRECT (PSTRING $call_sourcefile(S_invoke.FILES, pconfigcall_construct.SITE))), ENTRY (KSTRING $ptascii("line")) (DIRECT (PINT pconfigcall_construct.LINE)), ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING $ptascii("__invoke"))), ENTRY (KSTRING $ptascii("class")) (DIRECT (PSTRING $ptascii("Closure"))), ENTRY (KSTRING $ptascii("type")) (DIRECT (PSTRING $ptascii("->"))), ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_args_invoke))]
n_frame_invoke =/= n_frame
n_args_invoke =/= n_args
S_received.ARRAYS[n_args_invoke].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$node_children(S_received, HARRAY n_frame_invoke) = [HARRAY n_args_invoke]
$node_children(S_received, HARRAY n_args_invoke) = [HOBJECT n_fresh]
$trace_argument_array_valid(S_received, n_args_invoke)
$heap_owners($heap_graph(S_received), HARRAY n_frame_invoke) = 1
$heap_owners($heap_graph(S_received), HARRAY n_args_invoke) = 1
S_received.TODO = (CONFIG_INVOKE pconfigcall_construct) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_construct true) :: ptask_after_call*
$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall_construct true) = [HOBJECT n_capture, HOBJECT n_capture, HOBJECT n_fresh]
$fiber_capture_result_valid(S_received, n_capture, pconfigcall_construct, true)
$node_children(S_received, HOBJECT n_capture) = [HOBJECT n_receiver]
'''),
        'S_retired_step = $drive_steps(S_rejected, 1)': lines(r'''
S_rejected.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame)), ENTRY (KINT 1) (DIRECT (PARRAY n_frame_invoke))]
S_rejected.ARRAYS[n_args_invoke].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$node_children(S_rejected, HARRAY n_trace) = [HARRAY n_frame, HARRAY n_frame_invoke]
$node_children(S_rejected, HARRAY n_frame_invoke) = [HARRAY n_args_invoke]
$node_children(S_rejected, HARRAY n_args_invoke) = [HOBJECT n_fresh]
$heap_owners($heap_graph(S_rejected), HARRAY n_frame_invoke) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_args_invoke) = 1
'''),
        'S_before_catch_reached = $construct_error_seek(S_retired, 1, 1000)': lines(r'''
S_retired.ARRAYS[n_args_invoke].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$node_children(S_retired, HARRAY n_frame_invoke) = [HARRAY n_args_invoke]
$node_children(S_retired, HARRAY n_args_invoke) = [HOBJECT n_fresh]
$heap_owners($heap_graph(S_retired), HARRAY n_frame_invoke) = 1
$heap_owners($heap_graph(S_retired), HARRAY n_args_invoke) = 1
'''),
        'S_caught_step = $drive_steps(S_before_catch, 1)': lines(r'''
S_before_catch.ARRAYS[n_args_invoke].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
'''),
        'S_clear_before_reached = $construct_error_seek(S_caught, 3, 1000)': lines(r'''
S_caught.ARRAYS[n_args_invoke].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
'''),
        'S_clear_step = $drive_steps(S_clear_before, 1)': lines(r'''
S_clear_before.ARRAYS[n_args_invoke].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$node_children(S_clear_before, HARRAY n_trace) = [HARRAY n_frame, HARRAY n_frame_invoke]
'''),
        '$heap_owners($heap_graph(S_cleared), HOBJECT n_error) = 0': lines(r'''
~((HARRAY n_frame_invoke) <- S_cleared.ALLOCATIONS)
~((HARRAY n_args_invoke) <- S_cleared.ALLOCATIONS)
'''),
        f'$outputs(S_done.EVENTS) = $ptascii("{expected}")': lines(r'''
~((HARRAY n_frame_invoke) <- S_done.ALLOCATIONS)
~((HARRAY n_args_invoke) <- S_done.ALLOCATIONS)
'''),
    }
    assert all(prior[:genuine_count].count(check) == 1 for check in additions)
    genuine = []
    for check in prior[:genuine_count]:
        genuine += additions.get(check, [])
        genuine.append(replacements.get(check, check))
    controls = prior[genuine_count:] + lines(r'''
S_other_second_argument = S_rejected[.ARRAYS = $array_replace(S_rejected.ARRAYS, n_args_invoke, S_rejected.ARRAYS[n_args_invoke][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_body))]])]
S_other_second_argument.ARRAYS[n_args_invoke].ITEMS =/= [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$node_children(S_other_second_argument, HARRAY n_args_invoke) = [HOBJECT n_body]
$heap_graph(S_other_second_argument) =/= $heap_graph(S_rejected)
S_bad_second_alias = S_rejected[.ARRAYS = $array_replace(S_rejected.ARRAYS, n_args_invoke, S_rejected.ARRAYS[n_args_invoke][.ITEMS = [ENTRY (KINT 0) (ALIAS n_method_cell)]])]
~$trace_argument_array_valid(S_bad_second_alias, n_args_invoke)
~$trace_graph_valid(S_bad_second_alias, n_trace)
~$throwable_live(S_bad_second_alias, n_error)
S_bad_result_false = S_received[.TODO = (CONFIG_INVOKE pconfigcall_construct) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_construct false) :: ptask_after_call*]
~$fiber_capture_result_valid(S_bad_result_false, n_capture, pconfigcall_construct, false)
S_bad_result_sent = S_received[.TODO = (CONFIG_INVOKE pconfigcall_construct) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_construct[.SENT = eps] true) :: ptask_after_call*]
~$fiber_capture_result_valid(S_bad_result_sent, n_capture, pconfigcall_construct[.SENT = eps], true)
''')
    changes = {'$construct_peer_': '$construct_invoke_peer_',
               '$construct_error_': '$construct_invoke_error_'}
    def renamed(check):
        for old, new in changes.items():
            check = check.replace(old, new)
        return check
    checks = [renamed(check) for check in genuine + controls]
    prefix = renamed(text[:text.index('\ndec $main()')])
    prefix += '\ndec $main() : bool\ndef $main() = true\n'
    prefix += ''.join('  -- if ' + check + '\n' for check in checks)
    return prefix, checks, len(genuine), len(controls)
