<?php
#[Deprecated] const X = [];
$original = function($value = X, $last = 0) { echo $last, '|'; };
set_error_handler(function() { echo 'H|'; return true; });
$original(last: 1);
$copy = clone $original;
$copy(last: 2);
