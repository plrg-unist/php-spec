#!/usr/bin/env python3
"""Check changed integer exits through authenticated original tick history."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent
DERIVED = {}


def source(name):
    return (HERE / f'deprecated_late_tick_body_reexit_{name}.php').read_text()


VALID = ['$executor_tick_unwind(S) = (pexecutortick)',
         '~$executor_tick_valid(S, pexecutortick)',
         '$executor_tick_valid($executor_tick_history(S, pexecutortick.COMPLETION), pexecutortick)',
         '$executor_tick_unwind($executor_tick_history(S, pexecutortick.COMPLETION)) = eps',
         '$call_frame_scope(S, pframe, eps) = $constant_frame_scope(S[.EXITSTATUS = 263], pframe, eps)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
         '$gc_state_valid(S)', '$exit_status_valid(S)',
         '$executor_tick_scope(S)', '$destructor_operational(S)']


def exit_case(name, class_name, saved, status, events, parent, queue):
    records = '[pdestructioncleanup_parent, pdestructioncleanup_returned]' if parent else '[pdestructioncleanup_returned]'
    checks = [
        'pcallcontext.INSTANCE = eps', 'pcallcontext.TARGET = pdestructorcall_returned.TARGET',
        'pdestructorcall_returned.OBJECT = n_returned',
        'S.FRAMES = [pframe]', 'pframe.CONTEXT = eps',
        'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall_returned) :: ptask_saved*',
        '~pdestructorcall_returned.USER', 'pdestructorcall_returned.CALLER = eps',
        'pdestructorcall_returned.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
        'pdestructionoperation.COMPLETION = NORMAL', 'pdestructionoperation.PENDING = eps',
        'S.DESTRUCTION.CLEANUPS = eps', 'S.DESTRUCTION.ABANDONED = eps',
        'S.EXCEPTIONHANDLER = eps', 'S.EXCEPTIONHANDLERS = eps',
        'S.ERRORHANDLER.CALLBACK = eps',
        f'pexecutortick.COMPLETION = {saved}',
        f'S.SHUTDOWN.COMPLETION = {saved}', f'S.DESTRUCTION.COMPLETION = {saved}',
        f'S.EXITSTATUS = {status}', f'z_exit = {status}', 'S.COMPLETION = NORMAL',
        '$heap_owners($heap_graph(S), HOBJECT n_returned) = 2',
        '$destructor_context_valid(S, pcallcontext)',
        '$destructor_call_live(S, pdestructorcall_returned)',
        '$exit_unwind_valid(S, z_exit)', '$eager_bailout_unwind(S)',
        '$eager_bailout_source(S) = (DESTRUCTOR_RESULT pdestructorcall_returned)',
        f'$eager_bailout_records(S, DESTRUCTOR_RESULT pdestructorcall_returned) = ({records})',
        'S.EVENTS = [' + ', '.join(events) + ']', *VALID,
    ]
    if parent:
        checks[0:0] = [
            'S.DESTRUCTION.CALLS = [pdestructorcall_returned, pdestructorcall]',
            'pdestructorcall.OBJECT = n_arg', 'pdestructorcall.OPERATION = (pdestructionoperation)',
            '~pdestructorcall.USER', 'pdestructorcall.CALLER = eps',
            '$destructor_call_live(S, pdestructorcall)',
            '$eager_bailout_parent_pair(S, pdestructorcall)',
            '$eager_bailout_parent_ready(S, pdestructorcall)',
            '$eager_bailout_parent_shared(pdestructorcall, pdestructorcall_returned)',
        ]
        checks.insert(checks.index('S.FRAMES = [pframe]') + 1,
                      '$destructor_c_return_source(pframe.TODO, pdestructorcall)')
    else:
        checks.insert(0, 'S.DESTRUCTION.CALLS = [pdestructorcall_returned]')
    checks.extend([
        'PhpStep: S ~> S_raw',
        'S_left = $literal_reference_debt_step(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_raw))))',
        'S_left.TODO = [EXIT_UNWIND z_exit]', 'S_left.COMPLETION = NORMAL',
        'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
        'S_left.DESTRUCTION.CALLS = eps', 'S_left.DESTRUCTION.RELEASES = eps',
        'S_left.DESTRUCTION.FRAMES = eps', 'S_left.DESTRUCTION.OPERATIONS = eps',
        'S_left.DESTRUCTION.CLEANUPS = eps',
        f'S_left.DESTRUCTION.ABANDONED = {records}',
        'pdestructioncleanup_returned.SOURCE = DESTRUCTOR_RESULT pdestructorcall_returned',
        '$heap_owners($heap_graph(S_left), HOBJECT n_returned) = 2',
        '$eager_abandoned_valid(S_left, S_left.DESTRUCTION.ABANDONED)',
        '$eager_operation_source_valid(S_left, pdestructionoperation)',
        '$executor_tick_caught(S_left) = eps',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
        '$gc_state_valid(S_left)', 'S_left.EVENTS = S.EVENTS',
        'PhpStep: S_left ~> S_exit_raw',
        'S_exit = $literal_reference_debt_step(S_left, $sensitive_trace_freeze($source_exception_transition(S_left, $throwable_transition(S_left, S_exit_raw))))',
        'S_exit.COMPLETION = EXITED z_exit', 'S_exit.EXITSTATUS = z_exit',
        'S_exit.TODO = eps', 'S_exit.CURRENT = eps', 'S_exit.FRAMES = eps',
        'S_exit.DESTRUCTION.ABANDONED = S_left.DESTRUCTION.ABANDONED',
        '$executor_free_endpoint(S_exit)',
        '$executor_tick_bailout(S_exit) = (pexecutortick)',
        '$executor_tick_caught(S_exit) = ((pexecutortick, EXITED z_exit))',
        '$heap_owners($heap_graph(S_exit), HOBJECT n_returned) = 2',
        '$call_descriptors_valid(S_exit)', '$heap_valid($heap_graph(S_exit))',
        '$gc_state_valid(S_exit)', 'S_exit.EVENTS = S.EVENTS',
    ])
    if parent:
        checks.append('pdestructioncleanup_parent.SOURCE = DESTRUCTOR_C_RETURN pdestructorcall')
    if queue:
        checks.extend([
            'S_exit.SHUTDOWN.ENTRIES = [pshutdownentry]',
            'pshutdownentry.ARGS = [POBJECT n_queue]',
            '$callback_cache_nodes(pshutdownentry) = eps',
            '$heap_owners($heap_graph(S_exit), HOBJECT n_queue) = 1',
            'S_paused = $drive_steps(S_exit, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE]',
            'pexecutorqueue.ENTRIES = [pshutdownentry]',
            'pexecutorqueue.COMPLETION = EXITED z_exit',
            'S_paused.SHUTDOWN.ENTRIES = eps',
            'S_paused.DESTRUCTION.ABANDONED = S_exit.DESTRUCTION.ABANDONED',
            'S_queue = S_paused[.COMPLETION = NORMAL]',
            '$executor_queue_valid(S_queue, pexecutorqueue)',
            '$executor_scope(S_queue)', '~$executor_tick_scope(S_queue)',
            '$call_descriptors_valid(S_queue)', '$heap_valid($heap_graph(S_queue))',
            'S_done = $drive_steps(S_queue, 4000)',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("Q;")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_queue) = 0',
        ])
    else:
        checks.extend([
            'S_exit.SHUTDOWN.ENTRIES = eps', 'S_exit.TICKENTRIES = eps',
            '~$executor_module_owners(S_exit)',
            '$executor_free_finish(S_exit) = S_exit',
            '$output_drive_finalize(S_exit, 0) = S_exit',
            'S_done = $drive_steps(S_exit, 4000)', 'S_done.EVENTS = S.EVENTS',
        ])
    checks.extend([
        'S_done.COMPLETION = EXITED z_exit', 'S_done.EXITSTATUS = z_exit',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.TICKENTRIES = S_exit.TICKENTRIES', 'S_done.SHUTDOWN.ENTRIES = eps',
        'S_done.DESTRUCTION.CALLS = eps', 'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.DESTRUCTION.CLEANUPS = eps',
        'S_done.DESTRUCTION.ABANDONED = S_exit.DESTRUCTION.ABANDONED',
        f'S_done.SHUTDOWN.COMPLETION = {saved}', f'S_done.DESTRUCTION.COMPLETION = {saved}',
        'S_done.EXCEPTIONHANDLER = eps', 'S_done.EXCEPTIONHANDLERS = eps',
        '$heap_owners($heap_graph(S_done), HOBJECT n_returned) = 2',
        '$executor_free_finish(S_done) = S_done',
        '$drive_steps(S_done, 0) = S_done', '$drive_steps(S_done, 37) = S_done',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$gc_state_valid(S_done)', '$exit_status_valid(S_done)',
    ])
    return {'source': source(name),
            'stage': 'S.TODO = [EXIT_UNWIND z_exit] -- if S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_returned) -- if $object_name(S, n_returned) = $ptascii("' + class_name + '")',
            'checks': checks}


EVENTS = ['OUTPUT $ptascii("B;F;")', 'OUTPUT $ptascii("A;")', 'OUTPUT $ptascii("R;")']
review.CASES = {
    'fresh-body-reexit-keeps-c-protections-and-old-phase-history':
        exit_case('object', 'BodyReexit27Value', 'EXITED 263', 9, EVENTS, True, True),
    'alias-body-value-reexit-preserves-owner-field-and-old-main263':
        exit_case('array', 'BodyArrayReexit27Value', 'EXITED 263', 515, EVENTS, True, True),
    'static-closure-body-reexit-keeps-full519-and-pending-c-wrappers':
        exit_case('review_closure', 'BodyReexitClosure27Returned', 'EXITED 263', 519, EVENTS, True, True),
    'retained-body-value-reexits-after-original-c-and-child-retire':
        exit_case('review_retained', 'BodyReexitRetained27Returned', 'EXITED 263', 9,
                  EVENTS[:2] + ['OUTPUT $ptascii("K;")', EVENTS[2]], False, True),
    'cacheless-body-reexit-has-idempotent-noqueue-full519-terminal':
        exit_case('no_queue', 'BodyEmptyReexit27Value', 'EXITED 263', 519, EVENTS, True, False),
}


FRESH = list(review.CASES)[:3]
for name, count in zip(FRESH, [2, 3, 2]):
    checks = review.CASES[name]['checks']
    checks.extend([
        'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
        '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
        '$node_children(S, HOBJECT n_arg) = [HOBJECT n_held]',
        f'$heap_owners($heap_graph(S), HOBJECT n_arg) = {count}',
        '$heap_owners($heap_graph(S), HOBJECT n_held) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
        f'$heap_owners($heap_graph(S_left), HOBJECT n_arg) = {count}',
        '$heap_owners($heap_graph(S_left), HOBJECT n_later) = 1',
        '$heap_owners($heap_graph(S_left), HOBJECT n_callback) = 2',
        '$eager_abandoned_owner(pdestructioncleanup_parent.SOURCE) = [HOBJECT n_arg, HOBJECT n_arg, HOBJECT n_later, HOBJECT n_callback, HOBJECT n_callback]',
        '$eager_abandoned_owner(pdestructioncleanup_returned.SOURCE) = [HOBJECT n_returned, HOBJECT n_returned]',
        f'$heap_owners($heap_graph(S_done), HOBJECT n_arg) = {count}',
        '$heap_owners($heap_graph(S_done), HOBJECT n_held) = 1',
        '$heap_owners($heap_graph(S_done), HOBJECT n_later) = 1',
        '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 2',
    ])
review.CASES[FRESH[0]]['checks'].extend([
    'S_exit.TICKENTRIES = [ptickentry_tail]',
    'ptickentry_tail.ENTRY.ARGS = [POBJECT n_tailarg]',
    '$callback_cache_nodes(ptickentry_tail.ENTRY) = [HOBJECT n_tail, HOBJECT n_tail]',
    '$heap_owners($heap_graph(S_done), HOBJECT n_tailarg) = 1',
    '$heap_owners($heap_graph(S_done), HOBJECT n_tail) = 2',
])
review.CASES[FRESH[1]]['checks'].extend([
    '$node_children(S, HOBJECT n_returned) = [HOBJECT n_arg]',
    'S_exit.TICKENTRIES = eps',
])
review.CASES[FRESH[2]]['checks'].extend([
    'S_exit.TICKENTRIES = [ptickentry_tail]',
    'ptickentry_tail.ENTRY.ARGS = [POBJECT n_tailarg]',
    '$callback_cache_nodes(ptickentry_tail.ENTRY) = eps',
    '$heap_owners($heap_graph(S_done), HOBJECT n_tailarg) = 1',
])

RETAINED = 'retained-body-value-reexits-after-original-c-and-child-retire'
review.CASES[RETAINED]['checks'].extend([
    'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_returned]',
    '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
    'S.DESTRUCTION.CALLED = [n_arg, n_held, n_returned]',
    '$object_name(S, n_held) = $ptascii("BodyReexitRetained27Held")',
    '$heap_owners($heap_graph(S), HOBJECT n_arg) = 0',
    '$heap_owners($heap_graph(S), HOBJECT n_held) = 0',
    '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
    '$eager_abandoned_owner(pdestructioncleanup_returned.SOURCE) = [HOBJECT n_returned, HOBJECT n_returned, HOBJECT n_callback, HOBJECT n_callback]',
    '$heap_owners($heap_graph(S_done), HOBJECT n_arg) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_held) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 2',
    'S_exit.TICKENTRIES = [ptickentry_tail]',
    'ptickentry_tail.ENTRY.ARGS = [POBJECT n_tailarg]',
    '$callback_cache_nodes(ptickentry_tail.ENTRY) = eps',
    '$heap_owners($heap_graph(S_done), HOBJECT n_tailarg) = 1',
])

EMPTY = 'cacheless-body-reexit-has-idempotent-noqueue-full519-terminal'
review.CASES[EMPTY]['checks'].extend([
    'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg]',
    '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = eps',
    '$node_children(S, HOBJECT n_arg) = eps',
    '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
    '$heap_owners($heap_graph(S_left), HOBJECT n_arg) = 2',
    '$heap_owners($heap_graph(S_done), HOBJECT n_arg) = 2',
    '$eager_abandoned_owner(pdestructioncleanup_parent.SOURCE) = [HOBJECT n_arg, HOBJECT n_arg]',
    '$eager_abandoned_owner(pdestructioncleanup_returned.SOURCE) = [HOBJECT n_returned, HOBJECT n_returned]',
])

for name in [FRESH[2], EMPTY]:
    negative = ['$executor_tick_caught(S_exit[.EXITSTATUS = 7]) = eps']
    review.CASES[name]['checks'].extend(negative)
    DERIVED[name] = len(negative)
negative = ['$executor_tick_caught(S_exit[.COMPLETION = NORMAL]) = eps',
            '$executor_tick_caught(S_exit[.TODO = [EXIT_UNWIND z_exit]]) = eps',
            '$executor_tick_caught(S_exit[.DESTRUCTION.ABANDONED = eps]) = eps']
review.CASES[FRESH[0]]['checks'].extend(negative)
DERIVED[FRESH[0]] = len(negative)


ordinary_refusals = [
    '$executor_tick_unwind(S[.TODO = eps]) = eps',
    '~$executor_tick_active(S[.TODO = eps], pexecutortick)',
    '$call_frame_scope(S[.TODO = eps], pframe, eps) = $constant_frame_scope(S[.TODO = eps], pframe, eps)',
    '$executor_tick_unwind(S[.TODO = [EXIT_UNWIND 263]]) = eps',
    '~$executor_tick_active(S[.TODO = [EXIT_UNWIND 263]], pexecutortick)',
]
review.CASES[FRESH[0]]['checks'].extend(ordinary_refusals)
DERIVED[FRESH[0]] += len(ordinary_refusals)
review.CASES[FRESH[0]]['checks'].extend([
    'S_paused_unwind = $drive(S, 0)', 'S_paused_unwind.COMPLETION = BUDGET',
    '$executor_tick_unwind(S_paused_unwind) = (pexecutortick)',
    '$call_descriptors_valid(S_paused_unwind)',
    '$heap_owners($heap_graph(S_paused_unwind), HOBJECT n_arg) = 2',
    '$heap_owners($heap_graph(S_paused_unwind), HOBJECT n_returned) = 2',
])


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=480) else 1)
