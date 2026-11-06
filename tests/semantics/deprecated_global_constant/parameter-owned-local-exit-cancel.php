<?php
#[Deprecated] const X = [1];
function receive186($value = X) { echo 'BAD|'; }
class Local186 { function __destruct() { echo 'D|'; throw new Exception('local'); } }
set_error_handler(function($level, $message) { echo 'H|'; $local = new Local186(); exit; });
$result = 99;
try { $result = receive186(); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
