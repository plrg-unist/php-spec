<?php
class Item185 { public int $value = 3; }
#[Deprecated] const X = new Item185();
set_error_handler(function($level, $message) { echo 'H|'; return true; });
$first = X;
echo $first->value, '|';
$first->value = 7;
$second = constant('X');
echo $first === $second ? 'same|' : 'BAD|';
echo $second->value, '|';
