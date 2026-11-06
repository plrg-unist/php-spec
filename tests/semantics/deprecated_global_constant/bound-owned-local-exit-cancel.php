<?php
#[Deprecated] const X = [1];
$original = function($value = X) { echo 'BAD|'; };
$receive = $original->bindTo(null, null); $original = null;
class Local189 { function __destruct() { echo 'D|'; throw new Exception('local'); } }
set_error_handler(function() { echo 'H|'; $local = new Local189(); exit; });
$result = 99;
try { $result = $receive(); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
