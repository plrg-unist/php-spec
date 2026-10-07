#!/usr/bin/env python3
"""Author sources for known-value YIELD key-CV warning continuation."""
import generator_force_close_review as driver

CASES = {
    'promoted-missing-key-handler-original': (
        b'<?php\nfunction warn($n,$m,$f,$l){echo "W",$l,"|";return true;}set_error_handler("warn");\n$f=fn()=>yield $missingKey=>4;\n$g=$f();echo "C|",$g->current(),":",(int)($g->key()===null),"|";$g->send(8);echo $g->getReturn();\n',
        b'C|W3|4:1|8', 0),
    'computed-value-is-not-evaluated-again': (
        b'''<?php
$count=0;
function payload321(){++$GLOBALS["count"];echo "V|";return 29;}
function warn($n,$m,$f,$l){echo "W|";return true;}set_error_handler("warn");
$arrow=fn()=>yield $missingKey=>payload321();$generator=$arrow();unset($arrow);
echo "C|",$generator->current(),":",(int)($generator->key()===null),"|";
$generator->send(7);echo $generator->getReturn(),":",$count;
''', b'C|V|W|29:1|7:1', 0),
    'false-handler-suppressed-fallback-keeps-null-key': (
        b'''<?php
function warn($n,$m,$f,$l){echo "H|";return false;}
error_reporting(0);set_error_handler("warn");$arrow=fn()=>yield $missingKey=>4;
$generator=$arrow();unset($arrow);echo "C|",$generator->current(),":",(int)($generator->key()===null),"|";
$generator->send(8);echo $generator->getReturn(),":",error_reporting();
''', b'C|H|4:1|8:0', 0),
    'unhandled-suppressed-key-with-real-null-value': (
        b'''<?php
error_reporting(0);$arrow=fn()=>yield $missingKey=>null;
$generator=$arrow();unset($arrow);echo "C|",(int)($generator->current()===null),":",(int)($generator->key()===null),":",(int)$generator->valid(),"|";
$generator->send(7);echo $generator->getReturn();
''', b'C|1:1:1|7', 0),
    'key-handler-keeps-new-handler-registration': (
        b'''<?php
function second321($n,$m,$f,$l){echo "H2|";return true;}
function first321($n,$m,$f,$l){echo "H1|";set_error_handler("second321");return true;}
function seq321(){yield $missingKey=>4;yield $nextKey=>5;}
set_error_handler("first321");$generator=seq321();echo "C|",$generator->current(),":",(int)($generator->key()===null),"|";
$generator->next();echo $generator->current(),":",(int)($generator->key()===null),"|";
$generator->next();echo (int)$generator->valid();
''', b'C|H1|4:1|H2|5:1|0', 0),
    'key-throw-retains-temporary-generator-value': (
        b'''<?php
function payload321(){try{yield 2;}finally{echo "V|";}}
function value321(){$value=payload321();$value->current();return $value;}
$error=new Exception("key");function warn($n,$m,$f,$l){echo "W|";throw $GLOBALS["error"];}
set_error_handler("warn");$arrow=fn()=>yield $missingKey=>value321();$generator=$arrow();unset($arrow);echo "C|";
try{$generator->current();echo "X";}catch(Exception $caught){echo "E",(int)($caught===$error),"|";}
echo (int)$generator->valid(),"|";unset($generator);echo "Z";
''', b'C|W|E1|0|V|Z', 0),
    'active-fiber-key-warning-with-eager-object-default': (
        b'''<?php
class Default321 {function __construct(){echo "D",(int)(Fiber::getCurrent()!==null),"|";}}
function warn($n,$m,$f,$l){echo "W",(int)(Fiber::getCurrent()!==null),"|";return true;}set_error_handler("warn");
$fiber=new Fiber(function(){$arrow=fn($default=new Default321)=>yield $missingKey=>$default;$generator=$arrow();unset($arrow);echo "C|",(int)($generator->current() instanceof Default321),":",(int)($generator->key()===null),"|";$generator->send(4);echo $generator->getReturn(),"|";unset($generator);return 9;});
$fiber->start();echo "M",$fiber->getReturn();
''', b'D1|C|W1|1:1|4|M9', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/207-error-handler-runtime.watsup',
        'spec/semantics/310-generator-fiber-close.watsup',
        'spec/semantics/311-arrow-generators.watsup',
        'spec/semantics/321-yield-key-warning.watsup',
        'tests/semantics/yield_key_warning_prepare.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
