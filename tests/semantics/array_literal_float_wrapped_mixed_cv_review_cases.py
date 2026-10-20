"""Borrowed primitive payloads become array tables before deletion or throw."""

CASES = {
    'array-literal-wrapped-mixed-cv-review-delete-entry': b'''<?php
function literal_wrapped_mixed_cv_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["outside"]=$GLOBALS["replacement"];}
    else {$GLOBALS["outside"]=null;}
    $GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;return true;
}
$q=false;$outside=&$q;$initial=$q;
$next=44;$replacement=[$next,8];$unrelated=99;$key=-2.75;$calls=0;
set_error_handler("literal_wrapped_mixed_cv_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>$q
];
unset($a[-2]);$outside[0]=55;$outside[1]=66;
$copy=$replacement;$copy[0]=66;$copy[1]=88;
echo "R:",$outside[0],":",$replacement[0],":",$copy[0],":",$outside[1],":",$replacement[1],":",$copy[1],":",$q,":",$initial===false,":",isset($a[-2]),":",$calls,";";
$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$replacement[0]=77;$shared=$replacement;$shared[0]=88;$shared[1]=99;$outside=77;
echo "B:",$replacement[0],":",$shared[0],":",$copy[0],":",$replacement[1],":",$shared[1],":",$copy[1],":",$outside,":",$balance[3]===null,":",$q,":",$unrelated,":",$calls,";";
unset($a,$copy,$shared,$replacement,$q,$outside,$balance,$key,$unrelated);
echo "U:",isset($q),":",isset($outside),":",isset($replacement),":",isset($a),":",isset($balance),";";
''',
    'array-literal-wrapped-mixed-cv-review-supplied-throw': b'''<?php
function literal_wrapped_mixed_cv_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["outside"]=$GLOBALS["replacement"];$GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];}
    $GLOBALS["outside"]=44;$GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;return true;
}
$q=2.5;$outside=&$q;$initial=$q;
$next=44;$replacement=[$next,8];$unrelated=99;$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_wrapped_mixed_cv_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    1=>8,
    $key=>$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
unset($e);$outside[0]=55;$outside[1]=66;$copy=$replacement;$copy[0]=66;$copy[1]=88;
echo "R:",$outside[0],":",$replacement[0],":",$copy[0],":",$outside[1],":",$replacement[1],":",$copy[1],":",$q,":",$initial===2.5,":",$dest,":",$later,":",$calls,";";
$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$replacement[0]=77;$shared=$replacement;$shared[0]=88;$shared[1]=99;$outside=77;
echo "B:",$replacement[0],":",$shared[0],":",$copy[0],":",$replacement[1],":",$shared[1],":",$copy[1],":",$outside,":",$balance[3],":",$q,":",$unrelated,":",$dest,":",$later,":",$calls,";";
unset($copy,$shared,$replacement,$q,$outside,$balance,$key,$unrelated,$second);
echo "U:",isset($q),":",isset($outside),":",isset($replacement),":",isset($balance),":",isset($e),";";
''',
}
