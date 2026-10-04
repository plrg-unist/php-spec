#!/usr/bin/env python3
"""Source-reached renderer ownership, deferred exceptions and frozen events."""
import argparse
import json
from pathlib import Path
import exception_handler_state_review as fixture

SOURCES = {r['id']: r['source'] for r in json.loads(
    Path(__file__).with_name('shutdown_cases.json').read_text())}
VALID = fixture.VALID
DONE = [*fixture.DONE, 'S_done.CONSTCONTEXT = eps',
        'S_done.SHUTDOWN.RENDER = eps', 'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE']
fixture.CASES = {
    'renderer-is-sole-original-owner': {
        'source': SOURCES['render-captured-message-owner'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("w") '
                  '-- if $lookup(S.ENV, $ptascii("e")) = (n_cell) '
                  '-- if S.STORE[n_cell] = DEFINED PNULL'),
        'checks': [
            'S.SHUTDOWN.RENDER = (pshutdownrender)',
            'pshutdownrender.PHASE = SHUTDOWN_RENDER_TRACE',
            'pshutdownrender.MESSAGE = $ptascii("Array")',
            'pshutdownrender.ROOTMESSAGE = $ptascii("Array")',
            'pshutdownrender.PENDING = eps',
            '$throwable_field(S, pshutdownrender.ROOT, "message") = PSTRING $ptascii("later")',
            '$heap_owners($heap_graph(S), HOBJECT pshutdownrender.ROOT) = 1',
            'S.FRAMES = [pframe]',
            'pframe.TODO = [ERROR_HANDLER_RESULT perrorcall]',
            'perrorcall.RESUME = SHUTDOWN_RENDER pshutdownrender',
            'S_anchor = $constant_frame_scope(S, pframe, eps)',
            '$shutdown_render_valid(S_anchor, pshutdownrender)',
            '$error_entered_call_valid(S_anchor, perrorcall)',
            '~$call_task_valid(S, SHUTDOWN_RENDER pshutdownrender)',
            '~$shutdown_render_valid(S_anchor[.SHUTDOWN.RENDER = eps], pshutdownrender)',
            '~$shutdown_render_valid(S_anchor[.CONSTCONTEXT = ({ORIGIN pcallcontext.FUNCTION, LINE 2, FACTS eps})], pshutdownrender)',
            '~$error_entered_call_valid(S_anchor, perrorcall[.MESSAGE = $ptascii("wrong")])',
            'ptraceframe_builtin = {FILE eps, LINE $(-1), FUNCTION $ptascii("__toString"), CLASS ($ptascii("Exception")), TYPE ($ptascii("->")), ARGS eps, HASARGS true}',
            '$shutdown_render_trace_frame(S, pframe, eps) = [ptraceframe_builtin]',
            '$shutdown_render_trace_frame(S, pframe[.TODO = [ERROR_HANDLER_RESULT (perrorcall[.MESSAGE = $ptascii("wrong")])]], eps) = eps',
            '$eval_exception_trace(S) = [ptraceframe_handler, ptraceframe_builtin]',
            'ptraceframe_handler.FILE = eps', 'ptraceframe_handler.FUNCTION = $ptascii("w")',
            *VALID,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = REQUESTFATAL $ptascii("E") $ptascii("Array") 2',
            'S_done.EVENTS = [OUTPUT $ptascii("W;"), STDERR ptbytes_fatal, OUTPUT $ptascii("S;")]',
            '~((HOBJECT pshutdownrender.ROOT) <- S_done.ALLOCATIONS)',
            '$drive(S_paused[.COMPLETION = NORMAL], 2000) = S_done',
            *DONE,
        ],
    },
    'pending-warning-completes-builtin-cache': {
        'source': '<?php class E extends Exception{function change(){$this->message=[];}}'
                  'function s(){echo "S;";}register_shutdown_function("s");'
                  'function w($n,$m,$f,$l){echo "W;";set_exception_handler(function($e){echo "H;";});throw new Exception("warning");}'
                  '$e=new E("old");$e->__toString();$e->change();set_error_handler("w");error_reporting(3);throw $e;',
        'stage': ('S.TODO = [SHUTDOWN_RENDER pshutdownrender] '
                  '-- if pshutdownrender.PHASE = SHUTDOWN_RENDER_TRACE '
                  '-- if pshutdownrender.PENDING = (n_inner)'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps',
            '$shutdown_render_valid(S, pshutdownrender)',
            '$heap_owners($heap_graph(S), HOBJECT n_inner) = 1',
            '$task_nodes(SHUTDOWN_RENDER pshutdownrender) = [HOBJECT pshutdownrender.ROOT, HOBJECT n_inner]',
            '$throwable_previous_id(S, n_inner) = eps',
            '$throwable_field(S, pshutdownrender.ROOT, "string") = PSTRING ptbytes_before',
            'ptbytes_before =/= eps',
            '$shutdown_render_trace(S, pshutdownrender) = $ptascii("#0 {main}") ++ [10]',
            *VALID,
            'PhpStep: S ~> S_body',
            'S_body.TODO = [THROW_SEARCH n_inner, SHUTDOWN_RENDER pshutdownrender_return]',
            'pshutdownrender_return.PHASE = SHUTDOWN_RENDER_RETURN',
            'pshutdownrender_return.PENDING = (n_inner)',
            '$task_nodes(SHUTDOWN_RENDER pshutdownrender_return) = [HOBJECT pshutdownrender.ROOT]',
            '$heap_owners($heap_graph(S_body), HOBJECT n_inner) = 1',
            '$exception_dispatch_ready(S_body)',
            '$throwable_field(S_body, pshutdownrender.ROOT, "string") = PSTRING pshutdownrender_return.TEXT',
            'pshutdownrender_return.TEXT =/= ptbytes_before',
            '~$shutdown_render_valid(S_body, pshutdownrender)',
            '~$shutdown_render_valid(S_body, pshutdownrender_return[.CURRENT = n_inner])',
            'S_done = $drive(S_body, 2000)',
            'S_done.COMPLETION = REQUESTFATAL $ptascii("E") $ptascii("Array") 1',
            'S_done.EVENTS = [OUTPUT $ptascii("W;"), OUTPUT $ptascii("H;"), OUTPUT $ptascii("W;"), OUTPUT $ptascii("H;"), STDERR ptbytes_fatal, OUTPUT $ptascii("S;")]',
            *DONE,
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if fixture.run(args.case) else 1)
