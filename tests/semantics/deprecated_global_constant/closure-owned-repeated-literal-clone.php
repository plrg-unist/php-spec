<?php
#[Deprecated] const X = [];
function make188() { return function($value = X) { echo 'E|'; }; }
set_error_handler(function() { echo 'H|'; return true; });
$a = make188();
$cold = clone $a;
$cold(); $a();
$b = make188(); $b();
$warm = clone $a; $warm();
$a = null; $b = null; $cold = null; $warm = null;
$later = make188(); $later();
$other = function($value = X) { echo 'O|'; };
$other(); $other();
