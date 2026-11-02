"""A retained BYREF Generator keeps a changed ARRAY cell after its old copy dies."""

BODY = b'''<?php
class RefOwningLiveReview83 {public int $tag=4;}
function &refOwningLiveReview83() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $old=new RefOwningLiveReview83();
    $GLOBALS["oldWatch"]=WeakReference::create($old);
    $payload=[13,$old];$old=null;
    echo "Y1;";yield 1=>$payload;
    $payload[0]=31;
    $new=new RefOwningLiveReview83();
    $GLOBALS["newWatch"]=WeakReference::create($new);
    $payload[1]=$new;$new=null;
    echo "C:",$payload[0],":",
        (int)($GLOBALS["oldWatch"]->get()!==null),":",
        (int)($GLOBALS["newWatch"]->get()!==null),";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);$oldWatch=null;$newWatch=null;
$gen=refOwningLiveReview83();$genWatch=WeakReference::create($gen);
$result=99;$saved=new Exception("reference-owning-live-review83");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($oldWatch->get()===null),":",
        (int)($newWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][1];
    echo "A:",$trace[0]["args"][0],":",$arg[0],":",
        (int)($arg[1]===$oldWatch->get()),";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($oldWatch->get()===null),":",
        (int)($newWatch->get()===null),";";
}
echo "L:",(int)($oldWatch->get()===null),":",
    (int)($newWatch->get()===null),";";
unset($gen);echo "V:",(int)($genWatch->get()===null),":",
    (int)($oldWatch->get()===null),":",
    (int)($newWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$oldWatch,$newWatch,$result,$mode);
'''

CASES = {
    'config-generator-reference-owning-live-array-cow-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-owning-live-array-cow-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;C:31:1:1;T;'
EXPECTED = {
    'config-generator-reference-owning-live-array-cow-typeerror':
        PREFIX + b'E:1:99:6:0:0:0;A:precision:13:1;L:1:0;V:1:1:1;R:6:9;',
    'config-generator-reference-owning-live-array-cow-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:1:0;L:1:0;V:1:1:1;R:6:9;',
}
