#!/usr/bin/env python3
"""Declared property conversion precedes shared-reference type checks."""
from class_static_merged_bridge import main

CASES = [
    ('static-declared-string', b'<?php class A{public static string $p="1";} '
     b'class B{public static int|string $p="1";} B::$p=&A::$p;'
     b'$v=(A::$p=2);echo $v==="2"?"S":"N","|",A::$p,"|",B::$p;', {}, False),
    ('instance-declared-string', b'<?php class A{public string $p="1";'
     b'public int|string $q="1";} $a=new A;$a->q=&$a->p;'
     b'$v=($a->p=2);echo $v==="2"?"S":"N","|",$a->p,"|",$a->q;', {}, False),
    ('cv-string-union-conflict', b'<?php class A{public static string $p="1";} '
     b'class B{public static int|string $p="1";} B::$p=&A::$p;$r=&A::$p;'
     b'try{$r=2;}catch(TypeError $e){echo "E|";}echo A::$p,"|",B::$p;', {}, False),
    ('strict-static-declared-error', b'<?php declare(strict_types=1);'
     b'class A{public static string $p="1";} '
     b'class B{public static int|string $p="1";} B::$p=&A::$p;'
     b'try{A::$p=2;}catch(TypeError $e){echo $e->getMessage(),"|";}'
     b'echo A::$p,"|",B::$p;', {}, False),
    ('strict-instance-declared-error', b'<?php declare(strict_types=1);'
     b'class A{public string $p="1";public int|string $q="1";}'
     b'$a=new A;$a->q=&$a->p;try{$a->p=2;}catch(TypeError $e)'
     b'{echo $e->getMessage(),"|";}echo $a->p,"|",$a->q;', {}, False),
    ('strict-cv-reference-error', b'<?php declare(strict_types=1);'
     b'class A{public static string $p="1";} $r=&A::$p;'
     b'try{$r=2;}catch(TypeError $e){echo $e->getMessage(),"|";}echo A::$p;', {}, False),
    ('static-second-source-atomic', b'<?php class A{public static int|string $p=1;}'
     b'class B{public static int $p=1;} B::$p=&A::$p;'
     b'try{A::$p="x";}catch(TypeError $e){echo $e->getMessage(),"|";}'
     b'echo A::$p,"|",B::$p,"|";B::$p=3;echo A::$p;', {}, False),
    ('instance-second-source-atomic', b'<?php class A{public int|string $p=1;'
     b'public int $q=1;} $a=new A;$a->q=&$a->p;'
     b'try{$a->p="x";}catch(TypeError $e){echo $e->getMessage(),"|";}'
     b'echo $a->p,"|",$a->q,"|";$a->q=3;echo $a->p;', {}, False),
    ('static-declared-bool', b'<?php class A{public static bool $p=false;}'
     b'class B{public static int|bool $p=false;} B::$p=&A::$p;'
     b'$v=(A::$p=2);echo $v===true?"B":"N","|",A::$p===true?"B":"N",'
     b'"|",B::$p===true?"B":"N";', {}, False),
    ('cv-bool-union-conflict', b'<?php class A{public static bool $p=false;}'
     b'class B{public static int|bool $p=false;} B::$p=&A::$p;$r=&A::$p;'
     b'try{$r=2;}catch(TypeError $e){echo "E|";}'
     b'echo A::$p===false?"B":"N","|",B::$p===false?"B":"N";', {}, False),
    ('instance-declared-float', b'<?php class A{public float $p=1.0;'
     b'public int|float $q=1.0;} $a=new A;$a->q=&$a->p;'
     b'$v=($a->p=2);echo $v===2.0?"F":"N","|",$a->p===2.0?"F":"N",'
     b'"|",$a->q===2.0?"F":"N";', {}, False),
    ('static-lossy-one-notice', b'<?php class A{public static int $p=1;}'
     b'class B{public static int $p=1;} B::$p=&A::$p;'
     b'A::$p=2.3;echo A::$p,"|",B::$p;', {}, False),
    ('cv-lossy-two-notices', b'<?php class A{public static int $p=1;}'
     b'class B{public static int $p=1;} B::$p=&A::$p;$r=&A::$p;'
     b'$r=2.3;echo A::$p,"|",B::$p;', {}, False),
    ('untyped-static-generic-reference', b'<?php class A{public static string $p="1";}'
     b'class B{public static int|string $p="1";} class U{public static $p;}'
     b'B::$p=&A::$p;U::$p=&A::$p;try{U::$p=2;}catch(TypeError $e){echo "E|";}'
     b'echo A::$p,"|",B::$p,"|",U::$p;', {}, False),
    ('untyped-instance-generic-reference', b'<?php class A{public string $p="1";'
     b'public int|string $q="1";public $u;} $a=new A;'
     b'$a->q=&$a->p;$a->u=&$a->p;try{$a->u=2;}catch(TypeError $e){echo "E|";}'
     b'echo $a->p,"|",$a->q,"|",$a->u;', {}, False),
    ('dynamic-object-generic-reference', b'<?php class A{public string $p="1";'
     b'public int|string $q="1";} $a=new A;$a->q=&$a->p;$d=new stdClass;'
     b'$d->p=&$a->p;try{$d->p=2;}catch(TypeError $e){echo "E|";}'
     b'echo $a->p,"|",$a->q,"|",$d->p;', {}, False),
    ('typed-direct-conversion', b'<?php class A{public string $p="1";'
     b'public static string $q="1";} $a=new A;$v=($a->p=2);$w=(A::$q=3);'
     b'echo $v==="2"?"S":"N","|",$w==="3"?"S":"N",'
     b'"|",$a->p,"|",A::$q;', {}, False),
    ('static-compound-alias-conflict', b'<?php class A{public static string $p="1";}'
     b'class B{public static int|string $p="1";} B::$p=&A::$p;'
     b'try{A::$p+=1;}catch(TypeError $e){echo "E|";}echo A::$p,"|",B::$p;', {}, False),
    ('instance-compound-alias-conflict', b'<?php class A{public string $p="1";'
     b'public int|string $q="1";} $a=new A;$a->q=&$a->p;'
     b'try{$a->p+=1;}catch(TypeError $e){echo "E|";}echo $a->p,"|",$a->q;', {}, False),
    ('static-compound-two-notices', b'<?php class A{public static int $p=1;}'
     b'class B{public static int $p=1;} B::$p=&A::$p;'
     b'A::$p+=1.3;echo A::$p,"|",B::$p;', {}, False),
    ('typed-direct-compound', b'<?php class A{public string $p="1";'
     b'public static string $q="1";} $a=new A;$v=($a->p+=1);$w=(A::$q+=2);'
     b'echo $v==="2"?"S":"N","|",$w==="3"?"S":"N",'
     b'"|",$a->p,"|",A::$q;', {}, False),
]


if __name__ == '__main__':
    main(CASES, __file__)
