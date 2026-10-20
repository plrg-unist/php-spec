"""Owning by-value return temporaries keep a NULL-key backup without CV writeback."""

CASES = {
    'array-literal-null-key-return-array-value-global': b'''<?php
function null_returned_global_array() {
    $GLOBALS["produced"]++;echo "M:",$GLOBALS["produced"],";";
    return $GLOBALS["source"];
}
function null_returned_global_key($n,$m,$f,$l) {
    echo "D:",$n,":",$GLOBALS["produced"],":",$l,";";
    $GLOBALS["source"][0]=44;$GLOBALS["source"][1]=88;
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$seed=2;$source=[$seed,7];$produced=0;$key=null;$tail=7;
set_error_handler("null_returned_global_key",E_DEPRECATED);
$a=[
0=>9,
$key=>null_returned_global_array(),
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=55;$copy[4]=77;
$fresh=null_returned_global_array();$source[0]=99;
echo "R:",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$source[0],":",$source[1],":",$fresh[0],":",$fresh[1],":",$a[4],":",$copy[4],":",$key,":",$produced,";";
unset($a,$copy,$fresh,$source,$key,$seed,$tail,$produced);
echo "U:",isset($a),":",isset($copy),":",isset($fresh),":",isset($source),";";
''',
    'array-literal-null-key-return-array-value-global-reference': b'''<?php
function null_returned_reference_array() {
    $GLOBALS["produced"]++;echo "M:",$GLOBALS["produced"],";";
    return $GLOBALS["source"];
}
function null_returned_reference_key($n,$m,$f,$l) {
    echo "D:",$n,":",$GLOBALS["produced"],":",$l,";";
    $GLOBALS["outside"][0]=44;$GLOBALS["outside"][1]=88;
    unset($GLOBALS["source"]);$GLOBALS["source"]=$GLOBALS["replacement"];
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$seed=2;$source=[$seed,7];$outside=&$source;
$next=33;$replacement=[$next,8];$produced=0;$key=null;$tail=7;
set_error_handler("null_returned_reference_key",E_DEPRECATED);
$a=[
0=>9,
$key=>null_returned_reference_array(),
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=55;$copy[4]=77;$outside[0]=66;
$fresh=null_returned_reference_array();$source[0]=99;
echo "R:",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$outside[0],":",$outside[1],":",$source[0],":",$replacement[0],":",$fresh[0],":",$fresh[1],":",$a[4],":",$copy[4],":",$key,":",$produced,";";
unset($a,$copy,$fresh,$source,$outside,$replacement,$key,$seed,$next,$tail,$produced);
echo "U:",isset($a),":",isset($copy),":",isset($fresh),":",isset($source),":",isset($outside),";";
''',
}
