"""Independent BYVAL snapshots with sole and held scalar reference leaves."""

CASES = {
    'array-iterator-byval-fields-invalid-sole-leaf': b'''<?php
class InvalidSoleLeaf implements Iterator {
    public $hold;public $row;public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;}
    public function valid():bool {return $this->position<1;}
    public function current():mixed {echo "C;";return $this->row;}
    public function key():mixed {
        $this->row[0][0]=22;$this->row[1]=17;
        echo "K:",$this->row[0][0],":",$this->row[1],":",$GLOBALS["saved"][0][0],":",$GLOBALS["saved"][1],";";
        return false;
    }
    public function next():void {$this->position++;}
    public function __destruct() {
        echo "D:",$this->hold[0][0],":",$this->hold[1],":",$this->row[0][0],":",$this->row[1],":",$GLOBALS["dest"]===99,":",$GLOBALS["tail"],":",$GLOBALS["watch"]->get()===$this,";";
        $this->hold[0][0]=44;$this->hold[1]=31;$this->row[0][0]=55;$this->row[1]=66;
        $GLOBALS["other"]=42;$GLOBALS["tail"]=20;
        echo "M:",$this->hold[0][0],":",$this->hold[1],":",$this->row[0][0],":",$this->row[1],":",$GLOBALS["saved"][0][0],":",$GLOBALS["saved"][1],";";
    }
}
$seed=3;$child=[$seed];$leaf=2;$other=9;$dest=99;$tail=7;
$it=new InvalidSoleLeaf;$it->row=[$child,&$leaf];$it->hold=$it->row;$saved=$it->row;
unset($child,$leaf);$watch=WeakReference::create($it);echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,&$other,...$it,$tail++];echo "L;";}
catch (Error $e) {
    echo "E:",$e->getMessage()==="Keys must be of type int|string during array unpacking",":",$e->getPrevious()===null,":",$dest===99,":",$saved[0][0],":",$saved[1],":",$other,":",$tail,":",$watch->get()===null,":",isset($it),";";
}
$saved[1]=77;echo "S:",$saved[0][0],":",$saved[1],":",isset($leaf),";";
unset($e,$saved,$dest,$seed,$other,$watch,$tail);echo "U:",isset($it),":",isset($dest),":",isset($saved),";";
''',
    'array-iterator-byval-fields-retained-held-leaf': b'''<?php
class RetainedHeldLeaf implements Iterator {
    public $hold;public $row;public int $position=0;
    public function rewind():void {$this->position=0;}
    public function valid():bool {return $this->position<1;}
    public function current():mixed {echo "C;";return $this->row;}
    public function key():mixed {
        $this->row[0][0]=22;$this->row[1]=17;
        echo "K:",$this->row[0][0],":",$this->row[1],":",$GLOBALS["saved"][0][0],":",$GLOBALS["saved"][1],";";
        return "row";
    }
    public function next():void {$this->position++;}
    public function __destruct() {
        echo "D:",$this->hold[0][0],":",$this->hold[1],":",$this->row[0][0],":",$this->row[1],":",$GLOBALS["dest"]!==99,":",$GLOBALS["tail"],":",$GLOBALS["watch"]->get()===$this,";";
        $this->hold[0][0]=44;$this->hold[1]=31;$this->row[0][0]=55;$this->row[1]=66;
        $GLOBALS["other"]=42;$GLOBALS["tail"]=20;
        echo "M:",$this->hold[0][0],":",$this->hold[1],":",$this->row[0][0],":",$this->row[1],":",$GLOBALS["saved"][0][0],":",$GLOBALS["saved"][1],";";
    }
}
$seed=3;$child=[$seed];$leaf=2;$other=9;$dest=99;$tail=7;
$it=new RetainedHeldLeaf;$it->row=[$child,&$leaf];$it->hold=$it->row;$saved=$it->row;
unset($child);$watch=WeakReference::create($it);echo "P:",$watch->get()===$it,";";
$dest=[...$it,$tail++];
echo "B:",$dest["row"][0][0],":",$dest["row"][1],":",$dest[0],":",$tail,":",$saved[0][0],":",$saved[1],":",$it->row[0][0],":",$it->row[1],":",$watch->get()===$it,";";
unset($it);
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$dest[0],":",$tail,":",$saved[0][0],":",$saved[1],":",$leaf,":",$watch->get()===null,";";
$saved[0][0]=77;$saved[1]=88;echo "S:",$saved[0][0],":",$dest["row"][0][0],":",$dest["row"][1],":",$leaf,";";
unset($saved);$dest["row"][0][0]=99;echo "T:",$dest["row"][0][0],":",$dest["row"][1],":",$leaf,";";
unset($dest,$seed,$leaf,$other,$watch,$tail);echo "U:",isset($it),":",isset($dest),":",isset($saved),";";
''',
}

EXPECTED = {
    'array-iterator-byval-fields-invalid-sole-leaf': b'P:1;C;K:22:17:3:2;D:3:2:22:17:1:7:1;M:44:31:55:66:3:2;E:1:1:1:3:2:42:20:1:;S:3:77:;U:::;',
    'array-iterator-byval-fields-retained-held-leaf': b'P:1;C;K:22:17:3:17;B:3:17:7:8:3:17:22:17:1;D:3:17:22:17:1:8:1;M:44:66:55:66:3:66;R:3:66:7:20:3:66:66:1;S:77:3:88:88;T:99:88:88;U:::;',
}
