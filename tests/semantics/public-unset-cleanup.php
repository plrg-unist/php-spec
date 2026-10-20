<?php
class PublicUnsetProbe112 {
    public function __destruct() {
        global $child;
        echo 'V|';
        unset($child->value);
        echo 'v|';
    }
}
class PublicUnsetParent112 {
    public int $value;
    public function __unset(string $name): void {
        global $make;
        echo 'U|';
        if ($make) { $make = false; $local = new PublicUnsetProbe112(); }
        echo 'u|';
    }
    public function __destruct() { echo 'D|'; }
}
class PublicUnsetChild112 extends PublicUnsetParent112 {}
$make = true;
$child = new PublicUnsetChild112();
unset($child->value);
echo 'L:';
unset($child->value);
echo 'A|';
unset($child->value);
echo 'B|';
unset($child, $make);
echo 'E|';
