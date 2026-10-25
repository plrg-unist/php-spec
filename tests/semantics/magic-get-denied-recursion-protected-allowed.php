<?php
class AllowedParent122 {
    protected int $ghost = 3;
    public function __get($name) {
        echo 'G|';
        return $this->ghost; // READ122
    }
}
class AllowedChild122 extends AllowedParent122 {}
$child = new AllowedChild122();
echo 'A:';
echo $child->ghost, '|';
unset($child);
echo 'E|';
