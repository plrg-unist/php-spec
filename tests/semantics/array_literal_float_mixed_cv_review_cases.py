"""Mixed scalar/array CV deficits survive deletion and supplied-throw cleanup."""

CASES = {
    'array-literal-mixed-cv-review-delete-entry': b'''<?php
function literal_mixed_cv_peer_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        unset($GLOBALS["q"]);
        $GLOBALS["q"]=$GLOBALS["replacement"];
    } else {
        $GLOBALS["q"]=99;
    }
    $GLOBALS["key"]=9.5;return true;
}
error_reporting(0);$q=2;$seed=44;$replacement=[$seed];$key=-2.75;$calls=0;
set_error_handler("literal_mixed_cv_peer_delete",E_DEPRECATED);
$a=[
0=>8,
$key=>$q
];
unset($a[-2]);$q[0]=55;
echo "R:",$q[0],":",$replacement[0],":",isset($a[-2]),":",$a[0],":",$calls,";";
$key=3.5;
$b=[
$key=>$q
];
restore_error_handler();$copy=$replacement;$copy[0]=66;
echo "B:",$q,":",$b[3],":",$replacement[0],":",$copy[0],":",$calls,";";
unset($a,$b,$q,$replacement,$copy,$key,$seed,$calls);
echo "U:",isset($q),":",isset($replacement),":",isset($a),":",isset($b),";";
''',
    'array-literal-mixed-cv-review-supplied-throw': b'''<?php
function literal_mixed_cv_peer_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"]=$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];
    }
    $GLOBALS["q"]=99;$GLOBALS["key"]=9.5;return true;
}
error_reporting(0);$q=2;$seed=44;$replacement=[$seed];$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_mixed_cv_peer_throw",E_DEPRECATED);
try {
$dest=[
0=>8,
1=>7,
$key=>$q,
4=>$later++
];
} catch (Throwable $e) {echo "C:",($e===$second),":",($e->getPrevious()===NULL),":",$dest,":",$later,";";}
$q[0]=55;
echo "R:",$q[0],":",$replacement[0],":",$dest,":",$later,":",$calls,";";
$key=3.5;
$b=[
$key=>$q
];
restore_error_handler();$copy=$replacement;$copy[0]=66;
echo "B:",$q,":",$b[3],":",$replacement[0],":",$copy[0],":",$dest,":",$later,":",$calls,";";
unset($b,$q,$replacement,$copy,$key,$seed,$calls,$dest,$later,$second,$e);
echo "U:",isset($q),":",isset($replacement),":",isset($b),":",isset($e),";";
''',
}
