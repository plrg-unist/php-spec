<?php
class EffectiveRemoveRoot47 {
    public int $value = 100 { get => $this->value; }
}
class EffectiveRemoveFirst47 extends EffectiveRemoveRoot47 {
    public int $value { get => 7; }
}
class EffectiveRemoveBridge47 extends EffectiveRemoveFirst47 {}
class EffectiveRemoveSecond47 extends EffectiveRemoveBridge47 {
    public $value { get => 13; }
}
echo "UNREACHED|";
