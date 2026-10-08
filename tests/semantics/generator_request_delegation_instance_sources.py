#!/usr/bin/env python3
"""Actual359+360 Iterator-input interaction; expectation provisional until run."""
import generator_force_close_review as driver

CASES = {
    'request-iterator-input-child-before-outer': (
        b'''<?php
class ChildInputJoin360{function __destruct(){global $wi,$wg;echo "D",(int)($wi->get()===null),":",(int)($wg->get()!==null);}}
class IteratorInputJoin360 implements Iterator{public $value;function __construct(){global $wi;$this->value=new ChildInputJoin360;$wi=WeakReference::create($this);}function rewind():void{}function valid():bool{return true;}function current():mixed{return 7;}function key():mixed{return 0;}function next():void{}function __destruct(){echo "I";}}
function outerInputJoin360(){try{yield from new IteratorInputJoin360;}finally{echo "O";}}
$g=outerInputJoin360();$g->current();$wg=WeakReference::create($g);$keep=&$wg;echo "C|";
''', b'C|ID1:1O', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/281-fibers.watsup',
        'spec/semantics/289-generator-delegation.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'spec/semantics/359-instance-storage-pin.watsup',
        'spec/semantics/360-generator-request-delegation.watsup',
        'tests/semantics/generator_request_delegation_instance_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
