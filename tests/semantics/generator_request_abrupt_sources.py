#!/usr/bin/env python3
"""Handler-fatal lifetime controls; forecasts stay provisional until native run."""
import generator_force_close_review as driver

UNSUPPORTED = {
    'request-handler-fatal-abandons-cache-and-later-destructor': (
        b'''<?php
class PayloadHandlerFatal{function __destruct(){echo "D";}}
class LaterHandlerFatal{function __destruct(){echo "Q";}}
function caughtHandlerFatal($e){echo "H";throw new Exception("handler");}
set_exception_handler("caughtHandlerFatal");
function requestHandlerFatal(){try{yield new PayloadHandlerFatal;}finally{echo "F";throw new Exception("new");}}
$later=new LaterHandlerFatal;$g=requestHandlerFatal();$g->current();echo "C|";
''', b'C|FH', 'Generator request-close exception-handler failure', 255),
    'request-handler-fatal-render-retains-original-exception': (
        b'''<?php
class PayloadHandlerRender{function __destruct(){echo "D";}}
class LaterHandlerRender{function __destruct(){echo "Q";}}
function replacementHandlerRender($e){echo "X";}
class HandlerRenderException extends Exception{function __toString():string{set_exception_handler("replacementHandlerRender");global $wg,$wp,$we;echo "T",(int)($wg->get()!==null),":",(int)($wp->get()!==null),":",(int)($we->get()!==null);return "rendered-handler";}}
function caughtHandlerRender($e){global $we;$we=WeakReference::create($e);$keep=&$we;echo "H";throw new HandlerRenderException("handler");}
set_exception_handler("caughtHandlerRender");
function requestHandlerRender(){try{yield new PayloadHandlerRender;}finally{echo "F";throw new Exception("new");}}
$later=new LaterHandlerRender;$g=requestHandlerRender();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FHT1:1:1', 'Generator request-close exception-handler failure', 255),
    'request-fatal-releases-exception-before-bailout': (
        b'''<?php
class PayloadReleaseFatal{function __destruct(){echo "D";}}
class LaterReleaseFatal{function __destruct(){echo "Q";}}
class ReleaseRequestException extends Exception{function __destruct(){global $wg,$wp;echo "E",(int)($wg->get()!==null),":",(int)($wp->get()!==null);$this->message="later";error_reporting(0);}}
function requestReleaseFatal(){try{yield new PayloadReleaseFatal;}finally{echo "F";throw new ReleaseRequestException("new");}}
$later=new LaterReleaseFatal;$g=requestReleaseFatal();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FE1:1', 'Generator request-close uncaught exception', 255),
}

NATIVE_ERROR_PREFIXES = {
    'request-handler-fatal-abandons-cache-and-later-destructor': b'Fatal error: Uncaught Exception: handler',
    'request-handler-fatal-render-retains-original-exception': b'Fatal error: Uncaught rendered-handler',
    'request-fatal-releases-exception-before-bailout': b'Fatal error: Uncaught ReleaseRequestException: new',
}


def main():
    driver.CASES = {}
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = UNSUPPORTED
    driver.NATIVE_ERROR_PREFIXES = NATIVE_ERROR_PREFIXES
    driver.WATCHED += [
        'spec/semantics/152-throwable-runtime.watsup',
        'spec/semantics/168-user-string-runtime.watsup',
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
        'spec/semantics/363-generator-request-abrupt.watsup',
        'tests/semantics/generator_request_abrupt_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
