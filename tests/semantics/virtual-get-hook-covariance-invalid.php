<?php
class CovInvalidParent40 {
    public int $value { get => 7; }
}
class CovInvalidChild40 extends CovInvalidParent40 {
    public int|string $value { get => "wider"; }
}
echo "UNREACHED|";
