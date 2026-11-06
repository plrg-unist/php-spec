<?php
#[Deprecated] const X = [1];
class Receiver187 { public function receive($value = X) { echo 'BAD|'; } }
class Local187 { function __destruct() { echo 'D|'; throw new Exception('local'); } }
$receiver = new Receiver187();
set_error_handler(function($level, $message) { echo 'H|'; $local = new Local187(); exit; });
$result = 99;
try { $result = $receiver->receive(); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
