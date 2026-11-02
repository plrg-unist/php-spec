"""A BYVAL factory returns a BYREF Generator with a copied first ARRAY cell."""

BODY = b'''<?php
class FactoryFirstOwningReview91 {public int $tag=4;}
function &factoryFirstOwningBodyReview91() {
    $old=new FactoryFirstOwningReview91();
    $GLOBALS["oldWatch"]=WeakReference::create($old);
    $payload=[13,$old];$old=null;
    echo "Y0;";yield 0=>$payload;
    $payload[0]=31;
    $new=new FactoryFirstOwningReview91();$new->tag=8;
    $GLOBALS["newWatch"]=WeakReference::create($new);
    $payload[1]=$new;$new=null;
    echo "C:",$payload[0],":",
        (int)($GLOBALS["oldWatch"]->get()!==null),":",
        (int)($GLOBALS["newWatch"]->get()!==null),":",
        $payload[1]->tag,";";
    $payload=9;
    echo "W:",(int)($GLOBALS["oldWatch"]->get()!==null),":",
        (int)($GLOBALS["newWatch"]->get()===null),";";
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision",6);echo "T:",$value,";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function factoryFirstOwningReview91() {
    $gen=factoryFirstOwningBodyReview91();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision",14);$genWatch=null;$oldWatch=null;$newWatch=null;
$result=99;$saved=new Exception("factory-first-owning-review91");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...factoryFirstOwningReview91());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($oldWatch->get()===null),":",
        (int)($newWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][0];
    echo "A:",$arg[0],":",(int)($arg[1]===$oldWatch->get()),":",
        $arg[1]->tag,":",$trace[0]["args"][1],";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($oldWatch->get()===null),":",
        (int)($newWatch->get()===null),";";
}
echo "L:",(int)($genWatch->get()===null),":",
    (int)($oldWatch->get()===null),":",
    (int)($newWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$oldWatch,$newWatch,$result,$mode);
'''

CASES = {
    'config-generator-factory-first-owning-reference-array-cow-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-factory-first-owning-reference-array-cow-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;C:31:1:1:8;W:1:1;Y1;T:8;'
EXPECTED = {
    'config-generator-factory-first-owning-reference-array-cow-typeerror':
        PREFIX + b'E:1:99:6:1:0:1;A:13:1:4:7;L:1:1:1;R:6:9;',
    'config-generator-factory-first-owning-reference-array-cow-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:1:1;L:1:1:1;R:6:9;',
}
