"""NULL-key reset restores a captured reference payload despite CV rebinding."""

CASES = {
    'array-literal-null-key-wrapped-cv-scalar': b'''<?php
function literal_null_wrapped_scalar($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,":",$GLOBALS["outside"],";";
    $GLOBALS["outside"]=44;$GLOBALS["q"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;echo "H:",$GLOBALS["outside"],":",$GLOBALS["q"],";";return true;
}
$outside=2;$q=&$outside;$initial=$outside;$other=99;$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_wrapped_scalar",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""]=55;
echo "R:",$outside,":",$q,":",$other,":",$a[""],":",$copy[""],":",$initial,":",$key,":",$a[4],":",$calls,";";
$outside=77;$q=88;echo "B:",$outside,":",$q,":",$other,":",$a[""],":",$copy[""],":",$initial,";";
unset($q,$outside,$other,$initial,$a,$copy,$key,$tail,$calls);
echo "U:",isset($q),":",isset($outside),":",isset($other),":",isset($a),";";
''',
    'array-literal-null-key-wrapped-cv-array': b'''<?php
function literal_null_wrapped_array($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,":",$GLOBALS["outside"][0],";";
    $GLOBALS["outside"][0]=44;$GLOBALS["outside"][1]=88;$GLOBALS["changed"]=$GLOBALS["outside"];
    $GLOBALS["outside"][0]=55;$GLOBALS["q"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;echo "H:",$GLOBALS["outside"][0],":",$GLOBALS["outside"][1],":",$GLOBALS["q"],":",$GLOBALS["changed"][0],":",$GLOBALS["changed"][1],";";return true;
}
$seed=2;$outside=[$seed,7];$q=&$outside;$old_hold=$outside;$other=99;$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_wrapped_array",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=66;
echo "R:",$outside[0],":",$outside[1],":",$q,":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$old_hold[0],":",$old_hold[1],":",$changed[0],":",$changed[1],":",$key,":",$a[4],":",$calls,";";
$outside[0]=77;$a[""][1]=99;$q=88;
echo "B:",$outside[0],":",$outside[1],":",$q,":",$other,":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$old_hold[0],":",$old_hold[1],":",$changed[0],":",$changed[1],";";
unset($q,$outside,$old_hold,$changed,$other,$a,$copy,$key,$tail,$calls);
echo "U:",isset($q),":",isset($outside),":",isset($old_hold),":",isset($changed),":",isset($a),";";
''',
}
