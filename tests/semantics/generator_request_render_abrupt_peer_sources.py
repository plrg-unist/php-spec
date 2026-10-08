#!/usr/bin/env python3
"""Preserved request-fatal renderer throw and its original unsupported boundary."""
import generator_force_close_review as driver


UNSUPPORTED = {
    'peer-request-render-throws-with-live-generator-cache': (
        b'''<?php
class PayloadRenderAbort{function __destruct(){echo "D";}}
class LaterRenderAbort{function __destruct(){echo "Q";}}
class RenderAbortException extends Exception{function __toString():string{global $wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);throw new Exception("render");}}
function requestRenderAbort(){try{yield new PayloadRenderAbort;}finally{echo "F";throw new RenderAbortException("new");}}
$later=new LaterRenderAbort;$g=requestRenderAbort();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FT1:1', 'Generator request fatal rendering exception', 255),
}

CASES = {name: (row[0], row[1], row[3]) for name, row in UNSUPPORTED.items()}

EXTRA_WATCHED = [
    'spec/semantics/152-throwable-runtime.watsup',
    'spec/semantics/163-throwable-trace-storage.watsup',
    'spec/semantics/168-user-string-runtime.watsup',
    'spec/semantics/176-throwable-subclass-storage.watsup',
    'spec/semantics/206-error-handlers.watsup',
    'spec/semantics/207-error-handler-runtime.watsup',
    'spec/semantics/222-exception-handlers.watsup',
    'spec/semantics/231-shutdown-functions.watsup',
    'spec/semantics/237-display-errors.watsup',
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/296-weak-references.watsup',
    'spec/semantics/328-generator-reference-yields.watsup',
    'spec/semantics/340-generator-request-finally.watsup',
    'spec/semantics/355-generator-storage-pin.watsup',
    'spec/semantics/359-instance-storage-pin.watsup',
    'spec/semantics/360-generator-request-delegation.watsup',
    'spec/semantics/363-generator-request-abrupt.watsup',
    'tests/semantics/generator_request_render_abrupt_peer_sources.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.EXPECTED_STATUSES = {name: 'php_error' for name in CASES}
    driver.NATIVE_ERROR_PREFIXES = {
        'peer-request-render-throws-with-live-generator-cache':
            b'Fatal error: Uncaught Exception: render',
    }
    driver.WATCHED += EXTRA_WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
