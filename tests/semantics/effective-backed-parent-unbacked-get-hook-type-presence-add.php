<?php
class EffectiveAddRoot47 {
    public $value = 100 { get => $this->value; }
}
class EffectiveAddFirst47 extends EffectiveAddRoot47 {
    public $value { get => 7; }
}
class EffectiveAddBridge47 extends EffectiveAddFirst47 {}
class EffectiveAddSecond47 extends EffectiveAddBridge47 {
    public int $value { get => 13; }
}
echo "UNREACHED|";
