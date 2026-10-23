"""Runtime array constructors own one frozen TMP across NULL-key callbacks."""

CASES = {
    'array-literal-null-key-array-tmp-increment': b'''<?php
function null_tmp_increment_key($n,$m,$f,$l) {
    echo "D:",$n,":",$l,";H:",$GLOBALS["seed"],";";
    $GLOBALS["seed"]=44;$GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$seed=2;$key=null;$tail=7;
set_error_handler("null_tmp_increment_key",E_DEPRECATED);
$a=[
0=>9,
$key=>[$seed++,7],
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=55;$copy[4]=77;
$fresh=[$seed,7];$seed=99;
echo "R:",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$seed,":",$fresh[0],":",$fresh[1],":",$a[4],":",$copy[4],":",$key,";";
unset($a,$copy,$fresh,$key,$seed,$tail);
echo "U:",isset($a),":",isset($copy),":",isset($fresh),":",isset($seed),";";
''',
    'array-literal-null-key-array-tmp-reference-leaf': b'''<?php
function null_tmp_reference_key($n,$m,$f,$l) {
    echo "D:",$n,":",$l,";";
    $GLOBALS["outside"]=44;$GLOBALS["seed"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;
    echo "H:",$GLOBALS["outside"],":",$GLOBALS["seed"],";";return true;
}
$seed=2;$outside=&$seed;$other=33;$key=null;$tail=7;$held=[$seed,8];
set_error_handler("null_tmp_reference_key",E_DEPRECATED);
$a=[
0=>9,
$key=>[$seed,7],
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=55;$copy[4]=77;$outside=66;
$fresh=[$seed,7];$seed=99;$held[0]=88;
echo "R:",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$outside,":",$seed,":",$other,":",$fresh[0],":",$fresh[1],":",$held[0],":",$held[1],":",$a[4],":",$copy[4],":",$key,";";
unset($a,$copy,$fresh,$held,$seed,$outside,$other,$key,$tail);
echo "U:",isset($a),":",isset($copy),":",isset($fresh),":",isset($held),":",isset($seed),":",isset($outside),";";
''',
}
