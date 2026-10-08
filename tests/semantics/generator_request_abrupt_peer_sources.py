#!/usr/bin/env python3
"""Request-close fatal originals; native forecasts remain provisional until run."""
import generator_force_close_review as driver


UNSUPPORTED = {
    'peer-request-uncaught-finally-required': (
        b'''<?php
function request340(){try{yield 1;}finally{echo "F";throw new Exception("new");}}
$g=request340();echo "C|",$g->current(),"|";
''', b'C|1|F', 'Generator request-close uncaught exception', 255),
    'peer-request-handler-throw-required': (
        b'''<?php
function caught340($e){echo "H";throw new Exception("handler");}
set_exception_handler("caught340");
function request340(){try{yield 1;}finally{echo "F";throw new Exception("new");}}
$g=request340();echo "C|",$g->current(),"|";
''', b'C|1|FH', 'Generator request-close exception-handler failure', 255),
    'peer-request-fatal-abandons-cache-and-later-destructor': (
        b'''<?php
class PayloadFatalRequest{function __destruct(){echo "D";}}
class LaterFatalRequest{function __destruct(){echo "Q";}}
function requestFatal(){try{yield new PayloadFatalRequest;}finally{echo "F";throw new Exception("new");}}
$later=new LaterFatalRequest;$g=requestFatal();$g->current();echo "C|";
''', b'C|F', 'Generator request-close uncaught exception', 255),
    'peer-request-fatal-render-retains-generator-and-cache': (
        b'''<?php
class PayloadRenderRequest{function __destruct(){echo "D";}}
class LaterRenderRequest{function __destruct(){echo "Q";}}
class RenderRequestException extends Exception{function __toString():string{global $wg,$wp;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null);return "rendered-request";}}
function requestRender(){try{yield new PayloadRenderRequest;}finally{echo "F";throw new RenderRequestException("new");}}
$later=new LaterRenderRequest;$g=requestRender();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FT1:1', 'Generator request-close uncaught exception', 255),
}

NATIVE_ERROR_PREFIXES = {
    'peer-request-uncaught-finally-required': b'Fatal error: Uncaught Exception: new',
    'peer-request-handler-throw-required': b'Fatal error: Uncaught Exception: handler',
    'peer-request-fatal-abandons-cache-and-later-destructor': b'Fatal error: Uncaught Exception: new',
    'peer-request-fatal-render-retains-generator-and-cache': b'Fatal error: Uncaught rendered-request',
}


def main():
    driver.CASES = {}
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = UNSUPPORTED
    driver.NATIVE_ERROR_PREFIXES = NATIVE_ERROR_PREFIXES
    driver.WATCHED += [
        'spec/semantics/152-throwable-runtime.watsup',
        'spec/semantics/176-throwable-subclass-storage.watsup',
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/231-shutdown-functions.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'spec/semantics/360-generator-request-delegation.watsup',
        'tests/semantics/generator_request_abrupt_peer_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
