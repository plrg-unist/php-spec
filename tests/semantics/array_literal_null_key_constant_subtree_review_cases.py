"""Nested constant child graphs survive last-user deletion and supplied throw."""

CASES = {
    'array-literal-null-key-constant-subtree-review-delete-entry': b'''<?php
function literal_null_subtree_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    echo "H:",$GLOBALS["seed"],";";
    $GLOBALS["seed"]=99;$GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$seed=2;$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_subtree_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>[
    "left"=>["deep"=>[[2,8],[3,7]],"empty"=>[]],
    "right"=>[[4,6],[5,9]]
],
4=>$tail
];
restore_error_handler();$copy=$a;
$copy[""]["left"]["deep"][0][0]=66;$copy[""]["right"][1][1]=99;
echo "C:",$a[""]["left"]["deep"][0][0],":",$copy[""]["left"]["deep"][0][0],":",$a[""]["left"]["deep"][0][1],":",$copy[""]["left"]["deep"][0][1],":",$a[""]["left"]["deep"][1][0],":",$copy[""]["left"]["deep"][1][0],":",$a[""]["right"][1][1],":",$copy[""]["right"][1][1],":",$a[""]["right"][0][1],":",$copy[""]["right"][0][1],":",isset($a[""]["left"]["empty"][0]),":",$a[4],":",$seed,":",$calls,";";
unset($copy);unset($a[""]);
echo "R:",isset($a[""]),":",$a[0],":",$a[4],":",$seed,":",$key,":",$calls,":",isset($copy),";";
unset($a,$key,$seed,$tail,$calls);
echo "U:",isset($a),":",isset($copy),":",isset($seed),";";
''',
    'array-literal-null-key-constant-subtree-review-supplied-throw': b'''<?php
function literal_null_subtree_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    echo "H:",$GLOBALS["seed"],";";
    $GLOBALS["seed"]=99;$GLOBALS["key"]=9;$GLOBALS["dest"]=99;throw $GLOBALS["second"];
}
$seed=2;$key=null;$calls=0;$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_null_subtree_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    ""=>8,
    $key=>[[[2,8],[3,7]],[[4,6],[]]],
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
restore_error_handler();unset($e);
echo "R:",$seed,":",$key,":",$calls,":",$dest,":",$later,":",isset($e),";";
unset($key,$seed,$calls,$dest,$later,$second);
echo "U:",isset($seed),":",isset($dest),":",isset($second),";";
''',
}
