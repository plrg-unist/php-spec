#!/usr/bin/env python3
"""Independent reference-yield aliases, warning order and cache lifetimes."""
import generator_force_close_review as driver

CASES = {
    'undefined-value-cv-creates-null-reference-without-warning': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|";return true;}
function &give(){yield $absent;}
set_error_handler("warn");$generator=give();echo "A|";
foreach($generator as &$alias){echo (int)($alias===null),":",$generator->key(),"|";$alias=4;echo $generator->current();}
unset($alias);echo "|",(int)!$generator->valid();
''', b'A|1:0|4|1', 0),
    'key-warning-mutates-already-cached-reference': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|",$GLOBALS["generator"]->current(),":",(int)($GLOBALS["generator"]->key()===null),"|";$GLOBALS["value"]=12;echo $GLOBALS["generator"]->current(),"|";return true;}
function &give(&$value){yield $missingKey=>$value;}
set_error_handler("warn");$value=7;$generator=give($value);
echo "C|",$generator->current(),":",(int)($generator->key()===null),":",$value;
''', b'C|W3|7:1|12|12:1:12', 0),
    'key-warning-reference-overwrite-retires-payload-immediately': (
        b'''<?php
class Payload328 {function __destruct(){echo "P|";}}
$value=new Payload328;$weak=WeakReference::create($value);
function warn($n,$m,$f,$l){echo "W",$l,"|";$GLOBALS["value"]=null;echo (int)($GLOBALS["weak"]->get()===null),"|";return true;}
function &give(&$value){yield $missingKey=>$value;}
set_error_handler("warn");$generator=give($value);echo "C|",(int)($generator->current()===null),":",(int)($generator->key()===null);
''', b'C|W5|P|1|1:1', 0),
    'source-reference-rebind-does-not-retarget-cache-alias': (
        b'''<?php
function &give(&$value){yield $value;yield $value;}
$value=3;$generator=give($value);
foreach($generator as &$alias){echo $alias,"|";$alias=7;break;}
$replacement=2;$value=&$replacement;$value=9;
echo $alias,":",$generator->current(),":",$value,"|";unset($value);echo $alias,"|";
$generator->next();echo $generator->current();
''', b'3|7:7:9|7|7', 0),
    'foreach-alias-keeps-payload-after-generator-frame-close': (
        b'''<?php
class Payload328 {function __destruct(){echo "P|";}}
function &give(){$value=new Payload328;$GLOBALS["weak"]=WeakReference::create($value);try{yield $value;}finally{echo "F|";}}
$generator=give();echo "A|";
foreach($generator as &$alias){echo (int)($weak->get()!==null),"|";break;}
unset($generator);echo (int)($weak->get()!==null),":",(int)($alias instanceof Payload328),"|";
unset($alias);echo (int)($weak->get()===null);
''', b'A|1|F|1:1|P|1', 0),
    'current-array-snapshot-versus-live-foreach-reference': (
        b'''<?php
function &give(&$value){yield $value;}
$value=[1];$generator=give($value);$copy=$generator->current();$copy[0]=9;
echo $value[0],":",$generator->current()[0],"|";
foreach($generator as &$alias){$alias[0]=8;break;}
echo $value[0],":",$copy[0],":",$generator->current()[0];
''', b'1:1|8:9:8', 0),
    'arrow-reference-yield-detaches-value-capture-and-closure-owner': (
        b'''<?php
$value=5;$arrow=fn&()=>yield $value;$weakArrow=WeakReference::create($arrow);$generator=$arrow();unset($arrow);
foreach($generator as &$alias){echo $alias,"|";$alias=8;break;}
echo $value,":",$generator->current(),":",(int)($weakArrow->get()!==null),"|";
unset($generator);echo $alias,":",(int)($weakArrow->get()===null);
''', b'5|5:8:1|8:1', 0),
    'ordinary-generator-by-reference-iteration-rejects-before-body': (
        b'''<?php
function give(){echo "X|";yield 1;}
$generator=give();echo "C|";
try{foreach($generator as &$alias){echo "Y|";}}catch(Exception $error){echo $error->getMessage();}
''', b'C|You can only iterate a generator by-reference if it declared that it yields by-reference', 0),
    'literal-yield-notice-then-foreach-wraps-only-cache': (
        b'''<?php
function warn($n,$m,$f,$l){echo "N",$n,":",$l,"|";return true;}
function &give(){yield 5;}
set_error_handler("warn");$generator=give();echo "C|";
foreach($generator as &$alias){echo $alias,"|";$alias=8;echo $generator->current(),"|";break;}
echo $alias,"|";unset($generator);echo $alias;
''', b'C|N8:3|5|8|8|8', 0),
    'bare-yield-has-no-reference-notice-and-gets-cache-wrapper': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|";return true;}
function &give(){yield;}
set_error_handler("warn");$generator=give();
foreach($generator as &$alias){$alias=6;echo $generator->current(),":";break;}
echo $alias;
''', b'6:6', 0),
    'throwing-key-warning-closed-cache-keeps-reference-referent': (
        b'''<?php
class Payload328 {function __destruct(){echo "P|";}}
$value=new Payload328;$weak=WeakReference::create($value);$error=new Exception("key");
function warn($n,$m,$f,$l){echo "W",$l,"|";throw $GLOBALS["error"];}
function &give(&$value){try{yield $missingKey=>$value;}catch(Exception $caught){echo "I|";}finally{echo "F|";}}
set_error_handler("warn");$generator=give($value);echo "C|";
try{$generator->current();}catch(Exception $caught){echo "O",(int)($caught===$error),"|";}
unset($value);echo (int)($weak->get()!==null),"|";unset($generator);echo (int)($weak->get()===null),"Z";
''', b'C|W5|O1|1|P|1Z', 0),
    'undefined-value-and-key-warn-only-for-key-after-reference-cache': (
        b'''<?php
function warn($n,$m,$f,$l){echo $m,"@",$l,"|";return true;}
function &give(){yield $missingKey=>$missingValue;}
set_error_handler("warn");$generator=give();echo "C|",(int)($generator->current()===null),":",(int)($generator->key()===null);
''', b'C|Undefined variable $missingKey@3|1:1', 0),
    'literal-notice-throw-skips-body-and-suppresses-key-warning': (
        b'''<?php
function warn($n,$m,$f,$l){echo "N",$n,":",$l,"|";throw $GLOBALS["error"];}
function &give(){try{yield $missingKey=>5;}catch(Exception $caught){echo "I|";}finally{echo "F|";}}
set_error_handler("warn");$error=new Exception("notice");$generator=give();echo "C|";
try{$generator->current();}catch(Exception $caught){echo "O",(int)($caught===$error),":",(int)($caught->getPrevious()===null),"|";}
echo (int)$generator->valid(),":",(int)($generator->current()===null);
''', b'C|N8:3|O1:1|0:1', 0),
    'key-warning-property-owner-retirement-keeps-untyped-cache-alias': (
        b'''<?php
class Box328 {public int $value=4;function __destruct(){echo "B|";}}
$box=new Box328;$weakBox=WeakReference::create($box);$outside=&$box->value;
function warn($n,$m,$f,$l){echo "W",$l,"|";$GLOBALS["box"]=null;echo (int)($GLOBALS["weakBox"]->get()===null),"|";$GLOBALS["outside"]="free";return true;}
function &give(){yield $missingKey=>$GLOBALS["box"]->value;}
set_error_handler("warn");$generator=give();echo "C|",$generator->current(),":",(int)($generator->key()===null);
''', b'C|W5|B|1|free:1', 0),
    'ordinary-parent-delegates-live-reference-child-with-value-iteration': (
        b'''<?php
function &leaf(&$value){yield $value;yield $value;}
function parent328(&$value){yield from leaf($value);}
$value=3;$generator=parent328($value);$copy=$generator->current();$value=7;
echo $copy,":",$generator->current(),"|";
foreach($generator as $item){echo $item,"|";$item=9;}
echo $value;
''', b'3:7|7|7|7', 0),
    'this-fetch-uses-cache-reference-without-rebinding-instance': (
        b'''<?php
class Self328 {function &give(){yield $this;echo "I",(int)($this instanceof Self328),"|";}}
function warn($n,$m,$f,$l){echo "W",$l,"|";return true;}
set_error_handler("warn");$object=new Self328;$generator=$object->give();
foreach($generator as &$alias){echo (int)($alias===$object),":";$alias=null;}
echo (int)($object instanceof Self328);
''', b'1:I1|1', 0),
    'globals-fetch-uses-reference-to-snapshot-without-notice': (
        b'''<?php
function &give(){yield $GLOBALS;}
function warn($n,$m,$f,$l){echo "W",$l,"|";return true;}
set_error_handler("warn");$value=3;
foreach(give() as &$alias){$alias["value"]=8;break;}
echo $value,":",$alias["value"];
''', b'3:8', 0),
    'ordinary-previous-key-during-new-key-warning': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|",$GLOBALS["g"]->current(),":",$GLOBALS["g"]->key(),":",(int)$GLOBALS["g"]->valid(),"|";return true;}
function give(){yield 8=>1;yield $missingKey=>2;}
$g=give();set_error_handler("warn");echo "C|",$g->current(),":",$g->key(),"|";$g->next();echo $g->current(),":",(int)($g->key()===null);
''', b'C|1:8|W3|2:8:1|2:1', 0),
    'reference-previous-key-during-new-key-warning': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|",$GLOBALS["g"]->current(),":",$GLOBALS["g"]->key(),":",(int)$GLOBALS["g"]->valid(),"|";return true;}
function &give(&$value){yield 8=>$value;yield $missingKey=>$value;}
$value=4;$g=give($value);set_error_handler("warn");echo "C|",$g->current(),":",$g->key(),"|";$g->next();echo $g->current(),":",(int)($g->key()===null);
''', b'C|4:8|W3|4:8:1|4:1', 0),
    'ordinary-previous-value-during-new-value-warning': (
        b'''<?php
function warn($n,$m,$f,$l){echo "W",$l,"|",$GLOBALS["g"]->current(),":",$GLOBALS["g"]->key(),":",(int)$GLOBALS["g"]->valid(),"|";return true;}
function give(){yield 8=>1;yield $missingValue;}
$g=give();set_error_handler("warn");echo "C|",$g->current(),":",$g->key(),"|";$g->next();echo (int)($g->current()===null),":",$g->key();
''', b'C|1:8|W3|1:8:1|1:9', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.REQUEST_CASES = {'globals-fetch-uses-reference-to-snapshot-without-notice'}
    driver.WATCHED += [
        'spec/semantics/97-call-reference-acquisition.watsup',
        'spec/semantics/99-reference-returns.watsup',
        'spec/semantics/118-arrows.watsup',
        'spec/semantics/207-error-handler-runtime.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/311-arrow-generators.watsup',
        'spec/semantics/321-yield-key-warning.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'tests/semantics/reference_yield_review.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
