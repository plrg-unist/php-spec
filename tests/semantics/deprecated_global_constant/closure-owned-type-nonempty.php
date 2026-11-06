<?php
#[Deprecated] const X = [1];
$receive = function(int $value = X) { echo 'BAD|'; };
set_error_handler(function() { echo 'H|'; return true; });
try { $receive(); } catch (TypeError $e) { echo 'T|'; }
try { $receive(); } catch (TypeError $e) { echo 'T|'; }
