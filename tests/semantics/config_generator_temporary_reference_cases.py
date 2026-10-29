"""Native-first temporary BYREF Generator unpack witnesses."""

NORMAL = b'''<?php
function &temporaryReferenceNormal75() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision","6");echo "T;";
}
ini_set("precision","14");$result=99;echo "B;";
$result=ini_set(...temporaryReferenceNormal75());
echo "A:",$result,":",ini_get("precision"),";";
echo "R:",ini_set("precision","9"),":",ini_get("precision"),";";
'''

TERMINAL_THROW = b'''<?php
function &temporaryReferenceThrow75() {
    global $saved;
    $option="precision";echo "Y0;";yield 0=>$option;
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision","6");echo "T;";throw $saved;
}
ini_set("precision","14");$saved=new Exception("temporary-reference-stop75");
$result=99;echo "B;";
try {$result=ini_set(...temporaryReferenceThrow75());echo "BAD;";}
catch (Exception $caught) {
    echo "C:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),";";
}
echo "R:",ini_set("precision","9"),":",ini_get("precision"),";";
unset($caught,$saved,$result);
'''

CASES = {
    'config-generator-temporary-reference-normal': NORMAL,
    'config-generator-temporary-reference-terminal-throw': TERMINAL_THROW,
}

EXPECTED = {
    'config-generator-temporary-reference-normal':
        b'B;Y0;Y1;T;A:6:7;R:7:9;',
    'config-generator-temporary-reference-terminal-throw':
        b'B;Y0;Y1;T;C:1:1:99:6;R:6:9;',
}
