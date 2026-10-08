<?php
class Replacement350 { public function __toString(): string { echo 'WRONGCAST|'; return 'other350'; } }
class Payload350 { public function __destruct() { echo 'D|'; $GLOBALS['Array'] = 'DESTRUCTOR-TARGET'; } }
function warning350($c, $m, $f, $l) { echo 'W:', $l, ':', $m, '|'; $GLOBALS['name350'] = new Replacement350; echo 'HANDLER-AFTER|'; return true; }
set_error_handler('warning350');
$Array = 'before'; $other350 = 'WRONG'; $name350 = [new Payload350];
echo 'R:', ${$name350}, '|END';
