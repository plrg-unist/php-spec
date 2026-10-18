"""String leaves retain wrapper deficits through deletion and supplied throws."""

CASES = {
    'array-literal-string-leaf-review-delete-entry': b'''<?php
function literal_string_leaf_peer_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
error_reporting(0);$old_seed="old";$new_seed="new";
$q=[$old_seed];$outside=&$q;$replacement=[$new_seed];$key=-2.75;$calls=0;
set_error_handler("literal_string_leaf_peer_delete",E_DEPRECATED);
$a=[
0=>8,
$key=>&$q
];
unset($a[-2]);$probe=[&$q];unset($q);
$snapshot=$replacement[0];$copy=$probe;$copy[0][0][0]="X";
$replacement[0][0]="N";
echo "R:",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",$snapshot,":",$outside[0],":",isset($q),":",$calls,";";
$q=&$replacement;$key=3.5;
$b=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0][1]="Y";
echo "B:",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",$snapshot,":",$q[0],":",$b[3][0],":",$calls,";";
unset($a,$b,$q,$outside,$replacement,$probe,$copy,$shared,$snapshot,$key,$old_seed,$new_seed,$calls);
echo "U:",isset($q),":",isset($replacement),":",isset($probe),":",isset($b),";";
''',
    'array-literal-string-leaf-review-supplied-throw': b'''<?php
function literal_string_leaf_peer_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"]=&$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];
    }
    $GLOBALS["q"]=&$GLOBALS["outside"];$GLOBALS["key"]=9.5;return true;
}
error_reporting(0);$old_seed="old";$new_seed="new";
$q=[$old_seed];$outside=&$q;$replacement=[$new_seed];$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_string_leaf_peer_throw",E_DEPRECATED);
try {
$dest=[
0=>8,
1=>&$outside,
$key=>&$q,
4=>$later++
];
} catch (Throwable $e) {echo "C:",($e===$second),":",($e->getPrevious()===NULL),":",$dest,":",$later,";";}
$probe=[&$q];unset($q);
$snapshot=$replacement[0];$copy=$probe;$copy[0][0][0]="X";
$replacement[0][0]="N";
echo "R:",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",$snapshot,":",$outside[0],":",isset($q),":",$dest,":",$later,":",$calls,";";
$q=&$replacement;$key=3.5;
$b=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0][1]="Y";
echo "B:",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",$snapshot,":",$q[0],":",$b[3][0],":",$dest,":",$later,":",$calls,";";
unset($b,$q,$outside,$replacement,$probe,$copy,$shared,$snapshot,$key,$old_seed,$new_seed,$calls,$dest,$later,$second,$e);
echo "U:",isset($q),":",isset($replacement),":",isset($probe),":",isset($e),";";
''',
}
