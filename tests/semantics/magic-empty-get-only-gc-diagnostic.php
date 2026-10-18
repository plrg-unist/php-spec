<?php
class MagicGetOnlyParent91 {
    private int $value = 1;
    public int $ready = 1;
    public function __get($name) {
        echo 'G|';
        return 42;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicGetOnlyChild91 extends MagicGetOnlyParent91 {}
$child = new MagicGetOnlyChild91();
gc_collect_cycles();
echo 'N:', empty($child->value) ? 'T' : 'F', '|';
echo gc_status()['roots'], '|';
echo empty($child->ready) ? 'T' : 'F', '|';
echo $child->value, '|';
$child = null;
echo 'E|';
