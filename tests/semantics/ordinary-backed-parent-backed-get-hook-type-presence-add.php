<?php
class OrdinaryBackedAddRoot53 {
    public $value = 100;
}
class OrdinaryBackedAddFirst53 extends OrdinaryBackedAddRoot53 {
    public $value { get => 7; }
}
class OrdinaryBackedAddBridge53 extends OrdinaryBackedAddFirst53 {}
class OrdinaryBackedAddSecond53 extends OrdinaryBackedAddBridge53 {
    public int $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
