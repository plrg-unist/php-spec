"""Outside aliases retain the changed ARRAY cell after Generator retirement."""

BODY = b'''<?php
class RefOwningAliasReview84 {public int $tag=4;}
function &refOwningAliasReview84() {
    global $slot;
    $option="precision";echo "Y0;";yield 0=>$option;
    echo "Y1;";yield 1=>$slot;
    $slot[0]=31;
    $new=new RefOwningAliasReview84();
    $GLOBALS["newWatch"]=WeakReference::create($new);
    $slot[1]=$new;$new=null;
    echo "C:",$slot[0],":",
        (int)($GLOBALS["oldWatch"]->get()!==null),":",
        (int)($GLOBALS["newWatch"]->get()!==null),";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);
$old=new RefOwningAliasReview84();
$oldWatch=WeakReference::create($old);
$slot=[13,$old];$old=null;$alias =& $slot;$newWatch=null;
$gen=refOwningAliasReview84();$genWatch=WeakReference::create($gen);
$result=99;$saved=new Exception("reference-owning-alias-review84");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        $alias[0],":",(int)($oldWatch->get()===null),":",
        (int)($newWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][1];
    echo "P:",$trace[0]["args"][0],":",$arg[0],":",
        (int)($arg[1]===$oldWatch->get()),";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        $alias[0],":",(int)($oldWatch->get()===null),":",
        (int)($newWatch->get()===null),";";
}
echo "L:",(int)($oldWatch->get()===null),":",
    (int)($newWatch->get()===null),":",$alias[0],";";
unset($gen);echo "G:",(int)($genWatch->get()===null),":",
    (int)($oldWatch->get()===null),":",
    (int)($newWatch->get()===null),":",$alias[0],";";
unset($slot);echo "A:",$alias[0],":",
    (int)($newWatch->get()===null),";";
unset($alias);echo "U:",(int)($newWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$oldWatch,$newWatch,$result,$mode);
'''

CASES = {
    'config-generator-reference-owning-alias-array-cow-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-owning-alias-array-cow-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;C:31:1:1;T;'
EXPECTED = {
    'config-generator-reference-owning-alias-array-cow-typeerror':
        PREFIX + b'E:1:99:6:0:31:0:0;P:precision:13:1;L:1:0:31;G:1:1:0:31;A:31:0;U:1;R:6:9;',
    'config-generator-reference-owning-alias-array-cow-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:31:1:0;L:1:0:31;G:1:1:0:31;A:31:0;U:1;R:6:9;',
}
