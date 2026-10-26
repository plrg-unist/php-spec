"""Fixed bounds, pending throws, and the explicit borrowed-carrier release fence."""

CASES = {
    'string-offset-read-warning-review-default-bounds': b'''<?php
function string_read_default($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$m,":",$l,";";
    $GLOBALS["text"]="XYZ";$GLOBALS["key"]=0;$GLOBALS["tail"]=66;return false;
}
$text="abc";$key=7;$tail=7;$calls=0;$got=100;
set_error_handler("string_read_default",E_WARNING);
$got=$text[
    $key
];
restore_error_handler();
echo "R:",$got==="",":",$text,":",$key,":",$tail,":",$calls,":",$text[0],";";
unset($text,$key,$tail,$calls,$got);
echo "U:",isset($text),":",isset($got),":",isset($calls),";";
''',
    'string-offset-read-warning-review-supplied-throw': b'''<?php
function string_read_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$m,":",$l,";";
    $GLOBALS["text"]="uvwxyz";$GLOBALS["prefix"]="zz";$GLOBALS["key"]=3;$GLOBALS["dest"]=99;
    if ($GLOBALS["restore"]) {restore_error_handler();}
    throw $GLOBALS["second"];
}
$prefix="a";$text="abc";$key=1.5;$calls=0;$dest=100;$later=7;$restore=false;$second=new Exception("supplied");
set_error_handler("string_read_throw",E_WARNING);
try {
    $dest=$text[
        $key
    ];
    $later++;echo "N1;";
} catch (Exception $e) {echo "C1:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,":",$calls,";";}
unset($e);
$restore=true;$key=null;$dest=101;$prefix="a";
try {
    $dest=(
        $prefix."bc"
    )[
        $key
    ];
    $later++;echo "N2;";
} catch (Exception $e) {echo "C2:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,":",$calls,";";}
restore_error_handler();unset($e);
echo "R:",$text,":",$key,":",$prefix,":",$dest,":",$later,":",$calls,":",isset($e),";";
unset($prefix,$text,$key,$calls,$dest,$later,$restore,$second);
echo "U:",isset($prefix),":",isset($dest),":",isset($second),";";
''',
    'string-offset-read-warning-review-borrowed-drop': b'''<?php
function string_read_drop($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$m,":",$l,";";
    $GLOBALS["text"]="XYZ";$GLOBALS["key"]=99;$GLOBALS["tail"]=66;return true;
}
$prefix="a";$text=$prefix."bc";$key=1.5;$tail=7;$calls=0;$got=100;$later=7;
set_error_handler("string_read_drop",E_WARNING);
$got=$text[
    $key
];
$later++;restore_error_handler();
echo "R:",$got===null,":",$text,":",$key,":",$tail,":",$later,":",$calls,";";
unset($prefix,$text,$key,$tail,$calls,$got,$later);
echo "U:",isset($text),":",isset($got),":",isset($calls),";";
''',
}

BOUNDARIES = {
    'string-offset-read-warning-review-borrowed-drop': 'string offset borrowed carrier after callback',
}
