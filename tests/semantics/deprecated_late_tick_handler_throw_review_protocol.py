#!/usr/bin/env python3
"""Check nested bailout while a selected exception handler's value retires."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent
DERIVED = {}
PARENT = 'DESTRUCTOR_C_ABANDONED pdestructorcall pdestructorcall_returned'


def source(name):
    return (HERE / f'deprecated_late_tick_handler_throw_{name}.php').read_text()


VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
         '$gc_state_valid(S)', '$exit_status_valid(S)', '$executor_tick_scope(S)',
         '$destructor_operational(S)', '$output_final_destructors(S)']
EVENTS = ['OUTPUT $ptascii("B;F;")', 'OUTPUT $ptascii("A;")',
          'OUTPUT $ptascii("H;")', 'OUTPUT $ptascii("R;")']


def phase(completion, status):
    return [f'pexecutortick.COMPLETION = {completion}',
            f'S.SHUTDOWN.COMPLETION = {completion}',
            f'S.DESTRUCTION.COMPLETION = {completion}',
            f'S.EXITSTATUS = {status}', 'S.COMPLETION = NORMAL']


def stage(name):
    return ('S.TODO = (THROW_SEARCH n_cause) :: '
            '(DESTRUCTOR_C_RETURN pdestructorcall_returned) :: '
            '(DESTRUCTOR_RESULT pdestructorcall_returned) :: ptask_tail* '
            f'-- if $object_name(S, pdestructorcall_returned.OBJECT) = $ptascii("{name}")')


def pending(name, class_name, handler, completion, status, arg_owners):
    return {
        'source': source(name), 'stage': stage(class_name),
        'checks': [
            'S.DESTRUCTION.CALLS = [pdestructorcall_returned, pdestructorcall]',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
            'pdestructorcall_returned.OPERATION = (pdestructionoperation_value)',
            'pdestructionoperation_value.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            'pdestructionoperation_value.CLEANUP = (pdestructioncleanup_handler)',
            'pdestructioncleanup_handler.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            'S.DESTRUCTION.CLEANUPS = [pdestructioncleanup_handler]',
            '~pdestructioncleanup_handler.RELEASED',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation_value.COMPLETION = NORMAL',
            'pdestructorcall.OBJECT = n_arg',
            'pdestructorcall_returned.OBJECT = n_returned',
            'pexceptioncall.OBJECT = n_old', 'n_old =/= n_cause',
            '~pdestructorcall.USER', 'pdestructorcall.CALLER = eps',
            '~pdestructorcall_returned.USER',
            'pdestructorcall_returned.CALLER = eps',
            '$eager_bailout_frame_nodes(pdestructorcall.FRAME) = eps',
            '$eager_bailout_operation_nodes(pdestructorcall.OPERATION) = eps',
            '$instance_roots(pdestructorcall.PENDING) = eps',
            '$eager_bailout_frame_nodes(pdestructorcall_returned.FRAME) = eps',
            '$eager_bailout_operation_nodes(pdestructorcall_returned.OPERATION) = eps',
            '$instance_roots(pdestructorcall_returned.PENDING) = eps',
            '~$eager_bailout_parent_shared(pdestructorcall, pdestructorcall_returned)',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.DESTRUCTION.ABANDONED = eps', *phase(completion, status),
            'S.EXCEPTIONHANDLER = eps',
            'S.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue_previous?)*',
            '(pvalue_previous?)* = [eps]',
            f'$string_bytes(pexceptioncall.CALLBACK) = ($ptascii("{handler}"))',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$node_children(S, HOBJECT n_arg) = [HOBJECT n_held]',
            f'$heap_owners($heap_graph(S), HOBJECT n_arg) = {arg_owners}',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cause) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$destructor_call_live(S, pdestructorcall)',
            '$destructor_c_return_source(S.TODO, pdestructorcall)',
            '~$destructor_c_return_valid(S, pdestructorcall)',
            '$destructor_c_return_valid(S, pdestructorcall_returned)',
            '$eager_bailout_parent_ready(S, pdestructorcall)',
            '$eager_bailout_parent_omittable(pdestructorcall, pdestructorcall_returned)',
            '$eager_bailout_selected_covered(pdestructorcall_returned)',
            '$eager_bailout_source(S) = (DESTRUCTOR_RESULT pdestructorcall_returned)',
            '$eager_bailout_records(S, DESTRUCTOR_RESULT pdestructorcall_returned) = ([pdestructioncleanup_parent, pdestructioncleanup_returned])',
            '$eager_cleanup_valid(S, pdestructioncleanup_handler)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$eager_operation_source_valid(S, pdestructionoperation_value)',
            '$throwable_live(S, n_old)', '$throwable_live(S, n_cause)',
            'S.EVENTS = [' + ', '.join(EVENTS) + ']', *VALID,
            'PhpStep: S ~> S_raw',
            'S_after = $literal_reference_debt_step(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_raw))))',
            'S_raw.COMPLETION = UNCAUGHT n_cause',
            'S_after.COMPLETION = UNCAUGHT n_cause', 'S_after.TODO = eps',
            'S_after.CURRENT = eps', 'S_after.FRAMES = eps',
            'S_after.DESTRUCTION.CALLS = eps', 'S_after.DESTRUCTION.RELEASES = eps',
            'S_after.DESTRUCTION.FRAMES = eps', 'S_after.DESTRUCTION.OPERATIONS = eps',
            'S_after.DESTRUCTION.CLEANUPS = eps',
            'S_after.DESTRUCTION.ABANDONED = [pdestructioncleanup_handler, pdestructioncleanup_parent, pdestructioncleanup_returned]',
            f'pdestructioncleanup_parent.SOURCE = {PARENT}',
            'pdestructioncleanup_returned.SOURCE = DESTRUCTOR_RESULT pdestructorcall_returned',
            '$eager_abandoned_owner(pdestructioncleanup_handler.SOURCE) = [HOBJECT n_old]',
            '$eager_abandoned_owner(pdestructioncleanup_parent.SOURCE) = [HOBJECT n_arg, HOBJECT n_arg, HOBJECT n_later, HOBJECT n_callback, HOBJECT n_callback]',
            '$eager_abandoned_owner(pdestructioncleanup_returned.SOURCE) = [HOBJECT n_returned, HOBJECT n_returned]',
            f'$heap_owners($heap_graph(S_after), HOBJECT n_arg) = {arg_owners}',
            '$heap_owners($heap_graph(S_after), HOBJECT n_returned) = 2',
            '$heap_owners($heap_graph(S_after), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S_after), HOBJECT n_cause) = 1',
            '$heap_owners($heap_graph(S_after), HOBJECT n_later) = 1',
            '$heap_owners($heap_graph(S_after), HOBJECT n_callback) = 2',
            '$eager_cleanup_valid(S_after, pdestructioncleanup_handler)',
            '$eager_cleanup_valid(S_after, pdestructioncleanup_parent)',
            '$eager_cleanup_valid(S_after, pdestructioncleanup_returned)',
            '$executor_tick_abandoned(S_after, pdestructioncleanup_returned) = eps',
            f'$task_nodes({PARENT}) = eps',
            f'~$call_task_valid(S_after, {PARENT})',
            '$eager_abandoned_valid(S_after, S_after.DESTRUCTION.ABANDONED)',
            '$eager_operation_source_valid(S_after, pdestructionoperation)',
            '~$eager_operation_source_valid(S_after, pdestructionoperation_value)',
            '$eager_operation_source_valid($eager_bailout_history(S_after, pdestructorcall_returned), pdestructionoperation_value)',
            '$executor_tick_bailout(S_after) = (pexecutortick)',
            '$executor_tick_caught(S_after) = ((pexecutortick, UNCAUGHT n_cause))',
            f'S_after.EXITSTATUS = {status}',
            f'S_after.SHUTDOWN.COMPLETION = {completion}',
            f'S_after.DESTRUCTION.COMPLETION = {completion}',
            'S_after.EVENTS = S.EVENTS',
            'S_after.TICKENTRIES = S.TICKENTRIES',
            'S_after.SHUTDOWN.ENTRIES = S.SHUTDOWN.ENTRIES',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
            '$gc_state_valid(S_after)', '$exit_status_valid(S_after)',
        ],
    }


ABANDONED = [
    'S.DESTRUCTION.ABANDONED = [pdestructioncleanup_handler, pdestructioncleanup_parent, pdestructioncleanup_returned]',
    f'pdestructioncleanup_parent.SOURCE = {PARENT}',
    'pdestructioncleanup_returned.SOURCE = DESTRUCTOR_RESULT pdestructorcall_returned',
    'pdestructorcall.OPERATION = (pdestructionoperation)',
    'pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
    'pdestructorcall_returned.OPERATION = (pdestructionoperation_value)',
    'pdestructionoperation_value.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
    'pdestructioncleanup_handler.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
    'pdestructorcall.OBJECT = n_arg',
    'pdestructorcall_returned.OBJECT = n_returned', 'pexceptioncall.OBJECT = n_old',
    'pexecutortick.COMPLETION = NORMAL',
    'S.SHUTDOWN.COMPLETION = NORMAL', 'S.DESTRUCTION.COMPLETION = NORMAL',
    'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
    '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
    '$node_children(S, HOBJECT n_arg) = [HOBJECT n_held]',
    '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_returned) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_held) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
    'S.EXCEPTIONHANDLER = eps',
    'S.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue_previous?)*',
    '(pvalue_previous?)* = [eps]',
    'S.TICKENTRIES = [ptickentry_tail]',
    'ptickentry_tail.ENTRY.ARGS = [POBJECT n_tail]',
    '$callback_cache_nodes(ptickentry_tail.ENTRY) = eps',
    '$heap_owners($heap_graph(S), HOBJECT n_tail) = 1',
    '$eager_cleanup_valid(S, pdestructioncleanup_handler)',
    '$eager_cleanup_valid(S, pdestructioncleanup_parent)',
    '$eager_cleanup_valid(S, pdestructioncleanup_returned)',
    '$eager_operation_source_valid(S, pdestructionoperation)',
    '~$eager_operation_source_valid(S, pdestructionoperation_value)',
    '$eager_operation_source_valid($eager_bailout_history(S, pdestructorcall_returned), pdestructionoperation_value)',
    '$executor_tick_bailout(S) = (pexecutortick)',
    'S.EXITSTATUS = 255', 'S.COMPLETION = NORMAL',
]


review.CASES = {
    'handler-value-throw-preserves-two-c-calls-and-old-exception':
        pending('object', 'HandlerThrow25Value', 'handler_throw25_exception', 'NORMAL', 0, 2),
    'alias-handler-value-throw-keeps-real-owner-field-and-full-exit':
        pending('array', 'HandlerArrayThrow25Value', 'handler_array_throw25_exception', 'EXITED 263', 263, 3),
    'handler-closure-capture-throw-preserves-original-c-protections':
        pending('review_closure', 'HandlerThrowClosure25Returned', 'handler_throw_closure25_handler', 'NORMAL', 0, 2),
    'shared-handler-value-throws-after-handler-and-original-c-return': {
        'source': source('review_retained'),
        'stage': stage('HandlerThrowRetained25Returned'),
        'checks': [
            'S.DESTRUCTION.CALLS = [pdestructorcall_returned]',
            'pdestructorcall_returned.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
            'pdestructorcall_returned.OBJECT = n_returned',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_returned]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            'S.DESTRUCTION.CALLED = [n_arg, n_held, n_returned]',
            '$object_name(S, n_held) = $ptascii("HandlerThrowRetained25Held")',
            '~((HOBJECT n_arg) <- S.ALLOCATIONS)', '~((HOBJECT n_held) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_cause) = 1',
            'S.DESTRUCTION.ABANDONED = eps', 'S.DESTRUCTION.CLEANUPS = eps',
            'S.EXCEPTIONHANDLER = (pvalue_handler)',
            '$string_bytes(pvalue_handler) = ($ptascii("handler_throw_retained25_handler"))',
            'S.EXCEPTIONHANDLERS = [eps]', *phase('NORMAL', 0),
            '$destructor_c_return_valid(S, pdestructorcall_returned)',
            '$exception_dispatch_ready(S)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;"), OUTPUT $ptascii("K;"), OUTPUT $ptascii("R;")]',
            *VALID,
            'PhpStep: S ~> S_handler',
            'S_handler.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: (DESTRUCTOR_C_RETURN pdestructorcall_returned) :: (DESTRUCTOR_RESULT pdestructorcall_returned) :: ptask_tail*',
            'pexceptioncall.OBJECT = n_cause', 'pexceptioncall.CALLBACK = pvalue_handler',
            'S_handler.EXCEPTIONHANDLER = eps',
            'S_handler.EXCEPTIONHANDLERS = (pvalue_handler) :: [eps]',
            '$heap_owners($heap_graph(S_handler), HOBJECT n_cause) = 1',
            '$heap_owners($heap_graph(S_handler), HOBJECT n_returned) = 2',
            'S_handler.DESTRUCTION.ABANDONED = eps',
            '$exception_invoke_valid(S_handler, pexceptioncall)',
            '$destructor_c_return_valid(S_handler, pdestructorcall_returned)',
            '$call_descriptors_valid(S_handler)', '$heap_valid($heap_graph(S_handler))',
            'S_done = $drive_steps(S_handler, 4000)',
            'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
            'S_done.TODO = eps', 'S_done.TICKENTRIES = eps',
            'S_done.SHUTDOWN.ENTRIES = eps', 'S_done.DESTRUCTION.ABANDONED = eps',
            'S_done.DESTRUCTION.CALLS = eps', 'S_done.DESTRUCTION.CLEANUPS = eps',
            'S_done.EXCEPTIONHANDLER = (pvalue_handler)',
            'S_done.EXCEPTIONHANDLERS = [eps]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_cause) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_returned) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 0',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("H;"), OUTPUT $ptascii("C;"), OUTPUT $ptascii("Q;")]',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
            '$gc_state_valid(S_done)', '$exit_status_valid(S_done)',
        ],
    },
    'new-fatal-cause-retires-while-original-handler-cleanup-stays-owned': {
        'source': source('object'),
        'stage': 'S.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal true]',
        'checks': [
            *ABANDONED,
            'pexecutortickfatal.TICK = pexecutortick',
            'pexecutortickfatal.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("ignored-handler-value") 4',
            'n_cause = pexecutortickfatal.OBJECT',
            '$executor_tick_fatal_valid(S, pexecutortickfatal)',
            '$executor_report_cause(S, pexecutortickfatal.COMPLETION, n_cause)',
            '$throwable_live(S, n_cause)',
            '$heap_owners($heap_graph(S), HOBJECT n_cause) = 1',
            '$task_nodes(EXECUTOR_TICK_FATAL pexecutortickfatal true) = [HOBJECT n_cause]',
            '$task_nodes(EXECUTOR_TICK_FATAL pexecutortickfatal false) = eps',
            'S.EVENTS = [' + ', '.join(EVENTS) + ', STDERR ptbytes_fatal]',
            *VALID,
            'PhpStep: S ~> S_pending',
            'S_pending.DESTRUCTION.ABANDONED = S.DESTRUCTION.ABANDONED',
            '$heap_owners($heap_graph(S_pending), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S_pending), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S_pending), HOBJECT n_returned) = 2',
            '$heap_owners($heap_graph(S_pending), HOBJECT n_cause) = 1',
            '$executor_tick_scope(S_pending)', '$output_final_destructors(S_pending)',
            '$destructor_operational(S_pending)',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        ],
    },
    'nested-handler-fatal-keeps-tick-tail-and-continues-late-queue': {
        'source': source('object'),
        'stage': 'S.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal false]',
        'checks': [
            *ABANDONED,
            'pexecutortickfatal.TICK = pexecutortick',
            'pexecutortickfatal.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("ignored-handler-value") 4',
            'n_cause = pexecutortickfatal.OBJECT',
            '$executor_tick_fatal_valid(S, pexecutortickfatal)',
            '$heap_owners($heap_graph(S), HOBJECT n_cause) = 0',
            '$objectprops_at(S.OBJECTPROPS, n_cause) = eps',
            'S.SHUTDOWN.ENTRIES = [pshutdownentry]',
            'pshutdownentry.ARGS = [POBJECT n_queue]',
            '$callback_cache_nodes(pshutdownentry) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_queue) = 1',
            'S.EVENTS = [' + ', '.join(EVENTS) + ', STDERR ptbytes_fatal]',
            *VALID,
            'PhpStep: S ~> S_queue',
            'S_queue.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE]',
            'pexecutorqueue.ENTRIES = [pshutdownentry]',
            'pexecutorqueue.COMPLETION = pexecutortickfatal.COMPLETION',
            'S_queue.SHUTDOWN.ENTRIES = eps',
            'S_queue.DESTRUCTION.ABANDONED = S.DESTRUCTION.ABANDONED',
            '$executor_queue_valid(S_queue, pexecutorqueue)',
            '$executor_scope(S_queue)', '~$executor_tick_scope(S_queue)',
            '$heap_owners($heap_graph(S_queue), HOBJECT n_queue) = 1',
            '$call_descriptors_valid(S_queue)', '$heap_valid($heap_graph(S_queue))',
            'S_paused = $drive(S_queue, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = S_queue.TODO',
            'S_done = $drive_steps(S_queue, 4000)',
            'S_done.COMPLETION = pexecutortickfatal.COMPLETION',
            'S_done.EXITSTATUS = 255', 'S_done.TODO = eps',
            'S_done.SHUTDOWN.ENTRIES = eps', 'S_done.TICKENTRIES = [ptickentry_tail]',
            'S_done.DESTRUCTION.CALLS = eps', 'S_done.DESTRUCTION.RELEASES = eps',
            'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
            'S_done.DESTRUCTION.ABANDONED = S.DESTRUCTION.ABANDONED',
            '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S_done), HOBJECT n_returned) = 2',
            '$heap_owners($heap_graph(S_done), HOBJECT n_queue) = 0',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("Q;")]',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
            '$exit_status_valid(S_done)',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
        ],
    },
    'old-tick-parent-does-not-authorize-a-later-queue-selection': {
        'source': source('object'),
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_queue) :: ptask_tail* -- if $object_name(S, pdestructorcall_queue.OBJECT) = $ptascii("HandlerThrow25Queued")',
        'checks': [
            *ABANDONED,
            'pdestructorcall_queue.OPERATION = (pdestructionoperation_queue)',
            'pdestructionoperation_queue.SOURCE = EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE',
            'pdestructorcall_queue.OBJECT = n_queue',
            'S.DESTRUCTION.CALLS = [pdestructorcall_queue]',
            '$heap_owners($heap_graph(S), HOBJECT n_queue) = 2',
            '$destructor_enter_valid(S, pdestructorcall_queue)',
            '$executor_scope(S)', '~$executor_tick_scope(S)',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            '$gc_state_valid(S)', '$exit_status_valid(S)',
        ],
    },
}


array_checks = review.CASES['alias-handler-value-throw-keeps-real-owner-field-and-full-exit']['checks']
array_checks.insert(array_checks.index('$node_children(S, HOBJECT n_arg) = [HOBJECT n_held]') + 1,
                    '$node_children(S, HOBJECT n_returned) = [HOBJECT n_arg]')
array_checks.extend([
    'S_done = $drive_steps(S_after, 4000)',
    'S_done.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("array-handler-value") 7',
    'S_done.EXITSTATUS = 255', 'S_done.TODO = eps',
    'S_done.SHUTDOWN.COMPLETION = EXITED 263',
    'S_done.DESTRUCTION.COMPLETION = EXITED 263',
    'S_done.TICKENTRIES = eps', 'S_done.SHUTDOWN.ENTRIES = eps',
    'S_done.EVENTS = S.EVENTS ++ [STDERR ptbytes_fatal, OUTPUT $ptascii("Q;")]',
    '$heap_owners($heap_graph(S_done), HOBJECT n_arg) = 3',
    '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 1',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    '$gc_state_valid(S_done)', '$exit_status_valid(S_done)',
])
review.CASES['handler-closure-capture-throw-preserves-original-c-protections']['checks'].extend([
    'S_done = $drive_steps(S_after, 4000)',
    'S_done.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("handler-closure-value-fail") 4',
    'S_done.EXITSTATUS = 255', 'S_done.TODO = eps',
    'S_done.TICKENTRIES = eps', 'S_done.SHUTDOWN.ENTRIES = eps',
    'S_done.EVENTS = S.EVENTS ++ [STDERR ptbytes_fatal, OUTPUT $ptascii("Q;")]',
    '$heap_owners($heap_graph(S_done), HOBJECT n_arg) = 2',
    '$heap_owners($heap_graph(S_done), HOBJECT n_old) = 1',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    '$gc_state_valid(S_done)', '$exit_status_valid(S_done)',
])


OBJECT = 'handler-value-throw-preserves-two-c-calls-and-old-exception'
derived_object = [
    'pdestructionoperation_owned = pdestructionoperation[.VALUE = KNOWN (POBJECT n_held)]',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_owned) = [HOBJECT n_held]',
    '~$eager_bailout_parent_omittable(pdestructorcall[.OPERATION = (pdestructionoperation_owned)], pdestructorcall_returned)',
    'pdestructionoperation_owned_base = pdestructionoperation[.BASE = BASE_VALUE (KNOWN (POBJECT n_held))]',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_owned_base) = [HOBJECT n_held]',
    '~$eager_bailout_parent_omittable(pdestructorcall[.OPERATION = (pdestructionoperation_owned_base)], pdestructorcall_returned)',
    'pdestructionoperation_owned_completion = pdestructionoperation[.COMPLETION = UNCAUGHT n_old]',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_owned_completion) = [HOBJECT n_old]',
    '~$eager_bailout_parent_omittable(pdestructorcall[.OPERATION = (pdestructionoperation_owned_completion)], pdestructorcall_returned)',
    'pdestructionoperation_selected_completion = pdestructionoperation_value[.COMPLETION = UNCAUGHT n_old]',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_selected_completion) = [HOBJECT n_old]',
    'pdestructorcall_selected_completion = pdestructorcall_returned[.OPERATION = (pdestructionoperation_selected_completion)]',
    '~$eager_bailout_selected_covered(pdestructorcall_selected_completion)',
    '~$eager_bailout_parent_omittable(pdestructorcall[.PENDING = (n_old)], pdestructorcall_returned)',
    'pdestructionframe_owned = {PENDING eps, VALUE KNOWN (POBJECT n_held), CALLER eps, FUNCTION porigin_arg, ORIGIN eps, CONSTCONTEXT eps}',
    '$task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe_owned) = [HOBJECT n_held]',
    '~$eager_bailout_parent_omittable(pdestructorcall[.FRAME = (pdestructionframe_owned)], pdestructorcall_returned)',
    'pdestructionframe_pending = pdestructionframe_owned[.VALUE = KNOWN PNULL][.PENDING = (n_old)]',
    '$task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe_pending) = [HOBJECT n_old]',
    '~$eager_bailout_parent_omittable(pdestructorcall[.FRAME = (pdestructionframe_pending)], pdestructorcall_returned)',
    '~$eager_bailout_parent_source_valid(S_after[.DESTRUCTION.ABANDONED = [pdestructioncleanup_handler, pdestructioncleanup_parent]], pdestructioncleanup_parent.SOURCE)',
    '~$eager_bailout_parent_source_valid(S_after, DESTRUCTOR_C_ABANDONED pdestructorcall (pdestructorcall_returned[.LINE = $(pdestructorcall_returned.LINE + 1)]))',
]
review.CASES[OBJECT]['checks'].insert(
    review.CASES[OBJECT]['checks'].index('pdestructorcall.OBJECT = n_arg') + 1,
    'pdestructorcall.TARGET = METHOD_TARGET n_arg porigin_arg')
review.CASES[OBJECT]['checks'].extend(derived_object)
DERIVED[OBJECT] = len(derived_object)

ARRAY = 'alias-handler-value-throw-keeps-real-owner-field-and-full-exit'
derived_array = ['$executor_tick_caught(S_after[.EXITSTATUS = 7]) = eps',
                 '$executor_tick_caught(S_after[.SHUTDOWN.COMPLETION = NORMAL]) = eps']
review.CASES[ARRAY]['checks'].extend(derived_array)
DERIVED[ARRAY] = len(derived_array)

QUEUE = 'old-tick-parent-does-not-authorize-a-later-queue-selection'
derived_queue = [
    'pdestructioncleanup_queue = $eager_cleanup_record(S, DESTRUCTOR_RESULT pdestructorcall_queue)',
    'S_later = S[.DESTRUCTION.ABANDONED = S.DESTRUCTION.ABANDONED ++ [pdestructioncleanup_queue]]',
    '$eager_cleanup_valid(S_later, pdestructioncleanup_queue)',
    '$executor_abandoned(S_later, pdestructioncleanup_queue) = (pexecutorqueue)',
    '$executor_tick_parent_row(S_later, pdestructioncleanup_queue, pdestructioncleanup_parent) = eps',
    '$executor_tick_bailout(S_later) = eps',
    '$executor_renderable(S_later, n_old)',
    'S_later_throw = S_later[.TODO = eps][.COMPLETION = UNCAUGHT n_old]',
    '$executor_tick_caught(S_later_throw) = eps',
]
review.CASES[QUEUE]['checks'].extend(derived_queue)
DERIVED[QUEUE] = len(derived_queue)


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=480) else 1)
