<?php
#[Deprecated] const X = [];
class Holder188 {}
$original = function($value = [false && X, Y]) {
    echo $value[0] === false ? 'F|' : 'BAD|', $value[1], '|';
};
define('Y', 9);
$private = $original->bindTo(null, Holder188::class);
$private();
