"""Fresh typed-property owner-deficit and balanced cleanup witnesses."""

CASES = {
    'array-literal-float-ref-types-singleton': b'''<?php
class LiteralTypedBox22 {public int $slot=44;}
function literal_typed_singleton($n,$m,$f,$l) {
    $GLOBALS["phase"]++;
    echo "D:",$n,":",$l,":",$GLOBALS["phase"],";";
    if ($GLOBALS["phase"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["replacement"];
    } else {unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$box=new LiteralTypedBox22();$q=2;$outside=&$q;$replacement=&$box->slot;$key=1.5;$phase=0;
set_error_handler("literal_typed_singleton",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q
];
unset($q,$replacement);$copy=$a;$copy[1]="free";
echo "R:",$box->slot,":",$a[1],":",$copy[1],":",($copy[1]==="free"),":",$outside,";";
$q=&$box->slot;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();
$shared=$a;
try {$shared[1]=[];} catch (TypeError $bad) {echo "T:",($box->slot===44),":",($shared[1]===44),";";}
$shared[1]="55";
echo "B:",$box->slot,":",$a[1],":",$shared[1],":",($shared[1]===55),":",$copy[1],":",$balance[3],":",$q,":",$outside,";";
unset($bad,$box,$a,$copy,$shared,$balance,$q,$outside,$key);
echo "U:",isset($q),":",isset($box),";";
''',
    'array-literal-float-ref-types-supplied-throw': b'''<?php
class LiteralTypedThrowBox22 {public int $slot=44;}
function literal_typed_throw($n,$m,$f,$l) {
    $GLOBALS["phase"]++;
    echo "D:",$n,":",$l,":",$GLOBALS["phase"],";";
    if ($GLOBALS["phase"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];
    }
    unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    $GLOBALS["key"]=9.5;return true;
}
$box=new LiteralTypedThrowBox22();$second=new Exception();
$q=2;$outside=&$q;$replacement=&$box->slot;$key=1.5;$phase=0;$dest=100;$later=7;
set_error_handler("literal_typed_throw",E_DEPRECATED);
try {
    $dest=[
    0=>8,
    1=>&$outside,
    $key=>&$q,
    2=>$later++
    ];
} catch (Exception $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===NULL),":",$dest,":",$later,":",$q,":",$box->slot,":",$outside,";";
} finally {echo "F;";}
$probe=[&$replacement];unset($q,$replacement);$copy=$probe;$copy[0]="free";
echo "R:",$box->slot,":",$probe[0],":",$copy[0],":",($copy[0]==="free"),":",$dest,":",$later,";";
$q=&$box->slot;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();
$shared=$probe;$shared[0]="66";
echo "B:",$box->slot,":",$probe[0],":",$shared[0],":",($shared[0]===66),":",$copy[0],":",$balance[3],":",$q,":",$outside,";";
unset($box,$second,$e,$probe,$copy,$shared,$balance,$q,$outside,$key,$dest,$later);
echo "U:",isset($q),":",isset($box),";";
''',
}
