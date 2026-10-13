<?php
class OrdinaryRemoveRoot52 {
    public int $value = 100;
}
class OrdinaryRemoveFirst52 extends OrdinaryRemoveRoot52 {
    public int $value { get => 7; }
}
class OrdinaryRemoveBridge52 extends OrdinaryRemoveFirst52 {}
class OrdinaryRemoveSecond52 extends OrdinaryRemoveBridge52 {
    public $value { get => 13; }
}
echo "UNREACHED|";
