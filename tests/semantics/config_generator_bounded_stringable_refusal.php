<?php
class ConvertibleFirst {
    function __toString(): string {echo "STR;";return "precision";}
}
function &convertibleBody() {
    $first=new ConvertibleFirst();echo "Y0;";yield 0=>$first;
    $last=6;echo "Y1;";yield 1=>$last;echo "T;";
}
function convertibleFactory() {$g=convertibleBody();echo "P;";return $g;}
ini_set("precision",14);echo "B;";
try {$result=ini_set(...convertibleFactory());echo "R:",$result,":",ini_get("precision"),";";}
catch(Throwable $e) {echo "E:",get_class($e),":",$e->getMessage(),";";}
