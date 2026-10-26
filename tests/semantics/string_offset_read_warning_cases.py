"""String R-offset callbacks retain the selected bytes but reread cast offsets."""

CASES = {
    'string-offset-read-warning-interned-live-key': b'''<?php
function string_read_interned($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "W:",$n,":",$GLOBALS["calls"],":",($m==='String offset cast occurred'),":",$l,";";
    $GLOBALS["s"]="XY";$GLOBALS["key"]=2;return true;
}
$s="abcd";$key=1.5;$calls=0;$out=99;
set_error_handler("string_read_interned",E_WARNING);
echo "P;";
$out=$s[$key];
restore_error_handler();$copy=$s;$s[0]="Z";
echo "R:",$out,":",$s,":",$copy,":",$key,":",$calls,";";
unset($s,$key,$calls,$out,$copy);
echo "U:",isset($s),":",isset($out),":",isset($copy),";";
''',
    'string-offset-read-warning-runtime-carriers': b'''<?php
function string_read_runtime($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "W:",$n,":",$GLOBALS["calls"],":",($m==='String offset cast occurred'),":",($m==='Uninitialized string offset 9'),":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["key"]=-1.7;}
    elseif ($GLOBALS["calls"]===2) {$GLOBALS["head"]="XY";$GLOBALS["key"]=9;}
    else {$GLOBALS["head"]="z";$GLOBALS["key"]=0;}
    return true;
}
$head="ab";$s=$head."cd";$key=1.5;$calls=0;
set_error_handler("string_read_runtime",E_WARNING);
$stable=$s[$key];
$key=1.5;$head="AB";
$tmp=($head."CD")[$key];
restore_error_handler();
echo "R:",$stable,":",$tmp==="",":",$s,":",$head,":",$key,":",$calls,";";
unset($head,$s,$key,$calls,$stable,$tmp);
echo "U:",isset($s),":",isset($stable),":",isset($tmp),";";
''',
}
