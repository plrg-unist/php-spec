#!/usr/bin/env python3
"""Check handled null-C tick throws, real owners and resumed module cleanup."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent


def source(name):
    return (HERE / f'deprecated_late_tick_handler_{name}.php').read_text()


TICK = ['pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
        'pdestructorcall.OBJECT = n_arg', '~pdestructorcall.USER',
        'pdestructorcall.CALLER = eps', 'pdestructionoperation.COMPLETION = NORMAL',
        'pdestructionoperation.PENDING = eps', 'S.DESTRUCTION.ABANDONED = eps']
VALID = ['$executor_tick_valid(S, pexecutortick)', '$executor_tick_scope(S)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
         '$exit_status_valid(S)']
DONE = ['S_done = $drive_steps(S, 4000)', 'S_done.TODO = eps',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.TICKENTRIES = eps',
        'S_done.SHUTDOWN.ENTRIES = eps', 'S_done.DESTRUCTION.ABANDONED = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$exit_status_valid(S_done)']
DERIVED = {'handler-dispatch-keeps-original-module-owners': 3,
           'handler-frame-borrows-no-destructor-receiver': 2}


def phase(completion, status):
    return [f'pexecutortick.COMPLETION = {completion}',
            f'S.SHUTDOWN.COMPLETION = {completion}',
            f'S.DESTRUCTION.COMPLETION = {completion}',
            f'S.EXITSTATUS = {status}', 'S.COMPLETION = NORMAL']


review.CASES = {
    'handler-dispatch-keeps-original-module-owners': {
        'source': source('raw'),
        'stage': 'S.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
        'checks': [
            *TICK, *phase('NORMAL', 0),
            'n_exception = pexceptioncall.OBJECT',
            'S.EXCEPTIONHANDLER = eps',
            'S.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue_rest?)*',
            'pexceptioncall.TARGET = eps', 'pexceptioncall.SENT = eps',
            'pexceptioncall.RECEIVED = eps', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$task_nodes(EXCEPTION_HANDLER_INVOKE pexceptioncall) = [HOBJECT n_exception]',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$string_bytes($throwable_field(S, n_exception, "string")) = (eps)',
            '$exception_invoke_valid(S, pexceptioncall)',
            '$call_task_valid(S, EXCEPTION_HANDLER_INVOKE pexceptioncall)',
            '~$exception_invoke_valid(S[.EXCEPTIONHANDLER = (pexceptioncall.CALLBACK)], pexceptioncall)',
            '~$exception_invoke_valid(S[.EXCEPTIONHANDLERS = eps], pexceptioncall)',
            '~$executor_tick_active(S[.TODO = [EXCEPTION_HANDLER_INVOKE pexceptioncall]], pexecutortick)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID,
        ],
    },
    'handler-frame-borrows-no-destructor-receiver': {
        'source': source('review_exit263_tail_queue'),
        'stage': 'S.TODO = (EMIT z_echo) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("handler_tick21_scalar") -- if S.FRAMES = [pframe] -- if pframe.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_saved*',
        'checks': [
            *TICK, *phase('EXITED 263', 263),
            'n_exception = pexceptioncall.OBJECT', 'pcallcontext.ARGC = 1',
            'pcallcontext.CALLSITE = eps', 'pcallcontext.LINE = $(-1)',
            'pcallcontext.INSTANCE = eps', 'pcallcontext.RECEIVER = eps',
            'pcallcontext.EXTRA = eps',
            'pexceptioncall.RECEIVED = (KNOWN (POBJECT n_exception))',
            '$lookup(S.ENV, $ptascii("error")) = (n_parameter)',
            'S.STORE[n_parameter] = DEFINED (POBJECT n_exception)',
            'S.RESULT = KNOWN pvalue_echo', '$string_bytes(pvalue_echo) = ($ptascii("H;"))',
            'S.EXCEPTIONHANDLER = eps',
            'S.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue_rest?)*',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$exception_context_valid(S, pcallcontext)', '$call_current_valid(S)',
            '~$exception_context_valid(S[.CURRENT = (pcallcontext[.ARGC = 0])], pcallcontext[.ARGC = 0])',
            '~$exception_context_valid(S[.CURRENT = (pcallcontext[.CALLSITE = (pcallcontext.FUNCTION)])], pcallcontext[.CALLSITE = (pcallcontext.FUNCTION)])',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID,
        ],
    },
    'scalar-result-is-discarded-with-full-exit-still-263': {
        'source': source('review_exit263_tail_queue'),
        'stage': 'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
        'checks': [
            *TICK, *phase('EXITED 263', 263),
            'S.RESULT = KNOWN (PINT 23)', 'n_exception = pexceptioncall.OBJECT',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.EXCEPTIONHANDLER = eps',
            '$exception_result_valid(S, pexceptioncall)',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$string_bytes($throwable_field(S, n_exception, "string")) = (eps)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;")]',
            *VALID,
            'PhpStep: S ~> S_retval',
            'S_retval.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_retval) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_retval) :: (EXCEPTION_HANDLER_CLEAN pexceptioncall false) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
            'pdestructionrelease_retval.JOBS = eps',
            'pdestructionoperation_retval.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            'S_retval.RESULT = KNOWN PNULL', 'S_retval.EXITSTATUS = 263',
            '$heap_owners($heap_graph(S_retval), HOBJECT n_exception) = 1',
            '$output_final_destructors(S_retval)', '$destructor_operational(S_retval)',
            '$call_descriptors_valid(S_retval)', '$heap_valid($heap_graph(S_retval))',
        ],
    },
    'original-exception-retires-before-tail-and-queue-resume': {
        'source': source('review_exit263_tail_queue'),
        'stage': 'S.TODO = (EXCEPTION_HANDLER_CLEAN pexceptioncall true) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
        'checks': [
            *TICK, *phase('EXITED 263', 263),
            'n_exception = pexceptioncall.OBJECT', 'S.EXCEPTIONHANDLER = eps',
            'S.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue_rest?)*',
            'S.DESTRUCTION.CLEANUPS = [pdestructioncleanup]',
            'pdestructioncleanup.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            'pdestructioncleanup.RELEASED',
            '$eager_cleanup_valid(S, pdestructioncleanup)',
            '$task_nodes(EXCEPTION_HANDLER_CLEAN pexceptioncall true) = eps',
            '~((HOBJECT n_exception) <- S.ALLOCATIONS)',
            '$objectprops_at(S.OBJECTPROPS, n_exception) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            'S.TICKENTRIES = [ptickentry_tail]', 'ptickentry_tail.ENTRY.ARGS = [POBJECT n_tail_arg]',
            '$callback_cache_nodes(ptickentry_tail.ENTRY) = [HOBJECT n_tail, HOBJECT n_tail]',
            'S.SHUTDOWN.ENTRIES = [pshutdownentry]', 'pshutdownentry.ARGS = [POBJECT n_queue_arg]',
            '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_tail) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_tail_arg) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_queue_arg) = 1',
            '$call_task_valid(S, EXCEPTION_HANDLER_CLEAN pexceptioncall true)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;")]',
            *VALID,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = S.TODO', 'S_paused.EXITSTATUS = 263',
            *DONE, 'S_done.COMPLETION = EXITED 263', 'S_done.EXITSTATUS = 263',
            'S_done.EXCEPTIONHANDLER = (pexceptioncall.CALLBACK)',
            'S_done.EXCEPTIONHANDLERS = (pvalue_rest?)*',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_tail) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_queue_arg) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;"), OUTPUT $ptascii("L;"), OUTPUT $ptascii("C;"), OUTPUT $ptascii("U;"), OUTPUT $ptascii("T;"), OUTPUT $ptascii("Q;")]',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
        ],
    },
    'bound-fcc-still-releases-receiver-after-handled-argument': {
        'source': source('review_normal_bound'),
        'stage': 'S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_OPERATION_EXIT pdestructionoperation, EXECUTOR_TICK_RELEASE pexecutortick false] -- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY.ENTRY.TARGET = CLOSURE_TARGET n_callback',
        'checks': [
            *phase('NORMAL', 0), 'S.DESTRUCTION.ABANDONED = eps',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg]',
            'pexecutortick.RECEIVER = (n_receiver)',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_receiver, HOBJECT n_callback]',
            '$node_children(S, HOBJECT n_callback) = [HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '~(n_receiver <- S.DESTRUCTION.CALLED)',
            '~((HOBJECT n_arg) <- S.ALLOCATIONS)', 'S.EXCEPTIONHANDLER = (pvalue_handler)',
            '$string_bytes(pvalue_handler) = ($ptascii("handler_tick21_null"))',
            'S.EXCEPTIONHANDLERS = [pvalue_previous?]', 'pvalue_previous? = eps',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;")]',
            *VALID, *DONE, 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;"), OUTPUT $ptascii("R;")]',
        ],
    },
    'captured-child-destructor-runs-before-executor-inactivity': {
        'source': source('owning_capture'),
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_child) :: ptask_tail* -- if $object_name(S, pdestructorcall_child.OBJECT) = $ptascii("HandledCapture21Child") -- if pdestructorcall_child.OPERATION = (pdestructionoperation) -- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
        'checks': [
            *phase('EXITED 7', 7), 'S.DESTRUCTION.ABANDONED = eps',
            'n_child = pdestructorcall_child.OBJECT', '~pdestructorcall_child.USER',
            'pdestructorcall_child.CALLER = eps', 'pdestructorcall_child.PENDING = eps',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg]',
            'pexecutortick.ENTRY.ENTRY.TARGET = CLOSURE_TARGET n_callback',
            '~((HOBJECT n_arg) <- S.ALLOCATIONS)',
            '~((HOBJECT n_callback) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
            'S.EXCEPTIONHANDLER = (pvalue_handler)',
            '$string_bytes(pvalue_handler) = ($ptascii("handled_capture21_exception"))',
            'S.EXCEPTIONHANDLERS = [pvalue_previous?]', 'pvalue_previous? = eps',
            '$call_task_valid(S, DESTRUCTOR_ENTER pdestructorcall_child)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;")]',
            *VALID, *DONE, 'S_done.COMPLETION = EXITED 7', 'S_done.EXITSTATUS = 7',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;"), OUTPUT $ptascii("K;")]',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
