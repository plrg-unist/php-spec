<?php
class Name343 { public function __toString(): string { global $target343; echo 'CAST|'; $target343 = 'LIVE'; return 'target343'; } }
$target343 = 'before';
$name343 = new Name343;
echo 'R:', ${$name343}, '|END';
