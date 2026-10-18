"""Fresh flat-array wrapper ownership and child-table COW witnesses."""

CASES = {
    'array-literal-float-ref-arrays-singleton': b'''<?php
function literal_array_retarget($n,$m,$f,$l) {
    $GLOBALS["phase"]++;
    echo "D:",$n,":",$l,":",$GLOBALS["phase"],";";
    if ($GLOBALS["phase"]===1) {
        $GLOBALS["q"][0]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["replacement"];
    } else {unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$seed=2;$q=[$seed];$outside=&$q;$next=44;$replacement=[$next];$key=1.5;$phase=0;
set_error_handler("literal_array_retarget",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q
];
unset($q);$copy=$a;$copy[1][0]=55;
echo "R:",$replacement[0],":",$a[1][0],":",$copy[1][0],":",$outside[0],":",isset($q),";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$a;$shared[1][0]=77;
echo "B:",$replacement[0],":",$a[1][0],":",$shared[1][0],":",$copy[1][0],":",$balance[3][0],":",$q[0],":",$outside[0],":",$phase,";";
unset($a,$copy,$shared,$balance,$q,$outside,$replacement,$key);
echo "U:",isset($q),":",isset($a),":",isset($replacement),";";
''',
    'array-literal-float-ref-arrays-same-cell': b'''<?php
function literal_array_stable($n,$m,$f,$l) {
    echo "D:",$n,":",$l,";";
    $GLOBALS["q"][0]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    $GLOBALS["key"]=9.5;return true;
}
$seed=2;$q=[0=>$seed,4=>NULL,6=>false,8=>1.5];$outside=&$q;$key=2.5;
set_error_handler("literal_array_stable",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q
];
restore_error_handler();
echo "R:",$q[0],":",$outside[0],":",$a[2][0],":",($q===[0=>33,4=>NULL,6=>false,8=>1.5]),";";
unset($q,$outside);$copy=$a;$copy[2][0]=55;
echo "B:",$a[2][0],":",$copy[2][0],":",($a[2]===[0=>33,4=>NULL,6=>false,8=>1.5]),":",($copy[2]===[0=>55,4=>NULL,6=>false,8=>1.5]),";";
unset($a,$copy,$key);
echo "U:",isset($q),":",isset($outside),":",isset($a),";";
''',
}
