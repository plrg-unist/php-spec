<?php
#[A(1)] abstract class C extends B implements I,J {
use T,U { T::m insteadof U; U::m as private renamed; m as protected; }
public const int X=1,Y=2;
protected static ?int $a=null,$b=1;
var $old;
private readonly int $r;
final public function __construct(public int $p=1, protected readonly string $s='') {}
abstract protected function &f(?A $a): A|B;
public function g(): void { parent::f(); self::f(); static::f(); }
}
interface I extends J,K { public const X=1; public function f(): void; }
trait T { private function m() {} }
final readonly class R { public function __construct(public int $x) {} }
$x = new #[A] class(1) extends B implements I { public function __construct($x) {} };
