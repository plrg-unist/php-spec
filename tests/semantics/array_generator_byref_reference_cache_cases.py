"""By-reference Generator spread caches with a distinct outer cell and inner aliases."""

CASES = {
    'array-generator-byref-reference-cache-rebound': b'''<?php
function &byref_cache_values() {
    global $row;
    echo "B;";unset($GLOBALS["it"]);
    try {
        yield "ref"=>$row;
        echo "N;";$GLOBALS["leaf"]=3;
        $GLOBALS["row"]=[&$GLOBALS["other"],19];$GLOBALS["other"]=11;
    } finally {echo "F;";}
}
$leaf=2;$other=9;$row=[&$leaf,7];$hold=&$leaf;
$it=byref_cache_values();$watch=WeakReference::create($it);
echo "P:",$watch->get()===$it,";";
$out=[4=>8,...$it,9];
echo "D:",$watch->get()===null,":",isset($it),";";
echo "S:",$out["ref"][0],":",$row[0],":",$leaf,":",$other,":",$out["ref"][1],":",$row[1],";";
$out["ref"][1]=88;$hold=44;$other=66;
echo "R:",$out["ref"][0],":",$row[0],":",$leaf,":",$other,":",$out["ref"][1],":",$row[1],";";
unset($out,$row,$leaf,$hold,$other,$watch);
echo "U:",isset($it),":",isset($out),":",isset($row),":",isset($leaf),":",isset($hold),";";
''',
    'array-generator-byref-reference-cache-dropped': b'''<?php
function &byref_cache_values() {
    global $row;
    echo "B;";unset($GLOBALS["it"]);
    try {
        yield "ref"=>$row;
        echo "N;";$GLOBALS["row"]=[&$GLOBALS["other"],19];
    } finally {echo "F;";}
}
$leaf=2;$other=9;$row=[&$leaf,7];$it=byref_cache_values();
echo "P;";
$out=[4=>8,...$it,9];$saved=$out["ref"];
echo "S:",$out["ref"][0],":",$row[0],":",$leaf,":",$other,";";
unset($leaf);$out["ref"][1]=88;$saved[0]=44;
echo "R:",$out["ref"][0],":",$saved[0],":",$row[0],":",$out["ref"][1],":",$saved[1],":",$row[1],";";
unset($out,$saved,$row,$other);
echo "U:",isset($it),":",isset($out),":",isset($saved),":",isset($row),":",isset($leaf),";";
''',
    'array-generator-byref-reference-cache-body-throw': b'''<?php
function &byref_cache_throw() {
    global $row;
    echo "B;";unset($GLOBALS["it"]);
    try {
        yield "ref"=>$row;
        echo "N;";unset($GLOBALS["row"],$GLOBALS["leaf"]);
        throw $GLOBALS["second"];
    } finally {
        echo "F:",$GLOBALS["watch"]->get()!==null,":",isset($GLOBALS["row"]),":",isset($GLOBALS["leaf"]),";";
    }
}
$leaf=2;$row=[&$leaf,7];$second=new Exception("supplied");$dest=99;$later=7;
$it=byref_cache_throw();$watch=WeakReference::create($it);
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
