#!/usr/bin/env python3
"""Preserved request renderer throwing-handler fatal controls."""
import generator_request_render_handler_peer_sources as previous

driver = previous.driver

UNSUPPORTED = {
    'peer-request-render-handler-throws': (
        b'''<?php
class PayloadRenderHandlerAbort{function __destruct(){echo "D";}}
class LaterRenderHandlerAbort{function __destruct(){echo "Q";}}
class RenderHandlerAbort extends Exception{function __toString():string{global $wg,$wp,$wi;echo "U",(int)($wg->get()!==null),":",(int)($wp->get()!==null),":",(int)($wi->get()!==null),":",(int)(get_exception_handler()===null);return parent::__toString();}}
function handledRenderAbort($e){global $wi;$wi=WeakReference::create($e);echo "H";throw new RenderHandlerAbort("handler");}
class RenderHandlerParent extends Exception{function __toString():string{global $wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);set_exception_handler("handledRenderAbort");throw new Exception("render");}function __destruct(){echo "O";}}
function requestRenderHandlerAbort(){try{yield new PayloadRenderHandlerAbort;}finally{echo "F";throw new RenderHandlerParent("new");}}
$later=new LaterRenderHandlerAbort;$g=requestRenderHandlerAbort();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FT1:1HU1:1:1:1', 'Generator request fatal renderer handler or warning exception', 255),
    'peer-request-render-handler-throw-release-before-bailout': (
        b'''<?php
class PayloadRenderHandlerRelease{function __destruct(){echo "D";}}
class LaterRenderHandlerRelease{function __destruct(){echo "Q";}}
class RenderHandlerRelease extends Exception{function __toString():string{global $wg,$wp,$wi;echo "U",(int)($wg->get()!==null),":",(int)($wp->get()!==null),":",(int)($wi->get()!==null),":",(int)(get_exception_handler()===null);return parent::__toString();}function __destruct(){global $wg,$wp,$wi;echo "I",(int)($wg->get()!==null),":",(int)($wp->get()!==null),":",(int)($wi->get()!==null);error_reporting(0);}}
function handledRenderRelease($e){global $wi;$wi=WeakReference::create($e);echo "H";throw new RenderHandlerRelease("handler-release");}
class RenderHandlerReleaseParent extends Exception{function __toString():string{global $wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);set_exception_handler("handledRenderRelease");throw new Exception("render");}function __destruct(){echo "O";}}
function requestRenderHandlerRelease(){try{yield new PayloadRenderHandlerRelease;}finally{echo "F";throw new RenderHandlerReleaseParent("new");}}
$later=new LaterRenderHandlerRelease;$g=requestRenderHandlerRelease();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FT1:1HU1:1:1:1I1:1:1', 'Generator request fatal renderer handler or warning exception', 255),
}

CASES = {name: (row[0], row[1], row[3]) for name, row in UNSUPPORTED.items()}

EXTRA_WATCHED = previous.EXTRA_WATCHED + [
    'tests/semantics/generator_request_render_handler_throw_peer_sources.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.EXPECTED_STATUSES = {name: 'php_error' for name in CASES}
    driver.NATIVE_ERROR_PREFIXES = {
        'peer-request-render-handler-throws':
            b'Fatal error: Uncaught RenderHandlerAbort: handler',
        'peer-request-render-handler-throw-release-before-bailout':
            b'Fatal error: Uncaught RenderHandlerRelease: handler-release',
    }
    driver.WATCHED += EXTRA_WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
