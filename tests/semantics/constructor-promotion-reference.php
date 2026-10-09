<?php
class ReferencePromotion20 {
    public function __construct(public int &$value) { $value = 8; echo $this->value, '|'; }
}
$v = 4;
$o = new ReferencePromotion20($v);
$o->value = 9;
echo $v, '|';
try { $v = []; } catch (TypeError $e) { echo $e->getMessage(), '|'; }
echo $v, '|', $o->value;
