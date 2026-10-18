"""Reference-element retargeting: retained old owner and same-cell transfer."""

CASES = {
    'array-literal-float-ref-review-scalar-retarget': b'''<?php
function literal_float_ref_peer_scalar($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float -2.75 to int loses precision"),":",$l,":",($GLOBALS["dest"]===100),";";
    $GLOBALS["q"]=33;unset($GLOBALS["q"],$GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["q"]=44;$GLOBALS["key"]=9.5;
    $GLOBALS["next"]=4;$GLOBALS["tail"]=66;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(0);$q=2;$outside=&$q;$key=-2.75;$key_alias=&$key;
$next=1;$tail=8;$dest=100;$calls=0;
set_error_handler("literal_float_ref_peer_scalar",E_DEPRECATED);
$dest=[
0=>9,
$key=>&$q,
$next=>$tail
];
restore_error_handler();
echo "R:",$dest[0],":",$dest[-2],":",$dest[4],":",$outside,":",$q,":",$key,":",isset($dest[9]),":",$calls,";";
$q=55;$copy=$dest;$copy[-2]=88;
echo "A:",$dest[-2],":",$copy[-2],":",$q,":",$outside,";";
$probe=[&$outside];unset($outside);$probe_copy=$probe;$probe_copy[0]=77;
echo "G:",$probe[0],":",$probe_copy[0],":",$dest[-2],":",$q,";";
unset($dest,$copy,$q,$key,$next,$tail,$probe,$probe_copy);
echo "U:",isset($dest),":",isset($q),":",isset($outside),":",isset($key_alias),";";
''',
    'array-literal-float-ref-review-same-cell-rebind': b'''<?php
function literal_float_ref_peer_same($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Implicit conversion from float 1.5 to int loses precision"),":",$l,";";
    $GLOBALS["q"]=33;unset($GLOBALS["q"]);
    $GLOBALS["q"]=&$GLOBALS["outside"];
    $GLOBALS["key"]=9.5;$GLOBALS["next"]=4;$GLOBALS["tail"]=66;
    return true;
}
error_reporting(0);$q=2;$outside=&$q;$key=1.5;$next=2;$tail=8;
set_error_handler("literal_float_ref_peer_same",E_DEPRECATED);
$dest=[
0=>9,
$key=>&$q,
$next=>$tail
];
restore_error_handler();
echo "R:",$dest[1],":",$q,":",$outside,":",$dest[4],":",isset($dest[9]),";";
unset($q,$outside);$copy=$dest;$copy[1]=55;
echo "A:",$dest[1],":",$copy[1],":",$dest[4],":",$copy[4],";";
$dest[1]=77;
echo "B:",$dest[1],":",$copy[1],";";
unset($dest,$copy,$key,$next,$tail);
echo "U:",isset($dest),":",isset($copy),":",isset($q),":",isset($outside),";";
''',
}

NATIVE_PROBES = {
    'array-literal-float-ref-review-new-cell-deficit': b'''<?php
function literal_float_ref_peer_deficit($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);
        $GLOBALS["q"]=&$GLOBALS["replacement"];
    } else {
        unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    }
    return true;
}
error_reporting(0);$q=2;$outside=&$q;$replacement=44;$key=2.5;$calls=0;
set_error_handler("literal_float_ref_peer_deficit",E_DEPRECATED);
$a=[$key=>&$q];
restore_error_handler();
unset($q);$copy=$a;$copy[2]=55;
echo "R:",$a[2],":",$replacement,":",$copy[2],":",$outside,";";
$q=&$replacement;$key=3.5;
set_error_handler("literal_float_ref_peer_deficit",E_DEPRECATED);
$b=[$key=>&$q];
restore_error_handler();
$balanced_copy=$a;$balanced_copy[2]=77;
echo "B:",$a[2],":",$replacement,":",$copy[2],":",$b[3],":",$q,":",$outside,":",$balanced_copy[2],";";
unset($a,$b,$copy,$balanced_copy,$q,$replacement,$outside,$key);
echo "U:",isset($a),":",isset($q),":",isset($outside),";";
''',
}
