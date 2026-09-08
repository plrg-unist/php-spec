<?php
$a = 1 + 2 * 3 ** 4 / 5 % 6 - 7;
$b = !$a && ~$b || $c xor $d and $e or $f;
$c = $a << 2 >> 1 & $b | $c ^ $d;
$d = $a === $b; $d = $a !== $b; $d = $a == $b; $d = $a != $b; $d = $a <> $b;
$e = $a < $b; $e = $a <= $b; $e = $a > $b; $e = $a >= $b;
$f = $a <=> $b;
$g = $a ? $b : ($c ?: $d);
$h = ($a ?? $b) ?? $c;
$i = @($a . $b);
$j =& $a;
$a += 1; $a -= 1; $a *= 1; $a /= 1; $a %= 1; $a **= 1;
$a .= 'x'; $a &= 1; $a |= 1; $a ^= 1; $a <<= 1; $a >>= 1; $a ??= 1;
++$a; $a++; --$a; $a--;
$x = (int)$a; $x=(bool)$a; $x=(float)$a; $x=(string)$a; $x=(array)$a; $x=(object)$a; (void)$a;
$x = $a instanceof Foo; $x = clone $a;
include 'x'; include_once 'x'; require 'x'; require_once 'x';
eval($a); isset($a,$b[0]); empty($a); exit; exit(); exit(1); die('x');
