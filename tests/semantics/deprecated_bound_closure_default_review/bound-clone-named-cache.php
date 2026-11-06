<?php
#[Deprecated] const X = [];
$original = function($value = X, $last = 0) { echo $last, '|'; };
$first = $original->bindTo(null);
$selected = clone $first;
$original = null;
$first = null;
set_error_handler(function() { echo 'H|'; return true; });
$selected(last: 1);
$later = Closure::bind($selected, null, 'static');
$selected = null;
$later(last: 2);
