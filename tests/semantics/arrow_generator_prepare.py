#!/usr/bin/env python3
"""Core-only companions for PHP 8.5.10 arrow Generator compiler/runtime paths."""
import generator_force_close_review as driver

ROOT = driver.ROOT
run = driver.run
CASES = {
    'capture-and-argument-snapshots': (b'<?php\n$x=2;$f=fn($p)=>yield $p+$x;$x=9;$p=3;$g=$f($p);$p=8;echo "C",$g->current();$g->next();echo $g->getReturn()===null?"N":"X";echo "Z";\n', b'C5NZ', 0),
    'eager-default-before-body': (b'<?php\nclass Box {public $v;function __construct($v){echo "D";$this->v=$v;}}$f=fn($p=new Box(4))=>yield $p;$g=$f();echo "C";$o=$g->current();echo $o->v;$g->next();echo "Z";\n', b'DC4Z', 0),
    'eager-typed-receives': (b'<?php\n$f=fn(int $p)=>yield $p;echo "A";try{$g=$f([]);echo "X";}catch(TypeError $e){echo "T";}$g=$f("7");echo "C",$g->current();$g->next();echo "Z";\n', b'ATC7Z', 0),
    'parameter-reference-capture-value': (b'<?php\n$x=1;$r=2;$f=fn($v,&$q)=>yield [$v,$q,$x];$g=$f(3,$r);$r=4;$x=9;echo "C";$a=$g->current();echo $a[0],":",$a[1],":",$a[2];$g->next();echo "Z";\n', b'C3:4:1Z', 0),
    'sent-implicit-return': (b'<?php\n$f=fn()=>yield 7;$g=$f();echo $g->current();$g->send(9);echo $g->getReturn();echo $g->valid()?"X":"F";echo "Z";\n', b'79FZ', 0),
    'fresh-send-implicit-return': (b'<?php\n$f=fn()=>yield 1;$g=$f();echo $g->send(9)===null?"N":"X";echo $g->getReturn(),"Z";\n', b'N9Z', 0),
    'bare-yield-and-next-return': (b'<?php\n$f=fn()=>yield;$g=$f();echo $g->current()===null?"N":"X";echo $g->key();$g->next();echo $g->getReturn()===null?"N":"X";echo "Z";\n', b'N0NZ', 0),
    'used-yield-expression': (b'<?php\n$f=fn()=>1+(yield 2);$g=$f();echo $g->current(),":";$g->send(5);echo $g->getReturn(),"Z";\n', b'2:6Z', 0),
    'array-delegation-return': (b'<?php\n$f=fn():Generator=>yield from [3=>7,"8"=>8];$g=$f();foreach($g as $k=>$v){echo $k,":",$v,";";}echo $g->getReturn()===null?"N":"X";echo "Z";\n', b'3:7;8:8;NZ', 0),
    'generator-delegation-return': (b'<?php\nfunction child(){yield 1;return 9;}$f=fn():Iterator=>yield from child();$g=$f();echo $g->current();$g->next();echo $g->getReturn(),"Z";\n', b'19Z', 0),
    'nested-arrow-and-closure-classification': (b'<?php\n$f=fn()=>fn()=>yield 5;$inner=$f();echo $inner instanceof Closure?"C":"X";foreach($inner() as $v){echo $v;}$maker=fn()=>function(){yield 6;};$inner=$maker();echo $inner instanceof Closure?"C":"X";foreach($inner() as $v){echo $v;}echo "Z";\n', b'C5C6Z', 0),
    'one-level-intersection-admission': (b'<?php\n$f=fn():Iterator&Countable=>yield 1;$g=$f();echo $g instanceof Generator?"G":"X";echo $g instanceof Countable?"X":"N";echo $g->current();$g->send(7);echo $g->getReturn(),"Z";\n', b'GN17Z', 0),
    'return-payload-skips-string-coercion': (b'<?php\nclass Str {function __toString():string {echo "X";return "str";}}$f=fn():Generator|string=>yield 1;$g=$f();echo $g->current();$o=new Str;$g->send($o);echo $g->getReturn()===$o?"I":"X";echo "Z";\n', b'1IZ', 0),
    'private-captured-receiver-scope': (b'<?php\nclass Owner {private $v=4;private function tag(){return self::class.":".static::class;}function make(){return fn()=>yield [$this->v,$this->tag(),static::class];}}class Child extends Owner {}$o=new Child;$f=$o->make();unset($o);$g=$f();unset($f);$a=$g->current();echo $a[0],":",$a[1],":",$a[2];$g->next();echo "Z";\n', b'4:Owner:Child:ChildZ', 0),
    'static-lexical-and-called-scope': (b'<?php\nclass Owner {function make(){return static fn()=>yield [self::class,static::class];}}class Child extends Owner {}$o=new Child;$f=$o->make();unset($o);$g=$f();unset($f);$a=$g->current();echo $a[0],":",$a[1];$g->next();echo "Z";\n', b'Owner:ChildZ', 0),
    'initial-yield-operand-throws': (b'<?php\nfunction fail(){throw new Exception("boom");}$f=fn()=>yield fail();$g=$f();echo "C";try{$g->current();echo "X";}catch(Exception $e){echo "T";}echo $g->valid()?"X":"F";echo "Z";\n', b'CTFZ', 0),
    'temporary-child-force-close': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";}}$f=fn()=>yield from seq();$g=$f();echo $g->current();unset($g);echo "Z";\n', b'1FZ', 0),
    'active-fiber-child-close': (b'<?php\nfunction seq(){try{yield 1;}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"F":"X";}}$f=new Fiber(function(){$arrow=fn()=>yield from seq();$g=$arrow();echo $g->current();unset($g);echo "A";});$f->start();echo "Z";\n', b'1FAZ', 0),
    'missing-value-handler-late-reference-key': (b'<?php\n$key="old";function warn($n,$m,$f,$l){echo "W",$l,"|";$GLOBALS["key"]="new";$GLOBALS["missing"]=7;return true;}set_error_handler("warn");\n$f=fn(&$key)=>yield $key=>$missing;\n$g=$f($key);echo "C|",(int)($g->current()===null),":",$g->key(),"|";$g->send(8);echo $g->getReturn(),":",$key,":",$missing;\n', b'C|W3|1:new|8:new:7', 0),
    'missing-value-multiline-warning-line': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W",$l,"|";return true;}set_error_handler("warn");\n$f=fn()=>yield\n$missing;\n$g=$f();echo "C|",(int)($g->current()===null),"|";$g->send(9);echo $g->getReturn();\n', b'C|W4|1|9', 0),
    'missing-value-handler-throw-identity': (b'<?php\n$e=new Exception("handler");function warn($n,$m,$f,$l){echo "W",$l,"|";throw $GLOBALS["e"];}set_error_handler("warn");\n$f=fn()=>yield $missing;\n$g=$f();echo "C|";try{$g->current();echo "X";}catch(Exception $caught){echo (int)($caught===$e),":",$caught->getLine(),"|";}echo (int)$g->valid(),":",(int)($g->current()===null),"|";try{$g->getReturn();echo "X";}catch(Exception $caught){echo $caught->getMessage();}\n', b'C|W3|1:2|0:1|Cannot get return value of a generator that hasn\'t returned', 0),
    'missing-value-handler-throw-key-owner': (b'<?php\nfunction keygen(){try{yield 2;}finally{echo "K|";}}function keyval(){$k=keygen();$k->current();return $k;}function warn($n,$m,$f,$l){echo "W",$l,"|";throw new Exception("handler");}set_error_handler("warn");\n$f=fn()=>yield keyval()=>$missing;\n$g=$f();echo "C|";try{$g->current();echo "X";}catch(Exception $e){echo $e->getMessage(),"|";}echo (int)$g->valid(),"|";unset($g);echo "Z";\n', b'C|W3|handler|0|K|Z', 0),
    'missing-value-throw-suppresses-key-warning': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W",$l,"|";throw new Exception("handler");}set_error_handler("warn");\n$f=fn()=>yield $missingKey=>$missing;\n$g=$f();echo "C|";try{$g->current();echo "X";}catch(Exception $e){echo $e->getMessage(),"|";}echo (int)$g->valid();unset($g);echo "Z";\n', b'C|W3|handler|0Z', 0),
    'ordinary-generator-value-handler-throw-skips-body-unwind': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W",$l,"|";throw new Exception("handler");}set_error_handler("warn");\nfunction seq(){try{yield $missing;}catch(Exception $e){echo "I|";yield 2;}finally{echo "F|";}return 7;}\n$g=seq();echo "C|";try{$g->current();echo "X";}catch(Exception $e){echo "O",$e->getMessage(),"|";}echo (int)$g->valid();unset($g);echo "Z";\n', b'C|W3|Ohandler|0Z', 0),
    'delegated-value-handler-throw-enters-parent-catch': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W",$l,"|";throw new Exception("handler");}set_error_handler("warn");\n$f=fn()=>yield $missing;\nfunction wrap($g){try{yield from $g;echo "X";}catch(Exception $e){echo "P|";yield 5;}finally{echo "F|";}return 7;}\n$h=wrap($f());unset($f);echo "C|",$h->current(),"|";$h->next();echo $h->getReturn();\n', b'C|W3|P|5|F|7', 0),
    'missing-value-preserves-this-key': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W",$l,"|";return true;}set_error_handler("warn");\nclass Owner{function make(){return fn()=>yield $this=>$missing;}}\n$o=new Owner;$f=$o->make();$g=$f();unset($f);echo "C|",(int)($g->current()===null),":",(int)($g->key()===$o),"|";$g->send(8);echo $g->getReturn();\n', b'C|W3|1:1|8', 0),
    'missing-value-preserves-globals-snapshot-key': (b'<?php\n$marker=3;function warn($n,$m,$f,$l){echo "W",$l,"|";return true;}set_error_handler("warn");\nfunction go(){$f=fn()=>yield $GLOBALS=>$missing;$g=$f();unset($f);echo "C|",(int)($g->current()===null),":";$a=$g->key();echo $a["marker"],"|";$g->send(9);echo $g->getReturn();}go();\n', b'C|W3|1:3|9', 0),
}
DECLARATIONS = {
    'invalid-scalar-supertype': (b'<?php\n$f=fn():int=>yield 1;\necho "X";\n', b'Generator return type must be a supertype of Generator, int given', 2),
    'invalid-never-supertype': (b'<?php\n$f=fn():never=>yield 1;\necho "X";\n', b'Generator return type must be a supertype of Generator, never given', 2),
    'invalid-dnf-supertype': (b'<?php\n$f=fn():(Iterator&Countable)|false=>yield 1;\necho "X";\n', b'Generator return type must be a supertype of Generator, (Iterator&Countable)|false given', 2),
    'reference-arrow-yield-from': (b'<?php\n$f=fn&()=>yield from [1];\necho "X";\n', b'Cannot use "yield from" inside a by-reference generator', 2),
}
UNSUPPORTED = {}
# The unchanged reference-arrow-yield original is now normal in
# reference_yield_prepare.py; its old Unsupported evidence keeps its own cut.
# The unchanged missing-key original is now a normal321 case in
# yield_key_warning_prepare.py; its old Unsupported evidence keeps its own cut.
WATCHED = driver.WATCHED + [
    'spec/semantics/95-typed-calls.watsup',
    'spec/semantics/117-arrow-compiler.watsup',
    'spec/semantics/118-arrows.watsup',
    'spec/semantics/310-generator-fiber-close.watsup',
    'spec/semantics/311-arrow-generators.watsup',
    'spec/semantics/321-yield-key-warning.watsup',
    'tests/semantics/arrow_generator_prepare.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = DECLARATIONS
    driver.UNSUPPORTED = UNSUPPORTED
    driver.REQUEST_CASES = {'missing-value-preserves-globals-snapshot-key'}
    driver.WATCHED = WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
