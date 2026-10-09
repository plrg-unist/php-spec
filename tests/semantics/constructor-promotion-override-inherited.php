<?php
class OverrideBase20 { public int $value = 1; }
class OverrideChild20 extends OverrideBase20 {
    public function __construct(#[\Override] public int $value) { echo $this->value, "|"; }
}
$o = new OverrideChild20(7);
echo $o->value, "|";
$o->__construct(8);
echo $o->value;
