"""Undefined-key ARRAY acquisition keeps old owners and repays retarget debt."""

CASES = {
    'array-literal-undefined-key-array-cv-cycle': b'''<?php
function literal_undefined_array_cycle($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["first_key"]=9;$GLOBALS["q"][0]=44;
        $GLOBALS["new_hold"]=$GLOBALS["q"];$GLOBALS["tail"]=66;
    } else {
        $GLOBALS["second_key"]=11;$GLOBALS["q"]=$GLOBALS["old_hold"];
    }
    return true;
}
$seed=2;$q=[$seed,7];$old_hold=$q;$tail=7;$calls=0;
set_error_handler("literal_undefined_array_cycle",E_WARNING|E_DEPRECATED);
echo "P;";
$a=[
0=>9,
$first_key =>
$q,
4=>$tail
];
$a[""][1]=55;$q[0]=66;
$b=[
0=>8,
$second_key =>
$q
];
restore_error_handler();$copy=$b;$copy[""][0]=77;
echo "R:",$a[""][0],":",$a[""][1],":",$q[0],":",$q[1],":",$old_hold[0],":",$old_hold[1],":",$new_hold[0],":",$new_hold[1],":",$b[""][0],":",$b[""][1],":",$copy[""][0],":",$copy[""][1],":",$a[4],":",$first_key,":",$second_key,":",$calls,";";
unset($a,$b,$copy,$q,$old_hold,$new_hold,$seed,$tail,$first_key,$second_key,$calls);
echo "U:",isset($a),":",isset($b),":",isset($q),":",isset($new_hold),";";
''',
    'array-literal-undefined-key-array-cv-scalar-inverse': b'''<?php
function literal_undefined_array_scalar_inverse($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($n===E_WARNING) {
        $GLOBALS["missing"]=9;$GLOBALS["q"]=44;$GLOBALS["tail"]=66;
    } else {
        $GLOBALS["q"]=$GLOBALS["old_hold"];
    }
    return true;
}
$seed=2;$q=[$seed,7];$old_hold=$q;$tail=7;$calls=0;
set_error_handler("literal_undefined_array_scalar_inverse",E_WARNING|E_DEPRECATED);
$a=[
0=>9,
$missing =>
$q,
4=>$tail
];
$copy=$a;$copy[""]=55;$float_key=1.5;
$b=[
0=>8,
$float_key =>
$q
];
restore_error_handler();$b[1][1]=88;
echo "R:",$a[""],":",$copy[""],":",$q[0],":",$q[1],":",$old_hold[0],":",$old_hold[1],":",$b[1][0],":",$b[1][1],":",$a[4],":",$missing,":",$calls,";";
unset($a,$b,$copy,$q,$old_hold,$seed,$tail,$missing,$float_key,$calls);
echo "U:",isset($a),":",isset($b),":",isset($q),":",isset($copy),";";
''',
}
