"""Declared array field ownership during by-reference Iterator spread."""

CASES = {
    'array-iterator-owned-field-last-data': b'''<?php
class FieldLast implements Iterator {
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
$leaf=2;$other=9;$row=[[3],&$leaf,7];$saved=$row;$dest=99;$tail=7;
$it=new FieldLast;$it->hold=$row;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$dest=[4=>8,...$it,$tail++];
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$row[0][0],":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$dest[5],":",$tail,":",$watch->get()===null,":",isset($it),";";
unset($dest,$row,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($dest),":",isset($row),";";
''',
    'array-iterator-owned-field-retained-owner': b'''<?php
class FieldRetained implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {$this->position=0;echo "W;";}
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
$leaf=2;$other=9;$row=[[3],&$leaf,7];$saved=$row;$dest=99;$tail=7;
$it=new FieldRetained;$it->hold=$row;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$dest=[4=>8,...$it,$tail++];
echo "B:",$dest["row"][0][0],":",$dest["row"][1],":",$saved[0][0],":",$leaf,":",$other,":",$tail,":",$watch->get()===$it,";";
unset($it);
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$tail,":",$watch->get()===null,";";
unset($dest,$row,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($dest),":",isset($row),";";
''',
    'array-iterator-owned-field-key-throw': b'''<?php
class FieldThrow implements Iterator {
    public $hold;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {
        global $row;echo "K;";$row=[[11],&$GLOBALS["other"],19];unset($GLOBALS["row"]);
        echo "Q:",$GLOBALS["watch"]->get()===$this,";";throw $GLOBALS["first"];
    }
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $this->hold[0][0]=44;
        echo "M:",$this->hold[0][0],":",$GLOBALS["saved"][0][0],":",$this->hold[1],":",$GLOBALS["saved"][1],";";
        $GLOBALS["leaf"]=17;$GLOBALS["other"]=42;$GLOBALS["tail"]=20;
    }
}
$leaf=2;$other=9;$row=[[3],&$leaf,7];$saved=$row;$dest=99;$tail=7;
$first=new Exception("key");$it=new FieldThrow;$it->hold=$row;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,&$other,...$it,$tail++];echo "L;";}
catch (Exception $e) {
    echo "E:",$e===$first,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$tail,":",$watch->get()===null,";";
}
unset($e,$first,$dest,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($row),":",isset($first),";";
''',
    'array-iterator-owned-field-invalid-key': b'''<?php
class FieldInvalidKey implements Iterator {
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
$leaf=2;$other=9;$row=[[3],&$leaf,7];$saved=$row;$dest=99;$tail=7;
$it=new FieldInvalidKey;$it->hold=$row;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,&$other,...$it,$tail++];echo "L;";}
catch (Error $e) {
    echo "E:",$e->getMessage()=== "Keys must be of type int|string during array unpacking",":",$e->getPrevious()===null,":",$dest===99,":",$saved[0][0],":",$saved[1],":",$leaf,":",$other,":",$tail,":",$watch->get()===null,";";
}
unset($e,$dest,$saved,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($row),":",isset($dest),";";
''',
}
