"""Independent missing-list-key ordering, line and owner-retirement witnesses."""

CASES = {
    'list-missing-review-holes-reporting-fallback': b'''<?php
function list_peer_fallback($n,$s,$f,$l) { global $calls; $calls++; echo $n,":",$s,":",$l,";"; return false; }
error_reporting(0);$calls=0;$a=[4=>null];$x=7;$y=8;$z=9;set_error_handler("list_peer_fallback",E_WARNING);
list(
,
$x
,
,
$y
,
$z
)=
$a;
restore_error_handler();echo $x===null?1:0,":",$y===null?1:0,":",$z===null?1:0,":",$calls,";";
''',
    'list-missing-review-earlier-target-throw': b'''<?php
function list_peer_throw($n,$s,$f,$l) {
    global $a,$x;
    echo "W:",$x,":";
    $a[0]=11;
    $x=99;
    throw new Exception("kept");
}
$a=[0=>1,1=>2];$x=7;$y=8;$dest=100;set_error_handler("list_peer_throw");
try {$dest=([0=>$x,"3"=>$a,1=>$y]=$a);}
catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()===null?1:0,":";}
restore_error_handler();echo $x,":",$y,":",$dest,":",$a[0],":";$a[0]=12;echo $a[0],";";
''',
    'list-missing-review-shared-owner-retirement': b'''<?php
function list_peer_retire($n,$m,$f,$l) {echo "W:",$GLOBALS["before"],":";$GLOBALS["q"]=33;unset($GLOBALS["a"],$GLOBALS["q"]);return true;}
$q=2;$a=[0=>5,2=>&$q];$before=6;$x=7;$y=8;set_error_handler("list_peer_retire");
[$before,$x,$y]=$a;
restore_error_handler();echo $before,":",$x===null?1:0,":",$y,":",isset($a)?1:0,":",isset($q)?1:0,";";
''',
}
