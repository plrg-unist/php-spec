<?php
class RetainedPayload {public int $tag=4;}
function &retainedBody() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $value=new RetainedPayload();echo "Y1;";yield 1=>$value;
    $value->tag=8;ini_set("precision",6);echo "T;";
}
function retainedFactory() {
    $gen=retainedBody();
    $GLOBALS["retained"]=$gen;
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";return $gen;
}
ini_set("precision",14);$retained=null;$genWatch=null;echo "B;";
try {ini_set(...retainedFactory());echo "BAD;";}
catch(TypeError $error) {
    echo "E:",(int)($genWatch->get()!==null),":",ini_get("precision"),";";
    $trace=$error->getTrace();echo "A:",$trace[0]["args"][1]->tag,";";
    unset($trace,$error);
}
echo "L:",(int)($genWatch->get()!==null),";";
unset($retained);echo "U:",(int)($genWatch->get()===null),";";
