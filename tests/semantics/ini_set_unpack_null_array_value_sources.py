#!/usr/bin/env python3
"""Selected string INI calls retain inner array values across unpack retirement."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'unpacked-array-values-direct-default-and-selected-mixed-return': br'''<?php
function unpackArrayTrue76($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$call = 'InI_SeT'; $keep = $call; $warnings = 0; $result = 99;
echo 'B|';
try {
    try { $result = ini_set(...[3 => null, 7 => [2833]]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|M|'; set_error_handler('unpackArrayTrue76', 8192);
    try { $result = $call(...[3 => null, 'value' => [2843]]); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args'];
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $api[1][0], '|', $result, '|', $warnings;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'captured-string-unpack-array-before-option-cow-and-live-callee-rebinding': br'''<?php
function unpackArrayOption76() {
    global $call, $value, $arrayKeep, $effects;
    echo 'O|'; $effects++; $arrayKeep[0] = 'option-array76';
    $call = 'ini_get'; $value = 0; ini_set('precision', '7'); return null;
}
function unpackArrayFalse76($level, $message) {
    global $call, $value, $arrayKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array76'; $call = 'constant'; $value = 'handler-value76';
    ini_set('precision', '8'); return false;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call;
$part = 'captured'; $value = [$part . '-unpack-array76']; $arrayKeep = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('unpackArrayFalse76', 8192);
try { $result = $call(...['value' => $value, 'option' => unpackArrayOption76()]); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call, '|', $value, '|', $arrayKeep[0], '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-string-unpack-array-option-after-pack-and-live-value-effects': br'''<?php
declare(strict_types=1);
function strictUnpackArrayPack76() {
    global $call, $value, $arrayKeep, $pack, $effects;
    $earlier = $pack; echo 'P|'; $effects++; $arrayKeep[0] = 0;
    $call = 'ini_get'; $value = 0; $pack = [0, 0];
    ini_set('precision', '9'); return $earlier;
}
function strictUnpackArrayTrue76($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
$call = 'InI_SeT'; $keep = $call;
$value = [2857]; $arrayKeep = $value; $pack = [5 => null, 9 => $value];
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictUnpackArrayTrue76', 8192);
echo 'B|';
try { $result = $call(...strictUnpackArrayPack76()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $arrayKeep[0], '|', $pack[1], '|', $value, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'B|O|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
