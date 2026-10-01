#!/usr/bin/env python3
"""Temporary Closure::call scope shares live static cells across callback frames."""
from class_static_merged_bridge import main

CASES = [
    ('private-static-escaped-alias', b'<?php class A { private static int $p=1; '
     b'public function get(){return self::$p;} } '
     b'$f=function(){ $r=&A::$p; return [&$r]; }; $a=new A; '
     b'$v=$f->call($a);$v[0]=7;echo $a->get(),"|",$v[0];', {}, False),
    ('closure-name-live-statics', b'<?php class A { public int $p=1; public static $x=7; } '
     b'class C { public string $name="x"; } $nm=function(){global $a,$r;$a=null;'
     b'$r="s";A::$x=9;return $this->name;}; $a=new A;$r=&$a->p;'
     b'echo $a::${$nm->call(new C)},"|",$r;', {}, False),
    ('named-reference-static-isolation', b'<?php class A{public static string $p="3";} '
     b'$r=&A::$p;$f=function(int &$x){$x=9;return $x;};'
     b'echo $f->call(x:A::$p,newThis:new A),"|",A::$p==="3"?"S":"N","|",'
     b'$r==="3"?"S":"N";', {}, False),
]


if __name__ == '__main__':
    main(CASES, __file__)
