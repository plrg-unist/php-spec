#!/usr/bin/env python3
"""Generator storage pin through ordered throwing callbacks and RETURN reads."""
import generator_force_close_review as driver

CASES = {
    'closed-storage-pin-return-throw-priority': (
        b'''<?php
class CapturePinThrow355{function __destruct(){global $wg;echo "C",(int)($wg->get()!==null);throw new Exception("capture");}}
class ValuePinThrow355{function __destruct(){global $wg;$local=$wg->get();echo "V",(int)($local!==null),":",(int)($local->getReturn()===$this);throw new Exception("value");}}
$capture=new CapturePinThrow355;$value=new ValuePinThrow355;
$fn=function(&$value)use(&$capture){yield 1;return $value;};
$g=$fn($value);unset($fn);$g->current();$g->next();
$wg=WeakReference::create($g);unset($capture,$value);echo "C|";
try{unset($g);}catch(Throwable $error){echo "E",$error->getMessage(),":",$error->getPrevious()->getMessage();}
echo "|",(int)($wg->get()===null);
''', b'C|C1V1:1Evalue:capture|1', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/281-fibers.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'tests/semantics/generator_storage_pin_peer_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
