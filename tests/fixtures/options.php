<?php
function f() {} abstract class C { abstract function f(); }
declare(ticks=1); declare(ticks=1) {} declare(ticks=1): enddeclare;
$x = new class {}; $x = new C; $x = new C();
$x=[]; [,]=$x; $a = yield; $a = yield 1;
