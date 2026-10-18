"""Wrapper debt, child-table COW and thrown insertion use distinct owners."""

CASES = {
    'array-literal-ref-arrays-review-delete-child-cow': b'''<?php
function literal_arrays_peer_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"][0]=33;unset($GLOBALS["q"]);
        $GLOBALS["q"]=&$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=200;
    } else {
        unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    }
    return true;
}
error_reporting(0);$old_seed=2;$new_seed=44;
$q=[$old_seed];$outside=&$q;$replacement=[$new_seed];
$key=-2.75;$dest=100;$calls=0;
set_error_handler("literal_arrays_peer_delete",E_DEPRECATED);
$dest=[
0=>9,
$key=>&$q
];
restore_error_handler();unset($dest[-2]);
$probe=[&$replacement];unset($q);$copy=$probe;$copy[0][0]=55;
echo "R:",$dest[0],":",isset($dest[-2]),":",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",$outside[0],";";
$direct=$replacement;$probe[0][0]=66;
echo "M:",$direct[0],":",$replacement[0],":",$probe[0][0],":",$copy[0][0],";";
$q=&$replacement;$key=3.5;
set_error_handler("literal_arrays_peer_delete",E_DEPRECATED);
$balance=[$key=>&$q];
restore_error_handler();$shared=$probe;$shared[0][0]=77;
echo "B:",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",$direct[0],":",$outside[0],":",$q[0],":",$balance[3][0],":",$calls,";";
unset($dest,$probe,$copy,$direct,$shared,$balance,$q,$replacement,$outside,$key,$old_seed,$new_seed);
echo "U:",isset($dest),":",isset($q),":",isset($replacement),";";
''',
    'array-literal-ref-arrays-review-supplied-throw': b'''<?php
function literal_arrays_peer_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"][0]=33;unset($GLOBALS["q"]);
        $GLOBALS["q"]=&$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;
        throw $GLOBALS["second"];
    }
    unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    return true;
}
error_reporting(0);$old_seed=2;$new_seed=44;
$q=[$old_seed];$outside=&$q;$replacement=[$new_seed];
$key=1.5;$dest=100;$later=7;$calls=0;$second=new Exception("arrays-peer");
set_error_handler("literal_arrays_peer_throw",E_DEPRECATED);
try {
    $dest=[
    0=>8,
    1=>&$outside,
    $key=>&$q,
    2=>$later++
    ];
    echo "BAD;";
} catch (Exception $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===NULL),":",$dest,":",$later,":",$q[0],":",$outside[0],";";
} finally {echo "F;";}
restore_error_handler();$probe=[&$replacement];unset($q);$copy=$probe;$copy[0][0]=55;
echo "R:",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",$outside[0],";";
$q=&$replacement;$key=3.5;
set_error_handler("literal_arrays_peer_throw",E_DEPRECATED);
$balance=[$key=>&$q];
restore_error_handler();$shared=$probe;$shared[0][0]=77;
echo "B:",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",$outside[0],":",$q[0],":",$balance[3][0],":",$dest,":",$later,":",$calls,";";
unset($probe,$copy,$shared,$balance,$q,$replacement,$outside,$key,$old_seed,$new_seed,$e,$second);
echo "U:",isset($q),":",isset($replacement),":",isset($outside),";";
''',
}
