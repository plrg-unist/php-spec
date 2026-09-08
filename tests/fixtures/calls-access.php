<?php
foo(1, label: 2, other: $v); $f(...$args); Foo::m(1); $o->m(1); $o?->m(1);
Foo::{$m}(); $o->{$m}(); $o->$m(); ${$name}(); $$name();
$x = Foo::C; $x = Foo::{$c}; $x = Foo::$p; $x = Foo::${$p};
$x = $o->p; $x = $o?->p; $x = $o->{$p}; $x = $o?->{$p};
$x = $a[0]; $a[]=1; $x = (foo())[0];
$x = new Foo; $x = new Foo(1); $x = new $class(...$args); $x = new ($factory())(1);
$x = foo(...); $x = Foo::m(...); $x = $o->m(...);
$x = [1, 2 => &$a, ...$b,]; $x = array(1, 'k'=>2,); []=$a; [$a,,&$b]=$c; list($a,,$b)=$c;
$x = match($a) {1,2 => 'a', 3 => 'b', default => 'c',};
