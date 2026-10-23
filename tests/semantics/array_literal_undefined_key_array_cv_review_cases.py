"""Owning ARRAY values transfer stable owners or balance throw-time retargets."""

CASES = {
    'array-literal-undefined-key-array-cv-review-default': b'''<?php
function literal_undefined_array_default($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==='Undefined variable $missing'),":",$GLOBALS["calls"],":",$l,":",$GLOBALS["q"][0],";";
    $GLOBALS["held"][0]=44;$GLOBALS["missing"]=9;$GLOBALS["tail"]=66;return false;
}
$seed=2;$q=[$seed++,7];$held=$q;$tail=7;$calls=0;
set_error_handler("literal_undefined_array_default",E_WARNING|E_DEPRECATED);
$a=[
0=>9,
$missing
=>
$q,
$missing=>$tail
];
restore_error_handler();
$q[1]=77;$a[""][0]=55;
echo "R:",$a[""][0],":",$a[""][1],":",$q[0],":",$q[1],":",$held[0],":",$held[1],":",$a[9],":",$missing,":",$seed,":",$calls,";";
unset($a,$q,$held,$tail,$missing,$seed,$calls);
echo "U:",isset($a),":",isset($q),":",isset($held),";";
''',
    'array-literal-undefined-key-array-cv-review-throw-inverse': b'''<?php
function literal_undefined_array_throw_inverse($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==='Undefined variable $throw_key'||$m==='Undefined variable $inverse_key'),":",$GLOBALS["calls"],":",$l,":",$GLOBALS["q"][0],";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["throw_key"]=9;$GLOBALS["q"]=$GLOBALS["right"];$GLOBALS["dest"]=99;
        throw $GLOBALS["second"];
    }
    $GLOBALS["inverse_key"]=9;$GLOBALS["q"]=$GLOBALS["left"];return true;
}
$lseed=2;$rseed=20;$left=[$lseed++,7];$right=[$rseed++,8];$held=$right;$q=$left;
$calls=0;$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_undefined_array_throw_inverse",E_WARNING|E_DEPRECATED);
try {
    $dest=[
    0=>9,
    ""=>8,
    $throw_key
    =>
    $q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,":",$q[0],":",$right[0],":",$held[0],";";}
unset($e);$q=0;$right[0]=55;
echo "S:",$right[0],":",$held[0],":",$calls,";";
$q=$right;
$b=[
0=>6,
$inverse_key
=>
$q,
7=>$later
];
restore_error_handler();$right[0]=66;$b[""][1]=88;
echo "R:",$left[0],":",$left[1],":",$q[0],":",$q[1],":",$b[""][0],":",$b[""][1],":",$right[0],":",$right[1],":",$held[0],":",$held[1],":",$dest,":",$later,":",$calls,":",$lseed,":",$rseed,";";
unset($b,$q,$left,$right,$held,$throw_key,$inverse_key,$dest,$later,$second,$calls,$lseed,$rseed);
echo "U:",isset($b),":",isset($q),":",isset($right),":",isset($held),":",isset($second),";";
''',
}
