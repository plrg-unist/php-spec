#!/usr/bin/env python3
"""Independent fresh-store and ordinary storage-order candidates."""
import generator_force_close_review as driver

CASES = {
    'peer-fresh-store-closes-before-observer': (
        b'<?php class O340{function __destruct(){global $g;echo "P",(int)$g->valid(),":",(int)($g->current()===null);}} function fresh340(){echo "B";try{yield 1;}finally{echo "F";}} $g=fresh340();$ga=&$g;$o=new O340;$oa=&$o;echo "C|";',
        b'C|P0:1', 0),
    'peer-fresh-store-releases-reference-parameter': (
        b'''<?php
class Param340{function __destruct(){echo "D";}}
class Observer340{function __destruct(){global $g;echo "P",(int)$g->valid(),":",(int)($g->current()===null);}}
function fresh340(&$value){echo "B";try{yield $value;}finally{echo "F";}}
$value=null;$g=fresh340($value);$ga=&$g;$o=new Observer340;$oa=&$o;
$value=new Param340;unset($value);echo "C|";
''', b'C|DP0:1', 0),
    'peer-fresh-store-handler-precedes-later-parameter-release': (
        b'''<?php
class First349{function __destruct(){echo "A";throw new Exception("parameter");}}
class Second349{function __destruct(){echo "B";}}
class Observer349{function __destruct(){global $g;echo "P",(int)$g->valid(),":",(int)($g->current()===null);}}
function caught349($e){global $g,$w;echo "H",(int)($w->get()!==null),":",(int)$g->valid();}
set_exception_handler("caught349");
function fresh349(&$first,&$second){echo "X";try{yield 1;}finally{echo "F";}}
$first=null;$second=null;$g=fresh349($first,$second);$ga=&$g;$o=new Observer349;$oa=&$o;
$first=new First349;$second=new Second349;$w=WeakReference::create($second);$wa=&$w;
unset($first,$second);echo "C|";
''', b'C|AH1:0BP0:1', 0),
    'peer-reacquired-generator-releases-closure-before-cache': (
        b'<?php class Cap340{function __destruct(){echo "C";}} class Val340{function __destruct(){echo "V";}} class Obs340{function __destruct(){global $w;$h=$w->get();echo "P",(int)($h!==null);}} $capture=null;$value=null;$fn=function &(&$value)use(&$capture){try{$self=yield $value;yield $value;}finally{echo "F";}};$g=$fn($value);$g->current();$g->send($g);$w=WeakReference::create($g);$wa=&$w;unset($g,$fn);$o=new Obs340;$oa=&$o;$capture=new Cap340;$value=new Val340;unset($capture,$value);echo "C|";',
        b'C|FP1CV', 0),
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
        'tests/semantics/generator_request_fresh_peer_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
