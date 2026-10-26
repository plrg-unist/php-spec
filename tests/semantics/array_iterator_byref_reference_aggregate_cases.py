"""An Aggregate getter promotes a by-reference Iterator to spread DATA."""

CASES = {
    'array-iterator-byref-reference-aggregate-held': b'''<?php
class ByrefCacheCursor implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[&$GLOBALS["other"],19];return "ref";}
    public function next():void {echo "N;";$this->position++;}
}
class ByrefCacheAggregate implements IteratorAggregate {
    public function getIterator():Traversable {echo "G;";return $GLOBALS["cursor"];}
}
$leaf=2;$other=9;$row=[&$leaf,7];$saved=$row;$cursor=new ByrefCacheCursor;$it=new ByrefCacheAggregate;
echo "P;";$out=[4=>8,...$it,9];
echo "B:",$out["ref"][0],":",$row[0],":",$saved[0],":",$leaf,":",$other,";";
$out["ref"][1]=88;$other=66;$leaf=44;
echo "R:",$out["ref"][0],":",$row[0],":",$saved[0],":",$leaf,":",$other,":",$out["ref"][1],":",$row[1],":",$saved[1],";";
unset($out,$it,$cursor,$row,$saved,$leaf,$other);
echo "U:",isset($out),":",isset($it),":",isset($cursor),":",isset($row),":",isset($saved),";";
''',
}
