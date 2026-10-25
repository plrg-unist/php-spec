"""Nested runtime TMP graphs freeze before NULL-key callbacks and own child edges."""

CASES = {
    'array-literal-null-key-array-tmp-subtree-increment-cow': b'''<?php
function null_tmp_subtree_increment($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";H:",$GLOBALS["seed"],";";
    $GLOBALS["seed"]=44;$GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$seed=2;$key=null;$tail=7;$calls=0;
set_error_handler("null_tmp_subtree_increment",E_DEPRECATED);
echo "P;";
$a=[
0=>9,
$key=>[[[$seed++,7],8],[[3,4],[]]],
4=>$tail
];
restore_error_handler();$copy=$a;
$copy[""][0][0][0]=55;$copy[""][1][0][1]=77;$copy[""][1][1][]=88;
$fresh=[[[$seed++,7],8]];$seed=99;
echo "R:",$a[""][0][0][0],":",$a[""][0][0][1],":",$a[""][0][1],":",$copy[""][0][0][0],":",$copy[""][0][0][1],":",$a[""][1][0][1],":",$copy[""][1][0][1],":",isset($a[""][1][1][0]),":",$copy[""][1][1][0],":",$fresh[0][0][0],":",$seed,":",$a[4],":",$key,":",$calls,";";
unset($a,$copy,$fresh,$seed,$key,$tail,$calls);
echo "U:",isset($a),":",isset($copy),":",isset($fresh),":",isset($seed),";";
''',
    'array-literal-null-key-array-tmp-subtree-shared-child': b'''<?php
function null_tmp_subtree_shared($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";H:",$GLOBALS["row"][0],":",$GLOBALS["held"][1],";";
    $GLOBALS["row"][0]=44;$GLOBALS["held"][1]=55;
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$seed=2;$row=[$seed,7];$held=$row;$key=null;$tail=7;$calls=0;
set_error_handler("null_tmp_subtree_shared",E_DEPRECATED);
$a=[
0=>9,
$key=>[$row,$row,[[5,9],[]]],
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0][0]=66;$row[1]=88;$held[0]=77;
echo "C:",$a[""][0][0],":",$a[""][1][0],":",$copy[""][0][0],":",$copy[""][1][0],":",$a[""][1][1],":",$copy[""][1][1],":",$row[0],":",$row[1],":",$held[0],":",$held[1],":",$a[""][2][0][1],":",isset($a[""][2][1][0]),";";
unset($copy);unset($a[""]);
echo "R:",isset($a[""]),":",$row[0],":",$row[1],":",$held[0],":",$held[1],":",$a[0],":",$a[4],":",$key,":",$calls,";";
unset($a,$row,$held,$seed,$key,$tail,$calls);
echo "U:",isset($a),":",isset($row),":",isset($held),":",isset($seed),";";
''',
}
