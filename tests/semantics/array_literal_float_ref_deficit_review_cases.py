"""Reference count deficits survive entry removal and abrupt builder cleanup."""

CASES = {
    'array-literal-ref-deficit-review-delete-entry': b'''<?php
function literal_ref_deficit_peer_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);
        $GLOBALS["q"]=&$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=200;
    } else {
        unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    }
    return true;
}
error_reporting(0);$q=2;$outside=&$q;$replacement=44;$key=-2.75;$dest=100;$calls=0;
set_error_handler("literal_ref_deficit_peer_delete",E_DEPRECATED);
$dest=[
0=>9,
$key=>&$q
];
restore_error_handler();
unset($dest[-2]);
$probe=[&$replacement];unset($q);$copy=$probe;$copy[0]=55;
echo "R:",$dest[0],":",isset($dest[-2]),":",$replacement,":",$probe[0],":",$copy[0],":",$outside,";";
$q=&$replacement;$key=3.5;
set_error_handler("literal_ref_deficit_peer_delete",E_DEPRECATED);
$balance=[$key=>&$q];
restore_error_handler();
$balanced_copy=$probe;$balanced_copy[0]=77;
echo "B:",$replacement,":",$probe[0],":",$copy[0],":",$balanced_copy[0],":",$outside,":",$q,":",$balance[3],":",$calls,";";
unset($dest,$probe,$copy,$balanced_copy,$balance,$q,$replacement,$outside,$key);
echo "U:",isset($dest),":",isset($q),":",isset($outside),";";
''',
    'array-literal-ref-deficit-review-supplied-throw': b'''<?php
function literal_ref_deficit_peer_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);
        $GLOBALS["q"]=&$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;
        throw $GLOBALS["second"];
    }
    unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    return true;
}
error_reporting(0);$second=new Exception("kept");$q=2;$outside=&$q;$replacement=44;
$key=1.5;$dest=100;$later=7;$calls=0;
set_error_handler("literal_ref_deficit_peer_throw",E_DEPRECATED);
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
$probe=[&$replacement];unset($q);$copy=$probe;$copy[0]=55;
echo "R:",$replacement,":",$probe[0],":",$copy[0],":",$outside,":",$dest,":",$later,";";
$q=&$replacement;$key=3.5;
set_error_handler("literal_ref_deficit_peer_throw",E_DEPRECATED);
$balance=[$key=>&$q];
restore_error_handler();
$balanced_copy=$probe;$balanced_copy[0]=77;
echo "B:",$replacement,":",$probe[0],":",$copy[0],":",$balanced_copy[0],":",$outside,":",$q,":",$balance[3],":",$calls,";";
unset($probe,$copy,$balanced_copy,$balance,$q,$replacement,$outside,$key);
echo "U:",isset($q),":",isset($outside),":",$dest,":",$later,";";
''',
}
