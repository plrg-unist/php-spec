<?php
function warning350($c, $m, $f, $l) { echo 'W:', $l, ':', $m, '|'; restore_error_handler(); throw new Exception('conversion'); }
set_error_handler('warning350');
$name350 = [];
try { echo 'R:', ${$name350}, '|BAD|'; } catch (Throwable $e) { echo 'CAUGHT:', $e->getMessage(), '|'; }
echo 'END';
