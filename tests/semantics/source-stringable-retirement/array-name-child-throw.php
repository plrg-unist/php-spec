<?php
class Payload350 { public function __destruct() { echo 'D|'; throw new Exception('retire'); } }
function warning350($c, $m, $f, $l) { echo 'W:', $l, ':', $m, '|'; unset($GLOBALS['name350']); echo 'HANDLER-BAD|'; return true; }
set_error_handler('warning350');
$name350 = [new Payload350];
try { echo 'R:', ${$name350}, '|BAD|'; } catch (Throwable $e) { echo 'CAUGHT:', $e->getMessage(), '|'; }
echo 'END';
