"""Aggregate array spreads acquire an owned return before Iterator/Generator DATA."""

CASES = {
    'array-aggregate-unpack-fresh-iterator': b'''<?php
class ArraySpreadCursor implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function current():mixed {echo "C;";return $GLOBALS["row"];}
    public function key():mixed {echo "K;";$GLOBALS["row"][0]=44;return "slot";}
    public function next():void {echo "N;";$this->position++;}
}
class ArraySpreadFactory implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";unset($GLOBALS["agg"]);$GLOBALS["row"][0]=11;
        return new ArraySpreadCursor;
    }
}
$seed=2;$row=[$seed++,7];$tail=7;$agg=new ArraySpreadFactory;$hold=$agg;
echo "P;";
$out=["slot"=>8,"prefix"=>$row,...$agg,$tail++];
$before=$out;$out["slot"][0]=55;
echo "R:",$out["slot"][0],":",$before["slot"][0],":",$out["prefix"][0],":",$row[0],":",$seed,":",$tail,":",isset($agg),":",isset($hold),";";
echo "O:",$out===["slot"=>[55,7],"prefix"=>[2,7],0=>7],":",$before===["slot"=>[11,7],"prefix"=>[2,7],0=>7],";";
unset($seed,$row,$tail,$hold,$out,$before);
echo "U:",isset($agg),":",isset($hold),":",isset($out),";";
''',
    'array-aggregate-unpack-fresh-generator': b'''<?php
function array_aggregate_values($local) {
    echo "B;";unset($GLOBALS["hold"]);
    echo "D:",$GLOBALS["watch"]->get()===null,";";
    try {yield "first"=>$local;echo "N;";$local[0]=33;yield "second"=>$local;}
    finally {echo "F;";$GLOBALS["row"][0]=66;$GLOBALS["closed"]=44;}
}
class ArrayGeneratorFactory implements IteratorAggregate {
    public function getIterator():Traversable {
        echo "G;";unset($GLOBALS["agg"]);
        return array_aggregate_values($GLOBALS["row"]);
    }
}
$seed=2;$row=[$seed++,7];$tail=7;$closed=0;$agg=new ArrayGeneratorFactory;$hold=$agg;
$watch=WeakReference::create($agg);
echo "P;";
$out=["prefix"=>$row,...$agg,$tail++];
$before=$out;$out["first"][0]=55;$out["second"][1]=88;
echo "R:",$out["prefix"][0],":",$out["first"][0],":",$out["second"][0],":",$out["second"][1],":",$before["first"][0],":",$before["second"][1],":",$row[0],":",$closed,":",$seed,":",$tail,":",isset($agg),":",isset($hold),";";
echo "O:",$out===["prefix"=>[2,7],"first"=>[55,7],"second"=>[33,88],0=>7],":",$before===["prefix"=>[2,7],"first"=>[2,7],"second"=>[33,7],0=>7],";";
unset($seed,$row,$tail,$closed,$out,$before,$watch);
echo "U:",isset($agg),":",isset($hold),":",isset($out),";";
''',
}
