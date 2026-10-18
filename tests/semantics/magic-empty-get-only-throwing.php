<?php
class MagicGetOnlyParent91 {
    private int $value = 1;
    public int $ready = 1;
    public function __get($name) {
        echo 'G|';
        throw new Exception('get-only-stop');
    }
    public function __destruct() { echo 'D|'; }
}
class MagicGetOnlyChild91 extends MagicGetOnlyParent91 {}
$child = new MagicGetOnlyChild91();
echo 'X:', empty($child->value) ? 'T' : 'F', '|';
echo empty($child->ready) ? 'T' : 'F', '|';
try { echo $child->value, '|'; }
catch (Exception $caught) { echo 'C|'; }
$child = null;
echo 'E|';
