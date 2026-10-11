<?php
class BackedUntypedParent42 {
    public $value = 100 { get => $this->value; }
}
class BackedAddedChild42 extends BackedUntypedParent42 {
    public int $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
