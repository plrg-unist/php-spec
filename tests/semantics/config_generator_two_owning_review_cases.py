"""Two copied sends preserve multiplicity and identity for one shared object."""

BODY = b'''<?php
class TwoOwningReviewPayload80 {public int $tag=13;}
function twoOwningReviewBody80() {
    $payload=new TwoOwningReviewPayload80();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y0;";yield 0=>$payload;
    echo "Y1;";yield 1=>$payload;
    $payload->tag=31;echo "M:",$payload->tag,";";unset($payload);
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function twoOwningReviewFactory80() {
    $gen=twoOwningReviewBody80();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";return $gen;
}
ini_set("precision",14);$genWatch=null;$payloadWatch=null;$result=99;
$saved=new Exception("two-owning-review80");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...twoOwningReviewFactory80());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
    $trace=$error->getTrace();
    $arg0=$trace[0]["args"][0];$arg1=$trace[0]["args"][1];
    echo "A:",(int)($arg0===$arg1),":",
        (int)($arg0===$payloadWatch->get()),":",$arg0->tag,":",$arg1->tag,";";
    unset($arg0,$arg1,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
}
echo "U:",(int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-two-owning-same-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-two-owning-same-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;Y1;M:31;T;'
EXPECTED = {
    'config-generator-two-owning-same-object-typeerror':
        PREFIX + b'E:1:99:6:1:0;A:1:1:31:31;U:1;R:6:9;',
    'config-generator-two-owning-same-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:1;U:1;R:6:9;',
}
