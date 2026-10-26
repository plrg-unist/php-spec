"""Nested cache DAG retirement under Iterator key and Generator body throws."""

CASES = {
    'array-traversable-nested-cache-review-key-throw': b'''<?php
class ArrayNestedThrowCursor implements Iterator {
    public int $position=0;
    public function rewind(): void {echo "W;";$this->position=0;}
    public function valid(): bool {echo "V",$this->position,";";return $this->position<1;}
    public function current(): mixed {
        echo "C;";$value=$GLOBALS["tree"];
        unset($GLOBALS["tree"],$GLOBALS["leaf"]);return $value;
    }
    public function key(): mixed {
        echo "K;";$GLOBALS["before"][0]=44;throw $GLOBALS["second"];
    }
    public function next(): void {echo "N;";$this->position++;}
}
$seed=2;$leaf=[$seed++,7];$tree=[$leaf,[[$leaf]]];$before=$leaf;
$it=new ArrayNestedThrowCursor();$dest=99;$later=7;$second=new Exception("supplied");
echo "P;";
try {
    $dest=[$leaf,...$it,$later++];echo "L;";
} catch (Exception $e) {
    echo "C:",$e===$second,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$later,":",$before[0],":",$before[1],":",$seed,":",isset($leaf),":",isset($tree),":",$it->position,";";
}
$before[1]=55;echo "R:",$before[0],":",$before[1],";";
unset($e,$it,$seed,$before,$dest,$later,$second);
echo "U:",isset($it),":",isset($tree),":",isset($second),";";
''',
    'array-traversable-nested-cache-review-body-throw': b'''<?php
function array_nested_throw($local) {
    try {
        echo "B;";yield "first"=>$local;echo "N;";
        unset($GLOBALS["it"],$GLOBALS["tree"],$GLOBALS["leaf"]);
        $GLOBALS["before"][0]=44;throw $GLOBALS["second"];
    } finally {
        echo "F:",$GLOBALS["watch"]->get()!==null,";";
        $GLOBALS["later"]=$GLOBALS["later"]+1;
    }
}
$seed=2;$leaf=[$seed++,7];$tree=[$leaf,[[$leaf]]];$before=$leaf;
$it=array_nested_throw($tree);$watch=WeakReference::create($it);
$dest=99;$later=7;$second=new Exception("supplied");
echo "P;";
try {
    $dest=[$leaf,...$it,$later++];echo "L;";
} catch (Exception $e) {
    echo "C:",$e===$second,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$later,":",$before[0],":",$before[1],":",$seed,":",isset($it),":",isset($leaf),":",isset($tree),":",$watch->get()===null,";";
}
$before[1]=55;echo "R:",$before[0],":",$before[1],";";
unset($e,$seed,$before,$watch,$dest,$later,$second);
echo "U:",isset($it),":",isset($tree),":",isset($second),";";
''',
}

BOUNDARIES = {}
