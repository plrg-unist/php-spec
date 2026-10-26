"""Nested DIRECT cache graphs preserve shared child edges and selective COW."""

CASES = {
    'array-traversable-nested-cache-iterator-reference': b'''<?php
class NestedCacheIterator implements Iterator {
    public int $position=0;
    public function rewind():void {echo "W;";$this->position=0;}
    public function valid():bool {echo "V",$this->position,";";return $this->position<1;}
    public function &current():mixed {echo "C;";return $GLOBALS["row"];}
    public function key():mixed {echo "K;";$GLOBALS["row"][0][0]=44;return "tree";}
    public function next():void {echo "N;";$this->position++;}
}
$seed=2;$leaf=[$seed++,7];$row=[$leaf,$leaf,["fixed"=>[5,9]],[]];
$outside=&$row;$before=$row;$tail=7;$it=new NestedCacheIterator;
echo "P;";
$out=[4=>8,...$it,$tail++];
$outside[1][0]=66;$saved=$out;$out["tree"][0][1]=88;
echo "R:",$out["tree"][0][0],":",$out["tree"][0][1],":",$saved["tree"][0][1],":",$out["tree"][1][0],":",$row[1][0],":",$before[0][0],":",$leaf[0],":",$out["tree"][2]["fixed"][0],":",$out["tree"][3]===[],":",$seed,":",$tail,";";
echo "O:",$out===[4=>8,"tree"=>[[44,88],[2,7],["fixed"=>[5,9]],[]],5=>7],":",$saved===[4=>8,"tree"=>[[44,7],[2,7],["fixed"=>[5,9]],[]],5=>7],";";
unset($seed,$leaf,$row,$outside,$before,$tail,$it,$out,$saved);
echo "U:",isset($row),":",isset($outside),":",isset($out),";";
''',
    'array-traversable-nested-cache-generator-value': b'''<?php
function nested_cache_values($local) {
    echo "B;";unset($GLOBALS["it"]);
    yield "first"=>$local;
    echo "N;";$local[0][0]=44;
    yield "second"=>$local;
    echo "F;";
}
$seed=2;$leaf=[$seed++,7];$row=[$leaf,$leaf,["fixed"=>[5,9]],[]];
$tail=7;$it=nested_cache_values($row);
echo "P;";
$out=[4=>8,...$it,$tail++];
$saved=$out;$out["first"][1][1]=66;$out["second"][0][1]=88;
echo "R:",$out["first"][0][0],":",$out["first"][1][1],":",$out["second"][0][0],":",$out["second"][0][1],":",$saved["first"][1][1],":",$saved["second"][0][1],":",$row[0][0],":",$leaf[0],":",$out["second"][2]["fixed"][1],":",$out["second"][3]===[],":",$seed,":",$tail,":",isset($it),";";
echo "O:",$out===[4=>8,"first"=>[[2,7],[2,66],["fixed"=>[5,9]],[]],"second"=>[[44,88],[2,7],["fixed"=>[5,9]],[]],5=>7],":",$saved===[4=>8,"first"=>[[2,7],[2,7],["fixed"=>[5,9]],[]],"second"=>[[44,7],[2,7],["fixed"=>[5,9]],[]],5=>7],";";
unset($seed,$leaf,$row,$tail,$out,$saved);
echo "U:",isset($it),":",isset($row),":",isset($out),";";
''',
}
