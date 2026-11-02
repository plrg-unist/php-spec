"""A factory returned BYREF Generator leaves a changed ARRAY in two aliases."""

BODY = b'''<?php
class FactoryOwningAliasReview88 {public int $tag=4;}
function &factoryOwningAliasBodyReview88() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $old=new FactoryOwningAliasReview88();
    $GLOBALS["oldWatch"]=WeakReference::create($old);
    $payload=[13,$old];$old=null;
    $GLOBALS["slot"] =& $payload;
    $GLOBALS["alias"] =& $payload;
    echo "Y1;";yield 1=>$payload;
    $payload[0]=31;
    $new=new FactoryOwningAliasReview88();$new->tag=8;
    $GLOBALS["newWatch"]=WeakReference::create($new);
    $payload[1]=$new;$new=null;
    echo "C:",$payload[0],":",
        (int)($GLOBALS["oldWatch"]->get()!==null),":",
        (int)($GLOBALS["newWatch"]->get()!==null),":",
        $payload[1]->tag,";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function factoryOwningAliasReview88() {
    $gen=factoryOwningAliasBodyReview88();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision",14);$slot=null;$alias=null;
$genWatch=null;$oldWatch=null;$newWatch=null;$result=99;
$saved=new Exception("factory-owning-alias-review88");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...factoryOwningAliasReview88());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        $slot[0],":",$alias[0],":",
        (int)($oldWatch->get()===null),":",
        (int)($newWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][1];
    echo "Q:",$trace[0]["args"][0],":",$arg[0],":",
        (int)($arg[1]===$oldWatch->get()),":",$arg[1]->tag,";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        $slot[0],":",$alias[0],":",
        (int)($oldWatch->get()===null),":",
        (int)($newWatch->get()===null),";";
}
echo "L:",(int)($genWatch->get()===null),":",
    (int)($oldWatch->get()===null),":",
    (int)($newWatch->get()===null),":",$slot[0],":",$alias[0],";";
unset($slot);echo "A:",$alias[0],":",
    (int)($newWatch->get()===null),";";
unset($alias);echo "U:",(int)($newWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$oldWatch,$newWatch,$result,$mode);
'''

CASES = {
    'config-generator-factory-owning-alias-array-cow-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-factory-owning-alias-array-cow-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;Y1;C:31:1:1:8;T;'
EXPECTED = {
    'config-generator-factory-owning-alias-array-cow-typeerror':
        PREFIX + b'E:1:99:6:1:31:31:0:0;Q:precision:13:1:4;L:1:1:0:31:31;A:31:0;U:1;R:6:9;',
    'config-generator-factory-owning-alias-array-cow-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:31:31:1:0;L:1:1:0:31:31;A:31:0;U:1;R:6:9;',
}
