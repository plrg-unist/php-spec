"""Array spread copies Iterator currents after key callbacks and dereferencing."""

CASES = {
    'array-iterator-unpack-value-cow-keys': b'''<?php
class ArraySpreadValue implements Iterator {
    public function rewind(): void {echo "W;";$GLOBALS["i"]=0;unset($GLOBALS["it"]);}
    public function valid(): bool {echo "V:",$GLOBALS["i"],";";return $GLOBALS["i"]<3;}
    public function current(): mixed {echo "C:",$GLOBALS["i"],";";return $GLOBALS["row"];}
    public function key(): mixed {echo "K:",$GLOBALS["i"],";";if ($GLOBALS["i"]===0) {$GLOBALS["row"][0]=44;return "8";}if ($GLOBALS["i"]===1) {return "slot";}return "08";}
    public function next(): void {echo "N:",$GLOBALS["i"],";";$GLOBALS["i"]++;}
}
$seed=2;$row=[$seed++,7];$i=99;$tail=7;$it=new ArraySpreadValue();
echo "P;";
$out=["slot"=>9,4=>88,...$it,$tail++];
$copy=$out;$out[5][1]=55;$out["slot"][0]=66;
echo "R:",$out["slot"][0],":",$out["slot"][1],":",$out[4],":",$out[5][0],":",$out[5][1],":",$out[6],":",$out["08"][0],":",$copy["slot"][0],":",$copy[5][1],":",$row[0],":",$row[1],":",$seed,":",$tail,":",isset($it),";";
echo "O:",$out===["slot"=>[66,7],4=>88,5=>[2,55],"08"=>[44,7],6=>7],":",$copy===["slot"=>[44,7],4=>88,5=>[2,7],"08"=>[44,7],6=>7],";";
unset($seed,$row,$i,$tail,$out,$copy);
echo "U:",isset($it),":",isset($row),":",isset($out),";";
''',
    'array-iterator-unpack-reference-current': b'''<?php
class ArraySpreadReference implements Iterator {
    public function rewind(): void {echo "W;";$GLOBALS["i"]=0;unset($GLOBALS["it"]);}
    public function valid(): bool {echo "V:",$GLOBALS["i"],";";return $GLOBALS["i"]<1;}
    public function &current(): mixed {global $row;echo "C;";return $row;}
    public function key(): mixed {echo "K;";$GLOBALS["outside"][0]=44;unset($GLOBALS["row"]);$GLOBALS["row"]=[88,7];return "answer";}
    public function next(): void {echo "N;";$GLOBALS["i"]++;}
}
$seed=2;$row=[$seed++,7];$before=$row;$outside=&$row;$i=99;$tail=7;$it=new ArraySpreadReference();
echo "P;";
$out=["answer"=>9,4=>88,...$it,$tail++];
$seen=$out["answer"][0];$outside[1]=66;$out["answer"][0]=55;
echo "R:",$seen,":",$out["answer"][0],":",$out["answer"][1],":",$out[4],":",$out[5],":",$outside[0],":",$outside[1],":",$before[0],":",$before[1],":",$row[0],":",$row[1],":",$seed,":",$tail,":",isset($it),";";
echo "O:",$out===["answer"=>[55,7],4=>88,5=>7],";";
unset($seed,$row,$before,$outside,$i,$tail,$out,$seen);
echo "U:",isset($it),":",isset($row),":",isset($outside),";";
''',
}
