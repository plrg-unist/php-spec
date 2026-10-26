"""Last Iterator DATA destruction precedes literal continuation or cancellation."""

CASES = {
    'array-iterator-data-destructor-normal': b'''<?php
class ArrayDataNormal implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";unset($GLOBALS["it"]);$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function current():mixed {echo "C;";return $GLOBALS["row"];}
    public function key():mixed {echo "K;";return "row";}
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["dest"],":",$GLOBALS["tail"],";";
        $GLOBALS["row"][0]=44;$GLOBALS["tail"]=20;
    }
}
$seed=2;$row=[$seed++,7];$dest=99;$tail=7;$it=new ArrayDataNormal;
$watch=WeakReference::create($it);echo "P;";
$dest=[4=>8,...$it,$tail++];
echo "R:",$dest["row"][0],":",$row[0],":",$dest[5],":",$tail,":",$watch->get()===null,":",isset($it),";";
echo "O:",$dest===[4=>8,"row"=>[2,7],5=>20],":",$row===[44,7],";";
unset($seed,$row,$dest,$tail,$watch);
echo "U:",isset($it),":",isset($dest),";";
''',
    'array-iterator-data-destructor-normal-throw': b'''<?php
class ArrayDataThrow implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";unset($GLOBALS["it"]);$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function current():mixed {echo "C;";return $GLOBALS["row"];}
    public function key():mixed {echo "K;";return "row";}
    public function next():void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["dest"],":",$GLOBALS["tail"],";";
        $GLOBALS["row"][0]=44;$GLOBALS["tail"]=20;throw $GLOBALS["second"];
    }
}
$seed=2;$row=[$seed++,7];$dest=99;$tail=7;$second=new Exception("dtor");
$it=new ArrayDataThrow;$watch=WeakReference::create($it);echo "P;";
try {$dest=[4=>8,...$it,$tail++];echo "L;";}
catch (Exception $e) {
    echo "C:",$e===$second,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest,":",$tail,":",$row[0],":",$watch->get()===null,";";
}
$row[1]=55;echo "R:",$row[0],":",$row[1],";";
unset($e,$seed,$row,$dest,$tail,$watch,$second);
echo "U:",isset($it),":",isset($dest),":",isset($second),";";
''',
}
