<?php
#[Deprecated] const X = [];
$original = function($value = X) { echo 'E|'; };
$bound = $original->bindTo(null, null);
$bound();
