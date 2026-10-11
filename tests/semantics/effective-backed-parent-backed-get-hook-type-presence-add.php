<?php
class EffectiveBackedAddRoot48 {
    public $value = 100 { get => $this->value; }
}
class EffectiveBackedAddFirst48 extends EffectiveBackedAddRoot48 {
    public $value { get => 7; }
}
class EffectiveBackedAddBridge48 extends EffectiveBackedAddFirst48 {}
class EffectiveBackedAddSecond48 extends EffectiveBackedAddBridge48 {
    public int $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
