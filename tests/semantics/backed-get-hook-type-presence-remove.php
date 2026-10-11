<?php
class BackedTypedParent42 {
    public int $value = 100 { get => $this->value; }
}
class BackedMissingChild42 extends BackedTypedParent42 {
    public $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
