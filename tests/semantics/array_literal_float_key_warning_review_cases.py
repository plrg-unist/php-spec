"""Array-literal float keys: temporary array retention and reference identity."""

CASES = {
    'array-literal-float-review-inner-array': b'''<?php
function literal_float_peer_inner($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float -2.75 to int loses precision"),":",$l,":",($GLOBALS["dest"]===100),";";
    $GLOBALS["q"]=33;
    unset($GLOBALS["q"],$GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["q"]=&$GLOBALS["new_q"];$GLOBALS["key"]=&$GLOBALS["new_key"];
    $GLOBALS["next"]=4;$GLOBALS["tail"]=66;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(0);$q=2;$new_q=44;$key=-2.75;$key_alias=&$key;$new_key=9.5;
$next=1;$tail=8;$dest=100;$calls=0;
set_error_handler("literal_float_peer_inner",E_ALL);
$dest=[
0=>9,
$key=>[0=>&$q],
$next=>$tail
];
restore_error_handler();
echo "R:",$dest[0],":",$dest[-2][0],":",$dest[4],":",$q,":",$key,":",isset($dest[9]),":",$calls,";";
$dest[-2][0]=55;
echo "A:",$dest[-2][0],":",$q,":",$new_q,":",$tail,";";
unset($dest,$q,$new_q,$key,$new_key,$next,$tail);
echo "U:",isset($dest),":",isset($q),":",isset($key_alias),";";
''',
    'array-literal-float-review-reference-entry': b'''<?php
function literal_float_peer_reference($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 2.5 to int loses precision"),":",$l,":",($GLOBALS["dest"]===100),";";
    $GLOBALS["q"]=33;unset($GLOBALS["q"]);
    $GLOBALS["q"]=&$GLOBALS["new_q"];
    $GLOBALS["key"]=7.5;$GLOBALS["next"]=3;$GLOBALS["tail"]=66;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(0);$q=2;$outside=&$q;$new_q=44;$key=2.5;
$next=1;$tail=8;$dest=100;$calls=0;
set_error_handler("literal_float_peer_reference",E_ALL);
$dest=[
0=>9,
$key=>&$q,
$next=>$tail
];
restore_error_handler();
echo "R:",$dest[0],":",$dest[2],":",$dest[3],":",$outside,":",$q,":",$key,":",$calls,";";
$copy=$dest;$copy[2]=55;
echo "A:",$dest[2],":",$copy[2],":",$outside,":",$q,":",$new_q,";";
$q=77;
echo "B:",$dest[2],":",$copy[2],":",$outside,":",$q,";";
unset($dest,$copy,$q,$outside,$new_q,$key,$next,$tail);
echo "U:",isset($dest),":",isset($copy),":",isset($outside),";";
''',
}

BOUNDARIES = {
    'array-literal-float-review-reference-entry': 'array literal reference deficit lifetime',
}

NATIVE_PROBES = {
    'array-literal-float-review-reference-owner-probe': b'''<?php
function literal_float_owner_probe($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Implicit conversion from float 2.5 to int loses precision"),":",$l,";";
    $GLOBALS["q"]=33;unset($GLOBALS["q"]);
    $GLOBALS["q"]=&$GLOBALS["replacement"];
    return true;
}
$q=2;$outside=&$q;$replacement=44;$key=2.5;
set_error_handler("literal_float_owner_probe",E_DEPRECATED);
$a=[$key=>&$q];
restore_error_handler();
$probe=[&$outside];unset($outside);$copy=$probe;$copy[0]=66;
echo "R:",$a[2],":",$q,":",$replacement,":",$probe[0],":",$copy[0],";";
unset($a,$q,$replacement,$key,$probe,$copy);
echo "U:",isset($a),":",isset($q),":",isset($probe),";";
''',
}
