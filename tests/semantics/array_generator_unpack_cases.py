"""Native Generator array spreads: real resumes, copied values and final DATA."""

CASES = {
    'array-generator-unpack-value-cow-keys': b'''<?php
function array_spread_values($local) {
    echo "B;";
    yield "8" => $local;
    echo "N1;";$local[0]=44;
    yield "slot" => $local;
    echo "N2;";yield "08" => $local;
    echo "F;";
}
$seed=2;$row=[$seed++,7];$tail=7;
echo "P;";
$out=["slot"=>9,4=>88,...array_spread_values($row),$tail++];
$copy=$out;$out[5][1]=55;$out["slot"][0]=66;
echo "R:",$out["slot"][0],":",$out["slot"][1],":",$out[4],":",$out[5][0],":",$out[5][1],":",$out[6],":",$out["08"][0],":",$copy["slot"][0],":",$copy[5][1],":",$row[0],":",$row[1],":",$seed,":",$tail,";";
echo "O:",$out===["slot"=>[66,7],4=>88,5=>[2,55],"08"=>[44,7],6=>7],":",$copy===["slot"=>[44,7],4=>88,5=>[2,7],"08"=>[44,7],6=>7],";";
unset($seed,$row,$tail,$out,$copy);
echo "U:",isset($row),":",isset($out),";";
''',
    'array-generator-unpack-reference-current': b'''<?php
function &array_spread_refs() {
    global $row;
    echo "B;";unset($GLOBALS["it"]);
    yield "answer" => $row;
    echo "N;";$row[0]=44;unset($GLOBALS["row"]);$GLOBALS["row"]=[88,7];
    yield "again" => $row;
    echo "F;";
}
$seed=2;$row=[$seed++,7];$before=$row;$outside=&$row;$tail=7;$it=array_spread_refs();
echo "P;";
$out=["answer"=>9,4=>88,...$it,$tail++];
$seen=$out["answer"][0];$outside[1]=66;$out["answer"][0]=55;
echo "R:",$seen,":",$out["answer"][0],":",$out["answer"][1],":",$out["again"][0],":",$out["again"][1],":",$outside[0],":",$outside[1],":",$before[0],":",$before[1],":",$row[0],":",$row[1],":",$seed,":",$tail,":",isset($it),";";
echo "O:",$out===["answer"=>[55,7],4=>88,"again"=>[44,7],5=>7],";";
unset($seed,$row,$before,$outside,$tail,$out,$seen);
echo "U:",isset($it),":",isset($row),":",isset($outside),";";
''',
    'array-generator-unpack-last-data-finally': b'''<?php
function array_spread_bad_finally() {
    global $row;
    echo "B;";unset($GLOBALS["it"]);
    try {yield 0 => $row;echo "N;";yield true => $row;echo "L;";}
    finally {echo "F;";$row[0]=44;$GLOBALS["closed"]=33;}
}
$seed=2;$row=[$seed++,7];$closed=0;$later=7;$dest=99;$it=array_spread_bad_finally();
echo "P;";
try {
    $dest=[8,...$it,$later++];
} catch (Error $e) {
    echo "E:",$e->getMessage(),":",$e->getLine(),":",$e->getPrevious()===null,";";
}
echo "R:",$closed,":",$row[0],":",$row[1],":",$dest===99,":",$later,":",isset($it),";";
unset($e,$seed,$row,$closed,$later,$dest);
echo "U:",isset($it),":",isset($row),":",isset($e),";";
''',
}
