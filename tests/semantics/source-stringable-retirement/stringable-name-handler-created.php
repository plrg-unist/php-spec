<?php
class Name343 {
    public function __toString(): string { global $target343; echo 'CAST|'; $target343 = 'LIVE'; return 'target343'; }
    public function __destruct() { echo 'D|'; }
}
function warning343($c, $m, $f, $l) { global $missing343; echo 'W:', $l, ':', $m, '|'; $missing343 = new Name343; return true; }
set_error_handler('warning343');
$target343 = 'before';
echo 'R:', ${$missing343}, '|AFTER|';
unset($missing343);
echo 'END';
