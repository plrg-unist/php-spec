<?php
class Name343 {
    public function __toString(): string { echo 'CAST|'; return 'missing343'; }
    public function __destruct() { echo 'D|'; }
}
function warning343($c, $m, $f, $l) { global $name343, $missing343; echo 'W:', $l, ':', $m, '|'; $name343 = 'other343'; $missing343 = 'LATE'; echo 'HANDLED|'; return true; }
set_error_handler('warning343');
$other343 = 'WRONG'; $name343 = new Name343;
echo 'R:', ${$name343}, '|N:', $name343, '|T:', $missing343, '|END';
