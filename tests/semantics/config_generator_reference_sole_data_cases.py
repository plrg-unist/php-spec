"""Native-first sole-DATA Generator reference-cell retirement witnesses."""

NORMAL = b'''<?php
function &soleReferenceNormal73() {
    global $input;
    $option="precision";echo "Y0;";yield 0=>$option;
    $input=17;
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;echo "T;";
}
ini_set("precision","14");$input=soleReferenceNormal73();
$watch=WeakReference::create($input);$result=99;echo "B;";
$result=ini_set(...$input);
echo "A:",$result,":",ini_get("precision"),":",
    (int)($watch->get()===null),":",$input,";";
echo "R:",ini_set("precision","9"),":",ini_get("precision"),";";
unset($input,$watch,$result);
'''

TERMINAL_THROW = b'''<?php
function &soleReferenceThrow73() {
    global $input,$saved;
    $option="precision";echo "Y0;";yield 0=>$option;
    $input=17;
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision","6");echo "T;";throw $saved;
}
ini_set("precision","14");$saved=new Exception("sole-reference-stop73");
$input=soleReferenceThrow73();$watch=WeakReference::create($input);
$result=99;echo "B;";
try {$result=ini_set(...$input);echo "BAD;";}
catch (Exception $caught) {
    echo "C:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($watch->get()===null),":",$input,";";
}
echo "R:",ini_set("precision","9"),":",ini_get("precision"),";";
unset($input,$watch,$result,$caught,$saved);
'''

CASES = {
    'config-generator-reference-sole-data-normal': NORMAL,
    'config-generator-reference-sole-data-terminal-throw': TERMINAL_THROW,
}

EXPECTED = {
    'config-generator-reference-sole-data-normal':
        b'B;Y0;Y1;T;A:14:7:1:17;R:7:9;',
    'config-generator-reference-sole-data-terminal-throw':
        b'B;Y0;Y1;T;C:1:1:99:6:1:17;R:6:9;',
}
