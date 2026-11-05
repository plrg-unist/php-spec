<?php
const BASE = new stdClass();
$base = BASE;
$base->value = 1;
#[Deprecated] const X = [BASE];
const Y = 9;
$query = 'X';
$value = 99;
set_error_handler(function($level, $message) use (&$query) {
    echo 'H|';
    $query = 'Y';
    $inner = X;
    $leaf = $inner[0];
    $leaf->value = 5;
    throw new Exception('stop');
});
try { $value = constant($query); }
catch (Exception $e) { echo 'C|', $query, '|', $value, '|'; }
restore_error_handler();
echo 'A|', BASE->value, '|', constant($query), '|';
