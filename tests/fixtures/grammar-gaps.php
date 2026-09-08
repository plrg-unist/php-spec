<?php
namespace N;
use \A\B;
use function \A\{f,g as gg,};
use const A\{C,D,};
#[A,B] #[C] class C {
#[A] public const if=1;
const X=1;
#[A] public int $x=1 { get => $this->x; }
public public(set) int $y;
function f(): static { return $this; }
function g(): A&B&C {}
function h(): (A&B)|C|D {}
use T {} use U { m as renamed; n as if; }
}
function readonly() {} readonly();
function f(array $a, callable $b, A&B&C $c) { function g() {} #[A] function h() {} }
try {} catch (E $e) {} unset($a,$b);
$x = new readonly class {}; 
foreach ($a as list($x,$y)) {} foreach ($a as [$x,$y]) {}
switch($x) {; default; break;} switch($x): endswitch;
$x = match($x) {};
if ($x): endif;
for (; $x; $x++, (void) f()) {}
$x = +1; $x = $a & $b;
$f = function () {}; $f = #[A] function () {}; $f = static function () {};
$x = ``; $x = `literal`;
$x = $class::C; $x = $class::{$name}; $x = $class::$p; $x=$class::$m();
$x = [1][0]; $x = C::X[0]; $x = C[0]; $x = new C()->p;
$x = ($f)(); $x = 'strlen'('a'); $x = new C()();
$x = new $classes[0]; $x = new $o->class; $x = new $o?->class; $x = new C::$class; $x = new $o::$class;
list('a'=>list($x),list($y))=$a;
$x = "$o?->p ${a[0]} $a[-1] $a[$k]";

$x = $a & 1; class Bit { const X = 1; }
