<?php
namespace A\B {
use Foo\Bar;
use Foo\Bar as Baz, Other as O;
use function Foo\f, Foo\g as g;
use const Foo\X, Foo\Y as Y;
use Foo\{Bar, Baz as B};
use Foo\{Bar, function f, const C};
const X=1, Y=2;
$x = \Foo\f(); $x = namespace\f(); $x = Foo\f();
}
namespace { echo \A\B\X; }
