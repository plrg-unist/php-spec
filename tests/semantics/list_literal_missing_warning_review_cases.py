"""Literal-result effect replay and captured reference-cell identity."""

CASES = {
    'list-literal-review-pooled-holes-fallback': b'''<?php
function literal_peer_warning($n,$m,$f,$l) {
    global $calls,$x;
    $calls++;
    echo "H",$calls,":",$l,":",($x===null),";";
    $x=99;
    return false;
}
error_reporting(0);$calls=0;$x=7;$y=8;$z=9;$dest=100;
set_error_handler("literal_peer_warning",E_WARNING);
$dest=(list(
,
$x,
,
$y,
$z
)=
[4=>null]);
restore_error_handler();
echo "R:",$x,":",($y===null),":",($z===null),":",($dest[4]===null),":",isset($dest[1]),":",$calls,";";
''',
    'list-literal-review-reference-rebind': b'''<?php
function literal_peer_warning($n,$m,$f,$l) {
    echo "W:",$GLOBALS["q"],":";
    $GLOBALS["q"] =& $GLOBALS["other"];
    $GLOBALS["q"]=44;
    return true;
}
$q=2;$other=33;$x=7;$y=8;$dest=100;
set_error_handler("literal_peer_warning");
$dest=([$x,$y]=[1=>&$q]);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$dest[1],":",$q,":",$other,";";
$dest[1]=55;
echo "A:",$y,":",$dest[1],":",$q,":",$other,";";
unset($dest);
echo "U:",isset($dest),";";
''',
    'list-literal-review-pooled-throw': b'''<?php
function literal_peer_warning($n,$m,$f,$l) {
    $GLOBALS["x"]=99;
    throw $GLOBALS["second"];
}
$second=new Exception("same");$x=7;$y=8;$dest=100;
set_error_handler("literal_peer_warning");
try {
    $dest=([$x,$y]=[1=>2]);
    echo "BAD;";
} catch(Throwable $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===null),":",$x,":",$y,":",$dest,";";
} finally {echo "F;";}
restore_error_handler();
echo "END;";
''',
}
