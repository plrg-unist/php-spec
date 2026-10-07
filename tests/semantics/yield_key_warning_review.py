#!/usr/bin/env python3
"""Independent YIELD key-CV warning, cache and owner counterexamples."""
import generator_force_close_review as driver

CASES = {
    'key-warning-copies-reference-value-and-shared-opcode-line': (
        b'''<?php
$value=5;
function warn($n,$m,$f,$l){echo "W",$l,"|";$GLOBALS["value"]=9;$GLOBALS["missingKey"]="late";return true;}set_error_handler("warn");
$arrow=fn(&$value)=>yield
    $missingKey
    =>
    $value;
$generator=$arrow($value);unset($arrow);
echo "C|",$generator->current(),":",(int)($generator->key()===null),":",$value,":",$missingKey,"|";
$generator->send(8);echo $generator->getReturn();
''', b'C|W7|5:1:9:late|8', 0),
    'key-warning-keeps-integer-index': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|";return true;}
function seq(){yield 3=>4;yield $missingKey=>6;yield 7;}
set_error_handler("warn");$generator=seq();echo $generator->current(),":",$generator->key(),"|";
$generator->next();echo $generator->current(),":",(int)($generator->key()===null),"|";
$generator->next();echo $generator->current(),":",$generator->key();
''', b'4:3|W3|6:1|7:4', 0),
    'value-warning-then-key-warning-share-yield-opcode': (
        b'''<?php
function warn($n,$m,$f,$l){echo $m,"@",$l,"|";return true;}
set_error_handler("warn");$arrow=fn()=>yield
    $missingKey=>
    $missingValue;
$generator=$arrow();unset($arrow);echo "C|",(int)($generator->current()===null),":",(int)($generator->key()===null),"|";
$generator->send(9);echo $generator->getReturn();
''', b'C|Undefined variable $missingValue@5|Undefined variable $missingKey@5|1:1|9', 0),
    'key-warning-owns-value-during-reference-overwrite': (
        b'''<?php
class Payload321 {function __destruct(){echo "P|";}}
$value=new Payload321;$weak=WeakReference::create($value);
function warn($n,$m,$f,$l){echo "W",$l,"|";$GLOBALS["value"]=null;echo (int)($GLOBALS["weak"]->get()!==null),"|";return true;}
$arrow=fn(&$value)=>yield $missingKey=>$value;
set_error_handler("warn");$generator=$arrow($value);unset($arrow);echo "C|";
$generator->current();echo (int)($weak->get()!==null),"|";unset($generator);echo (int)($weak->get()===null),"Z";
''', b'C|W5|1|1|P|1Z', 0),
    'key-warning-throw-retains-new-value-and-arrow-owner': (
        b'''<?php
class Payload321 {function __destruct(){echo "P|";}}
function payload321(){$payload=new Payload321;$GLOBALS["weak"]=WeakReference::create($payload);return $payload;}
$error=new Exception("key");
function warn($n,$m,$f,$l){echo "W",$l,"|";throw $GLOBALS["error"];}
$arrow=fn()=>yield $missingKey=>payload321();$weakArrow=WeakReference::create($arrow);
set_error_handler("warn");$generator=$arrow();unset($arrow);echo "C|";
try{$generator->current();echo "X";}catch(Exception $caught){echo (int)($caught===$error),":",(int)($caught->getPrevious()===null),"|";}
echo (int)($weak->get()!==null),":",(int)($weakArrow->get()!==null),":",(int)($generator->current()===null),":",(int)$generator->valid(),"|";
unset($generator);echo (int)($weak->get()===null),":",(int)($weakArrow->get()===null),"Z";
''', b'C|W6|1:1|1:1:1:0|P|1:1Z', 0),
    'key-warning-delegated-arrow-keeps-closed-cache-owners': (
        b'''<?php
class Payload321 {function __destruct(){echo "V|";}}
function payload321(){$payload=new Payload321;$GLOBALS["weak"]=WeakReference::create($payload);return $payload;}
$error=new Exception("key");
function warn($n,$m,$f,$l){echo "W",$l,"|";throw $GLOBALS["error"];}
$arrow=fn()=>yield $missingKey=>payload321();$weakArrow=WeakReference::create($arrow);
function parent321($child){try{yield from $child;}catch(Exception $caught){echo "E",(int)($caught===$GLOBALS["error"]),"|";yield 5;}finally{echo "F|";}return 9;}
set_error_handler("warn");$child=$arrow();$generator=parent321($child);unset($arrow,$child);echo "C|";
echo $generator->current(),":",(int)($weak->get()!==null),":",(int)($weakArrow->get()!==null),"|";
$generator->next();echo $generator->getReturn(),":",(int)($weak->get()===null),":",(int)($weakArrow->get()===null),"Z";
''', b'C|W6|E1|5:1:1|F|V|9:1:1Z', 0),
    'key-warning-throw-skips-own-catch-and-finally': (
        b'''<?php
$error=new Exception("key");
function warn($n,$m,$f,$l){echo "W",$l,"|";throw $GLOBALS["error"];}
function seq(){try{yield $missingKey=>4;}catch(Exception $caught){echo "I|";yield 2;}finally{echo "F|";}return 7;}
set_error_handler("warn");$generator=seq();echo "C|";
try{$generator->current();echo "X";}catch(Exception $caught){echo "O",(int)($caught===$error),":",(int)($caught->getPrevious()===null),"|";}
echo (int)$generator->valid(),"|";unset($generator);echo "Z";
''', b'C|W4|O1:1|0|Z', 0),
    'key-warning-throw-enters-delegating-parent-catch': (
        b'''<?php
$error=new Exception("key");
function warn($n,$m,$f,$l){echo "W",$l,"|";throw $GLOBALS["error"];}
function leaf321(){try{yield $missingKey=>6;}finally{echo "L|";}}
function parent321($child){try{yield from $child;}catch(Exception $caught){echo "P",(int)($caught===$GLOBALS["error"]),":",(int)($caught->getPrevious()===null),"|";yield 5;}finally{echo "F|";}return 7;}
set_error_handler("warn");$child=leaf321();$generator=parent321($child);echo "C|",$generator->current(),":",(int)$child->valid(),"|";
unset($child);$generator->next();echo $generator->getReturn(),"Z";
''', b'C|W4|L|P1:1|5:0|F|7Z', 0),
    'key-warning-delegated-child-catch-precedes-parent': (
        b'''<?php
$error=new Exception("key");
function warn($n,$m,$f,$l){echo "W",$l,"|";throw $GLOBALS["error"];}
function leaf321(){try{yield $missingKey=>6;}catch(Exception $caught){echo "I",(int)($caught===$GLOBALS["error"]),":",(int)($caught->getPrevious()===null),"|";yield 12;}finally{echo "L|";}return 7;}
function parent321($child){try{yield from $child;echo "A|";}catch(Exception $caught){echo "P|";yield 5;}finally{echo "F|";}return 9;}
set_error_handler("warn");$child=leaf321();$generator=parent321($child);echo "C|",$generator->current(),":",(int)$child->valid(),"|";
unset($child);$generator->next();echo $generator->getReturn(),"Z";
''', b'C|W4|I1:1|12:1|L|A|F|9Z', 0),
    'value-warning-delegated-child-catch-suppresses-key-warning': (
        b'''<?php
$error=new Exception("value");
function warn($n,$m,$f,$l){echo $m,"@",$l,"|";throw $GLOBALS["error"];}
function leaf321(){try{yield $missingKey=>$missingValue;}catch(Exception $caught){echo "I",(int)($caught===$GLOBALS["error"]),":",(int)($caught->getPrevious()===null),"|";yield 12;}finally{echo "L|";}return 7;}
function parent321($child){try{yield from $child;echo "A|";}catch(Exception $caught){echo "P|";yield 5;}finally{echo "F|";}return 9;}
set_error_handler("warn");$child=leaf321();$generator=parent321($child);echo "C|",$generator->current(),":",(int)$child->valid(),"|";
unset($child);$generator->next();echo $generator->getReturn(),"Z";
''', b'C|Undefined variable $missingValue@4|I1:1|12:1|L|A|F|9Z', 0),
    'key-warning-direct-child-api-with-parked-parent': (
        b'''<?php
$error=new Exception("key");
function warn($n,$m,$f,$l){echo "W",$l,"|";throw $GLOBALS["error"];}
function leaf321(){try{yield 1;yield $missingKey=>6;}catch(Exception $caught){echo "I|";yield 12;}finally{echo "L|";}}
function parent321($child){try{yield from $child;}catch(Throwable $caught){echo "P|";yield 5;}finally{echo "F|";}return 9;}
set_error_handler("warn");$child=leaf321();$generator=parent321($child);echo "C|",$generator->current(),"|";
try{$child->next();echo "X";}catch(Exception $caught){echo "O",(int)($caught===$error),"|";}echo (int)$child->valid(),"|";
echo $generator->current(),"|";$generator->next();echo $generator->getReturn(),"Z";
''', b'C|1|W4|O1|0|P|5|F|9Z', 0),
    'key-warning-reentrant-cache-read-and-resume-refusal': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|";echo $GLOBALS["generator"]->current(),":",(int)($GLOBALS["generator"]->key()===null),":",(int)$GLOBALS["generator"]->valid(),"|";try{$GLOBALS["generator"]->next();echo "X";}catch(Error $caught){echo "N|";}return true;}
set_error_handler("warn");$arrow=fn()=>yield $missingKey=>11;
$generator=$arrow();unset($arrow);echo "C|",$generator->current(),":",(int)($generator->key()===null),"|";
$generator->send(9);echo $generator->getReturn();
''', b'C|W3|11:1:1|N|11:1|9', 0),
    'forced-close-rejects-before-key-warning': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|";return true;}
function seq(){try{yield 1;}finally{yield $missingKey=>4;}}
set_error_handler("warn");$generator=seq();echo $generator->current(),"|";
try{unset($generator);echo "X";}catch(Error $caught){echo $caught->getMessage(),"|";}echo "Z";
''', b'1|Cannot yield from finally in a force-closed generator|Z', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/207-error-handler-runtime.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/310-generator-fiber-close.watsup',
        'spec/semantics/311-arrow-generators.watsup',
        'spec/semantics/321-yield-key-warning.watsup',
        'tests/semantics/yield_key_warning_review.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
