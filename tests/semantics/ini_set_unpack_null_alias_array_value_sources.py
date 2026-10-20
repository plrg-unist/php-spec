#!/usr/bin/env python3
"""One unpack snapshot keeps an array's shared reference cell live."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'unpacked-alias-array-default-and-explicit-live-api-wrapper-cell': br'''<?php
function unpackAliasArrayTrue84($level, $message) {
    global $warnings, $leaf, $arrayKeep, $call, $value;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'true-array84'; $arrayKeep[] = 43;
    $call = 'ini_get'; $value = 0; return true;
}
$seed = 'runtime'; $leaf = $seed . '-unpack-array84';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = ini_set(...); $keep = $call; $warnings = 0; $result = 99;
echo 'B|';
try {
    try { $result = ini_set(...[3 => null, 7 => $old]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|E|'; set_error_handler('unpackAliasArrayTrue84', 8192);
    try { $result = $keep->__invoke(...['value' => $old, 'option' => null]); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args']; $wrapper = $trace[1]['args'];
        $leaf = 'after-error84';
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $wrapper[0] === null ? 'N' : 'BAD';
        echo '|', $api[1][0] === 'after-error84' ? 'L' : 'BAD';
        echo '|', $wrapper[1][0] === 'after-error84' ? 'L' : 'BAD';
        echo '|', isset($api[1][1]) || isset($wrapper[1][1]) ? 'BAD' : 'A';
        echo '|', $arrayKeep[1], '|', $result, '|', $warnings;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'captured-unpack-alias-array-before-option-cell-and-live-value-effects': br'''<?php
function unpackAliasArrayOption84() {
    global $call, $option, $value, $arrayKeep, $leaf, $effects;
    $earlier = $option; echo 'O|'; $effects++;
    $leaf = 'option-array84'; $arrayKeep[] = 31;
    $call = 'ini_get'; $option = 'precision'; $value = 0; return $earlier;
}
function unpackAliasArrayFalse84($level, $message) {
    global $call, $option, $value, $arrayKeep, $leaf, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'handler-array84'; $arrayKeep[] = 37;
    $call = 'constant'; $option = 'precision'; $value = 'handler-value84';
    ini_set('precision', '8'); return false;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call; $option = null;
$seed = 'captured'; $leaf = $seed . '-pack-array84';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('unpackAliasArrayFalse84', 8192);
try { $result = $call(...['value' => $value, 'option' => unpackAliasArrayOption84()]); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $old[0], '|', $arrayKeep[0], '|', $arrayKeep[1], '|', $arrayKeep[2];
    echo '|', isset($old[1]) ? 'BAD' : 'A';
    echo '|', $call, '|', $option, '|', $value, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-owned-unpack-alias-array-then-same-owner-explicit-mixed-weak': br'''<?php
declare(strict_types=1);
function strictUnpackAliasArrayPack84() {
    global $call, $replacement, $value, $pack, $leaf, $arrayKeep, $effects;
    $earlier = $pack; echo 'P|'; $effects++;
    $leaf = 'strict-array84'; $arrayKeep[] = 31;
    $call = $replacement; $value = 0; $pack = [0, 0]; return $earlier;
}
function strictUnpackAliasArrayTrue84($level, $message) {
    global $warnings, $leaf;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'weak-array84'; ini_set('precision', '8'); return true;
}
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$seed = 'strict'; $leaf = $seed . '-pack-array84';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$pack = [5 => null, 9 => $value]; $packOld = $pack;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictUnpackAliasArrayTrue84', 8192);
echo 'B|';
try {
    try { $result = $call(...strictUnpackAliasArrayPack84()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $old[0], '|', $arrayKeep[1], '|', $pack[1], '|', $value, '|', ini_get('precision');
    }
    echo '|E|';
    try { $result = $keep->__invoke(...[3 => null, 'value' => $old]); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $warnings, '|', $effects;
        echo '|', $old[0], '|', $arrayKeep[0], '|', $arrayKeep[1], '|', ini_get('precision');
    }
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
