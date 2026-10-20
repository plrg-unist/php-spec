"""NULL-key reset restores a captured reference payload after the CV rebinds."""

CASES = {
    'array-literal-null-key-wrapped-cv-review-delete-entry': b'''<?php
function literal_null_wrapped_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["outside"][0]=55;$GLOBALS["outside"][1]=88;$GLOBALS["q"]=&$GLOBALS["other"];$GLOBALS["key"]=9;$GLOBALS["tail"]=66;
    echo "H:",$GLOBALS["q"],":",$GLOBALS["outside"][0],":",$GLOBALS["outside"][1],";";return true;
}
$seed=2;$q=[$seed,7];unset($seed);$outside=&$q;$other=99;$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_wrapped_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=66;$copy[""][1]=99;
echo "R:",$q,":",$other,":",$outside[0],":",$outside[1],":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$key,":",$a[4],":",$calls,";";
unset($outside);unset($copy);unset($a[""]);
echo "B:",isset($outside),":",isset($copy),":",isset($a[""]),":",$q,":",$other,":",$a[0],":",$a[4],":",$calls,";";
unset($q,$other,$a,$key,$tail,$calls);
echo "U:",isset($q),":",isset($outside),":",isset($copy),":",isset($a),";";
''',
    'array-literal-null-key-wrapped-cv-review-supplied-throw': b'''<?php
function literal_null_wrapped_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["outside"][0]=55;$GLOBALS["outside"][1]=88;$GLOBALS["q"]=&$GLOBALS["other"];$GLOBALS["key"]=9;$GLOBALS["dest"]=99;
    echo "H:",$GLOBALS["q"],":",$GLOBALS["outside"][0],":",$GLOBALS["outside"][1],";";throw $GLOBALS["second"];
}
$seed=2;$q=[$seed,7];unset($seed);$outside=&$q;$other=99;$key=null;$calls=0;$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_null_wrapped_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    ""=>8,
    $key=>$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,":",$q,":",$other,":",$outside[0],":",$outside[1],";";}
restore_error_handler();unset($e);
echo "R:",$q,":",$other,":",$outside[0],":",$outside[1],":",$key,":",$calls,":",$dest,":",$later,":",isset($e),";";
unset($q,$outside,$other,$key,$calls,$dest,$later,$second);
echo "U:",isset($q),":",isset($outside),":",isset($dest),":",isset($second),";";
''',
}
