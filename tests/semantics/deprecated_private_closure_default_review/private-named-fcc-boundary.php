<?php
#[Deprecated] const X = [];
function named190($value = X) { echo 'E|'; }
$private = named190(...);
set_error_handler(function() { echo 'H|'; return true; });
$private();
