<?php
class OrdinaryBackedRemoveRoot53 {
    public int $value = 100;
}
class OrdinaryBackedRemoveFirst53 extends OrdinaryBackedRemoveRoot53 {
    public int $value { get => 7; }
}
class OrdinaryBackedRemoveBridge53 extends OrdinaryBackedRemoveFirst53 {}
class OrdinaryBackedRemoveSecond53 extends OrdinaryBackedRemoveBridge53 {
    public $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
