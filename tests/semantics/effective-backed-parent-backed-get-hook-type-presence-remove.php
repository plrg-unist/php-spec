<?php
class EffectiveBackedRemoveRoot48 {
    public int $value = 100 { get => $this->value; }
}
class EffectiveBackedRemoveFirst48 extends EffectiveBackedRemoveRoot48 {
    public int $value { get => 7; }
}
class EffectiveBackedRemoveBridge48 extends EffectiveBackedRemoveFirst48 {}
class EffectiveBackedRemoveSecond48 extends EffectiveBackedRemoveBridge48 {
    public $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
