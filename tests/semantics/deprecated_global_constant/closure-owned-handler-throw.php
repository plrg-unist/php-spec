<?php
#[Deprecated] const X = [1];
$receive = function($value = X) { echo 'BAD|'; };
set_error_handler(function() { echo 'H|'; throw new Exception('handler'); });
$result = 99;
try { $result = $receive(); } catch (Exception $e) { echo 'C|', $result, '|'; }
echo 'A|';
