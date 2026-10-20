#!/usr/bin/env python3
"""Unpack retirement preserves the earlier owning INI array value and callee."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-unpack-array-values-default-and-explicit-return-normalize-inner-value': br'''<?php
function ownedUnpackArrayTrue75($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$call = ini_set(...); $keep = $call; $warnings = 0; $result = 99;
echo 'B|';
try {
    try { $result = $call(...[3 => null, 7 => [2777]]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|T|'; set_error_handler('ownedUnpackArrayTrue75', 8192);
    try { $result = $keep->__invoke(...['value' => [2783], 'option' => null]); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args']; $wrapper = $trace[1]['args'];
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $wrapper[0] === null ? 'N' : ($wrapper[0] === '' ? 'E' : 'BAD');
        echo '|', $api[1][0], '|', $wrapper[1][0], '|', $result, '|', $warnings;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'captured-owned-unpack-array-before-later-option-cow-and-pack-retirement': br'''<?php
function ownedUnpackArrayOption75() {
    global $call, $replacement, $value, $arrayKeep, $effects;
    echo 'O|'; $effects++; $arrayKeep[0] = 'option-array75';
    $call = $replacement; $value = 0; ini_set('precision', '7'); return null;
}
function ownedUnpackArrayFalse75($level, $message) {
    global $call, $value, $arrayKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array75'; $call = 'constant'; $value = 'handler-value75';
    ini_set('precision', '8'); return false;
}
echo 'B|';
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$part = 'captured'; $value = [$part . '-unpack-array75']; $arrayKeep = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('ownedUnpackArrayFalse75', 8192);
try { $result = $call(...['value' => $value, 'option' => ownedUnpackArrayOption75()]); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call, '|', $value, '|', $arrayKeep[0], '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-owned-unpack-array-option-before-weak-explicit-mixed-value-error': br'''<?php
declare(strict_types=1);
function strictOwnedUnpackArrayPack75() {
    global $call, $replacement, $value, $arrayKeep, $pack, $effects;
    $earlier = $pack; echo 'P|'; $effects++; $arrayKeep[0] = 0;
    $call = $replacement; $value = 0; $pack = [0, 0];
    ini_set('precision', '9'); return $earlier;
}
function strictOwnedUnpackArrayTrue75($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$value = [2797]; $arrayKeep = $value; $pack = [5 => null, 9 => $value];
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictOwnedUnpackArrayTrue75', 8192);
echo 'B|';
try {
    try { $result = $call(...strictOwnedUnpackArrayPack75()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $arrayKeep[0], '|', $pack[1], '|', $value, '|', ini_get('precision');
    }
    echo '|E|';
    try { $result = $keep->__invoke(...[3 => null, 'value' => []]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result, '|', $warnings, '|', $effects, '|', ini_get('precision'); }
} finally { restore_error_handler(); echo '|Z'; }
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
