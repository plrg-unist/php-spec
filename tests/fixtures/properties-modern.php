<?php
class C {
public private(set) int $x=1;
protected protected(set) string $y;
public int $a { get => $this->x; set => $value; }
public int $b { &get { return $this->x; } set(int $v) { $this->x=$v; } }
public int $c { #[A] final get => 1; #[B] set => $value; }
public function __construct(public private(set) int $p=0, public int $q { get => 1; }) {}
}
interface I { public int $p { get; set; } }
