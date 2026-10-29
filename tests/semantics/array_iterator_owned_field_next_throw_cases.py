"""A field-owning Iterator throws from next() after spread insertion."""

CASES = {
    'array-iterator-owned-field-next-throw': b'''<?php
class FieldNextThrow implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[[11],&$GLOBALS["other"],19];return "row";}
    public function next():void {
        echo "N;";unset($GLOBALS["row"]);
        echo "Q:",$GLOBALS["watch"]->get()===$this,";";throw $GLOBALS["first"];
    }
    public function __destruct() {
        echo "D:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $this->hold[0][0]=44;
        echo "M:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$this->hold[1],":",$GLOBALS["saved"][1],";";
        $GLOBALS["leaf"]=17;$GLOBALS["other"]=42;$GLOBALS["tail"]=20;
    }
}
$leaf=2;$other=9;$row=[[3],&$leaf,7];$saved=$row;$dest=99;$tail=7;
$first=new Exception("next");$it=new FieldNextThrow;$it->hold=$row;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,...$it,$tail++];echo "L;";}
catch (Exception $e) {
    echo "E:",$e===$first,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$tail,":",$watch->get()===null,";";
}
unset($e,$first,$dest,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($row),":",isset($first),";";
''',
}
