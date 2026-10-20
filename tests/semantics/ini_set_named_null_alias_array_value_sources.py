#!/usr/bin/env python3
"""Named INI sends freeze array containers while their reference cells stay live."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'named-alias-array-true-handlers-and-live-api-wrapper-trace': br'''<?php
function namedNullAliasArrayTrue83($level, $message) {
    global $leaf, $arrayKeep, $value, $warnings, $call, $replacement;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'true-array83'; $arrayKeep[] = 43; $value = 0; $call = $replacement;
    return true;
}
$seed = 'runtime'; $leaf = $seed . '-named-array83';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$warnings = 0; $result = 99; set_error_handler('namedNullAliasArrayTrue83', 8192); echo 'B|';
try {
    try { $result = ini_set(value: $value, option: null); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|T|';
    try { $result = $keep->__invoke(null, value: $old); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|'; $trace = $e->getTrace();
        $leaf = 'after-error83';
        echo $trace[0]['args'][0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $trace[1]['args'][0] === null ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1][0] === 'after-error83' ? 'L' : 'BAD';
        echo '|', $trace[1]['args'][1][0] === 'after-error83' ? 'L' : 'BAD';
        echo '|', isset($trace[0]['args'][1][1]) || isset($trace[1]['args'][1][1]) ? 'BAD' : 'A';
        echo '|', $arrayKeep[2], '|', $result, '|', $warnings;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'named-alias-array-captured-before-option-cell-and-container-effects': br'''<?php
function namedNullAliasArrayOption83() {
    global $call, $option, $value, $leaf, $arrayKeep, $effects;
    $earlier = $option; echo 'O|'; $effects++;
    $leaf = 'option-array83'; $arrayKeep[] = 31;
    $call = 'ini_get'; $option = 'precision'; $value = 0;
    ini_set('precision', '7'); return $earlier;
}
function namedNullAliasArrayFalse83($level, $message) {
    global $call, $option, $value, $leaf, $arrayKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'handler-array83'; $arrayKeep[] = 37;
    $call = 'constant'; $option = 'precision'; $value = 'handler-value83';
    ini_set('precision', '8'); return false;
}
$seed = 'runtime'; $leaf = $seed . '-named-array83';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = 'InI_SeT'; $keep = $call; $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('namedNullAliasArrayFalse83', 8192);
echo 'B|';
try { $result = $call(value: $value, option: namedNullAliasArrayOption83()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $old[0], '|', $arrayKeep[0], '|', $arrayKeep[1], '|', $arrayKeep[2];
    echo '|', isset($old[1]) ? 'BAD' : 'A', '|', $call, '|', $option, '|', $value, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-owned-named-alias-array-then-same-owner-explicit-weak': br'''<?php
declare(strict_types=1);
function strictNamedNullAliasArrayOption83() {
    global $call, $option, $value, $leaf, $arrayKeep, $effects, $replacement;
    $earlier = $option; echo 'O|'; $effects++;
    $leaf = 'strict-array83'; $arrayKeep[] = 31;
    $call = $replacement; $option = 'precision'; $value = 0;
    ini_set('precision', '9'); return $earlier;
}
function strictNamedNullAliasArrayTrue83($level, $message) {
    global $warnings, $leaf;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'weak-array83'; return true;
}
$seed = 'runtime'; $leaf = $seed . '-named-array83';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = ini_set(...); $keep = $call; $replacement = ini_get(...); $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictNamedNullAliasArrayTrue83', 8192);
echo 'B|';
try {
    try { $result = $call(value: $value, option: strictNamedNullAliasArrayOption83()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $old[0], '|', $arrayKeep[1], '|', isset($old[1]) ? 'BAD' : 'A', '|', $value, '|', ini_get('precision');
    }
    echo '|E|';
    try { $result = $keep->__invoke(value: $old, option: null); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $warnings, '|', $old[0], '|', $arrayKeep[0], '|', $arrayKeep[1];
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
