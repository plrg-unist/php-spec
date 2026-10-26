"""Generator spread acquisition, retained suspension and real body failure."""

CASES = {
    'array-generator-unpack-review-acquisition-states': b'''<?php
function array_spread_states() {
    echo "B;";yield "first" => 2;
    echo "M;";yield 7 => 3;
    echo "E;";
}
$it=array_spread_states();$later=7;
echo "P0;";$peek=$it->current();echo "V0:",$peek,";";
$out=[4=>88,...$it,9];
echo "O0:",$out===[4=>88,"first"=>2,5=>3,6=>9],":",$it->valid(),";";
unset($out,$peek);
$it=array_spread_states();$dest=101;
echo "P1;";$it->current();$it->next();
try {
    $dest=[...$it,($later=88)];
    $later=99;echo "BAD1;";
} catch (Exception $e) {
    echo "E1:",$e->getMessage(),":",$e->getLine(),":",$e->getPrevious()===null,":",$e->getTrace()===[],";";
}
unset($e);
echo "R1:",$dest===101,":",$later,":",$it->current(),":",$it->valid(),";";
$it->next();echo "D1:",$it->valid(),";";
$dest=102;
echo "P2;";
try {
    $dest=[...$it,($later=88)];
    $later=99;echo "BAD2;";
} catch (Exception $e) {
    echo "E2:",$e->getMessage(),":",$e->getLine(),":",$e->getPrevious()===null,":",$e->getTrace()===[],";";
}
unset($e);
echo "R2:",$dest===102,":",$later,":",$it->current()===null,":",$it->valid(),":",$it->getReturn()===null,";";
unset($it,$later,$dest);
echo "U:",isset($it),":",isset($e),":",isset($dest),";";
''',
    'array-generator-unpack-review-shared-invalid-key': b'''<?php
function array_spread_shared_bad() {
    try {
        echo "B;";unset($GLOBALS["it"]);
        yield true => $GLOBALS["row"];
        echo "A;";$GLOBALS["row"][0]=44;
        yield "later" => $GLOBALS["row"];
    } finally {echo "F;";}
}
$seed=2;$row=[$seed];$it=array_spread_shared_bad();$hold=$it;$dest=100;$later=7;
echo "P;";
try {
    $dest=[$seed,...$it,($later=88)];
    $later=99;echo "BAD;";
} catch (Error $e) {
    echo "E:",$e->getMessage(),":",$e->getLine(),":",$e->getPrevious()===null,":",$e->getTrace()===[],";";
}
unset($e);
echo "C:",$dest===100,":",$later,":",isset($it),":",$hold->valid(),":",$hold->current()[0],";";
$row[0]=33;
echo "S:",$hold->current()[0],":",$row[0],";";
$hold->next();echo "N:",$hold->key(),":",$hold->current()[0],":",$row[0],":",$hold->valid(),";";
$hold->next();
echo "R:",$hold->valid(),":",$hold->current()===null,":",$hold->getReturn()===null,":",$dest===100,":",$later,";";
unset($seed,$row,$hold,$dest,$later);
echo "U:",isset($it),":",isset($hold),":",isset($row),";";
''',
    'array-generator-unpack-review-body-supplied-throw': b'''<?php
function array_spread_body_throw() {
    try {
        unset($GLOBALS["it"]);$GLOBALS["second"]=new Exception("supplied");echo "B;";
        yield "ok" => $GLOBALS["row"];
        echo "A;";$GLOBALS["row"][0]=44;throw $GLOBALS["second"];
    } finally {echo "F;";}
}
$seed=2;$row=[$seed];$it=array_spread_body_throw();$hold=$it;$dest=100;$later=7;$second=null;
echo "P;";
try {
    $dest=[$seed,...$it,($later=88)];
    $later=99;echo "BAD;";
} catch (Exception $e) {
    echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest===100,":",$later,":",$row[0],":",isset($it),":",$hold->valid(),";";
    $trace=$e->getTrace();
    if (isset($trace[0])) {echo "T:",$trace[0]["function"],":",$trace[0]["line"],":",isset($trace[1]),";";}
    else {echo "T:empty;";}
}
unset($e,$trace);
echo "R:",$row[0],":",$dest===100,":",$later,":",$hold->valid(),":",$hold->current()===null,";";
unset($seed,$row,$hold,$dest,$later,$second);
echo "U:",isset($it),":",isset($hold),":",isset($second),";";
''',
}
