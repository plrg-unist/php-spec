#!/usr/bin/env python3
"""Independent request-close originals; native observations must validate these cuts."""
import generator_force_close_review as driver

CASES = {
    'peer-pure-generator-request-finally': (
        b'''<?php
function request340(){try{yield 7;}finally{echo "F";}}
$g=request340();echo "C|",$g->current(),"|";
''', b'C|7|F', 0),
    'peer-request-shutdown-before-finally': (
        b'''<?php
function shutdown340(){echo "S";}
register_shutdown_function("shutdown340");
function request340(){try{yield 7;}finally{echo "F";}}
$g=request340();echo "C|",$g->current(),"|";
''', b'C|7|SF', 0),
    'peer-request-direct-globals-reverse': (
        b'''<?php
function request340($value,$label){try{yield $value;}finally{echo $label;}}
$a=request340(1,"A");$b=request340(2,"B");echo "C|",$a->current(),$b->current(),"|";
''', b'C|12|BA', 0),
    'peer-request-reference-globals-store-order': (
        b'''<?php
function request340($value,$label){try{yield $value;}finally{echo $label;}}
$a=request340(1,"A");$aa=&$a;$b=request340(2,"B");$bb=&$b;
echo "C|",$a->current(),$b->current(),"|";
''', b'C|12|AB', 0),
    'peer-request-handler-before-cache-retirement': (
        b'''<?php
class Payload340{function __destruct(){echo "D";}}
function caught340($e){global $w;echo "H",(int)($w->get()!==null),"|";}
set_exception_handler("caught340");
function request340(){try{yield new Payload340;}finally{echo "F";throw new Exception("new");}}
$g=request340();$w=WeakReference::create($g->current());$wa=&$w;echo "C|";
''', b'C|FH1|D', 0),
    'peer-request-store-close-retains-cache': (
        b'''<?php
class Payload340{public $value=8;function __destruct(){echo "D";}}
class Observer340{function __destruct(){global $g,$w;echo "P",(int)$g->valid(),":",(int)($g->current()===null),":",$w->get()->value,":",(int)($w->get()!==null);}}
function request340(){try{yield new Payload340;}finally{echo "F";}}
$g=request340();$ga=&$g;$w=WeakReference::create($g->current());$wa=&$w;
$observer=new Observer340;$oa=&$observer;echo "C|";
''', b'C|FDP0:1:8:1', 0),
    'peer-request-paused-finally-drops-backed-exception': (
        b'''<?php
function caught340($e){echo $e->getMessage(),":",$e->getPrevious()===null?"N":"P";}
set_exception_handler("caught340");
function request340(){try{try{throw new Exception("old");}finally{echo "A";yield 1;echo "X";}}finally{echo "O";throw new Exception("new");}}
$g=request340();echo "C|",$g->current(),"|";
''', b'C|A1|Onew:N', 0),
    'peer-request-store-zero-owner-bucket-remains-live': (
        b'''<?php
class Payload340{function __destruct(){echo "D";}}
class Observer340{function __destruct(){global $w;$h=$w->get();echo "P",(int)($h!==null);if($h!==null){echo ":",(int)$h->valid(),":",(int)($h->current()===null);}}}
function request340(){try{$self=yield 1;yield new Payload340;}finally{echo "F";}}
$g=request340();$g->current();$g->send($g);$w=WeakReference::create($g);$wa=&$w;
unset($g);$observer=new Observer340;$oa=&$observer;echo "C|";
''', b'C|FDP1:0:1', 0),
    'peer-request-store-reacquisition-later-release-frees-bucket': (
        b'''<?php
class Payload340{function __destruct(){echo "D";}}
class Observer340{function __destruct(){global $w;$h=$w->get();echo "P",(int)($h!==null);if($h!==null){echo ":",(int)$h->valid(),":",(int)($h->current()===null);}}}
class Later340{function __destruct(){global $w;echo "Q",(int)($w->get()===null);}}
function request340(){try{$self=yield 1;yield new Payload340;}finally{echo "F";}}
$g=request340();$g->current();$g->send($g);$w=WeakReference::create($g);$wa=&$w;
unset($g);$observer=new Observer340;$oa=&$observer;$later=new Later340;$la=&$later;echo "C|";
''', b'C|FDP1:0:1Q1', 0),
    'peer-request-handler-resume-keeps-zero-owner-bucket': (
        b'''<?php
class Payload340{function __destruct(){echo "D";}}
class Observer340{function __destruct(){global $w;$h=$w->get();echo "P",(int)($h!==null);if($h!==null){echo ":",(int)$h->valid(),":",(int)($h->current()===null);}}}
function caught340($e){echo "H";}
set_exception_handler("caught340");
function request340(){try{$self=yield 1;yield new Payload340;}finally{echo "F";throw new Exception("new");}}
$g=request340();$g->current();$g->send($g);$w=WeakReference::create($g);$wa=&$w;
unset($g);$observer=new Observer340;$oa=&$observer;echo "C|";
''', b'C|FHDP1:0:1', 0),
}

# The two historical abrupt originals now compare exactly in
# generator_request_abrupt_peer_sources.py (363); their old refusal cuts remain zero.


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.NATIVE_ERROR_PREFIXES = {}
    driver.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'tests/semantics/generator_force_close_protocol.py',
        'tests/semantics/generator_request_finally_sources.py',
        'tests/semantics/generator_request_finally_peer_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
