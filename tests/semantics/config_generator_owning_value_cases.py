"""Outside-retained by-value Generators keep copied owning option arguments."""

ARRAY_COW = b'''<?php
function owningArray77() {
    $array=[4];echo "Y0;";yield 0=>$array;
    $array[0]=5;echo "T:A:",$array[0],";";
    echo "Y1;";yield 1=>7;
    echo "F;";
}
ini_set("precision",14);$gen=owningArray77();$result=99;echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "C:A:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),";";
    $trace=$error->getTrace();echo "P:A:",$trace[0]["args"][0][0],";";
    unset($trace,$error);
}
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($gen,$result);
'''

INSTANCE_WEAK = b'''<?php
class OwningValue77 {public int $value=4;}
function owningInstance77() {
    $payload=new OwningValue77();
    $GLOBALS["watch"]=WeakReference::create($payload);
    echo "Y0;";yield 0=>$payload;
    $payload->value=5;
    unset($payload);
    echo "T:O:",(int)($GLOBALS["watch"]->get()!==null),";";
    echo "Y1;";yield 1=>7;
    echo "F:O:",(int)($GLOBALS["watch"]->get()!==null),";";
}
ini_set("precision",14);$watch=null;$gen=owningInstance77();$result=99;echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "C:O:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($watch->get()!==null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][0];
    echo "P:O:",(int)($arg===$watch->get()),":",$arg->value,";";
    unset($arg,$trace,$error);
}
echo "U:",(int)($watch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($gen,$watch,$result);
'''

CASES = {
    'config-generator-owning-array-cow': ARRAY_COW,
    'config-generator-owning-instance-weak': INSTANCE_WEAK,
}

EXPECTED = {
    'config-generator-owning-array-cow': b'B;Y0;T:A:5;Y1;F;C:A:1:99:14;P:A:4;R:14:9;',
    'config-generator-owning-instance-weak': b'B;Y0;T:O:1;Y1;F:O:1;C:O:1:99:14:1;P:O:1:5;U:1;R:14:9;',
}
