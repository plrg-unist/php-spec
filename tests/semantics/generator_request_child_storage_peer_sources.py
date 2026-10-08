#!/usr/bin/env python3
"""Post-report child storage original; expected observation awaits native baseline."""
import generator_force_close_review as driver


CASES = {
    'peer-request-fatal-std-child-before-bailout': (
        b'''<?php
class PayloadPostReport363{function __destruct(){echo "D";}}
class LaterPostReport363{function __destruct(){echo "Q";}}
class LeafPostReport363{function __destruct(){global $wg,$wp;echo "L",(int)($wg->get()!==null),":",(int)($wp->get()!==null);}}
class ChildExceptionPostReport363 extends Exception{public $child;}
function handlerPostReport363($e){echo "H";$x=new ChildExceptionPostReport363("handler");$x->child=(object)["leaf"=>new LeafPostReport363];throw $x;}
set_exception_handler("handlerPostReport363");
function requestPostReport363(){try{yield new PayloadPostReport363;}finally{echo "F";throw new Exception("new");}}
$later=new LaterPostReport363;$g=requestPostReport363();$wg=WeakReference::create($g);$keepGen=&$wg;
$wp=WeakReference::create($g->current());$keepPayload=&$wp;echo "C|";
''', b'C|FHL1:1', 255),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.EXPECTED_STATUSES = {name: 'php_error' for name in CASES}
    driver.NATIVE_ERROR_PREFIXES = {
        'peer-request-fatal-std-child-before-bailout':
            b'Fatal error: Uncaught ChildExceptionPostReport363: handler',
    }
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
        'spec/semantics/359-instance-storage-pin.watsup',
        'spec/semantics/360-generator-request-delegation.watsup',
        'spec/semantics/363-generator-request-abrupt.watsup',
        'tests/semantics/generator_request_child_storage_peer_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
