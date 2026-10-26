"""Aggregate promotion to an Iterator with an embedded scalar reference."""

CASES = {
    'array-traversable-reference-aggregate-alias-retained': b'''<?php
class RefCacheCursor implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function current():mixed {echo "C;";return $GLOBALS["row"];}
    public function key():mixed {echo "K;";$GLOBALS["leaf"]=3;return "ref";}
    public function next():void {echo "N;";$this->position++;}
}
class RefCacheAggregate implements IteratorAggregate {
    public function getIterator():Traversable {echo "G;";return $GLOBALS["cursor"];}
}
$leaf=2;$row=[&$leaf,7];$cursor=new RefCacheCursor;$it=new RefCacheAggregate;
echo "P;";
$out=[4=>8,...$it,9];
echo "B:",$out["ref"][0],":",$row[0],":",$leaf,";";
$out["ref"][1]=88;$leaf=44;
echo "R:",$out["ref"][0],":",$row[0],":",$leaf,":",$out["ref"][1],":",$row[1],";";
unset($out,$it,$cursor,$row,$leaf);
echo "U:",isset($out),":",isset($row),":",isset($leaf),";";
''',
}
