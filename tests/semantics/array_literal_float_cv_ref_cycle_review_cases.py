"""Cross-family table/CELL biases survive deletion and supplied throw."""

CASES = {
    'array-literal-cv-ref-cycle-review-delete-entry': b'''<?php
function literal_cv_ref_cycle_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][1]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {unset($GLOBALS["q"]);$GLOBALS["q"]=$GLOBALS["old_hold"];}
    $GLOBALS["key"]=9.5;return true;
}
$old_seed=2;$q=[$old_seed,7];$old_hold=$q;
$new_seed=44;$replacement=[$new_seed,8];$key=-2.75;$calls=0;
set_error_handler("literal_cv_ref_cycle_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>$q
];
unset($a[-2]);$probe=[&$q];unset($q);$snapshot=$replacement;
$copy=$probe;$copy[0][0]=55;$copy[0][1]=88;
$replacement[0]=66;$replacement[1]=66;
echo "R:",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",$snapshot[0],":",$replacement[1],":",$probe[0][1],":",$copy[0][1],":",$old_hold[0],":",$old_hold[1],":",isset($q),":",isset($a[-2]),":",$calls,";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0]=77;$shared[0][1]=99;$q[0]=88;$q[1]=99;
echo "B:",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",$snapshot[0],":",$replacement[1],":",$probe[0][1],":",$shared[0][1],":",$copy[0][1],":",$q[0],":",$balance[3][0],":",$old_hold[0],":",$q[1],":",$balance[3][1],":",$old_hold[1],":",$calls,";";
unset($a,$probe,$copy,$shared,$replacement,$q,$old_hold,$balance,$snapshot,$key);
echo "U:",isset($q),":",isset($replacement),":",isset($a),":",isset($balance),";";
''',
    'array-literal-cv-ref-cycle-review-supplied-throw': b'''<?php
function literal_cv_ref_cycle_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][1]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];$GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];}
    unset($GLOBALS["q"]);$GLOBALS["q"]=$GLOBALS["old_hold"];$GLOBALS["key"]=9.5;return true;
}
$old_seed=2;$q=[$old_seed,7];$old_hold=$q;
$new_seed=44;$replacement=[$new_seed,8];$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_cv_ref_cycle_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    1=>$old_hold,
    $key=>$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
unset($e);$probe=[&$q];unset($q);$snapshot=$replacement;
$copy=$probe;$copy[0][0]=55;$copy[0][1]=88;$replacement[0]=66;$replacement[1]=66;
echo "R:",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",$snapshot[0],":",$replacement[1],":",$copy[0][1],":",$old_hold[0],":",$old_hold[1],":",isset($q),":",$dest,":",$later,":",$calls,";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0]=77;$shared[0][1]=99;$q[0]=88;$q[1]=99;
echo "B:",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",$snapshot[0],":",$replacement[1],":",$copy[0][1],":",$q[0],":",$balance[3][0],":",$old_hold[0],":",$q[1],":",$balance[3][1],":",$old_hold[1],":",$dest,":",$later,":",$calls,";";
unset($probe,$copy,$shared,$replacement,$q,$old_hold,$balance,$snapshot,$key,$second);
echo "U:",isset($q),":",isset($replacement),":",isset($balance),":",isset($e),";";
''',
}
