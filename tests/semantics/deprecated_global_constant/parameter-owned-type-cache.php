<?php
#[Deprecated] const X = [];
function receive186(int $value = X) { echo 'BAD|'; }
set_error_handler(function($level, $message) { echo 'H|'; return true; });
try { receive186(); } catch (TypeError $e) { echo 'T|'; }
try { receive186(); } catch (TypeError $e) { echo 'T|'; }
