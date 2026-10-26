"""An Aggregate getter promotes a destructor-bearing by-reference Iterator."""

CASES = {
    'array-iterator-byref-destructor-aggregate': b'''<?php
class ByrefDtorCursor implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";unset($GLOBALS["cursor"]);$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[&$GLOBALS["alias"],19];return "row";}
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $GLOBALS["alias"]=42;$GLOBALS["tail"]=20;
    }
}
class ByrefDtorAggregate implements IteratorAggregate {
    public function getIterator():Traversable {echo "G;";return $GLOBALS["cursor"];}
}
$leaf=2;$alias=9;$row=[&$leaf,7];$saved=$row;$dest=99;$tail=7;
$cursor=new ByrefDtorCursor;$it=new ByrefDtorAggregate;
$watch=WeakReference::create($cursor);
echo "P:",$watch->get()===$cursor,";";
$dest=[4=>8,...$it,$tail++];
echo "R:",$dest["row"][0],":",$row[0],":",$saved[0],":",$leaf,":",$alias,":",$dest[5],":",$tail,":",$watch->get()===null,":",isset($cursor),";";
unset($dest,$it,$row,$saved,$leaf,$alias,$watch,$tail);
echo "U:",isset($it),":",isset($cursor),":",isset($dest),";";
''',
}
