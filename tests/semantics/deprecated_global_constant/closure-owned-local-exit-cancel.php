<?php
#[Deprecated] const X = [1];
$receive = function($value = X) { echo 'BAD|'; };
class Local188 { function __destruct() { echo 'D|'; throw new Exception('local'); } }
set_error_handler(function() { echo 'H|'; $local = new Local188(); exit; });
$result = 99;
try { $result = $receive(); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
