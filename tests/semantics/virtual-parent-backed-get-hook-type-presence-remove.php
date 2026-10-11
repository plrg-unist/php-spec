<?php
class CrossBackedRemoveParent45 {
    public int $value { get => 7; }
}
class CrossBackedRemoveChild45 extends CrossBackedRemoveParent45 {
    public $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
