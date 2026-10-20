"""String reference leaves separate leaf aliases, string copies and outer debt."""

CASES = {
    'array-literal-string-alias-review-delete-entry': b'''<?php
function literal_string_alias_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][1]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$old_leaf="old";$q=[&$old_leaf,7];$outside=&$q;unset($old_leaf);
$seed="new";$new_leaf=$seed;$replacement=[&$new_leaf,8];unset($new_leaf);$key=-2.75;$calls=0;
set_error_handler("literal_string_alias_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q
];
unset($a[-2]);$probe=[&$q];unset($q);$snapshot=$replacement[0];
$copy=$probe;$copy[0][0][0]="X";$copy[0][1]=88;
$replacement[0][0]="N";$replacement[1]=66;$mid=$replacement[0];
echo "R:",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",$snapshot,":",$mid,":",$seed,":",$replacement[1],":",$probe[0][1],":",$copy[0][1],":",$outside[0],":",$outside[1],":",isset($q),":",$calls,";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0][1]="Y";$shared[0][1]=99;
echo "B:",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",$snapshot,":",$mid,":",$seed,":",$replacement[1],":",$probe[0][1],":",$shared[0][1],":",$copy[0][1],":",$q[0],":",$balance[3][0],":",$q[1],":",$calls,";";
unset($a,$probe,$copy,$shared,$replacement,$q,$outside,$balance,$snapshot,$mid,$seed,$key);
echo "U:",isset($q),":",isset($replacement),":",isset($old_leaf),":",isset($new_leaf),";";
''',
    'array-literal-string-alias-review-supplied-throw': b'''<?php
function literal_string_alias_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][1]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];$GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];}
    $GLOBALS["q"]=&$GLOBALS["outside"];$GLOBALS["key"]=9.5;return true;
}
$old_leaf="old";$q=[&$old_leaf,7];$outside=&$q;unset($old_leaf);
$seed="new";$new_leaf=$seed;$replacement=[&$new_leaf,8];$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_string_alias_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    1=>&$outside,
    $key=>&$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
$probe=[&$q];unset($q);$snapshot=$replacement[0];
$copy=$probe;$copy[0][0][0]="X";$copy[0][1]=88;
$replacement[0][0]="N";$replacement[1]=66;$mid=$replacement[0];
echo "R:",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",$new_leaf,":",$snapshot,":",$mid,":",$seed,":",$replacement[1],":",$copy[0][1],":",$outside[0],":",$outside[1],":",isset($q),":",$dest,":",$later,":",$calls,";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0][1]="Y";$shared[0][1]=99;
echo "B:",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",$new_leaf,":",$snapshot,":",$mid,":",$seed,":",$replacement[1],":",$copy[0][1],":",$q[0],":",$balance[3][0],":",$q[1],":",$dest,":",$later,":",$calls,";";
unset($probe,$copy,$shared,$replacement,$q,$outside,$balance,$snapshot,$mid,$seed,$key,$new_leaf,$e,$second);
echo "U:",isset($q),":",isset($replacement),":",isset($old_leaf),":",isset($new_leaf),";";
''',
}
