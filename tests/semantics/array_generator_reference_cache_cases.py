"""By-value Generator spread caches with embedded scalar references."""

CASES = {
    'array-generator-reference-cache-alias-retained': b'''<?php
function reference_cache_values() {
    echo "B;";unset($GLOBALS["it"]);
    try {
        yield "ref"=>$GLOBALS["row"];
        echo "N;";$GLOBALS["leaf"]=3;
    } finally {echo "F;";}
}
$leaf=2;$row=[&$leaf,7];$it=reference_cache_values();$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$out=[4=>8,...$it,9];
echo "D:",$watch->get()===null,":",isset($it),";";
echo "B:",$out["ref"][0],":",$row[0],":",$leaf,";";
$out["ref"][1]=88;$leaf=44;
echo "R:",$out["ref"][0],":",$row[0],":",$leaf,":",$out["ref"][1],":",$row[1],";";
unset($out,$row,$leaf,$watch);
echo "U:",isset($it),":",isset($out),":",isset($row),":",isset($leaf),";";
''',
    'array-generator-reference-cache-alias-dropped': b'''<?php
function reference_cache_values() {
    echo "B;";unset($GLOBALS["it"]);
    try {
        yield "ref"=>$GLOBALS["row"];
        echo "N;";$GLOBALS["leaf"]=3;
    } finally {echo "F;";}
}
$leaf=2;$row=[&$leaf,7];$it=reference_cache_values();
echo "P;";
$out=[4=>8,...$it,9];
echo "B:",$out["ref"][0],":",$row[0],":",$leaf,";";
unset($leaf);$out["ref"][1]=88;$row[0]=44;
echo "R:",$out["ref"][0],":",$row[0],":",$out["ref"][1],":",$row[1],";";
unset($out,$row);
echo "U:",isset($it),":",isset($out),":",isset($row),":",isset($leaf),";";
''',
    'array-generator-reference-cache-body-throw': b'''<?php
function reference_cache_throw() {
    echo "B;";unset($GLOBALS["it"]);
    try {
        yield "ref"=>$GLOBALS["row"];
        echo "N;";
        unset($GLOBALS["row"],$GLOBALS["leaf"]);
        throw $GLOBALS["second"];
    } finally {
        echo "F:",$GLOBALS["watch"]->get()!==null,":",isset($GLOBALS["row"]),":",isset($GLOBALS["leaf"]),";";
    }
}
$leaf=2;$row=[&$leaf,7];$second=new Exception("supplied");$dest=99;$later=7;
$it=reference_cache_throw();$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
try {
    $dest=[4=>8,...$it,$later++];echo "L;";
} catch (Exception $e) {
    echo "C:",$e===$second,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$dest===99,":",$later,":",$watch->get()===null,";";
}
unset($e,$second,$dest,$later,$watch);
echo "U:",isset($it),":",isset($row),":",isset($leaf),":",isset($second),";";
''',
}
