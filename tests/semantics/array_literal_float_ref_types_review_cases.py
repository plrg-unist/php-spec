"""Typed old owners and multiple live type sources distinguish reference debt."""

CASES = {
    'array-literal-ref-types-review-old-typed-delete': b'''<?php
class LiteralOldTyped22 { public int $slot=2; }
function literal_types_peer_old($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);
        $GLOBALS["q"]=&$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=200;
    } else {
        unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    }
    return true;
}
error_reporting(0);$box=new LiteralOldTyped22;$q=&$box->slot;$outside=&$q;
$replacement=44;$key=-2.75;$dest=100;$calls=0;
set_error_handler("literal_types_peer_old",E_DEPRECATED);
$dest=[
0=>9,
$key=>&$q
];
restore_error_handler();
unset($dest[-2]);
$probe=[&$replacement];unset($q);$copy=$probe;$copy[0]=55;
echo "R:",$dest[0],":",isset($dest[-2]),":",$replacement,":",$probe[0],":",$copy[0],":",$box->slot,":",$outside,";";
try {$outside=[];echo "BAD;";}
catch (TypeError $e) {echo "T:",($box->slot===33),":",($outside===33),";";}
unset($e);$q=&$replacement;$key=3.5;
set_error_handler("literal_types_peer_old",E_DEPRECATED);
$balance=[$key=>&$q];
restore_error_handler();
$balanced_copy=$probe;$balanced_copy[0]=77;$balance[3]="77";
echo "B:",$replacement,":",$probe[0],":",$copy[0],":",$balanced_copy[0],":",$box->slot,":",$outside,":",$q,":",$balance[3],":",$calls,";";
unset($dest,$probe,$copy,$balanced_copy,$balance,$q,$replacement,$outside,$key,$box);
echo "U:",isset($dest),":",isset($q),":",isset($box),";";
''',
    'array-literal-ref-types-review-two-property-sources': b'''<?php
class LiteralPairTyped22 { public int $slot=44; }
function literal_types_peer_pair($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);
        $GLOBALS["q"]=&$GLOBALS["replacement"];
        $GLOBALS["key"]=9.5;$GLOBALS["dest"]=200;
    } else {
        unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["outside"];
    }
    return true;
}
error_reporting(0);$left=new LiteralPairTyped22;$right=new LiteralPairTyped22;
$right->slot=&$left->slot;$replacement=&$left->slot;
$q=2;$outside=&$q;$key=1.5;$dest=100;$calls=0;
set_error_handler("literal_types_peer_pair",E_DEPRECATED);
$dest=[
0=>9,
$key=>&$q
];
restore_error_handler();
unset($q,$replacement);$copy=$dest;
try {$copy[1]=[];echo "BAD;";}
catch (TypeError $e) {echo "T:",($left->slot===44),":",($right->slot===44),":",($dest[1]===44),";";}
unset($e);$copy[1]="55";
echo "R:",$left->slot,":",$right->slot,":",$dest[1],":",$copy[1],":",$outside,";";
$q=&$left->slot;$key=3.5;
set_error_handler("literal_types_peer_pair",E_DEPRECATED);
$balance=[$key=>&$q];
restore_error_handler();
$balanced_copy=$dest;$balanced_copy[1]=77;
echo "B:",$left->slot,":",$right->slot,":",$dest[1],":",$copy[1],":",$balanced_copy[1],":",$outside,":",$q,":",$balance[3],":",$calls,";";
unset($dest,$copy,$balanced_copy,$balance,$q,$outside,$key,$left,$right);
echo "U:",isset($dest),":",isset($q),":",isset($left),":",isset($right),";";
''',
}
