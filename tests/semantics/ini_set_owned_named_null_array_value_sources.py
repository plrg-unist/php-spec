#!/usr/bin/env python3
"""Retained INI_SET Closures receive named NULL options before array rejection."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-named-array-values-return-through-api-and-wrapper-frames': br'''<?php
function ownedNamedArrayTrue73($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$call = ini_set(...); $keep = $call; $warnings = 0; $result = 99;
set_error_handler('ownedNamedArrayTrue73', 8192);
echo 'B|';
try {
    try { $result = $call->__invoke(value: [2617], option: null); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args']; $wrapper = $trace[1]['args'];
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $wrapper[0] === null ? 'N' : ($wrapper[0] === '' ? 'E' : 'BAD');
        echo '|', $api[1][0], '|', $wrapper[1][0], '|', $result, '|', $warnings;
    }
    echo '|M|';
    try { $result = $keep(null, value: []); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result, '|', $warnings; }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep(value: '11', option: 'precision'), '|', ini_get('precision');
''',
    'captured-owned-named-array-before-live-owner-replacement-and-cow': br'''<?php
function ownedNamedArrayOption73() {
    global $call, $replacement, $option, $value, $arrayKeep, $effects;
    echo 'O|'; $effects++; $arrayKeep[0] = 'option-array73';
    $call = $replacement; $option = 'precision'; $value = 0;
    ini_set('precision', '7'); return null;
}
function ownedNamedArrayFalse73($level, $message) {
    global $call, $option, $value, $arrayKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array73'; $call = 'constant'; $option = 'precision';
    $value = 'handler-value73'; ini_set('precision', '8'); return false;
}
echo 'B|';
$call = ini_set(...); $keep = $call; $replacement = ini_get(...); $option = null;
$part = 'captured'; $value = [$part . '-owned-array73']; $arrayKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('ownedNamedArrayFalse73', 8192);
try { $result = $call(value: $value, option: ownedNamedArrayOption73()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call, '|', $option, '|', $value, '|', $arrayKeep[0], '|', $old[0], '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep(value: '11', option: 'precision'), '|', ini_get('precision');
''',
    'strict-owned-named-array-option-before-weak-explicit-value-error': br'''<?php
declare(strict_types=1);
function strictOwnedArrayOption73() {
    global $call, $replacement, $value, $arrayKeep, $effects;
    echo 'O|'; $effects++; $arrayKeep[0] = 0; $call = $replacement; $value = 0;
    ini_set('precision', '9'); return null;
}
function strictOwnedArrayTrue73($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$value = [2633]; $arrayKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictOwnedArrayTrue73', 8192);
echo 'B|';
try {
    try { $result = $call(value: $value, option: strictOwnedArrayOption73()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $arrayKeep[0], '|', $old[0], '|', ini_get('precision');
    }
    echo '|E|';
    try { $result = $keep->__invoke(null, value: [2641]); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $warnings, '|', $effects, '|', $value, '|', ini_get('precision');
    }
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
