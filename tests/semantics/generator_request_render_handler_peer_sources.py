#!/usr/bin/env python3
"""Preserved native-observed request renderer handler originals."""
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
    'peer-request-render-inner-dtor-before-handler-restore': (
        b'''<?php
class PayloadRenderInnerDtor{function __destruct(){echo "D";}}
class LaterRenderInnerDtor{function __destruct(){echo "Q";}}
class InnerHandledRender extends Exception{function __destruct(){global $wg,$wp;echo "I",(int)($wg->get()!==null),":",(int)($wp->get()!==null),":",(int)(get_exception_handler()===null);}}
function handledInnerRenderDtor($e){global $wg,$wp;echo "H",(int)($wg->get()!==null),":",(int)($wp->get()!==null);}
class RenderInnerDtorException extends Exception{function __toString():string{global $wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);set_exception_handler("handledInnerRenderDtor");throw new InnerHandledRender("render");}function __destruct(){global $wg,$wp;echo "O",(int)($wg->get()!==null),":",(int)($wp->get()!==null);}}
function requestRenderInnerDtor(){try{yield new PayloadRenderInnerDtor;}finally{echo "F";throw new RenderInnerDtorException("new");}}
$later=new LaterRenderInnerDtor;$g=requestRenderInnerDtor();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FT1:1H1:1I1:1:1O1:1', 'Generator request fatal rendering exception', 255),
}

CASES = {name: (row[0], row[1], row[3]) for name, row in UNSUPPORTED.items()}

EXTRA_WATCHED = previous.EXTRA_WATCHED + [
    'spec/semantics/157-throwable-properties.watsup',
    'spec/semantics/158-throwable-methods.watsup',
    'spec/semantics/164-throwable-trace-methods.watsup',
    'tests/semantics/generator_request_render_handler_peer_sources.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.EXPECTED_STATUSES = {name: 'php_error' for name in CASES}
    driver.NATIVE_ERROR_PREFIXES = {
        'peer-request-render-handler-returns':
            b'Warning: RenderHandlerException::__toString() must return a string',
        'peer-request-render-inner-dtor-before-handler-restore':
            b'Warning: RenderInnerDtorException::__toString() must return a string',
    }
    driver.WATCHED += EXTRA_WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
