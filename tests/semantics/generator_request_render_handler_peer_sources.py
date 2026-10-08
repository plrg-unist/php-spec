#!/usr/bin/env python3
"""Unchanged live-handler renderer original; native forecasts are provisional."""
import generator_request_render_abrupt_peer_sources as previous

driver = previous.driver

UNSUPPORTED = {
    'peer-request-render-handler-returns': (
        b'''<?php
class PayloadRenderHandler{function __destruct(){echo "D";}}
class LaterRenderHandler{function __destruct(){echo "Q";}}
function handledRenderInner($e){global $wg,$wp;echo "H",(int)($wg->get()!==null),":",(int)($wp->get()!==null);}
class RenderHandlerException extends Exception{function __toString():string{global $wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);set_exception_handler("handledRenderInner");throw new Exception("render");}function __destruct(){global $wg,$wp;echo "O",(int)($wg->get()!==null),":",(int)($wp->get()!==null);}}
function requestRenderHandler(){try{yield new PayloadRenderHandler;}finally{echo "F";throw new RenderHandlerException("new");}}
$later=new LaterRenderHandler;$g=requestRenderHandler();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FT1:1H1:1O1:1', 'Generator request fatal rendering exception', 255),
}

EXTRA_WATCHED = previous.EXTRA_WATCHED + [
    'tests/semantics/generator_request_render_handler_peer_sources.py',
]


def main():
    driver.CASES = {}
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = UNSUPPORTED
    driver.NATIVE_ERROR_PREFIXES = {
        'peer-request-render-handler-returns':
            b'Warning: RenderHandlerException::__toString() must return a string',
    }
    driver.WATCHED += EXTRA_WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
