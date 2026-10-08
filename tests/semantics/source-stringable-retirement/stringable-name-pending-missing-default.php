<?php
class Name343 {
    public function __toString(): string { global $name343; echo 'CAST|'; $name343 = 'other343'; return 'missing343'; }
    public function __destruct() { echo 'D|'; throw new Exception('retire'); }
}
$name343 = new Name343;
try { echo 'R:', ${$name343}, '|AFTER|'; } catch (Throwable $e) { echo 'CAUGHT:', $e->getMessage(), '|'; }
echo 'N:', $name343, '|T:', (isset($missing343) ? $missing343 : 'none'), '|END';
