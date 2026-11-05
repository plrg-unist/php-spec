<?php
const DONOR185 = new stdClass();
#[Deprecated] const X = DONOR185;
class Local185 {
    function __destruct() { echo 'D|'; throw new Exception('local'); }
}
set_error_handler(function($level, $message) { echo 'H|'; $local = new Local185(); exit; });
try { eval('const Y185 = X;'); }
catch (Exception $e) { echo 'C|'; }
echo defined('Y185') ? 'BAD|' : 'missing|';
