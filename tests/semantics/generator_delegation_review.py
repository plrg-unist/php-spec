#!/usr/bin/env python3
"""Independent ordinary-source by-value yield-from counterexamples."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from generator_review import run
from user_iterator import source as iterator_source

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'generator-fiber-arrayaccess-value-read-and-property-aliases': (b'<?php\n$key=3;\nclass Bag implements ArrayAccess {\n public $v=7;\n function offsetExists($k):bool{return true;}\n function offsetGet($k):mixed{echo "G";return $this->v;}\n function offsetSet($k,$v):void{$this->v=$v;}\n function offsetUnset($k):void{}\n}\nclass It implements Iterator {\n public $i=0;public $b;\n function __construct($b){$this->b=$b;}\n function rewind():void{echo "R";}\n function valid():bool{echo "V";return $this->i<1;}\n function &current():mixed{echo "C";echo $this->b["k"];return $this->b->v;}\n function key():mixed{echo "K";$this->b->v=9;return [&$GLOBALS["key"]];}\n function next():void{echo "N";++$this->i;}\n}\nclass Owner {\n private $p=7;\n private function seq($i){yield from $i;echo self::class,":",static::class,":",$this->p;return [$this->p,&$GLOBALS["key"]];}\n public function make($i){return $this->seq($i);}\n}\nclass Child extends Owner{}\n$o=new Child;$bag=new Bag;$it=new It($bag);\n$f=new Fiber(function($it)use($o){return $o->make($it);});\n$f->start($it);$g=$f->getReturn();unset($f,$o);\necho $g->current(),":",$g->key()[0];\n$bag->v=8;$key=4;echo ":",$g->current(),":",$g->key()[0];\n$g->next();$key=5;echo ":",$g->getReturn()[0],":",$g->getReturn()[1];\n', b'RVCG7K9:3:8:4NVOwner:Child:7:7:5'),
    'array-keys-and-own-index': (b'<?php\nfunction seq(){yield "pre";yield from [8=>"a","x"=>"b"];yield "post";}$g=seq();foreach($g as $k=>$v){echo $k,":",$v,";";}', b'0:pre;8:a;x:b;1:post;'),
    'array-empty-and-expression-result': (b'<?php\nfunction seq(){echo "B";$x=yield from [];echo $x===null?"N":"X";$y=yield from [1,2];echo $y===null?"N":"X";return 9;}$g=seq();echo "C";foreach($g as $v){echo $v;}echo $g->getReturn();', b'CBN12N9'),
    'array-reference-live-cache': (b'<?php\n$r=4;$a=[&$r,6];function seq($a){yield from $a;}$g=seq($a);echo $g->current();$r=9;echo ":",$g->current();$a[1]=8;$g->next();echo ":",$g->current();$g->next();echo $g->getReturn()===null?"N":"X";', b'4:9:6N'),
    'array-send-ignored': (b'<?php\nfunction seq(){$r=yield from [4,5];echo $r===null?"N":"X";return 7;}$g=seq();echo $g->send(99);echo $g->send(88)===null?"N":"X";echo $g->getReturn();', b'5NN7'),
    'array-throw-cancels-remainder': (b'<?php\nfunction seq(){try{yield from [1,2,3];echo "X";}catch(Exception $e){echo $e->getMessage();yield 8;}return 9;}$g=seq();echo $g->current();echo $g->throw(new Exception("E"));$g->next();echo $g->getReturn();', b'1E89'),
    'array-throw-finally-suspends': (b'<?php\nfunction seq(){try{yield from [1,2];}finally{echo "F";$x=yield 3;echo $x;}}$g=seq();$e=new Exception("E");echo $g->current();echo $g->throw($e);try{$g->send("S");}catch(Exception $x){echo $x===$e?"I":"X";}echo $g->valid()?"T":"F";', b'1F3SIF'),
    'invalid-value-caught-at-expression': (b'<?php\nfunction seq(){foreach([null,4,false,"x",new stdClass] as $v){try{$r=yield from $v;echo "X";}catch(Error $e){echo $e->getMessage(),";";}}yield 7;}$g=seq();echo $g->current();$g->next();', b'Can use "yield from" only with arrays and Traversables;Can use "yield from" only with arrays and Traversables;Can use "yield from" only with arrays and Traversables;Can use "yield from" only with arrays and Traversables;Can use "yield from" only with arrays and Traversables;7'),
    'operand-exception-skips-delegation': (b'<?php\nfunction operand(){echo "A";throw new Exception("E");}function seq(){try{yield from operand();}catch(Exception $e){echo $e->getMessage();yield 7;}}$g=seq();echo "C";echo $g->current();$g->next();', b'CAE7'),
    'generator-forward-send-and-return': (b'<?php\nfunction inner(){echo "I";$x=yield "k"=>1;echo $x;yield "j"=>$x+1;return 9;}function outer($g){echo "O";$r=yield from $g;echo "R",$r;yield "z"=>$r;return $r+1;}$i=inner();$g=outer($i);echo "C";echo $g->send(4),":",$g->key();$g->next();echo ":",$g->current();$g->next();echo ":",$g->getReturn(),":",$i->getReturn();', b'COI45:jR9:9:10:9'),
    'generator-already-paused-not-advanced': (b'<?php\nfunction inner(){$x=yield 4;echo $x;yield 5;return 6;}function outer($i){return yield from $i;}$i=inner();echo $i->current();$g=outer($i);echo ":",$g->current(),":",$i->current();echo ":",$g->send(8);$g->next();echo ":",$g->getReturn();', b'4:4:4:85:6'),
    'generator-prior-cache-and-own-index': (b'<?php\nfunction inner(){yield "k"=>1;return 7;}function outer($i){yield "pre";$r=yield from $i;echo "R",$r;yield "post";return 9;}$i=inner();$g=outer($i);echo $g->current(),":",$g->key(),"|";$g->next();echo $g->current(),":",$g->key(),"|";$i->next();echo $g->current(),":",$g->key(),"|";$g->next();echo $g->current(),":",$g->key(),"|";$g->next();echo $g->getReturn();', b'pre:0|1:k|1:0|R7post:1|9'),
    'generator-direct-exhaustion-getters': (b'<?php\nfunction inner(){yield "a"=>1;yield "b"=>2;return 7;}function outer($i){echo "O";$r=yield from $i;echo "R",$r;yield "c"=>8;return 9;}$i=inner();$g=outer($i);echo $g->current(),":",$g->key(),"|";$i->next();echo $g->current(),":",$g->key(),"|";$i->next();echo $i->getReturn(),"|";try{echo "r",$g->getReturn();}catch(Throwable $e){echo get_class($e),":",$e->getMessage();}echo "|";echo $g->valid()?"T":"F";echo ":",$g->current(),":",$g->key(),"|";$g->next();echo $g->current(),":",$g->key(),":",$g->valid()?"T":"F","|";$g->next();echo $g->current()===null?"N":"X";echo ":",$g->valid()?"T":"F",":",$g->getReturn();', b"O1:a|2:b|7|rException:Cannot get return value of a generator that hasn't returned|T:2:|R78:c:T|N:F:9"),
    'generator-nested-completed-leaf-cache': (b'<?php\nfunction inner(){yield "a"=>1;yield "b"=>2;return 7;}function middle($i){return yield from $i;}function outer($m){return yield from $m;}$i=inner();$m=middle($i);$g=outer($m);$g->current();$i->next();$i->next();echo $g->current(),":",$g->key()===null?"N":"X",":",$g->valid()?"T":"F";$g->next();echo ":",$g->getReturn();', b'2:N:T:7'),
    'generator-detached-reference-retval': (b'<?php\n$r=4;function inner(&$r){yield [&$r];return [&$r];}function outer(){return yield from $GLOBALS["i"];}$i=inner($r);$g=outer();$g->current();$i->next();unset($i);$g->current();$r=9;$g->next();echo $g->getReturn()[0];unset($g);echo "Z";', b'9Z'),
    'generator-empty-return-no-spurious-yield': (b'<?php\nfunction inner(){if(false)yield 1;echo "I";return 8;}function outer(){echo "O";return yield from inner();}$g=outer();echo "C";echo $g->current()===null?"N":"X";echo $g->getReturn(),":",$g->valid()?"T":"F";', b'COIN8:F'),
    'generator-nested-send-expression': (b'<?php\nfunction leaf(){$x=yield 1;return $x+1;}function middle(){return (yield from leaf())+1;}function outer(){return (yield from middle())+1;}$g=outer();echo $g->send(4)===null?"N":"X";echo $g->getReturn();', b'N7'),
    'generator-fresh-throw-active-leaf': (b'<?php\nfunction inner(){echo "I";try{yield 1;}catch(Exception $e){echo $e->getMessage();yield 2;}return 7;}function outer(){echo "O";return yield from inner();}$g=outer();echo "C";echo $g->throw(new Exception("E"));$g->next();echo ":",$g->getReturn();', b'COIE2:7'),
    'generator-fresh-child-initialization-exception': (b'<?php\nfunction inner(){echo "I";throw new Exception("initial");yield 1;}function outer(){echo "O";try{yield from inner();}finally{echo "F";}}$g=outer();$e=new Exception("input");echo "C";try{$g->throw($e);}catch(Exception $x){echo $x===$e?"I":"X";echo ":",$x->getMessage(),":",$x->getPrevious()->getMessage();}echo $g->valid()?"T":"F";', b'COIFI:input:initialF'),
    'generator-forward-throw-catch': (b'<?php\nfunction inner(){try{yield 1;}catch(Exception $e){echo $e->getMessage();yield 2;}return 7;}function outer(){echo "O";$r=yield from inner();echo "R",$r;return $r+1;}$g=outer();echo $g->current();echo $g->throw(new Exception("E"));$g->next();echo $g->getReturn();', b'O1E2R78'),
    'generator-inner-throw-outer-catch-finally': (b'<?php\nfunction inner(){try{yield 1;throw new Exception("E");}finally{echo "I";}}function outer(){try{yield from inner();}catch(Exception $e){echo $e->getMessage();yield 3;}finally{echo "O";}}$g=outer();echo $g->current();$g->next();echo $g->current();$g->next();', b'1IE3O'),
    'generator-injected-finally-send': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "F";$x=yield 2;echo $x;}}function outer(){try{yield from inner();}catch(Exception $e){echo $e->getMessage();yield 3;}return 8;}$g=outer();echo $g->current();echo $g->throw(new Exception("E"));echo $g->send("S");$g->next();echo $g->getReturn();', b'1F2SE38'),
    'generator-array-reference-retval-copy': (b'<?php\n$r=4;function inner(&$r){yield [&$r];return [&$r];}function outer($i){$a=yield from $i;$a[1]=8;return $a;}$i=inner($r);$g=outer($i);$v=$g->current();$r=9;$g->next();echo $g->getReturn()[0],":",$g->getReturn()[1],":",isset($i->getReturn()[1])?"X":"N",":",$v[0];', b'9:8:N:9'),
    'generator-closed-completed-input': (b'<?php\nfunction inner(){yield 1;return 7;}function outer($i){try{$r=yield from $i;echo "R",$r;}catch(Error $e){echo $e->getMessage();}yield 3;}$i=inner();$i->next();echo $i->getReturn(),"|";$g=outer($i);echo $g->current();$g->next();', b'7|Generator passed to yield from was aborted without proper return and is unable to continue3'),
    'generator-aborted-input': (b'<?php\nfunction inner(){throw new Exception("E");yield 1;}function outer($i){try{yield from $i;}catch(Error $e){echo $e->getMessage();}yield 3;}$i=inner();try{$i->current();}catch(Exception $e){echo $e->getMessage(),"|";}$g=outer($i);echo $g->current();$g->next();', b'E|Generator passed to yield from was aborted without proper return and is unable to continue3'),
    'generator-shared-parents-progress-and-return': (b'<?php\nfunction inner(){yield 1;yield 2;return 7;}function outer($i,$n){$r=yield from $i;echo $n,$r;return $r+1;}$i=inner();$a=outer($i,"A");$b=outer($i,"B");echo $a->current(),":",$b->current();$a->next();echo ":",$b->current();$b->next();echo ":",$b->getReturn(),":";$a->next();echo $a->getReturn();', b'1:1:2B7:8:A78'),
    'generator-shared-abort-distinct-exception': (b'<?php\nfunction inner(){yield 1;throw new Exception("E");}function outer($i,$n){try{yield from $i;}catch(Exception $e){echo $n,get_class($e),":",$e->getMessage(),";";}return 8;}$i=inner();$a=outer($i,"A");$b=outer($i,"B");echo $a->current(),$b->current();$a->next();$b->next();echo $a->getReturn(),$b->getReturn();', b'11AException:E;BClosedGeneratorException:Generator yielded from aborted, no return value available;88'),
    'generator-nested-independent-completion-key': (b'<?php\nfunction inner(){yield "k"=>1;return 7;}function middle($i){yield 6=>"m-pre";return yield from $i;}function outer($m){yield 8=>"o-pre";return yield from $m;}$i=inner();$m=middle($i);$g=outer($m);echo $m->current(),":",$g->current(),"|";$m->next();$g->next();echo $g->current(),":",$g->key(),"|";$i->next();echo $g->current(),":",$g->key(),"|";$g->next();echo $g->valid()?"T":"F",":",$g->getReturn();', b'm-pre:o-pre|1:k|1:6|F:7'),
    'generator-waiting-parent-reentry-preserves-frame': (b'<?php\nfunction inner(){yield 1;try{$GLOBALS["b"]->next();}catch(Error $e){echo $e->getMessage(),"|";}yield 2;return 7;}function outer($i,$n){$r=yield from $i;echo $n,$r;return $r+1;}$i=inner();$a=outer($i,"A");$b=outer($i,"B");echo $a->current(),":",$b->current(),"|";$a->next();echo $b->current(),":",$b->valid()?"T":"F","|";try{$b->rewind();echo "R";}catch(Throwable $e){echo get_class($e),":",$e->getMessage();}$b->next();echo ":",$b->getReturn(),"|";$a->next();echo $a->getReturn();', b'1:1|Cannot resume an already running generator|2:T|RB7:8|A78'),
    'generator-live-chain-trace': (b'<?php\nfunction inner($n){yield 1;throw new Exception("E");}function middle($i){yield from $i;}function outer($i){yield from $i;}function resume($g){$g->next();}$i=inner(4);$m=middle($i);$g=outer($m);$g->current();try{resume($g);}catch(Exception $e){foreach($e->getTrace() as $r){echo $r["function"],":";if($r["function"]==="inner")echo $r["args"][0];echo ";";}}', b'inner:4;middle:;outer:;next:;resume:;'),
    'generator-direct-delegate-trace-excludes-waiters': (b'<?php\nfunction inner(){yield 1;throw new Exception("E");}function outer($i){yield from $i;}$i=inner();$g=outer($i);$g->current();try{$i->next();}catch(Exception $e){foreach($e->getTrace() as $r){echo $r["function"],";";}}try{$g->current();}catch(Exception $e){echo get_class($e);}', b'inner;next;ClosedGeneratorException'),
    'generator-self-delegation-error': (b'<?php\nfunction seq(){try{yield from yield 1;}catch(Error $e){echo $e->getMessage();yield 3;}}$g=seq();echo $g->send($g);$g->next();', b'Impossible to yield from the Generator being currently run3'),
    'generator-reentrant-through-parent': (b'<?php\nfunction inner(){yield 1;try{$GLOBALS["g"]->next();}catch(Error $e){echo $e->getMessage(),"|";}yield 2;}function outer($i){yield from $i;}$i=inner();$g=outer($i);echo $g->current();$g->next();echo $g->current();$g->next();', b'1Cannot resume an already running generator|2'),
    'generator-rewind-after-advancement': (b'<?php\nfunction inner(){yield 1;yield 2;}function outer($i){yield from $i;}$i=inner();$g=outer($i);echo $g->current();$g->rewind();echo $g->current();$g->next();try{$g->rewind();}catch(Exception $e){echo "R";}echo $g->current();$g->next();', b'11R2'),
    'iterator-callback-order-and-null-return': (iterator_source('function seq(){echo "B";$r=yield from new It;echo $r===null?"Z":"X";return 7;}$g=seq();echo "A";foreach($g as $k=>$v){echo "[",$k,":",$v,"]";}echo $g->getReturn();'), b'ABRVCK[20:10]NVCK[21:11]NVZ7'),
    'iterator-raw-array-key': (iterator_source('function seq(){yield from new It;}foreach(seq() as $k=>$v){echo $k[0],":",$v,";";}', {'key': 'function key():mixed {echo "K";return [$this->i];}'}), b'RVCK0:10;NVCK1:11;NV'),
    'iterator-send-ignored': (iterator_source('function seq(){$r=yield from new It;echo $r===null?"Z":"X";return 7;}$g=seq();echo $g->send(9);echo $g->send(8)===null?"N":"X";echo $g->getReturn();'), b'RVCKNVCK11NVZN7'),
    'iterator-current-reference-live-cache': (iterator_source('function seq($i){yield from $i;}$i=new It;$g=seq($i);echo $g->current(),":";$i->v=8;echo $g->current();$g->next();', {'current': 'function &current():mixed {echo "C";return $this->v;}', 'key': 'function key():mixed {echo "K";$this->v=9;return 0;}', 'valid': 'function valid():bool {echo "V";return $this->i<1;}'}, 'public $i=0;public $v=7;'), b'RVCK9:8NV'),
    'iterator-current-reference-rebind': (iterator_source('function seq($i){yield from $i;}$i=new It;$g=seq($i);echo $g->current(),":";$GLOBALS["old"]=8;echo $g->current();$g->next();', {'current': 'function &current():mixed {$this->v=&$GLOBALS["old"];echo "C";return $this->v;}', 'key': 'function key():mixed {echo "K";$GLOBALS["replacement"]=9;$this->v=&$GLOBALS["replacement"];return 0;}', 'valid': 'function valid():bool {echo "V";return $this->i<1;}'}, 'public $i=0;public $v=7;', prefix='$old=7;'), b'RVCK7:8NV'),
    'iterator-valid-reference-consumed': (iterator_source('function seq(){yield from new It;}foreach(seq() as $k=>$v){echo $k,":",$v,";";}', {'valid': 'function &valid():bool {echo "V";$this->ok=$this->i<2;return $this->ok;}'}, 'public $i=0;public $ok=true;'), b'RVCK20:10;NVCK21:11;NV'),
    'iterator-key-reference-copied': (iterator_source('function seq($i){yield from $i;}$i=new It;$g=seq($i);$g->current();echo $g->key();$i->k=99;echo ":",$g->key();$g->next();echo $g->key();$g->next();', {'key': 'function &key():mixed {echo "K";$this->k=20+$this->i;return $this->k;}'}, 'public $i=0;public $k=20;'), b'RVCK20:20NVCK21NV'),
    'iterator-inherited-private-generator-scope': (iterator_source('class DerivedIt extends It{}class Owner{private $v=7;private function seq($i){yield from $i;echo self::class,":",static::class,":",$this->v;}public function make($i){return $this->seq($i);}}class Child extends Owner{}$o=new Child;$g=$o->make(new DerivedIt);unset($o);echo $g->current();$g->next();echo $g->current();$g->next();'), b'RVCK10NVCK11NVOwner:Child:7'),
    'iterator-valid-nan-handler': (iterator_source('function seq(){yield from new It;}function warning($n,$m,$f,$l){echo "H",$n===E_WARNING?"W":"X",$m==="unexpected NAN value was coerced to bool"?"M":"X",$l===$GLOBALS["site"]?"L":"X",":";return true;}$site=__LINE__;set_error_handler("warning");$g=seq();echo $g->current();$g->next();', {'valid': '#[ReturnTypeWillChange] function valid(){echo "V";return $this->i<1?NAN:false;}'}), b'RVHWML:CK10NV'),
    'iterator-valid-nan-throw': (iterator_source('function seq(){try{yield from new It;}catch(Exception $e){echo $e->getMessage();yield 8;}finally{echo "F";}}function warning($n,$m,$f,$l){echo "H",$n===E_WARNING?"W":"X",$m==="unexpected NAN value was coerced to bool"?"M":"X",$l===$GLOBALS["site"]?"L":"X",":";throw new Exception("E");}$site=__LINE__;set_error_handler("warning");$g=seq();echo $g->current();$g->next();', {'valid': '#[ReturnTypeWillChange] function valid(){echo "V";return NAN;}'}), b'RVHWML:E8F'),
    'iterator-valid-nan-reference-retained': (iterator_source('function seq($i){yield from $i;}function warning($n,$m,$f,$l){$GLOBALS["nan"]=1.0;$GLOBALS["replacement"]=false;$GLOBALS["it"]->v=&$GLOBALS["replacement"];unset($GLOBALS["nan"]);echo "H";return true;}$it=new It;set_error_handler("warning");$g=seq($it);echo $g->current();$g->next();', {'valid': '#[ReturnTypeWillChange] function &valid(){echo "V";if($this->i<1){$this->v=&$GLOBALS["nan"];return $this->v;}return $GLOBALS["no"];}'}, 'public $i=0;public $v=7;', prefix='$nan=NAN;$no=false;'), b'RVHCK10NV'),
    'iterator-throw-stops-next': (iterator_source('function seq(){try{yield from new It;echo "X";}catch(Exception $e){echo $e->getMessage();yield 8;}}$g=seq();echo $g->current();echo $g->throw(new Exception("E"));$g->next();'), b'RVCK10E8'),
}
for stage in ['rewind', 'valid', 'current', 'key', 'next']:
    typ = {'rewind': 'void', 'next': 'void', 'valid': 'bool'}.get(stage, 'mixed')
    method = f'function {stage}():{typ} {{echo "{stage[0].upper()}";throw new Exception("E");}}'
    program = 'function seq(){try{$r=yield from new It;echo "X";}catch(Exception $e){echo $e->getMessage();yield 8;}}$g=seq();foreach($g as $v){echo $v;}'
    CASES['iterator-throw-' + stage] = (iterator_source(program, {stage: method}), {'rewind': b'RE8', 'valid': b'RVE8', 'current': b'RVCE8', 'key': b'RVCKE8', 'next': b'RVCK10NE8'}[stage])
for name, value in [('zero', b'0.0'), ('integer-sign-bit', b'(-PHP_INT_MAX-1)')]:
    CASES['iterator-valid-nan-reference-' + name] = (CASES['iterator-valid-nan-reference-retained'][0].replace(b'$GLOBALS["nan"]=1.0;', b'$GLOBALS["nan"]=' + value + b';'), b'RVH')

DECLARATIONS = {
    'global-yield-from': (b'<?php\nyield from [];', b'The "yield" expression can only be used inside a function', 2),
    'byref-yield-from-source-line': (b'<?php\nfunction &seq(){\n echo "B";\n yield from [];\n}\n', b'Cannot use "yield from" inside a by-reference generator', 4),
    'byref-prior-static-error': (b'<?php\nfunction &seq(){\n break;\n yield from [];\n}\n', b"'break' not in the 'loop' or 'switch' context", 3),
    'byref-yield-from-forbidden': (b'<?php\nfunction &seq(){yield from [];}', b'Cannot use "yield from" inside a by-reference generator', 2),
}
UNSUPPORTED = {
    'generator-fiber-arrayaccess-reference-read-required': (CASES['generator-fiber-arrayaccess-value-read-and-property-aliases'][0].replace(b'function offsetGet(', b'function &offsetGet('), CASES['generator-fiber-arrayaccess-value-read-and-property-aliases'][1]),
    'generator-fiber-arrayaccess-reference-dimension-required': (b'<?php\n$key=3;\nclass Bag implements ArrayAccess {\n public $v=7;\n function offsetExists($k):bool{return true;}\n function &offsetGet($k):mixed{echo "G";return $this->v;}\n function offsetSet($k,$v):void{$this->v=$v;}\n function offsetUnset($k):void{}\n}\nclass It implements Iterator {\n public $i=0;public $b;\n function __construct($b){$this->b=$b;}\n function rewind():void{echo "R";}\n function valid():bool{echo "V";return $this->i<1;}\n function &current():mixed{echo "C";return $this->b["k"];}\n function key():mixed{echo "K";$this->b->v=9;return [&$GLOBALS["key"]];}\n function next():void{echo "N";++$this->i;}\n}\nclass Owner {\n private $p=7;\n private function seq($i){yield from $i;echo self::class,":",static::class,":",$this->p;return [$this->p,&$GLOBALS["key"]];}\n public function make($i){return $this->seq($i);}\n}\nclass Child extends Owner{}\n$o=new Child;$bag=new Bag;$it=new It($bag);\n$f=new Fiber(function($it)use($o){return $o->make($it);});\n$f->start($it);$g=$f->getReturn();unset($f,$o);\necho $g->current(),":",$g->key()[0];\n$bag->v=8;$key=4;echo ":",$g->current(),":",$g->key()[0];\n$g->next();$key=5;echo ":",$g->getReturn()[0],":",$g->getReturn()[1];\n', b'RVCGK9:3:8:4NVOwner:Child:7:7:5'),
    'aggregate-required': (iterator_source('').replace(b'class It ', b'class Inner ') + b'\nclass Aggregate implements IteratorAggregate{function getIterator():Traversable{echo "G";return new Inner;}}function seq(){yield from new Aggregate;}foreach(seq() as $v){echo $v;}', b'GRVCK10NVCK11NV'),
    'force-close-delegation-finally': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function outer(){try{yield from inner();}finally{echo "O";}}$g=outer();echo $g->current();unset($g);echo "Z";', b'1IOZ'),
    'iterator-valid-nan-raw-type-change': (CASES['iterator-valid-nan-reference-retained'][0].replace(b'$GLOBALS["nan"]=1.0;', b'$GLOBALS["nan"]=false;'), b'RVHCK10NV'),
}
UNSUPPORTED_REASONS = {
    'generator-fiber-arrayaccess-reference-read-required': 'ArrayAccess by-reference result protocol',
    'generator-fiber-arrayaccess-reference-dimension-required': 'ArrayAccess read-write/reference dimension protocol',
    "aggregate-required": "internal interface method contract",
    "force-close-delegation-finally": "started generator force-close finalizer",
    "iterator-valid-nan-raw-type-change": "yield from valid NaN raw payload type change",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['pin', 'native', 'full'], default='full')
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES) + list(DECLARATIONS) + list(UNSUPPORTED)
    assert names and len(set(names)) == len(names) and all(n in CASES or n in DECLARATIONS or n in UNSUPPORTED for n in names)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    php = ROOT / '.tools/php/bin/php'
    flags = [v for key, value in profile.items() for v in ['-d', f'{key}={value}']]
    directory = Path(tempfile.mkdtemp(prefix='generator-delegation-review-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'mode': args.mode, 'records': [], 'agreements': 0, 'unsupported': 0,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'tools': {'php_sha256': hashlib.sha256(php.read_bytes()).hexdigest(), 'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    print(directory, flush=True)
    try:
        (directory / 'candidate.diff').write_bytes(subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT))
        (directory / 'case-fixture.py').write_bytes(Path(__file__).read_bytes())
        identity = run([str(php), '-n', *flags, '-r', 'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,get_loaded_extensions(),ini_get_all(null,false)]);'], directory / 'runtime', 10)
        assert identity.returncode == 0 and not identity.stderr
        report['runtime'] = json.loads(identity.stdout)
        assert report['runtime'][:4] == ['8.5.10', 'cli', 8, False]
        assert all(report['runtime'][5][key] == value for key, value in profile.items())
        if args.mode == 'full':
            report['tools']['adapter_sha256'] = hashlib.sha256((ROOT / '_build/default/adapter/main.exe').read_bytes()).hexdigest()
        for name in names:
            case = directory / name
            case.mkdir()
            source = CASES[name][0] if name in CASES else DECLARATIONS[name][0] if name in DECLARATIONS else UNSUPPORTED[name][0]
            path = case / 'source.php'
            path.write_bytes(source)
            row = {'id': name, 'source_sha256': hashlib.sha256(source).hexdigest()}
            report['records'].append(row)
            native = run([str(php), '-n', *flags, str(path)], case / 'native', 10)
            row.update(native_exit=native.returncode, native_stdout=base64.b64encode(native.stdout).decode(), native_stderr=base64.b64encode(native.stderr).decode())
            if name in DECLARATIONS:
                message, line = DECLARATIONS[name][1:]
                expected_error = b'Fatal error: ' + message + b' in ' + os.fsencode(path) + f' on line {line}\nStack trace:\n#0 {{main}}\n'.encode()
                assert native.returncode == 255 and not native.stdout and native.stderr == expected_error, (name, native.stderr)
            else:
                expected = CASES[name][1] if name in CASES else UNSUPPORTED[name][1]
                assert native.returncode == 0 and not native.stderr, (name, native)
                if args.mode != 'pin':
                    assert expected is not None and native.stdout == expected, (name, native.stdout, expected)
            if args.mode == 'full':
                model = run([str(ROOT / 'bin/php-semantics'), str(path), '--steps', '100000', '--timeout', '60'], case / 'model', 90)
                row['model_exit'] = model.returncode
                assert not model.stderr, (name, model.stderr)
                observation = json.loads(model.stdout)
                row['model_status'] = observation['status']
                if name in UNSUPPORTED:
                    assert model.returncode == 1 and observation['status'] == 'unsupported' and observation['reason'] == UNSUPPORTED_REASONS[name], (name, observation)
                    report['unsupported'] += 1
                else:
                    assert model.returncode == 0 and observation['status'] == ('static_rejection' if name in DECLARATIONS else 'normal'), (name, observation)
                    assert observation['reason'] is None
                    assert observation['exit_status'] == native.returncode
                    assert base64.b64decode(observation['stdout'], validate=True) == native.stdout
                    assert base64.b64decode(observation['stderr'], validate=True) == native.stderr
                    report['agreements'] += 1
                assert observation['frontend'] == 'accepted' and observation['checked'] == 'program'
            row['passed'] = True
            print(name, repr(native.stdout), 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(directory / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()
