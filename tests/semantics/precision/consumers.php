<?php
$value=12.3456789;
class PrecisionWrite {
    public function __toString(): string { ini_set('precision','2tail'); echo 'C|'; return 'left'; }
}
function receive(string $argument) { echo 'T:',$argument,'|'; }
class PrecisionSlot { public string $value; }
ini_set('precision','5junk');
$earlier=(string)$value;
$object=new PrecisionWrite;
echo 'B:',$earlier,'|';
echo $object.$value,'|';
ini_set('precision','5junk');
echo "P{$value}{$object}{$value}|";
receive($value);
$slot=new PrecisionSlot;
$slot->value=$value;
echo 'S:',$slot->value,'|';
$left='X';
$left.=$value;
echo 'A:',$left,'|';
ini_restore('precision');
echo 'R:',$value,'|END';
