<?php
class MagicIssetOnlyParent90 {
    private int $value = 1;
    public function __isset(string $name): bool {
        global $child;
        echo 'I|';
        $child = null;
        echo 'i|';
        throw new Exception('isset-only-stop');
    }
    public function __destruct() { echo 'D|'; }
}
class MagicIssetOnlyChild90 extends MagicIssetOnlyParent90 {}
$child = new MagicIssetOnlyChild90();
echo 'X:';
try { echo empty($child->value) ? 'T' : 'F', '|'; }
catch (Exception $caught) { echo 'C|'; }
echo 'E|';
