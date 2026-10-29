"""Independent retained Iterator with an empty pooled field and late COW."""

CASES = {
    'array-iterator-pooled-field-retained-empty': b'''<?php
class RetainedEmptyField implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {$this->position=0;}
    public function valid():bool {return $this->position<1;}
    public function &current():mixed {global $row;return $row;}
    public function key():mixed {global $row;$row=[[11],&$GLOBALS["other"]];return "row";}
    public function next():void {$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["dest"]!==99,":",$GLOBALS["tail"],":",$this->hold===[],":",$GLOBALS["saved"]===[],";";
        $this->hold[]=44;
        echo "M:",$this->hold[0],":",$GLOBALS["saved"]===[],";";
        $GLOBALS["other"]=42;$GLOBALS["tail"]=20;
    }
}
$leaf=2;$other=9;$row=[[5],&$leaf];$dest=99;$tail=7;
$it=new RetainedEmptyField;$it->hold=[];$saved=$it->hold;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$dest=[...$it,$tail++];
echo "B:",$dest["row"][0][0],":",$dest["row"][1],":",$dest[0],":",$tail,":",$saved===[],":",$watch->get()===$it,";";
unset($it);
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$dest[0],":",$tail,":",$saved===[],":",$watch->get()===null,";";
unset($dest,$row,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($dest),":",isset($saved),";";
''',
}
