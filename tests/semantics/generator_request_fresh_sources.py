#!/usr/bin/env python3
"""Fresh request frames: activation, real receivers and preserved Closure owners."""
import generator_force_close_review as driver

CASES = {
    'fresh-pure-request-activation': (
        b'''<?php
function fresh349(){echo "B";try{yield 1;}finally{echo "F";}}
$g=fresh349();$ga=&$g;echo "C|";
''', b'C|', 0),
    'fresh-self-reference-becomes-borrowed-store-bucket': (
        b'''<?php
class Observer349{function __destruct(){global $w;$h=$w->get();echo "P",(int)($h!==null);if($h!==null){echo ":",(int)$h->valid(),":",(int)($h->current()===null);}}}
function fresh349(&$self){echo "B";try{yield 1;}finally{echo "F";}}
$g=fresh349($g);$w=WeakReference::create($g);$wa=&$w;unset($g);
$o=new Observer349;$oa=&$o;echo "C|";
''', b'C|P1:0:1', 0),
    'fresh-closure-owner-survives-frame-retirement': (
        b'''<?php
class Capture349{function __destruct(){echo "C";}}
class Value349{function __destruct(){echo "V";}}
class Observer349{function __destruct(){global $g,$w;echo "P",(int)($w->get()!==null),":",(int)$g->valid(),":",(int)($g->current()===null);}}
$capture=null;$value=null;$fn=function(&$value)use(&$capture){echo "B";try{yield $value;}finally{echo "F";}};
$w=WeakReference::create($fn);$wa=&$w;$g=$fn($value);$ga=&$g;unset($fn);
$o=new Observer349;$oa=&$o;$capture=new Capture349;$value=new Value349;
unset($capture,$value);echo "C|";
''', b'C|VP1:0:1C', 0),
    'fresh-method-releases-real-receiver': (
        b'''<?php
class Maker349{function fresh(){echo "B";try{yield 1;}finally{echo "F";}}function __destruct(){echo "M";}}
class Observer349{function __destruct(){global $g,$w;echo "P",(int)($w->get()===null),":",(int)$g->valid();}}
$m=new Maker349;$w=WeakReference::create($m);$wa=&$w;$g=$m->fresh();$ga=&$g;
unset($m);$o=new Observer349;$oa=&$o;echo "C|";
''', b'C|MP1:0', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'tests/semantics/generator_request_fresh_sources.py',
        'tests/semantics/generator_request_fresh_peer_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
