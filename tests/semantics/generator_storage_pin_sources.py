#!/usr/bin/env python3
"""Original probes for Generator free_storage weak liveness and readable caches."""
import generator_force_close_review as driver

CASES = {
    'closed-storage-weak-target-live-through-children': (
        b'''<?php
class CaptureWeak349{function __destruct(){global $wg;echo "C",(int)($wg->get()!==null);}}
class ValueWeak349{function __destruct(){global $wg;echo "V",(int)($wg->get()!==null);}}
$capture=new CaptureWeak349;$value=new ValueWeak349;
$fn=function(&$value)use(&$capture){yield 1;return $value;};
$g=$fn($value);unset($fn);$g->current();$g->next();
$wg=WeakReference::create($g);unset($capture,$value);echo "C|";unset($g);
''', b'C|C1V1', 0),
    'closed-storage-return-readable-through-children': (
        b'''<?php
class CaptureReturn349{function __destruct(){global $wg;$g=$wg->get();echo "C",(int)($g!==null),":",(int)($g->getReturn() instanceof ValueReturn349);}}
class ValueReturn349{function __destruct(){global $wg;$g=$wg->get();echo "V",(int)($g!==null),":",(int)($g->getReturn()===$this);}}
$capture=new CaptureReturn349;$value=new ValueReturn349;
$fn=function(&$value)use(&$capture){yield 1;return $value;};
$g=$fn($value);unset($fn);$g->current();$g->next();
$wg=WeakReference::create($g);unset($capture,$value);echo "C|";unset($g);echo "|",(int)($wg->get()===null);
''', b'C|C1:1V1:1|1', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'tests/semantics/generator_storage_pin_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
