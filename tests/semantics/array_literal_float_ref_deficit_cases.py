"""Fresh balanced reference-count deficit and inverse-retarget witnesses."""

CASES = {
    'array-literal-float-ref-deficit-shared-copy': b'''<?php
function literal_deficit_shared($n,$m,$f,$l) {
    $GLOBALS["phase"]++;
    echo "D:",$n,":",$l,":",$GLOBALS["phase"],";";
    if ($GLOBALS["phase"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["replacement"];
    } else {unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;
    return true;
}
$q=2;$outside=&$q;$replacement=44;$buddy=&$replacement;$key=2.5;$phase=0;
set_error_handler("literal_deficit_shared",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q,
1=>7
];
unset($q);$copy=$a;$copy[2]=55;
echo "A:",$a[2],":",$copy[2],":",$replacement,":",$buddy,":",($a===[0=>9,2=>55,1=>7]),";";
$q=&$replacement;$key=3.5;
$b=[
$key=>&$q
];
restore_error_handler();
$again=$a;$again[2]=77;
echo "B:",$a[2],":",$copy[2],":",$again[2],":",$replacement,":",$buddy,":",$b[3],":",$q,":",$outside,";";
$b[3]=88;echo "C:",$q,":",$outside,":",$replacement,";";
unset($a,$b,$copy,$again,$q,$outside,$replacement,$buddy,$key);
echo "U:",isset($q),":",isset($replacement),";";
''',
    'array-literal-float-ref-deficit-stable-bias': b'''<?php
function literal_deficit_stable($n,$m,$f,$l) {
    $GLOBALS["phase"]++;
    echo "D:",$n,":",$l,":",$GLOBALS["phase"],";";
    if ($GLOBALS["phase"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["replacement"];
    } elseif ($GLOBALS["phase"]===2) {
        unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["replacement"];
    } else {unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$q=2;$outside=&$q;$replacement=44;$key=1.5;$phase=0;
set_error_handler("literal_deficit_stable",E_DEPRECATED);
$a=[
$key=>&$q
];
$key=2.5;
$b=[
$key=>&$q
];
unset($q,$b);$copy=$a;$copy[1]=55;
echo "A:",$a[1],":",$copy[1],":",$replacement,":",$outside,";";
$q=&$replacement;$key=3.5;
$c=[
$key=>&$q
];
restore_error_handler();
$balanced=$a;$balanced[1]=77;
echo "B:",$a[1],":",$copy[1],":",$balanced[1],":",$replacement,":",$c[3],":",$q,":",$outside,";";
unset($a,$c,$copy,$balanced,$q,$outside,$replacement,$key);
echo "U:",isset($q),":",isset($replacement),";";
''',
    'array-literal-float-ref-deficit-multiplicity': b'''<?php
function literal_deficit_repeat($n,$m,$f,$l) {
    $GLOBALS["phase"]++;
    echo "D:",$n,":",$l,":",$GLOBALS["phase"],";";
    if ($GLOBALS["phase"]<=2) {
        $GLOBALS["q"]=30+$GLOBALS["phase"];unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["replacement"];
    } elseif ($GLOBALS["phase"]===3) {unset($GLOBALS["q"]);$GLOBALS["q"]=99;}
    else {unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$q=2;$outside=&$q;$replacement=44;$buddy=&$replacement;$extra=&$replacement;$key=1.5;$phase=0;
set_error_handler("literal_deficit_repeat",E_DEPRECATED);
$a=[
$key=>&$q
];
$q=&$outside;$key=2.5;
$b=[
$key=>&$q
];
unset($q,$buddy,$extra);$copy=$a;$copy[1]=55;
echo "A:",$a[1],":",$b[2],":",$copy[1],":",$replacement,":",$outside,";";
$q=&$replacement;$key=3.5;
$c=[
$key=>&$q
];
$middle=$a;$middle[1]=66;
echo "M:",$a[1],":",$b[2],":",$middle[1],":",$replacement,":",$c[3],";";
$q=&$replacement;$key=4.5;
$d=[
$key=>&$q
];
restore_error_handler();
$balanced=$a;$balanced[1]=77;
echo "B:",$a[1],":",$b[2],":",$copy[1],":",$middle[1],":",$balanced[1],":",$replacement,":",$c[3],":",$d[4],":",$q,":",$outside,";";
$old_probe=[&$outside];unset($d,$q,$outside);$old_copy=$old_probe;$old_copy[0]=88;
echo "G:",$old_probe[0],":",$old_copy[0],":",$replacement,":",$c[3],";";
unset($a,$b,$c,$copy,$middle,$balanced,$old_probe,$old_copy,$replacement,$key);
echo "U:",isset($q),":",isset($replacement),";";
''',
}
