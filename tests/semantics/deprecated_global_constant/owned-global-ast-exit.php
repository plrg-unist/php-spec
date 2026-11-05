<?php
const DONOR185 = new stdClass();
#[Deprecated] const X = DONOR185;
register_shutdown_function(function() { echo 'S|', defined('Y185') ? 'BAD|' : 'missing|'; });
set_error_handler(function($level, $message) { echo 'H|'; exit; });
eval('const Y185 = X;');
echo 'BAD|';
