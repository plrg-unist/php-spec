"""NULL literal keys restore ordinary ARRAY CVs before insertion or throw."""

CASES = {
    'array-literal-null-key-review-delete-entry': b'''<?php
function literal_null_key_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["q"][0]=55;$GLOBALS["q"][1]=88;$GLOBALS["key"]=9;$GLOBALS["tail"]=66;
    echo "H:",$GLOBALS["q"][0],":",$GLOBALS["q"][1],";";return true;
}
$seed=2;$q=[$seed,7];unset($seed);$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_key_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=66;$copy[""][1]=99;
echo "R:",$q[0],":",$q[1],":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$key,":",$a[4],":",$calls,";";
unset($q);unset($copy);unset($a[""]);
echo "B:",isset($q),":",isset($copy),":",isset($a[""]),":",$a[0],":",$a[4],":",$key,":",$calls,";";
unset($a,$key,$tail,$calls);
echo "U:",isset($a),":",isset($q),":",isset($copy),";";
''',
    'array-literal-null-key-review-supplied-throw': b'''<?php
function literal_null_key_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["q"][0]=55;$GLOBALS["q"][1]=88;$GLOBALS["key"]=9;$GLOBALS["dest"]=99;
    echo "H:",$GLOBALS["q"][0],":",$GLOBALS["q"][1],";";throw $GLOBALS["second"];
}
$seed=2;$q=[$seed,7];unset($seed);$key=null;$calls=0;$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_null_key_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    ""=>8,
    $key=>$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,":",$q[0],":",$q[1],";";}
restore_error_handler();unset($e);
echo "R:",$q[0],":",$q[1],":",$key,":",$calls,":",$dest,":",$later,":",isset($e),";";
unset($q,$key,$calls,$dest,$later,$second);
echo "U:",isset($q),":",isset($dest),":",isset($second),";";
''',
}
