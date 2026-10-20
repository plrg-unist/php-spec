"""Captured reference payloads retain table deficits after deletion or throw."""

CASES = {
    'array-literal-wrapped-array-cv-review-delete-entry': b'''<?php
function literal_wrapped_array_cv_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["outside"]=$GLOBALS["replacement"];}
    else {$GLOBALS["outside"]=$GLOBALS["old_hold"];}
    $GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;return true;
}
$seed=2;$q=[$seed,7];$outside=&$q;$old_hold=$q;
$next=44;$replacement=[$next,8];$unrelated=99;$key=-2.75;$calls=0;
set_error_handler("literal_wrapped_array_cv_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>$q
];
unset($a[-2]);$outside[0]=55;$outside[1]=66;
$copy=$replacement;$copy[0]=66;$copy[1]=88;
echo "R:",$outside[0],":",$replacement[0],":",$copy[0],":",$outside[1],":",$replacement[1],":",$copy[1],":",$q,":",$old_hold[0],":",$old_hold[1],":",isset($a[-2]),":",$calls,";";
$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$replacement[0]=77;$shared=$replacement;$shared[0]=88;$shared[1]=99;$outside[0]=99;$outside[1]=99;
echo "B:",$replacement[0],":",$shared[0],":",$copy[0],":",$replacement[1],":",$shared[1],":",$copy[1],":",$outside[0],":",$balance[3][0],":",$old_hold[0],":",$outside[1],":",$balance[3][1],":",$old_hold[1],":",$q,":",$unrelated,":",$calls,";";
unset($a,$copy,$shared,$replacement,$q,$outside,$old_hold,$balance,$key,$unrelated);
echo "U:",isset($q),":",isset($outside),":",isset($replacement),":",isset($a),":",isset($balance),";";
''',
    'array-literal-wrapped-array-cv-review-supplied-throw': b'''<?php
function literal_wrapped_array_cv_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["outside"]=$GLOBALS["replacement"];$GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];}
    $GLOBALS["outside"]=$GLOBALS["old_hold"];$GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;return true;
}
$seed=2;$q=[$seed,7];$outside=&$q;$old_hold=$q;
$next=44;$replacement=[$next,8];$unrelated=99;$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_wrapped_array_cv_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    1=>$old_hold,
    $key=>$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
unset($e);$outside[0]=55;$outside[1]=66;$copy=$replacement;$copy[0]=66;$copy[1]=88;
echo "R:",$outside[0],":",$replacement[0],":",$copy[0],":",$outside[1],":",$replacement[1],":",$copy[1],":",$q,":",$old_hold[0],":",$old_hold[1],":",$dest,":",$later,":",$calls,";";
$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$replacement[0]=77;$shared=$replacement;$shared[0]=88;$shared[1]=99;$outside[0]=99;$outside[1]=99;
echo "B:",$replacement[0],":",$shared[0],":",$copy[0],":",$replacement[1],":",$shared[1],":",$copy[1],":",$outside[0],":",$balance[3][0],":",$old_hold[0],":",$outside[1],":",$balance[3][1],":",$old_hold[1],":",$q,":",$unrelated,":",$dest,":",$later,":",$calls,";";
unset($copy,$shared,$replacement,$q,$outside,$old_hold,$balance,$key,$unrelated,$second);
echo "U:",isset($q),":",isset($outside),":",isset($replacement),":",isset($balance),":",isset($e),";";
''',
}
