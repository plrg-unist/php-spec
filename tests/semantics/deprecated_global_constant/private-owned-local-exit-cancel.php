<?php
#[Deprecated] const X = [1];
class Scope190 {}
$original = function($value = X) { echo 'BAD|'; };
$scoped = $original->bindTo(null, Scope190::class);
$receive = $scoped->bindTo(null, null); $original = $scoped = null;
class Local190 { function __destruct() { echo 'D|'; throw new Exception('local'); } }
set_error_handler(function() { echo 'H|'; $local = new Local190(); exit; });
$result = 99;
try { $result = $receive(); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
