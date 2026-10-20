<?php
class PublicUnsetParent112 {
    public int $value;
    public function __unset(string $name): void {
        echo 'U|';
        unset($this->value);
        $this->value = 7;
        echo 'u|';
    }
    public function __destruct() { echo 'D|'; }
}
class PublicUnsetChild112 extends PublicUnsetParent112 {}
$child = new PublicUnsetChild112();
echo 'I:';
unset($child->value);
echo 'B|';
unset($child->value);
echo $child->value, '|';
unset($child->value);
echo 'C|';
unset($child->value);
echo $child->value, '|';
unset($child);
echo 'E|';
