<?php
#[Deprecated] const X = [1];
class Receiver187 { public function receive($value = X) { echo 'BAD|'; } }
$receiver = new Receiver187();
set_error_handler(function($level, $message) { echo 'H|'; throw new Exception('handler'); });
$result = 99;
try { $result = $receiver->receive(); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
