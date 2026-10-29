"""Independent shared field edges, selected row cache, and delayed retirement."""

CASES = {
    'array-iterator-fields-retained-shared-child': b'''<?php
class RetainedSharedFields implements Iterator {
    public $first;
    public $second;
    public $row;
    public int $position=0;
    public function rewind():void {$this->position=0;}
    public function valid():bool {return $this->position<1;}
    public function &current():mixed {echo "C;";return $this->row;}
    public function key():mixed {
        $this->second[0][0]=22;
        $this->row=[$this->first[0],&$GLOBALS["other"]];
        echo "K:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],";";
        return "row";
    }
    public function next():void {$this->position++;}
    public function __destruct() {
        echo "D:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["dest"]!==99,":",$GLOBALS["tail"],":",$GLOBALS["watch"]->get()===$this,";";
        $this->first[0][0]=44;$this->row[0][0]=55;
        $GLOBALS["other"]=42;$GLOBALS["tail"]=20;
        echo "M:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["other"],";";
    }
}
$seed=3;$child=[$seed];$leaf=2;$other=9;$dest=99;$tail=7;
$it=new RetainedSharedFields;$it->first=[$child,1];$it->second=$it->first;$it->row=[$child,&$leaf];
$saved=$it->first;unset($child);$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$dest=[...$it,$tail++];
echo "B:",$dest["row"][0][0],":",$dest["row"][1],":",$dest[0],":",$tail,":",$saved[0][0],":",$it->second[0][0],":",$watch->get()===$it,";";
unset($it);
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$dest[0],":",$tail,":",$saved[0][0],":",$watch->get()===null,";";
$saved[0][0]=66;echo "S:",$saved[0][0],":",$dest["row"][0][0],";";
unset($saved);$dest["row"][0][0]=77;echo "T:",$dest["row"][0][0],":",$dest["row"][1],":",$leaf,";";
unset($dest,$seed,$leaf,$other,$watch,$tail);
echo "U:",isset($it),":",isset($dest),":",isset($saved),";";
''',
}

