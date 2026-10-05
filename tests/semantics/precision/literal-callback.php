<?php
class PrecisionLiteral {
    public function __toString(): string {
        ini_set('precision', '1');
        return 'X';
    }
}
$value = 12.3456789;
ini_set('precision', '3');
$object = new PrecisionLiteral;
echo 'C:', $object . 12.3456789, '|', $object . $value, '|';
ini_restore('precision');
echo 'R:', 12.3456789 . $object, '|END';
