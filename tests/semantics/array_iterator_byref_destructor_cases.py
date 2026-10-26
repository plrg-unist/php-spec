"""A real Iterator destructor observes a spread builder after raw current rebinding."""

CASES = {
    'array-iterator-byref-destructor-last-data': b'''<?php
class ByrefDtorLast implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";unset($GLOBALS["it"]);$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[&$GLOBALS["alias"],19];return "row";}
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $GLOBALS["alias"]=42;$GLOBALS["tail"]=20;
    }
}
$leaf=2;$alias=9;$row=[&$leaf,7];$saved=$row;$dest=99;$tail=7;
$it=new ByrefDtorLast;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$dest=[4=>8,...$it,$tail++];
echo "R:",$dest["row"][0],":",$row[0],":",$saved[0],":",$leaf,":",$alias,":",$dest["row"][1],":",$dest[5],":",$tail,":",$watch->get()===null,":",isset($it),";";
unset($dest,$row,$saved,$leaf,$alias,$watch,$tail);
echo "U:",isset($it),":",isset($dest),":",isset($row),";";
''',
    'array-iterator-byref-destructor-retained-owner': b'''<?php
class ByrefDtorRetained implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[&$GLOBALS["alias"],19];return "row";}
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $GLOBALS["alias"]=42;$GLOBALS["tail"]=20;
    }
}
$leaf=2;$alias=9;$row=[&$leaf,7];$saved=$row;$dest=99;$tail=7;
$it=new ByrefDtorRetained;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$dest=[4=>8,...$it,$tail++];
echo "B:",$dest["row"][0],":",$row[0],":",$saved[0],":",$leaf,":",$alias,":",$dest[5],":",$tail,":",$watch->get()===$it,";";
unset($it);
echo "R:",$dest["row"][0],":",$row[0],":",$saved[0],":",$leaf,":",$alias,":",$dest[5],":",$tail,":",$watch->get()===null,";";
unset($dest,$row,$saved,$leaf,$alias,$watch,$tail);
echo "U:",isset($it),":",isset($dest),":",isset($row),";";
''',
    'array-iterator-byref-destructor-key-throw': b'''<?php
class ByrefDtorThrow implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";unset($GLOBALS["it"]);$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {
        global $row;echo "K;";$row=[&$GLOBALS["alias"],19];
        unset($GLOBALS["row"]);echo "Q:",$GLOBALS["watch"]->get()===$this,";";
        throw $GLOBALS["first"];
    }
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],";";
        $GLOBALS["alias"]=42;$GLOBALS["tail"]=20;
    }
}
$leaf=2;$alias=9;$row=[&$leaf,7];$dest=99;$tail=7;
$first=new Exception("key");$it=new ByrefDtorThrow;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,&$alias,...$it,$tail++];echo "L;";}
catch (Exception $e) {
    echo "E:",$e===$first,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$alias,":",$tail,":",$watch->get()===null,";";
}
unset($e,$first,$dest,$leaf,$alias,$watch,$tail);
echo "U:",isset($it),":",isset($row),":",isset($first),";";
''',
}
