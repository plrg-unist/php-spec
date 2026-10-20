"""NULL-key conversion restores the value CV, including a shared key/value CV."""

CASES = {
    'array-literal-null-key-same-cv': b'''<?php
function literal_null_same($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,":",$GLOBALS["q"]===null,";";
    $GLOBALS["q"]=44;$GLOBALS["tail"]=66;echo "H:",$GLOBALS["q"],";";return true;
}
$q=null;$tail=7;$calls=0;
set_error_handler("literal_null_same",E_DEPRECATED);
$a=[
0=>9,
$q=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""]=55;
echo "R:",$q===null,":",$a[""]===null,":",$copy[""],":",$a[0],":",$a[4],":",$calls,";";
$q=77;echo "B:",$q,":",$a[""]===null,":",$copy[""],";";
unset($q,$a,$copy,$tail);
echo "U:",isset($q),":",isset($a),":",isset($copy),";";
''',
    'array-literal-null-key-array-snapshot': b'''<?php
function literal_null_array($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,":",$GLOBALS["q"][0],";";
    $GLOBALS["q"][0]=44;$GLOBALS["q"][1]=88;$GLOBALS["changed"]=$GLOBALS["q"];
    $GLOBALS["q"][0]=55;echo "H:",$GLOBALS["q"][0],":",$GLOBALS["q"][1],":",$GLOBALS["changed"][0],":",$GLOBALS["changed"][1],";";
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$seed=2;$q=[$seed,7];$old_hold=$q;$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_array",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=66;
echo "R:",$q[0],":",$q[1],":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$old_hold[0],":",$changed[0],":",$changed[1],":",$a[4],":",$key,":",$calls,";";
$q[0]=77;$a[""][1]=99;
echo "B:",$q[0],":",$q[1],":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$old_hold[0],":",$old_hold[1],":",$changed[0],":",$changed[1],";";
unset($q,$old_hold,$changed,$a,$copy,$key,$tail);
echo "U:",isset($q),":",isset($old_hold),":",isset($changed),":",isset($a),";";
''',
}
