"""Copied owning prefixes retire independently of a retained Generator cache."""

BODY = b'''<?php
class OwningReviewPayload77 {public $tag=13;}
function owningReview77() {
    $payload=new OwningReviewPayload77();
    $GLOBALS["watch"]=WeakReference::create($payload);
    echo "Y0;";
    yield 0=>$payload;
    unset($payload);
    if ($GLOBALS["phase"]==="early") {
        echo "X:",(int)($GLOBALS["watch"]->get()!==null),";";
        ini_set("precision",6);
        throw $GLOBALS["saved"];
    }
    echo "Y1;";
    yield 1=>7;
    echo "F:",(int)($GLOBALS["watch"]->get()!==null),";";
    ini_set("precision",6);
    throw $GLOBALS["saved"];
}
ini_set("precision",14);$watch=null;$result=99;
$saved=new Exception("owning-prefix-review77");
$gen=owningReview77();
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (Exception $caught) {
    echo "E:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($watch->get()===null),";";
}
unset($caught,$saved,$gen);
echo "U:",(int)($watch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($watch,$result,$phase);
'''

CASES = {
    'config-generator-owning-prefix-retained-cache-throw':
        BODY + b'$phase="early";\n' + CALL,
    'config-generator-owning-prefix-replaced-cache-throw':
        BODY + b'$phase="terminal";\n' + CALL,
}

EXPECTED = {
    'config-generator-owning-prefix-retained-cache-throw':
        b'B;Y0;X:1;E:1:1:99:6:0;U:1;R:6:9;',
    'config-generator-owning-prefix-replaced-cache-throw':
        b'B;Y0;Y1;F:1;E:1:1:99:6:1;U:1;R:6:9;',
}
