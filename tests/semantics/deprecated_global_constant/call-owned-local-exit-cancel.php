<?php
#[Deprecated] const X = [];
class Receiver191 {}
$receiver = new Receiver191();
$fn = function($value = X) { echo 'BAD|'; };
class Local191 { function __destruct() { echo 'D|'; throw new Exception('local'); } }
set_error_handler(function() { echo 'H|'; $local = new Local191(); exit; });
$result = 99;
try { $result = $fn->call($receiver); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
