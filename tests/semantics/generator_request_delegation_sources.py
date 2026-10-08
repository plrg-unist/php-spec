#!/usr/bin/env python3
"""Request delegation cache originals; expectations are provisional until run."""
import generator_force_close_review as driver

CASES = {
    'request-array-delegate-retains-current-through-storage': (
        b'''<?php
class ValueRequest360{function __destruct(){global $wg;$local=$wg->get();echo "D",(int)($local!==null),":",(int)($local->current()===null);}}
function arrayRequest360(){try{yield from [new ValueRequest360];}finally{echo "O";}}
$g=arrayRequest360();$g->current();$wg=WeakReference::create($g);$wa=&$wg;echo "C|";
''', b'C|OD1:1', 0),
    'request-iterator-delegate-retires-input-before-finally-keeps-current': (
        b'''<?php
class ValueRequest360{function __destruct(){global $wg;$local=$wg->get();echo "D",(int)($local!==null),":",(int)($local->current()===null);}}
class IteratorRequest360 implements Iterator{
private $value;
function __construct(){$this->value=new ValueRequest360;}
function rewind():void{}
function valid():bool{return true;}
function current():mixed{return $this->value;}
function key():mixed{return 0;}
function next():void{}
function __destruct(){echo "I";}
}
function iteratorRequest360(){try{yield from new IteratorRequest360;}finally{echo "O";}}
$g=iteratorRequest360();$g->current();$wg=WeakReference::create($g);$wa=&$wg;echo "C|";
''', b'C|IOD1:1', 0),
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
        'spec/semantics/289-generator-delegation.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'tests/semantics/generator_request_delegation_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
