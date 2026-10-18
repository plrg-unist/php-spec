"""Finite lossy-float array-literal keys enter real deprecation callbacks."""

CASES = {
    'array-literal-float-key-live-cv': b'''<?php
function array_literal_float_live($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 1.5 to int loses precision"),":",$l,":",$GLOBALS["value"],";";
    $GLOBALS["value"]=33;$GLOBALS["key"]=9.5;$GLOBALS["next"]=4;$GLOBALS["tail"]=44;$GLOBALS["dest"]=99;
    return true;
}
$key=1.5;$value=20;$next=2;$tail=30;$dest=100;$calls=0;
set_error_handler("array_literal_float_live",E_DEPRECATED);
$dest=[
$key=>$value,
$next=>$tail
];
restore_error_handler();
echo "R:",$dest[1],":",$dest[4],":",($dest===[1=>33,4=>44]),":",$value,":",$key,":",$next,":",$calls,";";
$copy=$dest;$copy[1]=77;
echo "C:",$dest[1],":",$copy[1],";";
unset($dest,$copy,$key,$value,$next,$tail);
echo "U:",isset($dest),":",isset($copy),";";
''',
    'array-literal-float-key-duplicate': b'''<?php
function array_literal_float_duplicate($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 1.5 to int loses precision"),":",$l,":",$GLOBALS["q"],";";
    $GLOBALS["q"]=33;$GLOBALS["value"]=44;
    unset($GLOBALS["q"]);$GLOBALS["q"]=55;
    $GLOBALS["key"]=9.5;$GLOBALS["next"]=4;$GLOBALS["tail"]=66;
    return true;
}
$key=1.5;$q=2;$old=&$q;$value=7;$next=3;$tail=8;$dest=100;$calls=0;
set_error_handler("array_literal_float_duplicate",E_DEPRECATED);
$dest=[
0=>10,
1=>&$q,
2=>12,
$key=>$value,
$next=>$tail
];
restore_error_handler();
echo "R:",$dest[1],":",($dest===[0=>10,1=>44,2=>12,4=>66]),":",$old,":",$q,":",$value,":",$calls,";";
$copy=$dest;$copy[1]=77;
echo "C:",$dest[1],":",$copy[1],":",$old,":",$q,";";
unset($dest,$copy,$q,$old,$key,$value,$next,$tail);
''',
    'array-literal-float-key-supplied-throw': b'''<?php
function array_literal_float_throw($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Implicit conversion from float 1.5 to int loses precision"),":",$l,":",$GLOBALS["q"],":",$GLOBALS["r"],";";
    $GLOBALS["q"]=33;$GLOBALS["r"]=44;$GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;
    unset($GLOBALS["q"],$GLOBALS["r"],$GLOBALS["key"]);
    throw $GLOBALS["second"];
}
$second=new Exception("kept");$key=1.5;$q=2;$r=3;$later=7;$dest=100;
set_error_handler("array_literal_float_throw",E_DEPRECATED);
try {
    $dest=[
    1=>[0=>&$q],
    $key=>[1=>&$r],
    2=>$later++
    ];
} catch (Throwable $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===null),":",$dest,":",$later,";";
} finally {echo "F;";}
restore_error_handler();
echo "U:",isset($q),":",isset($r),":",isset($key),";";
''',
}
