"""Flat-array acquired-reference counts after ordinary scalar retargeting."""

CASES = {
    'array-literal-float-ref-array-scalar-normal': b'''<?php
function literal_array_scalar($n,$m,$f,$l) {
    echo "D:",$n,":",$l,";";
    $GLOBALS["q"][0]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=44;
    $GLOBALS["key"]=8.5;$GLOBALS["tail"]=66;$GLOBALS["dest"]=200;return true;
}
$seed=2;$q=[$seed];$outside=&$q;$key=1.5;$tail=7;$dest=100;
set_error_handler("literal_array_scalar",E_DEPRECATED);
$dest=[
0=>9,
$key=>&$q,
4=>$tail
];
restore_error_handler();$q=55;
echo "R:",$dest[0],":",$dest[1],":",$dest[4],":",$q,":",$outside[0],":",$key,";";
$probe=[&$outside];unset($outside,$q);$copy=$probe;$copy[0][0]=55;
echo "G:",$probe[0][0],":",$copy[0][0],":",$dest[1],";";
$direct=$probe[0];$probe[0][0]=66;
echo "C:",$probe[0][0],":",$copy[0][0],":",$direct[0],";";
unset($probe,$copy,$direct,$dest,$key);
echo "U:",isset($q),":",isset($outside),":",isset($dest),";";
''',
    'array-literal-float-ref-array-scalar-throw': b'''<?php
function literal_array_scalar_throw($n,$m,$f,$l) {
    echo "D:",$n,":",$l,";";
    $GLOBALS["q"][0]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=44;
    $GLOBALS["key"]=8.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];
}
$seed=2;$q=[$seed];$outside=&$q;$key=1.5;$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_array_scalar_throw",E_DEPRECATED);
try {
$dest=[
0=>8,
1=>&$outside,
$key=>&$q,
2=>$later++
];
} catch (Throwable $e) {echo "C:",($e===$second),":",($e->getPrevious()===NULL),":",$dest,":",$later,";";}
restore_error_handler();
echo "R:",$q,":",$outside[0],":",$dest,":",$later,";";
$probe=[&$outside];unset($outside,$q);$copy=$probe;$copy[0][0]=55;
echo "G:",$probe[0][0],":",$copy[0][0],":",$dest,":",$later,";";
$direct=$probe[0];$probe[0][0]=66;
echo "B:",$probe[0][0],":",$copy[0][0],":",$direct[0],";";
unset($probe,$copy,$direct,$key,$second,$e);
echo "U:",isset($q),":",isset($outside),":",isset($probe),";";
''',
}
