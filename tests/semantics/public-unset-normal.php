<?php
class PublicUnsetParent112 {
    public int $value = 41;
    public function __unset(string $name): void {
        global $child;
        echo 'U|';
        $child = null;
        echo 'u|';
    }
    public function __destruct() { echo 'D|'; }
}
class PublicUnsetChild112 extends PublicUnsetParent112 {}
$child = new PublicUnsetChild112();
unset($child->value);
echo 'N:';
unset($child->value);
echo 'A|';
unset($child);
echo 'E|';
