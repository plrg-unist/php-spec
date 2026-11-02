#!/usr/bin/env python3
"""Reach the source Closure wrapper's inner-warning trace frames."""
from deprecated_closure_invoke_review_cases import CASES as SOURCES
import fiber_state_review as review


review.CASES = {
    'invoke-inner-warning-trace-head-inherits-call-location': {
        'source': SOURCES['invoke-inner-warning-trace-head-inherits-call-location'].decode(),
        'stage': 'S.CURRENT = (pcallcontext) '
                 '-- if $error_context_call(S, pcallcontext) = (perrorcall) '
                 '-- if perrorcall.RESUME = CLOSURE_INVOKE_ENTER ptask_source',
        'checks': [
            '$closure_invoke_source(ptask_source) = ((CLOSURE_TARGET n_closure, pnamedargs, porigin, z))',
            'z = 80',
            'perrorcall.LEVEL = 16384',
            '$closure_invoke_warning_context(S, pcallcontext)',
            '$trace_context(S, S.ENV, S.CURRENT) = [ptraceframe_head, ptraceframe_wrapper]',
            'ptraceframe_head.FILE = $call_sourcefile(S.FILES, porigin)',
            'ptraceframe_head.LINE = z',
            'ptraceframe_head.FUNCTION = $ptascii("head_notice")',
            'ptraceframe_wrapper.FILE = ptraceframe_head.FILE',
            'ptraceframe_wrapper.LINE = ptraceframe_head.LINE',
            'ptraceframe_wrapper.FUNCTION = $ptascii("__invoke")',
            'ptraceframe_wrapper.CLASS = ($ptascii("Closure"))',
            '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_done = $drive_steps(S, 4000)',
            'S_done.COMPLETION = NORMAL',
            r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=150) else 1)
