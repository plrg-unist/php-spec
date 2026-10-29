"""A pooled declared ARRAY field survives Iterator spread and separates on write."""

CASES = {
    'array-iterator-pooled-field-last-data': b'''<?php
class PoolFieldLast implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
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
$leaf=2;$other=9;$row=[[5],&$leaf,8];$saved=[[3],7];$dest=99;$tail=7;
$it=new PoolFieldLast;$it->hold=$saved;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$dest=[4=>8,...$it,$tail++];
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$row[0][0],":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$dest[5],":",$tail,":",$watch->get()===null,":",isset($it),";";
unset($dest,$row,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($dest),":",isset($row),";";
''',
    'array-iterator-pooled-field-key-throw': b'''<?php
class PoolFieldThrow implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {
        global $row;echo "K:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],";";
        $this->hold[0][0]=22;$row=[[11],&$GLOBALS["other"],19];unset($GLOBALS["row"]);
        echo "Q:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["watch"]->get()===$this,";";throw $GLOBALS["first"];
    }
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $this->hold[0][0]=44;
        echo "M:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$this->hold[1],":",$GLOBALS["saved"][1],";";
        $GLOBALS["leaf"]=17;$GLOBALS["other"]=42;$GLOBALS["tail"]=20;
    }
}
$leaf=2;$other=9;$row=[[5],&$leaf,8];$saved=[[3],7];$dest=99;$tail=7;
$first=new Exception("key");$it=new PoolFieldThrow;$it->hold=$saved;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,&$other,...$it,$tail++];echo "L;";}
catch (Exception $e) {
    echo "E:",$e===$first,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$tail,":",$watch->get()===null,";";
}
unset($e,$first,$dest,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($row),":",isset($first),";";
''',
    'array-iterator-pooled-field-invalid-key': b'''<?php
class PoolFieldInvalid implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[[11],&$GLOBALS["other"],19];unset($GLOBALS["row"]);return false;}
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $this->hold[0][0]=44;
        echo "M:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$this->hold[1],":",$GLOBALS["saved"][1],";";
        $GLOBALS["leaf"]=17;$GLOBALS["other"]=42;$GLOBALS["tail"]=20;
    }
}
$leaf=2;$other=9;$row=[[5],&$leaf,8];$saved=[[3],7];$dest=99;$tail=7;
$it=new PoolFieldInvalid;$it->hold=$saved;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,&$other,...$it,$tail++];echo "L;";}
catch (Error $e) {
    echo "E:",$e->getMessage()=== "Keys must be of type int|string during array unpacking",":",$e->getPrevious()===null,":",$dest===99,":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$tail,":",$watch->get()===null,";";
}
unset($e,$dest,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($row),":",isset($dest),";";
''',
}
