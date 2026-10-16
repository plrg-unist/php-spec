"""Non-NUL request-string key cells and numeric-string reference selection."""

CASES = {
    'list-quiet-cv-review-request-key-cell-retire': b'''<?php
function list_quiet_cv_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==='Undefined array key "old-row"'),":",$l,":",$GLOBALS["key"],";";
    $GLOBALS["x"]=99;$GLOBALS["key_alias"]="discarded";
    unset($GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["key"]=&$GLOBALS["replacement"];
    $GLOBALS["next"]="old";$GLOBALS["a"]["old-row"]=77;
    return true;
}
$prefix="old";$key=$prefix."-row";$key_alias=&$key;$replacement="new";$next="other";$value=22;
$a=["old"=>11,"other"=>$value];$x=7;$y=8;$dest=100;$calls=0;
set_error_handler("list_quiet_cv_peer");
$dest=([
$key=>$x,
$next=>$y
]=
$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$key,":",$replacement,":",$a["old-row"],":",isset($dest["old-row"]),":",$dest["other"],":",$calls,";";
$key="later";
echo "A:",$key,":",$replacement,":",$y,";";
unset($dest,$a,$key,$replacement);
echo "U:",isset($key),":",isset($key_alias),":",isset($dest),";";
''',
    'list-quiet-cv-review-numeric-string-reference': b'''<?php
function list_quiet_cv_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$l,":",($m==="Undefined array key 2"),":",$GLOBALS["key"],":",$GLOBALS["missing"],":",$GLOBALS["late"],";";
    $GLOBALS["key"]="02";$GLOBALS["q"]=33;
    $GLOBALS["missing"]=99;$GLOBALS["a"][2]=77;
    return false;
}
error_reporting(0);$key="2";$q=2;$a=[0=>10,"02"=>&$q];$copy=$a;
$missing=7;$late=8;$dest=100;$calls=0;
set_error_handler("list_quiet_cv_peer",E_WARNING);
$dest=(list(
$key=>$missing,
$key=>&$late
)=
$a);
restore_error_handler();
echo "R:",($missing===null),":",$late,":",$key,":",$dest[2],":",isset($copy[2]),":",$copy["02"],":",$calls,";";
$late=44;$key="2";
echo "A:",$q,":",$a["02"],":",$dest["02"],":",$copy["02"],":",$dest[2],":",$key,";";
unset($dest,$a,$copy,$q,$late);
echo "U:",isset($dest),":",isset($a),":",isset($copy),":",isset($late),";";
''',
}
