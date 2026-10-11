<?php
class CovBackedBadParent44 {
    public int $value { get => 1; }
}
class CovBackedBadChild44 extends CovBackedBadParent44 {
    public int|string $value = 200 { get => $this->value; }
}
echo "UNREACHED|";
