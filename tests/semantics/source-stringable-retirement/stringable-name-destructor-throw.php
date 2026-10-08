<?php
class Name343 {
    public function __toString(): string { global $name343; echo 'CAST|'; $name343 = 'other343'; return 'missing343'; }
    public function __destruct() { echo 'D|'; throw new Exception('retire'); }
}
function warning343($c, $m, $f, $l) { global $missing343; echo 'W:', $l, ':', $m, '|'; $missing343 = 'LATE'; return true; }
set_error_handler('warning343');
$name343 = new Name343;
try { echo 'R:', ${$name343}, '|AFTER|'; } catch (Throwable $e) { echo 'CAUGHT:', $e->getMessage(), '|'; }
echo 'N:', $name343, '|T:', (isset($missing343) ? $missing343 : 'none'), '|END';
