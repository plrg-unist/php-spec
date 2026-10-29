"""Multiple Iterator fields preserve selected references and independent COW."""

POOLED = b'''<?php
class FieldsPool implements Iterator {
    public $first;public $second;public $row;public $mark;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {echo "C;";return $this->row;}
    public function key():mixed {
        echo "K:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],";";
        $this->second[0][0]=22;$this->row=[[11],&$GLOBALS["other"],19];
        $GLOBALS["escaped"]=&$this->row;
        echo "Q:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],";";
        return "row";
    }
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["pool"][0][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],":",$this->mark,";";
        $this->first[0][0]=44;$this->row[0][0]=55;
        $GLOBALS["leaf"]=31;$GLOBALS["other"]=42;$GLOBALS["tail"]=20;$this->mark++;
        echo "M:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["pool"][0][0],":",$this->mark,";";
    }
}
$leaf=2;$other=9;$marker=0;$pool=[[3],7];$saved=$pool;$dest=99;$tail=7;
$it=new FieldsPool;$it->first=$pool;$it->second=$pool;$it->row=$pool;$it->mark=&$marker;
$watch=WeakReference::create($it);echo "P:",$watch->get()===$it,";";
$dest=[4=>8,...$it,$tail++];
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$escaped[0][0],":",$escaped[1],":",$saved[0][0],":",$saved[1],":",$pool[0][0],":",$marker,":",$dest[5],":",$tail,":",$watch->get()===null,":",isset($it),";";
unset($dest,$escaped,$saved,$pool,$leaf,$other,$marker,$watch,$tail);
echo "U:",isset($it),":",isset($dest),":",isset($escaped),";";
'''

CASES = {
    'array-iterator-fields-last-data': b'''<?php
class FieldsLast implements Iterator {
    public $first;public $second;public $row;public $mark;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {echo "C;";return $this->row;}
    public function key():mixed {
        echo "K:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],";";
        $this->second[0][0]=22;$this->row=[[11],&$GLOBALS["other"],19];
        $GLOBALS["escaped"]=&$this->row;
        echo "Q:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],";";
        return "row";
    }
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["pool"][0][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],":",$this->mark,";";
        $this->first[0][0]=44;$this->row[0][0]=55;
        $GLOBALS["leaf"]=31;$GLOBALS["other"]=42;$GLOBALS["tail"]=20;$this->mark++;
        echo "M:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["pool"][0][0],":",$this->mark,";";
    }
}
$seed=3;$child=[$seed];$leaf=2;$other=9;$marker=0;$pool=[[13],17];$dest=99;$tail=7;
$it=new FieldsLast;$it->first=[$child,&$leaf,7];$it->second=$pool;$it->row=[$child,&$other,19];$it->mark=&$marker;
$saved=$it->first;$watch=WeakReference::create($it);unset($child);
echo "P:",$watch->get()===$it,";";
$dest=[4=>8,...$it,$tail++];
echo "R:",$dest["row"][0][0],":",$dest["row"][1],":",$escaped[0][0],":",$escaped[1],":",$saved[0][0],":",$saved[1],":",$pool[0][0],":",$marker,":",$dest[5],":",$tail,":",$watch->get()===null,":",isset($it),";";
unset($dest,$escaped,$saved,$pool,$leaf,$other,$marker,$watch,$tail,$seed);
echo "U:",isset($it),":",isset($dest),":",isset($escaped),";";
''',
    'array-iterator-fields-key-throw': b'''<?php
class FieldsThrow implements Iterator {
    public $first;public $second;public $row;public $mark;
    public int $position=0;
    public function rewind():void {unset($GLOBALS["it"]);$this->position=0;echo "W;";}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {echo "C;";return $this->row;}
    public function key():mixed {
        echo "K:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],";";
        $this->second[0][0]=22;$this->row=[[11],&$GLOBALS["other"],19];
        $GLOBALS["escaped"]=&$this->row;
        echo "Q:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],";";
        throw $GLOBALS["first_error"];
    }
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["pool"][0][0],":",$GLOBALS["dest"]===99,":",$GLOBALS["watch"]->get()===$this,":",$GLOBALS["tail"],":",$this->mark,";";
        $this->first[0][0]=44;$this->row[0][0]=55;
        $GLOBALS["leaf"]=31;$GLOBALS["other"]=42;$GLOBALS["tail"]=20;$this->mark++;
        echo "M:",$this->first[0][0],":",$this->second[0][0],":",$this->row[0][0],":",$GLOBALS["saved"][0][0],":",$GLOBALS["pool"][0][0],":",$this->mark,";";
    }
}
$seed=3;$child=[$seed];$leaf=2;$other=9;$marker=0;$pool=[[13],17];$dest=99;$tail=7;
$first_error=new Exception("key");$it=new FieldsThrow;
$it->first=[$child,&$leaf,7];$it->second=$pool;$it->row=[$child,&$other,19];$it->mark=&$marker;
$saved=$it->first;$watch=WeakReference::create($it);unset($child);
echo "P:",$watch->get()===$it,";";
try {$dest=[4=>8,&$other,...$it,$tail++];echo "L;";}
catch (Exception $e) {
    echo "E:",$e===$first_error,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$escaped[0][0],":",$escaped[1],":",$saved[0][0],":",$saved[1],":",$pool[0][0],":",$marker,":",$tail,":",$watch->get()===null,";";
}
$escaped[0][0]=66;echo "S:",$escaped[0][0],":",$saved[0][0],";";
unset($e,$first_error,$dest,$escaped,$saved,$pool,$leaf,$other,$marker,$watch,$tail,$seed);
echo "U:",isset($it),":",isset($escaped),":",isset($first_error),";";
''',
    'array-iterator-fields-pooled': POOLED,
    # Historical A64 boundary; A65 now validates this by-value route.
    'array-iterator-fields-byval-boundary': POOLED.replace(
        b'function &current()', b'function current()', 1),
}
