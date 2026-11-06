<?php
#[Deprecated] const X = [1];
function receive186($value = X) { echo 'BAD|'; }
set_error_handler(function($level, $message) { echo 'H|'; throw new Exception('stop'); });
$result = 99;
try { $result = receive186(); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
