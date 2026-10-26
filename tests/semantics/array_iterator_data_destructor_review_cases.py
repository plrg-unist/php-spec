"""Iterator DATA destruction under invalid-key and supplied key exceptions."""

CASES = {
    'array-iterator-data-destructor-review-invalid-key': b'''<?php
class ArrayDataInvalidKey implements Iterator {
    public int $position=0;
    public function rewind(): void {echo "W;";$this->position=0;unset($GLOBALS["it"]);}
    public function valid(): bool {echo "V",$this->position,";";return $this->position<1;}
    public function current(): mixed {echo "C;";return $GLOBALS["row"];}
    public function key(): mixed {echo "K;";return false;}
    public function next(): void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["dest"]===99,":",$GLOBALS["tail"],":",$GLOBALS["watch"]->get()===$this,";";
        $GLOBALS["row"][0]=44;$GLOBALS["tail"]=20;
    }
}
$seed=2;$row=[$seed++,7];$it=new ArrayDataInvalidKey();
$watch=WeakReference::create($it);$dest=99;$tail=7;
echo "P;";
try {
    $dest=[$row,...$it,$tail++];echo "L;";
} catch (Error $e) {
    echo "E:",$e->getMessage(),":",$e->getLine(),":",$e->getPrevious()===null,":",$e->getTrace()===[],";";
}
echo "R:",$dest===99,":",$tail,":",$row[0],":",$row[1],":",$seed,":",$watch->get()===null,":",isset($it),";";
unset($e,$seed,$row,$watch,$dest,$tail);
echo "U:",isset($it),":",isset($row),":",isset($e),";";
''',
    'array-iterator-data-destructor-review-replacement-throw': b'''<?php
class ArrayDataReplacementThrow implements Iterator {
    public int $position=0;
    public function rewind(): void {echo "W;";$this->position=0;unset($GLOBALS["it"]);}
    public function valid(): bool {echo "V",$this->position,";";return $this->position<1;}
    public function current(): mixed {echo "C;";return $GLOBALS["row"];}
    public function key(): mixed {echo "K;";throw $GLOBALS["first"];}
    public function next(): void {echo "N;";$this->position++;}
    public function __destruct() {
        echo "D:",$GLOBALS["dest"]===99,":",$GLOBALS["tail"],":",$GLOBALS["watch"]->get()===$this,";";
        $GLOBALS["row"][0]=44;$GLOBALS["tail"]=20;throw $GLOBALS["second"];
    }
}
$seed=2;$row=[$seed++,7];$it=new ArrayDataReplacementThrow();
$watch=WeakReference::create($it);$dest=99;$tail=7;
$first=new Exception("first");$second=new Exception("second");
echo "P;";
try {
    $dest=[$row,...$it,$tail++];echo "L;";
} catch (Exception $e) {
    echo "E:",$e===$second,":",$e->getPrevious()===$first,":",$first->getPrevious()===null,":",$e->getTrace()===[],";";
}
echo "R:",$dest===99,":",$tail,":",$row[0],":",$row[1],":",$seed,":",$watch->get()===null,":",isset($it),";";
unset($e,$seed,$row,$watch,$dest,$tail,$first,$second);
echo "U:",isset($it),":",isset($row),":",isset($e),";";
''',
}

BOUNDARIES = {}
