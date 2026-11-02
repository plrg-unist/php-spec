<?php
class OldPayload {public int $tag=4;}
class SidePayload {function __destruct() {echo "D;";}}
function &effectfulFirstCellBody() {
    $first=new OldPayload();echo "Y0;";yield 0=>$first;
    $first=new SidePayload();
    $last=new OldPayload();$last->tag=8;
    echo "Y1;";yield 1=>$last;
    ini_set("precision",6);echo "T;";
}
ini_set("precision",14);echo "B;";
try {ini_set(...effectfulFirstCellBody());echo "BAD;";}
catch(TypeError $error) {
    $trace=$error->getTrace();
    $firstArg=$trace[0]["args"][0];$lastArg=$trace[0]["args"][1];
    echo "E:",$firstArg->tag,":",$lastArg->tag,":",ini_get("precision"),";";
    unset($firstArg,$lastArg,$trace,$error);
}
