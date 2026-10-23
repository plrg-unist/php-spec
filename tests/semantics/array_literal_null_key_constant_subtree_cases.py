"""Nested constant children remain frozen across NULL-key callbacks and COW."""

CASES = {
    'array-literal-null-key-constant-subtree-repeated': b'''<?php
function null_subtree_make($key) {
    $GLOBALS["produced"]++;echo "P:",$GLOBALS["produced"],";";
    $a=[
    0=>9,
    $key=>[[2,7],[2,8]],
    4=>$GLOBALS["tail"]
    ];
    echo "L:",$GLOBALS["produced"],":",$key===null,";";return $a;
}
function null_subtree_key($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if (isset($GLOBALS["held"])) {
        $GLOBALS["held"][0]=44;$GLOBALS["a"][""][0][1]=99;
    }
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$key=null;$tail=7;$calls=0;$produced=0;
set_error_handler("null_subtree_key",E_DEPRECATED);
$a=null_subtree_make($key);$held=$a[""][0];$copy=$a;$copy[""][1][1]=77;
echo "A:",$a[""][0][0],":",$a[""][0][1],":",$copy[""][1][1],":",$held[0],":",$held[1],":",$calls,";";
$key=null;$tail=7;$b=null_subtree_make($key);
restore_error_handler();
echo "B:",$a[""][0][0],":",$a[""][0][1],":",$copy[""][0][0],":",$copy[""][0][1],":",$copy[""][1][1],":",$held[0],":",$held[1],":",$b[""][0][0],":",$b[""][0][1],":",$b[""][1][1],":",$calls,":",$produced,";";
$b[""][0][0]=55;
echo "R:",$a[""][0][0],":",$a[""][0][1],":",$copy[""][0][0],":",$copy[""][0][1],":",$held[0],":",$held[1],":",$b[""][0][0],":",$b[""][0][1],":",$a[4],":",$copy[4],":",$b[4],":",$key,":",$calls,":",$produced,";";
unset($a,$b,$copy,$held,$key,$tail,$calls,$produced);
echo "U:",isset($a),":",isset($b),":",isset($copy),":",isset($held),";";
''',
    'array-literal-null-key-constant-subtree-empty': b'''<?php
function null_empty_subtree_key($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$key=null;$tail=7;$calls=0;
set_error_handler("null_empty_subtree_key",E_DEPRECATED);
$a=[
0=>9,
$key=>[[],[[]]],
4=>$tail
];
restore_error_handler();$copy=$a;$held=$a[""][1][0];
$copy[""][0][]=55;$copy[""][1][0][]=77;$copy[4]=88;$a[""][0][]=66;
echo "R:",$a[""][0][0],":",$copy[""][0][0],":",isset($a[""][1][0][0]),":",$copy[""][1][0][0],":",isset($held[0]),":",$a[4],":",$copy[4],":",$key,":",$calls,";";
unset($a,$copy,$held,$key,$tail,$calls);
echo "U:",isset($a),":",isset($copy),":",isset($held),";";
''',
}
