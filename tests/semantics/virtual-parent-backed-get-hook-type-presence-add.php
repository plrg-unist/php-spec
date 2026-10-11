<?php
class CrossBackedAddParent45 {
    public $value { get => 7; }
}
class CrossBackedAddChild45 extends CrossBackedAddParent45 {
    public int $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
