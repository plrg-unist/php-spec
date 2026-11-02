<?php
function &sameCellBody() {
    $value=[13];echo "Y0;";yield 0=>$value;
    $value[0]=31;echo "Y1;";yield 1=>$value;
    $value[0]=42;ini_set("precision",6);echo "T:",$value[0],";";
}
ini_set("precision",14);echo "B;";
try {ini_set(...sameCellBody());echo "BAD;";}
catch(TypeError $error) {
    $trace=$error->getTrace();
    $first=$trace[0]["args"][0];$second=$trace[0]["args"][1];
    echo "A:",$first[0],":",$second[0],":",ini_get("precision"),";";
    unset($first,$second,$trace,$error);
}
