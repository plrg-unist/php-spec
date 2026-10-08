#!/usr/bin/env python3
"""Author originals for Generator reference-yield aliases and lifetime."""
import generator_force_close_review as driver

CASES = {
    'parameter-alias-and-value-api-snapshot': (
        b'''<?php
function &leaf328(&$slot){yield 10=>$slot;echo "R",$slot,"|";yield 11=>$slot;}
$slot=4;$generator=leaf328($slot);$snapshot=$generator->current();
$slot=6;echo "C",$snapshot,"|A",$generator->current(),"|";
foreach($generator as $key=>&$value){echo $key,":",$value,"|";$value+=2;}
$value=19;echo $slot,"|";unset($value);echo $slot,"|",(int)$generator->valid();
''', b'C4|A6|10:6|R8|11:8|19|19|0', 0),
    'dimension-alias-separates-copied-array': (
        b'''<?php
function &leaf328(&$array){yield $array[0];echo $array[0],"|";yield $array[1];}
$array=[4,5];$copy=$array;
foreach(leaf328($array) as &$value){$value+=3;}
echo $array[0],":",$array[1],"|",$copy[0],":",$copy[1],"|";
$value=12;echo $array[1];
''', b'7|7:8|4:5|12', 0),
    'typed-property-alias-outlives-property-owner': (
        b'''<?php
class Box328 {public int $value=4;}
function &leaf328($box){yield $box->value;echo "I",$box->value,"|";}
$box=new Box328;
foreach(leaf328($box) as &$value){$value=7;}
try{$value="bad";}catch(TypeError $error){echo "T|";}
echo $box->value,"|";unset($box);$value="free";echo $value;
''', b'I7|T|7|free', 0),
    'post-break-alias-owns-payload-after-generator-close': (
        b'''<?php
class Payload328 {function __destruct(){echo "D|";}}
function &leaf328(){try{$value=new Payload328;yield $value;}finally{echo "F|";}}
$generator=leaf328();
foreach($generator as &$value){echo "B|";break;}
$weak=WeakReference::create($value);unset($generator);
echo (int)($weak->get()!==null),"|";unset($value);echo (int)($weak->get()===null);
''', b'B|F|1|D|1', 0),
    'source-unset-rebind-keeps-distinct-cache-alias': (
        b'''<?php
function &leaf328(){$value=4;yield $value;unset($value);$value=9;yield $value;echo "R",$value;}
$generator=leaf328();
foreach($generator as &$value){echo $value,"|";if($value===4){$held=&$value;$value=6;}else{$value=12;}}
echo "|",$held,":",$value;
''', b'4|9|R12|6:12', 0),
    'bare-constant-and-temporary-cache-wrappers': (
        b'''<?php
function &leaf328(){yield;yield 4;yield 1+2;}
function notice328($number,$message,$file,$line){echo "N",$line,"|";return true;}
set_error_handler("notice328");
foreach(leaf328() as &$value){echo (int)($value===null),":",$value,"|";$value=8;}
echo $value;
''', b'1:|N2|0:4|N2|0:3|8', 0),
    'reference-arrow-invocation-retains-capture-snapshot': (
        b'''<?php
$value=4;$arrow=fn&()=>yield $value;$generator=$arrow();
foreach($generator as &$alias){$alias=9;}
echo $value,":",$alias,":";
$next=$arrow();echo $next->current();
''', b'4:9:4', 0),
    'reference-call-result-keeps-original-cell': (
        b'''<?php
function &slot328(&$slot){return $slot;}
function &leaf328(&$slot){yield slot328($slot);}
$slot=4;$generator=leaf328($slot);$snapshot=$generator->current();
$slot=6;echo $snapshot,":",$generator->current(),"|";
foreach($generator as &$alias){$alias=9;}
echo $slot,":",$alias;
''', b'4:6|9:9', 0),
    'value-call-notice-keeps-copied-result': (
        b'''<?php
function value328(){global $slot;return $slot;}
function &leaf328(){yield value328();}
function notice328($number,$message,$file,$line){global $slot;$slot=9;echo "N",$line,"|";return true;}
$slot=4;set_error_handler("notice328");$generator=leaf328();
echo "C|",$generator->current(),":",$slot,"|";
foreach($generator as &$alias){echo $alias,"|";$alias=6;}
echo $slot,":",$alias;
''', b'C|N3|4:9|4|9:6', 0),
    'temporary-new-object-creates-cache-reference-without-notice': (
        b'''<?php
class Payload328 {function __destruct(){echo "P|";}}
function &leaf328(){yield new Payload328;}
function notice328($number,$message,$file,$line){echo "N|";return true;}
set_error_handler("notice328");$generator=leaf328();$value=$generator->current();
$weak=WeakReference::create($value);unset($value);echo "C|";
foreach($generator as &$alias){echo "A|";}
unset($generator);echo (int)($weak->get()!==null),"|";
unset($alias);echo (int)($weak->get()===null);
''', b'C|A|1|P|1', 0),
    'same-undefined-key-value-is-defined-by-write-acquisition': (
        b'''<?php
function &leaf328(){yield $value=>$value;echo "B",(int)isset($value),"|";}
function warning328($number,$message,$file,$line){echo "W|";return true;}
set_error_handler("warning328");
foreach(leaf328() as $key=>&$alias){echo (int)($key===null),":",(int)($alias===null),"|";$alias=4;}
echo $alias;
''', b'1:1|B1|4', 0),
    'readonly-reference-fetch-precedes-old-cache-release': (
        b'''<?php
class Payload328 {function __destruct(){echo "D|";}}
class Box328 {public readonly int $value;function __construct(){$this->value=4;}}
function &leaf328($box){yield new Payload328;try{yield $box->value;}catch(Error $error){echo "E|";$next=2;yield $next;}}
$generator=leaf328(new Box328);echo (int)($generator->current() instanceof Payload328),"|";
$generator->next();echo $generator->current();
''', b'1|E|D|2', 0),
    'handler-retval-retirement-keeps-key-and-notice-ingress': (
        b'''<?php
class Retval328 {function __destruct(){echo "D";try{$value=$GLOBALS["generator"]->current();echo ":",$value;}catch(Error $error){echo ":R";}echo "|";}}
function warn328($number,$message,$file,$line){echo "W",$number,"|";return new Retval328;}
function &leaf328(&$value){yield $missingKey=>$value;yield $otherKey=>5;}
set_error_handler("warn328");$value=4;$generator=leaf328($value);
echo "C|",$generator->current(),"|";$generator->next();echo $generator->current();
''', b'C|W2|D:4|4|W8|D:4|W2|D:5|5', 0),
    'old-cache-destructor-mutates-delayed-value-cv': (
        b'''<?php
class Payload328 {public $slot;function __construct(&$slot){$this->slot=&$slot;}function __destruct(){$this->slot=9;echo "D|";}}
function &leaf328(){$next=2;yield new Payload328($next);yield $next;}
$generator=leaf328();echo "C|",(int)($generator->current() instanceof Payload328),"|";
$generator->next();echo $generator->current();
''', b'C|1|D|9', 0),
    'promoted-reference-arrow-value-iteration': (
        b'<?php\n$x=5;$f=fn&()=>yield $x;foreach($f() as $v){echo $v;}echo "Z";\n', b'5Z', 0),
    'destructuring-inner-reference-mutates-producer-array': (
        b'<?php\nfunction &g(&$a){yield $a;} $a=[1]; $g=g($a); foreach($g as [&$v]){$v=9; break;} echo $a[0],":",$g->current()[0];\n',
        b'9:9', 0),
    'destructuring-inner-reference-retains-value-api-copy': (
        b'''<?php
function &g(&$array){yield $array;}
$array=[1];$generator=g($array);$copy=$generator->current();
foreach($generator as [&$value]){$value=9;break;}
echo $copy[0],":",$array[0],":",$generator->current()[0];
unset($generator);$value=12;echo "|",$array[0];
''', b'1:9:9|12', 0),
    'destructuring-inner-reference-wraps-value-cache': (
        b'''<?php
function &g(){yield [1];}
function notice328($number,$message){echo "N|";return true;}
set_error_handler("notice328");$generator=g();$copy=$generator->current();
foreach($generator as [&$value]){$value=9;break;}
echo $copy[0],":",$generator->current()[0],":",$value;
unset($generator);$value=12;echo "|",$value;
''', b'N|1:9:9|12', 0),
    'destructuring-inner-reference-rejects-value-producer-before-body': (
        b'''<?php
function g(){echo "B";yield [1];}
$generator=g();try{foreach($generator as [&$value]){echo "X";}}
catch(Exception $error){echo "E|";}
echo $generator->current()[0];
''', b'E|B1', 0),
}

DECLARATIONS = {
    'reference-generator-still-rejects-yield-from': (
        b'<?php\nfunction &leaf328(){yield from [4];}\n',
        b'Cannot use "yield from" inside a by-reference generator', 2),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = DECLARATIONS
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/99-reference-returns.watsup',
        'spec/semantics/118-arrows.watsup',
        'spec/semantics/207-error-handler-runtime.watsup',
        'spec/semantics/236-eval-declaration-notices.watsup',
        'spec/semantics/243-file-warning-continuations.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/311-arrow-generators.watsup',
        'spec/semantics/321-yield-key-warning.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'tests/semantics/reference_yield_prepare.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
