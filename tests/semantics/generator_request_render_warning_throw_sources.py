#!/usr/bin/env python3
"""Observed request renderer warning throw and C-root handler redispatch."""
import generator_request_render_handler_peer_sources as previous

driver = previous.driver

CASES = {
    'request-render-warning-handler-throws': (
        b'''<?php
class PayloadRenderWarningThrow{function __destruct(){echo "D";}}
class LaterRenderWarningThrow{function __destruct(){echo "Q";}}
function handledWarningThrow($e){global $wi;echo $e->getMessage()==="render"?"H":"J";$wi=WeakReference::create($e);}
function warningRenderThrow($level,$message,$file,$line){global $wg,$wp,$wi;echo "W",(int)($wg->get()!==null),":",(int)($wp->get()!==null),":",(int)($wi->get()===null);throw new Exception("warning");}
class RenderWarningThrowParent extends Exception{function __toString():string{global $wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);set_exception_handler("handledWarningThrow");set_error_handler("warningRenderThrow");throw new Exception("render");}function __destruct(){global $wg,$wp;echo "O",(int)($wg->get()!==null),":",(int)($wp->get()!==null);}}
function requestRenderWarningThrow(){try{yield new PayloadRenderWarningThrow;}finally{echo "F";throw new RenderWarningThrowParent("new");}}
$later=new LaterRenderWarningThrow;$g=requestRenderWarningThrow();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FT1:1HW1:1:1JO1:1', 255),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.EXPECTED_STATUSES = {name: 'php_error' for name in CASES}
    driver.NATIVE_ERROR_PREFIXES = {
        'request-render-warning-handler-throws':
            b'Fatal error: Uncaught \n  thrown in {file} on line 7\n',
    }
    driver.WATCHED += previous.EXTRA_WATCHED + [
        'tests/semantics/generator_request_render_warning_throw_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
