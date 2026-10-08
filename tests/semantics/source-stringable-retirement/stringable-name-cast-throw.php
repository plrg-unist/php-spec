<?php
class Name343 {
    public function __toString(): string { global $name343, $target343; echo 'CAST|'; $name343 = 'other343'; $target343 = 'WRITTEN'; throw new Exception('cast'); }
    public function __destruct() { echo 'D|'; }
}
$target343 = 'before'; $name343 = new Name343;
try { echo 'R:', ${$name343}, '|AFTER|'; } catch (Throwable $e) { echo 'CAUGHT:', $e->getMessage(), '|'; }
echo 'N:', $name343, '|T:', $target343, '|END';
