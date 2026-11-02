<?php
$mode="normal";
class FactoryAliasPayload {public int $tag=4;}
function &factoryAliasBody() {
    $first=new FactoryAliasPayload();
    $GLOBALS["watch"]=WeakReference::create($first);
    echo "Y0;";yield 0=>$first;
    $last=$first;$first=9;
    $GLOBALS["alias0"] =& $last;$GLOBALS["alias1"] =& $last;
    echo "Y1;";yield 1=>$last;
    $last->tag=8;echo "M:",$last->tag,";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") throw $GLOBALS["saved"];
}
function factoryAlias() {
    $g=factoryAliasBody();
    $GLOBALS["gw"]=WeakReference::create($g);
    echo "P;";return $g;
}
ini_set("precision",14);
$watch=null;$gw=null;$alias0=null;$alias1=null;
$saved=new Exception("saved");$result=99;
echo "B;";
try {$result=ini_set(...factoryAlias());echo "BAD;";}
catch(TypeError $e) {
    echo "E:",(int)($gw->get()===null),":",(int)($watch->get()!==null),":",$result,":",ini_get("precision"),";";
    $trace=$e->getTrace();$a=$trace[0]["args"][0];$b=$trace[0]["args"][1];
    echo "A:",(int)($a===$b),":",$a->tag,":",$b->tag,";";
    unset($a,$b,$trace,$e);
}
catch(Exception $e) {
    echo "S:",(int)($e===$saved),":",(int)($gw->get()===null),":",(int)($watch->get()!==null),";";
}
echo "L:",(int)($watch->get()!==null),";";
unset($alias0);echo "U0:",(int)($watch->get()!==null),";";
unset($alias1);echo "U1:",(int)($watch->get()!==null),";";
