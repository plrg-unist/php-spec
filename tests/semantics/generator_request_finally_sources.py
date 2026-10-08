#!/usr/bin/env python3
"""Request-finally originals, including the unchanged former Unsupported source."""
import generator_force_close_review as driver
import reference_yield_terminal_review as prior

CASES = {
    'reference-terminal-active-finally-required': (
        prior.UNSUPPORTED['reference-terminal-active-finally-required'][0], b'C|7|F', 0),
    'request-container-held-generator': (
        b'''<?php
function request340(){try{yield 7;}finally{echo "F";}}
$a=[request340()];echo "C|",$a[0]->current(),"|";
''', b'C|7|F', 0),
    'request-nested-finally-skips-body-and-catch': (
        b'''<?php
function request340(){try{try{yield 7;echo "X";}catch(Throwable $e){echo "C";}finally{echo "I";}}finally{echo "O";}echo "S";}
$g=request340();echo "C|",$g->current(),"|";
''', b'C|7|IO', 0),
    'request-forced-reference-yield-rejects-before-cv': (
        b'''<?php
function &request340(&$value){try{yield $value;}finally{try{yield $missing;}catch(Error $e){echo "E";}echo "F";}}
$value=7;$g=request340($value);echo "C|",$g->current(),"|";
''', b'C|7|EF', 0),
    'request-resurrection-repeats-global-pass-once': (
        b'''<?php
class Payload340{function __destruct(){echo "D";}}
function request340(){try{yield new Payload340;}finally{global $w;echo "F";$GLOBALS["saved"]=$w->get();$GLOBALS["again"]=1;}}
$g=request340();$w=WeakReference::create($g);$wa=&$w;$g->current();echo "C|";
''', b'C|FD', 0),
    'request-resurrection-computed-global-receiver': (
        b'''<?php
class Payload340{function __destruct(){echo "D";}}
function request340(){try{yield new Payload340;}finally{echo "F";$GLOBALS["saved"]=$GLOBALS["w"]->get();$GLOBALS["again"]=1;}}
$g=request340();$w=WeakReference::create($g);$wa=&$w;$g->current();echo "C|";
''', b'C|FD', 0),
    'generator-live-name-and-weak-target-through-phases': (
        b'''<?php
function request340(){yield 7;}
$g=request340();$w=WeakReference::create($g);
echo get_class($g),"|",(int)($w->get()===$g),"|",$g->current(),"|";
$g->next();echo get_class($g),"|",(int)($w->get()===$g),"|";
unset($g);echo (int)($w->get()===null);
''', b'Generator|1|7|Generator|1|1', 0),
    'request-legacy-terminal-global': (
        driver.UNSUPPORTED['request-end-required'][0], b'1ZF', 0),
    'request-legacy-self-cache-cycle': (
        driver.UNSUPPORTED['self-cache-cycle-required'][0], b'12ZF', 0),
}

WATCHED = driver.WATCHED + [
    'spec/semantics/222-exception-handlers.watsup',
    'spec/semantics/257-request-destructors.watsup',
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/328-generator-reference-yields.watsup',
    'spec/semantics/340-generator-request-finally.watsup',
    'tests/semantics/reference_yield_terminal_review.py',
    'tests/semantics/generator_request_finally_sources.py',
    'tests/semantics/generator_request_finally_peer_sources.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED = WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
