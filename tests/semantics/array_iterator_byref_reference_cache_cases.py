"""A raw Iterator current reference is dereferenced after key callbacks."""

CASES = {
    'array-iterator-byref-reference-cache-held': b'''<?php
class ByrefCacheCursor implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[&$GLOBALS["other"],19];return "ref";}
    public function next():void {echo "N;";$this->position++;}
}
$leaf=2;$other=9;$row=[&$leaf,7];$saved=$row;$it=new ByrefCacheCursor;
echo "P;";$out=[4=>8,...$it,9];
echo "B:",$out["ref"][0],":",$row[0],":",$saved[0],":",$leaf,":",$other,":",$out["ref"][1],":",$row[1],":",$saved[1],";";
$out["ref"][1]=88;$other=66;$leaf=44;
echo "R:",$out["ref"][0],":",$row[0],":",$saved[0],":",$leaf,":",$other,":",$out["ref"][1],":",$row[1],":",$saved[1],";";
unset($out,$it,$row,$saved,$leaf,$other);
echo "U:",isset($out),":",isset($it),":",isset($row),":",isset($saved),":",isset($leaf),":",isset($other),";";
''',
    'array-iterator-byref-reference-cache-dropped': b'''<?php
class ByrefCacheCursor implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {global $row;echo "K;";$row=[&$GLOBALS["other"],19];return "ref";}
    public function next():void {echo "N;";$this->position++;}
}
$leaf=2;$other=9;$row=[&$leaf,7];$saved=$row;$it=new ByrefCacheCursor;
echo "P;";$out=[4=>8,...$it,9];
echo "B:",$out["ref"][0],":",$row[0],":",$saved[0],":",$other,";";
unset($other);$out["ref"][1]=88;$row[0]=44;
echo "R:",$out["ref"][0],":",$row[0],":",$saved[0],":",$out["ref"][1],":",$row[1],":",$saved[1],";";
unset($out,$it,$row,$saved,$leaf);
echo "U:",isset($out),":",isset($it),":",isset($row),":",isset($saved),":",isset($leaf),":",isset($other),";";
''',
    'array-iterator-byref-reference-cache-key-throw': b'''<?php
class ByrefThrowCursor implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {global $row;echo "C;";return $row;}
    public function key():mixed {
        echo "K;";unset($GLOBALS["it"],$GLOBALS["row"],$GLOBALS["leaf"]);
        echo "Q:",$GLOBALS["watch"]->get()!==null,":",isset($GLOBALS["row"]),":",isset($GLOBALS["leaf"]),";";
        throw $GLOBALS["second"];
    }
    public function next():void {echo "N;";$this->position++;}
}
$leaf=2;$row=[&$leaf,7];$second=new Exception("supplied");$dest=99;$later=7;
$it=new ByrefThrowCursor;$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,...$it,$later++];echo "L;";}
catch (Exception $e) {
    echo "T:",$e===$second,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$later,":",$watch->get()===null,";";
}
unset($e,$second,$dest,$later,$watch);
echo "U:",isset($it),":",isset($row),":",isset($leaf),":",isset($second),";";
''',
}
