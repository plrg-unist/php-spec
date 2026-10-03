#!/usr/bin/env python3
"""Direct static setter consumers: original-source/native tuples, bounded scope."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def source(declaration, body):
    return ('<?php class A{' + declaration + '}' + body).encode()


CASES = {
    'simple-denied': source('public private(set) static int $p=1;',
                           'function rhs(){echo "R";return 2;}try{A::$p=rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p;'),
    'simple-uninitialized-denied': source('public private(set) static int $p;',
                           'function rhs(){echo "R";return 2;}try{A::$p=rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",isset(A::$p)?"set":"unset";'),
    'string-callback-denied': source('public private(set) static string $p="old";',
                           'class D{public function __toString():string{echo "T";return "s";}}function rhs(){echo "R";return new D;}try{A::$p=rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p;'),
    'private-string-callback-allowed': source('public private(set) static string $p="old";public function put($x){return self::$p=$x;}',
                           'class D{public function __toString():string{echo "T";return "s";}}$a=new A;echo $a->put(new D),"|",A::$p;'),
    'protected-string-callback-allowed': source('public protected(set) static string $p="old";',
                           'class B extends A{public function put($x){return self::$p=$x;}}class D{public function __toString():string{echo "T";return "s";}}$b=new B;echo $b->put(new D),"|",A::$p;'),
    'private-simple-allowed': source('public private(set) static int $p=1;public function put($x){return self::$p=$x;}',
                           '$a=new A;echo $a->put(2),"|",A::$p;'),
    'compound-denied': source('public protected(set) static int $p=1;',
                           'function rhs(){echo "R";return 2;}try{A::$p+=rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p;'),
    'compound-zero-denied': source('public private(set) static int $p=1;',
                           'try{A::$p/=0;}catch(Error $e){echo $e->getMessage();}'),
    'compound-uninitialized': source('public protected(set) static int $p;',
                           'function rhs(){echo "R";return 2;}try{A::$p+=rhs();}catch(Error $e){echo "|",$e->getMessage();}'),
    'compound-update-allowed': source('public private(set) static int $p=1;public function put(){self::$p+=2;echo self::$p++,"|",++self::$p;}',
                           '$a=new A;$a->put();echo "|",A::$p;'),
    'update-deprecation-denied': source('public private(set) static string $p="hello!";',
                           'try{A::$p--;}catch(Error $e){echo $e->getMessage();}echo "|",A::$p;'),
    'coalesce-present': source('public private(set) static ?int $p=1;',
                           'function rhs(){echo "R";return 2;}echo A::$p??=rhs();'),
    'coalesce-null-denied': source('public private(set) static ?int $p=null;',
                           'function rhs(){echo "R";return 2;}try{A::$p??=rhs();}catch(Error $e){echo "|",$e->getMessage();}'),
    'coalesce-uninitialized-denied': source('public private(set) static ?int $p;',
                           'function rhs(){echo "R";return 2;}try{A::$p??=rhs();}catch(Error $e){echo "|",$e->getMessage();}'),
    'coalesce-uninitialized-allowed': source('public private(set) static ?int $p;public function put(){return self::$p??=2;}',
                           '$a=new A;echo $a->put(),"|",A::$p;'),
    'dimension-denied': source('public private(set) static array $p=[];',
                           'function key_set(){echo "K";return 0;}function rhs(){echo "R";return 2;}try{A::$p[key_set()]=rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p===[]?"empty":"changed";'),
    'nested-dimension-denied': source('public private(set) static array $p=[[1]];',
                           'function rhs(){echo "R";return 2;}try{A::$p[0][0]=rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p[0][0];'),
    'append-denied': source('public private(set) static array $p=[];',
                           'try{A::$p[]=2;}catch(Error $e){echo $e->getMessage();}'),
    'string-offset-denied': source('public private(set) static string $p="abc";',
                           'try{A::$p[0]="s";}catch(Error $e){echo $e->getMessage();}echo "|",A::$p;'),
    'scalar-dimension-denied': source('public private(set) static int $p=1;',
                           'try{A::$p[0]=2;}catch(Error $e){echo $e->getMessage();}'),
    'dimension-compound-denied': source('public private(set) static array $p=[1];',
                           'try{A::$p[0]/=0;}catch(Error $e){echo $e->getMessage();}'),
    'dimension-coalesce-denied': source('public private(set) static array $p=[];',
                           'function rhs(){echo "R";return 2;}try{A::$p[0]??=rhs();}catch(Error $e){echo "|",$e->getMessage();}'),
    'dimensions-allowed': source('public private(set) static array $p=[[1]];public function put(){self::$p[0][0]+=2;self::$p[0][]=4;self::$p[1]??=[5];unset(self::$p[0][1]);}',
                           '$a=new A;$a->put();echo A::$p[0][0],"|",A::$p[1][0],"|",isset(A::$p[0][1])?"set":"unset";'),
    'untyped-auto-array-regression': source('public static $p=null;',
                           'A::$p[]=2;echo A::$p[0];'),
    'dimension-uninitialized-error-chain': source('public private(set) static int $p;',
                           'try{A::$p[0]=2;}catch(Error $e){echo $e->getMessage(),"|",$e->getPrevious()?->getMessage();}echo "|",isset(A::$p)?"set":"unset";'),
    'dimension-null-error-chain': source('public private(set) static ?int $p=null;',
                           'try{A::$p[0]=2;}catch(Error $e){echo $e->getMessage(),"|",$e->getPrevious()?->getMessage();}echo "|",A::$p===null?"null":"other";'),
    'dimension-false-error-chain': source('public private(set) static bool $p=false;',
                           'try{A::$p[0]=2;}catch(Error $e){echo $e->getMessage(),"|",$e->getPrevious()?->getMessage();}echo "|",A::$p===false?"false":"other";'),
    'reference-read-denied': source('public private(set) static int $p=1;',
                           'try{$r=&A::$p;}catch(Error $e){echo $e->getMessage();}'),
    'reference-write-cv-denied': source('public private(set) static int $p=1;',
                           'try{A::$p=&$missing;}catch(Error $e){echo $e->getMessage();}echo "|",isset($missing)?"set":"unset";echo "|",$missing;'),
    'reference-uninitialized-error-chain': source('public private(set) static int $p;',
                           'try{$r=&A::$p;}catch(Error $e){echo $e->getMessage(),"|",$e->getPrevious()?->getMessage();}echo "|",isset(A::$p)?"set":"unset";'),
    'reference-nullable-initialization': source('public private(set) static ?int $p;',
                           'try{$r=&A::$p;}catch(Error $e){echo $e->getMessage(),"|",$e->getPrevious()?->getMessage();}echo "|",A::$p===null?"null":"other";'),
    'byref-send-denied': source('public private(set) static int $p=1;',
                           'function take(&$x){echo "C";$x=2;}try{take(A::$p);}catch(Error $e){echo $e->getMessage();}'),
    'byvalue-send-allowed': source('public private(set) static int $p=1;',
                           'function take($x){echo "C",$x;}take(A::$p);'),
    'unpack-byref-read': source('public private(set) static array $p=[1];',
                           'function take(&$x){echo "C";$x=2;}take(...A::$p);echo "|",A::$p[0];'),
    'escaped-alias': source('public private(set) static int $p=1;public function &ref(){return self::$p;}',
                           '$a=new A;$r=&$a->ref();$r=2;echo A::$p;'),
    'escaped-alias-type-source': source('public private(set) static int $p=1;public function &ref(){return self::$p;}',
                           '$a=new A;$r=&$a->ref();try{$r=[];}catch(TypeError $e){echo $e->getMessage();}echo "|",A::$p;'),
    'array-read-copy': source('public private(set) static array $p=[1];',
                           '$x=A::$p;$x[0]=2;echo A::$p[0],"|",$x[0];'),
    'foreach-reference-denied': source('public private(set) static array $p=[1];',
                           'try{foreach(A::$p as &$x){echo "C";}}catch(Error $e){echo $e->getMessage();}'),
    'foreach-reference-allowed': source('public private(set) static array $p=[1];public function put(){foreach(self::$p as &$x){$x=2;}}',
                           '$a=new A;$a->put();echo A::$p[0];'),
    'foreach-value-allowed': source('public private(set) static array $p=[1];',
                           'foreach(A::$p as $x){echo $x;}'),
    'unset-dimension-denied': source('public private(set) static array $p=[];',
                           'function key_set(){echo "K";return 0;}try{unset(A::$p[key_set()]);}catch(Error $e){echo "|",$e->getMessage();}'),
    'unset-uninitialized-silent': source('public private(set) static array $p;',
                           'function key_set(){echo "K";return 0;}unset(A::$p[key_set()]);echo "done";'),
    'whole-unset': source('public private(set) static int $p=1;',
                           'try{unset(A::$p);}catch(Error $e){echo $e->getMessage();}'),
    'simple-undefined-cv-order': source('public private(set) static int $p=1;',
                           'try{A::$p=$missing;}catch(Error $e){echo $e->getMessage();}'),
    'simple-get-denied-cv-order': source('private static int $p=1;',
                           'try{A::$p=$missing;}catch(Error $e){echo $e->getMessage();}'),
    'compound-undefined-cv-order': source('public private(set) static int $p=1;',
                           'try{A::$p+=$missing;}catch(Error $e){echo $e->getMessage();}'),
    'coalesce-undefined-cv-order': source('public private(set) static ?int $p=null;',
                           'try{A::$p??=$missing;}catch(Error $e){echo $e->getMessage();}'),
    'coalesce-get-denied-cv-order': source('private static ?int $p=null;',
                           'try{A::$p??=$missing;}catch(Error $e){echo $e->getMessage();}'),
    'protected-child-allowed': source('public protected(set) static int $p=1;',
                           'class B extends A{public function put(){self::$p=2;}}$b=new B;$b->put();echo A::$p,"|",B::$p;'),
    'private-child-denied': source('public private(set) static int $p=1;',
                           'class B extends A{public function put(){self::$p=2;}}$b=new B;try{$b->put();}catch(Error $e){echo $e->getMessage();}'),
    'protected-prototype-sibling': source('public protected(set) static int $p=1;public function put(){B::$p=4;}',
                           'class B extends A{public protected(set) static int $p=2;}class C extends A{public function putB(){B::$p=3;}}$c=new C;$c->putB();echo B::$p,"|";$a=new A;$a->put();echo B::$p;'),
    'ordinary-private-regression': source('private static int $p=1;public function put(){return self::$p=2;}',
                           '$a=new A;echo $a->put();try{echo A::$p;}catch(Error $e){echo "|",$e->getMessage();}'),
    'foreach-reference-denied-line': b'<?php\nclass A {public private(set) static array $p=[1];}\ntry {\n foreach (\n  A::$p\n  as &$x\n ) {echo "C";}\n} catch(Error $e) {echo $e->getLine(),"|",$e->getMessage();}\n',
    'foreach-reference-uninitialized-line': b'<?php\nclass A {public private(set) static array $p;}\ntry {\n foreach (\n  A::$p\n  as &$x\n ) {echo "C";}\n} catch(Error $e) {echo $e->getLine(),"|",$e->getMessage(),"|",$e->getPrevious()->getLine(),"|",$e->getPrevious()->getMessage();}\n',
}


CASES.update({
    'reference-deferred-named-class': b'<?php function &rhs(){echo "R";if(true){class A{public private(set) static int $p=1;}}$v=2;return $v;}try{A::$p=&rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p;',
    'reference-deferred-string-class': b'<?php function &rhs(){echo "R";if(true){class A{public private(set) static int $p=1;}}$v=2;return $v;}try{("A")::$p=&rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p;',
    'reference-deferred-property-cv': source('public private(set) static int $p=1;public static int $q=3;',
        '$name="p";function &rhs(){global $name;echo "R";$name="q";$v=2;return $v;}A::${$name}=&rhs();echo "|",A::$p,"|",A::$q;'),
    'reference-captured-dynamic-class': source('public private(set) static int $p=1;',
        'class B{public static int $p=3;}$class="A";function &rhs(){global $class;echo "R";$class="B";$v=2;return $v;}try{$class::$p=&rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p,"|",B::$p;'),
    'reference-captured-property-call': source('public private(set) static int $p=1;public static int $q=3;',
        '$name="p";function name(){echo "N";return "p";}function &rhs(){global $name;echo "R";$name="q";$v=2;return $v;}try{A::${name()}=&rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p,"|",A::$q;'),
    'reference-return-denied': source('public private(set) static int $p=1;',
        'function &rhs(){echo "R";$v=2;return $v;}try{A::$p=&rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p;'),
    'reference-dimension-denied': source('public private(set) static int $p=1;',
        '$a=[2];function key_ref(){echo "K";return 0;}try{A::$p=&$a[key_ref()];}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p,"|",$a[0];'),
    'reference-return-allowed': source('public private(set) static int $p=1;public function put(){self::$p=&rhs();}',
        'function &rhs(){echo "R";$v=2;return $v;}$a=new A;$a->put();echo "|",A::$p;'),
    'reference-dimension-allowed-type-source': source('public private(set) static int $p=1;public function put(&$a){self::$p=&$a[0];}',
        '$values=[2];$a=new A;$a->put($values);$values[0]=3;echo A::$p;try{$values[0]=[];}catch(TypeError $e){echo "|",$e->getMessage();}echo "|",A::$p;'),
})
EXPECTED = {
    'reference-deferred-named-class': b'R|Cannot indirectly modify private(set) property A::$p from global scope|1',
    'reference-deferred-string-class': b'R|Cannot indirectly modify private(set) property A::$p from global scope|1',
    'reference-deferred-property-cv': b'R|1|2',
    'reference-captured-dynamic-class': b'R|Cannot indirectly modify private(set) property A::$p from global scope|1|3',
    'reference-captured-property-call': b'NR|Cannot indirectly modify private(set) property A::$p from global scope|1|3',
    'reference-write-cv-denied': b'Cannot indirectly modify private(set) property A::$p from global scope|unset|',
    'reference-return-denied': b'R|Cannot indirectly modify private(set) property A::$p from global scope|1',
    'reference-dimension-denied': b'K|Cannot indirectly modify private(set) property A::$p from global scope|1|2',
    'reference-return-allowed': b'R|2',
    'reference-dimension-allowed-type-source': b'3|Cannot assign array to reference held by property A::$p of type int|3',
}

RECEIVER_CASES = {
    'receiver-uninitialized-write': b'<?php class A{public private(set) static object $p;}try{A::$p->x=2;}catch(Error $e){echo $e->getMessage(),"|";}echo isset(A::$p)?"set":"unset";',
    'receiver-uninitialized-rw': b'<?php class A{public private(set) static object $p;}try{A::$p->x+=2;}catch(Error $e){echo $e->getMessage(),"|";}echo isset(A::$p)?"set":"unset";',
    'receiver-uninitialized-unset': b'<?php class A{public private(set) static object $p;}unset(A::$p->x);echo "done|",isset(A::$p)?"set":"unset";',
    'receiver-direct-demands': b'<?php class O{public int $x=1;public array $a=[1];}class A{public private(set) static object $p;public static function init(){self::$p=new O;}}function take(&$x){$x=6;}function &ref(){return A::$p->x;}A::init();A::$p->x=2;A::$p->x+=2;echo A::$p->x++,"|",A::$p->x;$v=6;A::$p->x=&$v;take(A::$p->x);$r=&ref();$r=7;foreach(A::$p->a as &$v){$v=3;}echo "|",A::$p->x,"|",A::$p->a[0];unset(A::$p->x);echo "|",isset(A::$p->x)?"set":"unset";',
    'receiver-alias-demands': b'<?php class O{public int $x=1;public array $a=[1];public ?O $q=null;public ?int $z=null;}class A{public private(set) static object $p;public static function init(){self::$p=new O;self::$p->q=new O;}public function &get(){return self::$p;}}function take(&$x){$x=4;}function &ref(){return A::$p->x;}A::init();$a=new A;$r=&$a->get();echo "COALESCE|",A::$p->x??=2,"|";try{A::$p->z??=2;}catch(Error $e){echo "ABSENT|",$e->getMessage(),"|";}try{A::$p->x=2;}catch(Error $e){echo "W|",$e->getMessage(),"|";}try{A::$p->x+=2;}catch(Error $e){echo "RW|",$e->getMessage(),"|";}try{unset(A::$p->x);}catch(Error $e){echo "U|",$e->getMessage(),"|";}try{$x=&A::$p->x;}catch(Error $e){echo "REF|",$e->getMessage(),"|";}try{take(A::$p->x);}catch(Error $e){echo "SEND|",$e->getMessage(),"|";}try{foreach(A::$p->a as &$v){echo "C";}}catch(Error $e){echo "FOREACH|",$e->getMessage(),"|";}try{foreach(A::$p->a as [&$v]){echo "C";}}catch(Error $e){echo "LIST|",$e->getMessage(),"|";}try{$x=&ref();}catch(Error $e){echo "RETURN|",$e->getMessage(),"|";}try{A::$p->q->x=2;}catch(Error $e){echo "NESTED|",$e->getMessage(),"|";}$r->x=4;echo A::$p->x,"|",A::$p->q->x;',
    'receiver-rhs-live-alias': b'<?php class O{public int $x=1;}class A{public private(set) static object $p;public static function init(){self::$p=new O;}public static function rhs(){echo "R";global $r;$r=&self::$p;return 3;}}A::init();try{A::$p->x=A::rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p->x;',
    'receiver-deferred-name': b'<?php class O{public int $x=1;public int $y=2;}class A{public private(set) static object $p;public static function init(){self::$p=new O;}}$name="x";function rhs(){echo "R";global $name;$name="y";return 3;}A::init();A::$p->{$name}=rhs();echo "|",A::$p->x,"|",A::$p->y;',
    'receiver-captured-class': b'<?php class O{public int $x=1;}class A{public private(set) static object $p;public static function init(){self::$p=new O;}public static function wrap(){global $r;$r=&self::$p;}}class B{public static object $p;}function rhs(){echo "R";global $class;$class="B";return 3;}A::init();A::wrap();B::$p=new O;$class="A";try{$class::$p->x=rhs();}catch(Error $e){echo "|",$e->getMessage();}echo "|",A::$p->x,"|",B::$p->x;',
    'receiver-multiline-line': b'<?php\nclass A{public private(set) static object $p;}\ntry{\n A::$p\n ->x=2;\n}catch(Error $e){echo $e->getLine(),"|",$e->getMessage();}\n',
    'setter-current-ini-callback': b'<?php class K{function __toString(){echo "I";ini_set("include_path","inner\\0tail");return "include_path";}}class P{function __toString(){echo "T",ini_set(new K,"outer");return "ok";}}class A{public private(set) static string $p="old";public static function put($x){self::$p=$x;echo self::$p;}}ini_set("include_path","seed");A::put(new P);echo "|",A::$p,"|",ini_set("include_path","after");',
}
CASES.update(RECEIVER_CASES)
CASES['unset-continuation'] = b'<?php class O{public int $x=1;private int $y=2;}class A{public private(set) static object $p;public static int $q=1;public static function init(){self::$p=new O;}public function &get(){return self::$p;}}$o=new O;unset($o->x);echo "N|",isset($o->x)?"set":"unset";try{unset($o->y);}catch(Error $e){echo "|P|",$e->getMessage();}try{unset(A::$q);}catch(Error $e){echo "|S|",$e->getMessage();}A::init();$a=new A;$r=&$a->get();try{unset(A::$p->x);}catch(Error $e){echo "|A|",$e->getMessage();}echo "|",A::$p->x,"|",A::$q;'
EXPECTED['unset-continuation'] = b'N|unset|P|Cannot access private property O::$y|S|Attempt to unset static property A::$q|A|Cannot indirectly modify private(set) property A::$p from global scope|1|1'
denial = b'Cannot indirectly modify private(set) property A::$p from global scope'
EXPECTED.update({
    'receiver-uninitialized-write': denial + b'|unset',
    'receiver-uninitialized-rw': b'Typed static property A::$p must not be accessed before initialization|unset',
    'receiver-uninitialized-unset': b'done|unset',
    'receiver-direct-demands': b'4|5|7|3|unset',
    'receiver-alias-demands': b'COALESCE|1|ABSENT|' + denial + b'|' + b''.join(tag + b'|' + denial + b'|' for tag in [b'W', b'RW', b'U', b'REF', b'SEND', b'FOREACH', b'LIST', b'RETURN', b'NESTED']) + b'4|1',
    'receiver-rhs-live-alias': b'R|' + denial + b'|1',
    'receiver-deferred-name': b'R|1|3',
    'receiver-captured-class': b'R|' + denial + b'|1|1',
    'receiver-multiline-line': b'4|' + denial,
    'setter-current-ini-callback': b'TIinner\0tailok|ok|outer',
})
CASES['array-inherited-setter'] = b'<?php class A{public private(set) static string $p="old";public function put($v){return static::$p=$v;}}class B extends A{}class V{function __toString(){echo "T";return "x";}}$f=[new B,"put"];echo $f(new V),"|",A::$p,"|",B::$p;'
EXPECTED['array-inherited-setter'] = b'Tx|x|x'
CASES['handler-array-inherited-setter'] = b'<?php set_error_handler(function($code,$message,$file,$line){echo "H",func_num_args();return true;});class A{public private(set) static string $p="old";public function put($v){return static::$p=$v;}}class B extends A{}class V{function __toString(){echo "T";trigger_error("w",E_USER_NOTICE);return "x";}}$f=[new B,"put"];echo $f(new V),"|",A::$p,"|",B::$p;'
EXPECTED['handler-array-inherited-setter'] = b'TH4x|x|x'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
             'tests/semantics/static_set_access.py', 'tests/semantics/static_set_compiler.py',
             'tests/semantics/static_set_access_protocol.py', 'tests/semantics/profile.json',
             'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py',
             'tests/semantics/typed_static_invoke_set_protocol.py',
             'tests/semantics/typed_static_string_protocol.py',
             'tests/semantics/typed_static_string_assignment.py',
             'tests/semantics/_build/default/numeric_runner.exe',
             'tests/validate.py', 'frontend/wire.py', 'spec/schema.json',
             '.tools/php-file.so', '.tools/php/bin/php', '_build/default/adapter/main.exe']
    names += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'frontend').glob('*.php'))]
    return {name: sha(ROOT / name) for name in names}


def main():
    import typed_static_invoke_set_protocol as driver
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = inputs()
    out = Path(tempfile.mkdtemp(prefix='static-set-access-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    report = {'result': 'fail', 'selected': selected, 'records': [], 'inputs': before,
              'profile': profile, 'cwd': str(ROOT), 'revision': subprocess.check_output(
                  ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'Direct backed static setters, deferred reference RHS and escaped alias types.'}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
            row = {'id': name, 'source_sha256': sha(path), 'passed': False, 'completed': False}
            report['records'].append(row)
            native = driver.process([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)],
                                    directory / 'native', 30, directory)
            assert native.returncode == 0, (name, native.returncode)
            if name in EXPECTED:
                expected_stderr = (b'Warning: Undefined variable $missing in ' + os.fsencode(path) + b' on line 1\n'
                                   if name == 'reference-write-cv-denied' else b'')
                assert native.stdout == EXPECTED[name] and native.stderr == expected_stderr, (name, native.stdout, native.stderr)
            facts = {'version': 2, 'main': driver.b64(os.fsencode(path)),
                     'cwd': driver.b64(os.fsencode(directory)), 'include_path': driver.b64(b'.:'),
                     'entries': [], 'chdir_entries': []}
            facts_path = directory / 'snapshot.json'; facts_path.write_text(json.dumps(facts, sort_keys=True) + '\n')
            model = driver.process([str(ROOT / 'bin/php-semantics'), str(path), '--file-snapshot',
                str(facts_path), '--steps', '100000', '--timeout', '60'], directory / 'model', 90, directory)
            assert model.returncode == 0 and not model.stderr
            actual = json.loads(model.stdout)
            assert actual['frontend'] == 'accepted' and actual['checked'] == 'program'
            assert actual['status'] == 'normal' and actual['exit_status'] == 0
            assert actual['reason'] is None and actual['diagnostic'] is None
            assert base64.b64decode(actual['stdout'], validate=True) == native.stdout
            assert base64.b64decode(actual['stderr'], validate=True) == native.stderr
            row.update(passed=True, completed=True, actual=actual)
            print(name, 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after_inputs'] = inputs()
        if report['after_inputs'] != before:
            report['result'] = 'fail'
        report['raw_files'] = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'bytes': p.stat().st_size,
            'mode': oct(p.stat().st_mode & 0o7777)} for p in sorted(out.rglob('*')) if p.is_file()}
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
