#!/usr/bin/env python3
"""Independent original core-language witnesses for arrow Generators."""
import sys

import generator_force_close_review as driver

ROOT = driver.ROOT
run = driver.run
CASES = {
    'sent-identity-supertype': (b'<?php\n$f=fn():Iterator=>yield 4;$g=$f();unset($f);$sent=new stdClass;echo $g->current(),"|";(int)$g->send($sent);echo (int)($g->getReturn()===$sent),"|",(int)$g->valid();\n', b'4|1|0', 0),
    'key-value-and-next-result': (b'<?php\nfunction mark($v){echo $v;return $v;}$f=fn()=>yield mark("K")=>mark("V");$g=$f();unset($f);echo "C|",$g->current(),":",$g->key(),"|";$g->next();echo (int)($g->getReturn()===null);\n', b'C|KVV:K|1', 0),
    'default-eager-type-eager-body-deferred': (b'<?php\nclass Box{function __construct(){echo "D|";}}function body($x){echo "B|";return $x;}$f=fn(int $n=2,$x=new Box)=>yield body($n);echo "A|";$g=$f();echo "C|",$g->current(),"|";$g->next();try{$f([]);}catch(TypeError $e){echo "T|";}echo (int)($g->getReturn()===null);\n', b'A|D|C|B|2|T|1', 0),
    'parameter-shadow-and-received-reference': (b'<?php\n$x=1;$r=2;$f=fn($x,&$r)=>yield [$x,$r];$g=$f(x:4,r:$r);$x=7;$r=8;unset($f);$v=$g->current();echo $v[0],":",$v[1],"|";$g->next();echo $x,":",$r;\n', b'4:8|7:8', 0),
    'implicit-reference-capture-is-value': (b'<?php\n$x=1;$r=&$x;$f=fn()=>yield $r;$x=2;$g=$f();unset($f,$x,$r);echo "C|",$g->current(),"|";$g->send(5);echo $g->getReturn();\n', b'C|1|5', 0),
    'captured-array-embedded-reference': (b'<?php\n$r=2;$a=[&$r,5];$f=fn()=>yield $a;$a[1]=9;$g=$f();unset($f,$a);$r=7;$v=$g->current();echo $v[0],":",$v[1];$v[0]=8;$v[2]=1;echo ":",$r,":",(int)isset($g->current()[2]);$g->next();echo (int)($g->getReturn()===null);\n', b'7:5:8:01', 0),
    'undefined-capture-warning-is-deferred': (b'<?php\nfunction warn($n,$m,$f,$l){echo "W",$l,"|";return true;}set_error_handler("warn");\n$f=fn()=>yield $missing;\necho "A|";$g=$f();echo "C|";echo (int)($g->current()===null),"|";$g->send(8);echo $g->getReturn();\n', b'A|C|W3|1|8', 0),
    'nested-arrow-does-not-mark-parent': (b'<?php\n$x=3;$outer=fn()=>fn()=>yield $x;$x=9;$inner=$outer();echo (int)($inner instanceof Closure),"|";$g=$inner();unset($outer,$inner);echo $g->current(),"|";$g->send(6);echo $g->getReturn();\n', b'1|3|6', 0),
    'dead-yield-still-generator': (b'<?php\n$f=fn():Generator=>false?(yield 1):7;$g=$f();unset($f);echo (int)($g instanceof Generator),"|",(int)($g->current()===null),"|",$g->getReturn();\n', b'1|1|7', 0),
    'yield-result-expression-return': (b'<?php\n$f=fn():Generator=>(yield 2)+3;$g=$f();echo $g->current(),"|";$g->send(4);echo $g->getReturn(),"|",(int)$g->valid();\n', b'2|7|0', 0),
    'array-delegation-implicit-null-return': (b'<?php\n$r=5;$a=["left"=>&$r,9=>7];$f=fn():iterable=>yield from $a;$g=$f();unset($f,$a);$r=6;echo $g->key(),":",$g->current(),"|";$r=8;echo $g->current(),"|";$g->send(12);echo $g->key(),":",$g->current(),"|";$g->next();echo (int)($g->getReturn()===null);\n', b'left:6|8|9:7|1', 0),
    'generator-delegation-used-return': (b'<?php\n$child=fn():Generator=>yield "C";$g=$child();$outer=fn():Traversable=>yield from $g;$h=$outer();unset($child,$outer,$g);$sent=new stdClass;echo $h->current(),"|";$h->send($sent);echo (int)($h->getReturn()===$sent),"|",(int)$h->valid();\n', b'C|1|0', 0),
    'inherited-private-lexical-and-receiver-scope': (b'<?php\nclass Owner{private $v=4;private function value(){return $this->v;}public function make(){return fn()=>yield [$this->value(),self::class,static::class];}}class Child extends Owner{private $v=9;}$c=new Child;$f=$c->make();$g=$f();unset($c,$f);$v=$g->current();echo $v[0],":",$v[1],":",$v[2];$g->next();\n', b'4:Owner:Child', 0),
    'static-arrow-this-error-is-deferred': (b'<?php\nclass Owner{function make(){return static fn()=>yield $this;}}$c=new Owner;$f=$c->make();$g=$f();unset($c,$f);echo "C|";try{$g->current();}catch(Error $e){echo $e->getMessage(),"|";}echo (int)$g->valid();\n', b'C|Using $this when not in object context|0', 0),
    'one-level-intersection-native-acceptance': (b'<?php\ninterface Extra{}$f=fn():Generator&Extra=>yield 8;$g=$f();echo (int)($g instanceof Generator),":",(int)($g instanceof Extra),"|",$g->current();$g->send(9);echo "|",$g->getReturn();\n', b'1:0|8|9', 0),
    'arrow-delegation-active-fiber-close': (b'<?php\nfunction leaf(){try{yield 1;}finally{echo "L",(int)(Fiber::getCurrent()!==null),"|";}}function wrap($g){try{yield from $g;}finally{echo "W",(int)(Fiber::getCurrent()!==null),"|";}}$f=new Fiber(function(){$a=fn()=>yield from leaf();$g=wrap($a());unset($a);echo $g->current(),"|";unset($g);echo "A|";return 6;});$f->start();echo "M",$f->getReturn();\n', b'1|W1|L1|A|M6', 0),
    'value-handler-throw-discards-pending-finally': (b'<?php\nfunction warn($n,$m,$f,$l){echo "H",$l,"|";throw new Exception("new");}set_error_handler("warn");\nfunction seq(){try{throw new Exception("old");}finally{echo "F|";yield $missing;echo "BAD";}}\n$g=seq();try{$g->current();}catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()===null?"null":$e->getPrevious()->getMessage(),"|";}echo (int)$g->valid();unset($g);echo "Z";\n', b'F|H3|new:null|0Z', 0),
}
DECLARATIONS = {
    'never-supertype-before-body': (b'<?php\n$f=fn():never=>yield $missing;echo "BAD";\n', b'Generator return type must be a supertype of Generator, never given', 2),
    'dnf-nested-compatible-atom-is-invalid': (b'<?php\ninterface Extra{}$f=fn():(Generator&Extra)|false=>yield 1;echo "BAD";\n', b'Generator return type must be a supertype of Generator, (Generator&Extra)|false given', 2),
    'reference-yield-from-static-rejection': (b'<?php\n$f=fn&()=>yield from [];echo "BAD";\n', b'Cannot use "yield from" inside a by-reference generator', 2),
    'multiline-header-supertype-line': (b'<?php\n$f=fn(\n$x=0\n):int=>\nyield 1;\n', b'Generator return type must be a supertype of Generator, int given', 3),
    'multiline-reference-yield-from-line': (b'<?php\n$f=fn&()=>\nyield from\n[1];\n', b'Cannot use "yield from" inside a by-reference generator', 4),
}
UNSUPPORTED = {}
WATCHED = driver.WATCHED + [
    'spec/semantics/117-arrow-compiler.watsup',
    'spec/semantics/118-arrows.watsup',
    'spec/semantics/281-fibers.watsup',
    'spec/semantics/310-generator-fiber-close.watsup',
    'spec/semantics/311-arrow-generators.watsup',
    'tests/semantics/arrow_generator_review.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = DECLARATIONS
    driver.UNSUPPORTED = UNSUPPORTED
    # Native preparation does not depend on a concurrently authored model.
    native = '--mode' in sys.argv and sys.argv[sys.argv.index('--mode') + 1] == 'native'
    driver.WATCHED = ['tests/semantics/arrow_generator_review.py', 'tests/semantics/profile.json'] if native else WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
