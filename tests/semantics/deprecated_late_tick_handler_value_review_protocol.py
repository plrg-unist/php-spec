#!/usr/bin/env python3
"""Check owning handler results while the original null-C call is pending."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent
DERIVED = {}


def source(name):
    return (HERE / f'deprecated_late_tick_handler_value_{name}.php').read_text()


review.CASES = {
    'handler-result-child-keeps-original-c-and-exception-protections': {
        'source': source('object'),
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_returned) :: ptask_tail* -- if $object_name(S, pdestructorcall_returned.OBJECT) = $ptascii("HandlerValue24Result")',
        'checks': [
            'S.DESTRUCTION.CALLS = [pdestructorcall_returned, pdestructorcall_arg]',
            'pdestructorcall_arg.OPERATION = (pdestructionoperation_tick)',
            'pdestructionoperation_tick.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
            'pdestructorcall_returned.OPERATION = (pdestructionoperation_value)',
            'pdestructionoperation_value.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            'pdestructionoperation_value.CLEANUP = (pdestructioncleanup)',
            'S.DESTRUCTION.CLEANUPS = [pdestructioncleanup]',
            'pdestructioncleanup.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            '~pdestructioncleanup.RELEASED',
            'pdestructionoperation_value.COMPLETION = NORMAL',
            'pdestructionoperation_value.PENDING = eps',
            'pdestructionoperation_tick.COMPLETION = NORMAL',
            'pdestructionoperation_tick.PENDING = eps',
            'n_arg = pdestructorcall_arg.OBJECT',
            'n_returned = pdestructorcall_returned.OBJECT',
            'n_exception = pexceptioncall.OBJECT',
            '~pdestructorcall_arg.USER', 'pdestructorcall_arg.CALLER = eps',
            '~pdestructorcall_returned.USER',
            'pdestructorcall_returned.CALLER = eps',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.COMPLETION = NORMAL',
            'S.DESTRUCTION.ABANDONED = eps',
            'pexecutortick.COMPLETION = NORMAL',
            'S.SHUTDOWN.COMPLETION = NORMAL',
            'S.DESTRUCTION.COMPLETION = NORMAL', 'S.EXITSTATUS = 0',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$node_children(S, HOBJECT n_arg) = [HOBJECT n_child]',
            '$node_children(S, HOBJECT n_returned) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_exception) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            'S.EXCEPTIONHANDLER = eps',
            'S.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue_previous?)*',
            '(pvalue_previous?)* = [eps]',
            '$string_bytes(pexceptioncall.CALLBACK) = ($ptascii("handler_value24_exception"))',
            '$value_nodes(pexceptioncall.CALLBACK) = eps',
            '$throwable_live(S, n_exception)',
            '$destructor_call_live(S, pdestructorcall_arg)',
            '$destructor_c_return_source(S.TODO, pdestructorcall_arg)',
            '~$destructor_c_return_valid(S, pdestructorcall_arg)',
            '$destructor_enter_valid(S, pdestructorcall_returned)',
            '$eager_cleanup_valid(S, pdestructioncleanup)',
            '$eager_operation_source_valid(S, pdestructionoperation_value)',
            '$eager_operation_source_valid(S, pdestructionoperation_tick)',
            '$executor_tick_valid(S, pexecutortick)', '$executor_tick_scope(S)',
            '$output_final_destructors(S)', '$destructor_operational(S)',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            '$gc_state_valid(S)', '$exit_status_valid(S)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;")]',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
