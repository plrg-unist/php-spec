#!/usr/bin/env python3
"""NULL option reception rejects a retained getter Closure without invoking it."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'null-getter-closure-default-and-true-handler-keep-original-value': br'''<?php
function nullGetterTrue79($level, $message) {
    global $warnings, $value;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $value = 0; ini_set('precision', '9'); return true;
}
$value = ini_get(...); $getterKeep = $value;
$call = 'InI_SeT'; $callKeep = $call; $warnings = 0; $result = 99;
echo 'B|';
try {
    try { $result = ini_set(null, $value); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|T|'; set_error_handler('nullGetterTrue79', 8192);
    try { $result = $call(null, $value); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args'];
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $api[1] === $getterKeep ? 'I' : 'BAD';
        echo '|', $result, '|', $warnings, '|', $value;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $callKeep('precision', '11'), '|', $getterKeep('precision');
''',
    'captured-selected-null-getter-before-value-and-callee-rebinding': br'''<?php
function nullGetterValue79() {
    global $call, $option, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $call = 'ini_get'; $option = 'precision'; $value = 0;
    ini_set('precision', '7'); return $earlier;
}
function nullGetterFalse79($level, $message) {
    global $call, $option, $value, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $call = 'constant'; $option = 'precision'; $value = 'handler-value79';
    ini_set('precision', '8'); return false;
}
echo 'B|'; $call = 'InI_SeT'; $callKeep = $call;
$getterName = 'InI_GeT'; $value = $getterName(...); $getterKeep = $value; $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('nullGetterFalse79', 8192);
try { $result = $call($option, nullGetterValue79()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call, '|', $option, '|', $value, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|G|', $getterKeep('precision'), '|R|', $callKeep('precision', '11'), '|', $getterKeep('precision');
''',
    'strict-null-getter-option-rejection-after-value-effects': br'''<?php
declare(strict_types=1);
function strictNullGetterValue79() {
    global $call, $option, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $call = 'ini_get'; $option = 'precision'; $value = 0;
    ini_set('precision', '9'); return $earlier;
}
function strictNullGetterTrue79($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$value = ini_get(...); $getterKeep = $value; $option = null;
$call = 'InI_SeT'; $callKeep = $call;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictNullGetterTrue79', 8192);
echo 'B|';
try { $result = $call($option, strictNullGetterValue79()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call, '|', $option, '|', $value, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|G|', $getterKeep('precision'), '|R|', $callKeep('precision', '11'), '|', $getterKeep('precision');
''',
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'B|V|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
