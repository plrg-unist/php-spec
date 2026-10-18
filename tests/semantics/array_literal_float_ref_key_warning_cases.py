"""Reference literal elements retain acquired wrappers across float-key handlers."""

CASES = {
    'array-literal-float-ref-stable': b'''<?php
function literal_float_ref_stable($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 2.5 to int loses precision"),":",$l,";";
    $GLOBALS["q"]=33;$GLOBALS["key"]=9.5;$GLOBALS["next"]=4;$GLOBALS["tail"]=66;$GLOBALS["dest"]=99;
    return true;
}
$q=2;$outside=&$q;$key=2.5;$next=1;$tail=8;$dest=100;$calls=0;
set_error_handler("literal_float_ref_stable",E_DEPRECATED);
$dest=[
0=>9,
$key=>&$q,
$next=>$tail
];
restore_error_handler();
echo "R:",$dest[2],":",$q,":",$outside,":",$dest[4],":",$key,":",$calls,";";
$copy=$dest;$copy[2]=55;
echo "A:",$dest[2],":",$copy[2],":",$q,":",$outside,";";
unset($q,$outside,$copy);
$probe=$dest;$probe[2]=66;
echo "S:",$dest[2],":",$probe[2],";";
unset($dest,$probe,$key,$next,$tail);
''',
    'array-literal-float-ref-scalar-throw': b'''<?php
function literal_float_ref_throw($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Implicit conversion from float 1.5 to int loses precision"),":",$l,":",$GLOBALS["outside"],";";
    $GLOBALS["q"]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=44;
    $GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;
    throw $GLOBALS["second"];
}
$second=new Exception("kept");$q=2;$outside=&$q;$key=1.5;$later=7;$dest=100;
set_error_handler("literal_float_ref_throw",E_DEPRECATED);
try {
    $dest=[
    0=>8,
    1=>&$outside,
    $key=>&$q,
    2=>$later++
    ];
} catch (Throwable $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===null),":",$dest,":",$later,":",$q,":",$outside,";";
} finally {echo "F;";}
restore_error_handler();
$probe=[&$outside];unset($outside);$copy=$probe;$copy[0]=66;
echo "G:",$probe[0],":",$copy[0],":",$q,":",$dest,";";
unset($probe,$copy,$q,$key);
''',
    'array-literal-float-ref-repeated-scalar': b'''<?php
function literal_float_ref_repeat($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 2.5 to int loses precision"),":",$l,":",$GLOBALS["calls"],";";
    $GLOBALS["q"]=30+$GLOBALS["calls"];unset($GLOBALS["q"]);$GLOBALS["q"]=40+$GLOBALS["calls"];
    $GLOBALS["key"]=9.5;
    return true;
}
$q=2;$outside=&$q;$key=2.5;$calls=0;
set_error_handler("literal_float_ref_repeat",E_DEPRECATED);
$first=[
$key=>&$q
];
$q=&$outside;$key=2.5;
$second=[
$key=>&$q
];
restore_error_handler();
echo "R:",$first[2],":",$second[2],":",$q,":",$outside,":",$calls,";";
$probe=[&$outside];unset($outside);$copy=$probe;$copy[0]=66;
echo "G:",$probe[0],":",$copy[0],":",$q,":",$first[2],":",$second[2],";";
unset($first,$second,$probe,$copy,$q,$key);
''',
}
