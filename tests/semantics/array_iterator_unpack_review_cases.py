"""Independent array-spread Iterator error priority and cached-current cleanup."""

CASES = {
    'array-iterator-unpack-review-invalid-bool-key': b'''<?php
class ArraySpreadInvalid implements Iterator {
    public $i=0;
    public function rewind(): void {$this->i=0;echo "W;";}
    public function valid(): bool {echo "V;";return $this->i===0;}
    public function current(): mixed {echo "C;";return $GLOBALS["row"];}
    public function key(): mixed {echo "K;";$GLOBALS["row"][0]=44;return true;}
    public function next(): void {echo "N;";$this->i=$this->i+1;}
}
$seed=2;$row=[$seed];$it=new ArraySpreadInvalid();$dest=100;$later=7;
echo "P;";
try {
    $dest=[$seed,...$it,($later=88)];
    $later=99;echo "BAD;";
} catch (Error $e) {
    echo "E:",$e->getMessage(),":",$e->getLine(),":",$e->getPrevious()===null,";";
}
unset($e);
echo "R:",$dest===100,":",$later,":",$row[0],":",isset($it),":",isset($e),";";
unset($seed,$row,$it,$dest,$later);
echo "U:",isset($row),":",isset($it),":",isset($dest),";";
''',
    'array-iterator-unpack-review-supplied-throw': b'''<?php
class ArraySpreadThrow implements Iterator {
    public $i=0;
    public function rewind(): void {$this->i=0;echo "W;";}
    public function valid(): bool {echo "V;";return $this->i===0;}
    public function current(): mixed {
        echo "C;";
        if ($GLOBALS["mode"]===0) {$GLOBALS["row"][0]=22;throw $GLOBALS["second"];}
        return $GLOBALS["row"];
    }
    public function key(): mixed {
        echo "K;";$GLOBALS["row"][0]=44;unset($GLOBALS["it"]);
        if ($GLOBALS["mode"]===1) {throw $GLOBALS["second"];}
        return 3;
    }
    public function next(): void {echo "N;";$GLOBALS["row"][0]=55;throw $GLOBALS["second"];}
}
$seed=2;$row=[$seed];$mode=0;$it=new ArraySpreadThrow();$dest=100;$later=7;$second=new Exception("supplied");
echo "P0;";
try {
    $dest=[$seed,...$it,($later=88)];
    $later=99;echo "BAD0;";
} catch (Exception $e) {
    echo "C0:",$e===$second,":",$e->getPrevious()===null,":",$dest===100,":",$later,":",$row[0],":",isset($it),";";
}
unset($e);
$seed=7;$row=[$seed];$mode=1;$dest=101;
echo "P1;";
try {
    $dest=[$seed,...$it,($later=88)];
    $later=99;echo "BAD1;";
} catch (Exception $e) {
    echo "C1:",$e===$second,":",$e->getPrevious()===null,":",$dest===101,":",$later,":",$row[0],":",isset($it),";";
}
unset($e);
$seed=7;$row=[$seed];$mode=2;$dest=102;$it=new ArraySpreadThrow();
echo "P2;";
try {
    $dest=[$seed,...$it,($later=88)];
    $later=99;echo "BAD2;";
} catch (Exception $e) {
    echo "C2:",$e===$second,":",$e->getPrevious()===null,":",$dest===102,":",$later,":",$row[0],":",isset($it),";";
}
unset($e);
echo "R:",$row[0],":",$later,":",isset($it),":",isset($e),";";
unset($seed,$row,$mode,$it,$dest,$later,$second);
echo "U:",isset($row),":",isset($it),":",isset($second),";";
''',
    'array-iterator-unpack-review-generator-boundary': b'''<?php
function array_spread_generator() {echo "G;";yield 3;}
$it=array_spread_generator();$out=100;$later=7;
echo "P;";
$out=[...$it];
$later=88;
echo "R:",$out[0],":",$later,";";
unset($it,$out,$later);
echo "U:",isset($it),":",isset($out),";";
''',
}
