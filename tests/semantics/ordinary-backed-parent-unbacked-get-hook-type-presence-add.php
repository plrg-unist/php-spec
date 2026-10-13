<?php
class OrdinaryAddRoot52 {
    public $value = 100;
}
class OrdinaryAddFirst52 extends OrdinaryAddRoot52 {
    public $value { get => 7; }
}
class OrdinaryAddBridge52 extends OrdinaryAddFirst52 {}
class OrdinaryAddSecond52 extends OrdinaryAddBridge52 {
    public int $value { get => 13; }
}
echo "UNREACHED|";
