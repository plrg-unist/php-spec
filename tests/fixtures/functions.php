<?php
#[A] function &f(#[P] ?int &$a, string $b='x', ...$rest): mixed { global $g,$$n,${$n}; static $s=1,$t; return $a; }
$f = #[A] static function &(int $x=1) use (&$a,$b): int { return $a; };
$f = #[A] static fn(int $a): int => $a+1;
function gen() { yield; yield 1; yield 1 => 2; yield from $xs; $a = yield 3; }
