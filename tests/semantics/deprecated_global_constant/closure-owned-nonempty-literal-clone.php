<?php
#[Deprecated] const X = [1];
function make188() { return static function($value = X) { echo $value[0], '|'; }; }
set_error_handler(function() { echo 'H|'; return true; });
$a = make188(); $a();
$b = make188(); $b();
$c = clone $a; $c(); $a();
