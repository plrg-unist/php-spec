<?php
class Name343 {
    public function __toString(): string { global $name343, $target343; echo 'CAST|'; $name343 = 'other343'; $target343 = 'CAST-TARGET'; echo 'RETURN|'; return 'target343'; }
    public function __destruct() { global $target343; echo 'D|'; $target343 = 'DESTRUCTOR-TARGET'; }
}
$target343 = 'before'; $other343 = 'WRONG';
$name343 = new Name343;
echo 'R:', ${$name343}, '|N:', $name343, '|END';
