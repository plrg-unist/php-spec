"""Independent sole-leaf COW witness for an Iterator's owning array field."""

CASES = {
    'array-iterator-owned-field-singleton-leaf': b'''<?php
class FieldSolo implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;}
    public function valid():bool {return $this->position<1;}
    public function &current():mixed {global $row;return $row;}
    public function key():mixed {global $row;$row=[[11],&$GLOBALS["other"]];return "row";}
    public function next():void {$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["dest"]===99,":",$this->hold[0][0],":",$GLOBALS["saved"][0][0],";";
        $this->hold[0][0]=44;$this->hold[1]=17;
        echo "M:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$this->hold[1],":",$GLOBALS["saved"][1],";";
        $GLOBALS["tail"]=20;
    }
}
$leaf=2;$other=9;$row=[[3],&$leaf];$saved=$row;unset($leaf);
$dest=99;$tail=7;$it=new FieldSolo;$it->hold=$row;$watch=WeakReference::create($it);
$dest=[...$it,$tail++];
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$saved[0][0],":",$saved[1],":",$dest[0],":",$tail,":",$watch->get()===null,";";
unset($dest,$row,$saved,$other,$watch,$tail);
echo "U:",isset($it),":",isset($row),":",isset($saved),";";
''',
}
