"""Aggregate promotion into a field-owning destructor Iterator."""

CASES = {
    'array-iterator-owned-field-aggregate': b'''<?php
class FieldCursor implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["cursor"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[[11],&$GLOBALS["other"],19];return "row";}
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $this->hold[0][0]=44;
        echo "M:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$this->hold[1],":",$GLOBALS["saved"][1],";";
        $GLOBALS["leaf"]=17;$GLOBALS["other"]=42;$GLOBALS["tail"]=20;
    }
}
class FieldAggregate implements IteratorAggregate {
    public function getIterator():Traversable {echo "G;";return $GLOBALS["cursor"];}
}
$leaf=2;$other=9;$row=[[3],&$leaf,7];$saved=$row;$dest=99;$tail=7;
$cursor=new FieldCursor;$cursor->hold=$row;$it=new FieldAggregate;$watch=WeakReference::create($cursor);
echo "P:",$watch->get()===$cursor,";";
$dest=[4=>8,...$it,$tail++];
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$row[0][0],":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$dest[5],":",$tail,":",$watch->get()===null,":",isset($cursor),";";
unset($dest,$it,$row,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($cursor),":",isset($dest),";";
''',
}
