#!/usr/bin/env python3
"""Separate unpack groups preserve earlier NULL and owning ARRAY captures."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'two-pack-null-array-default-and-explicit-reversed-returned-trace': br'''<?php
function iniTwoPackTrue86($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$keep = ini_set(...); $warnings = 0; $result = 99; echo 'B|';
try {
    try { $result = ini_set(...[3 => null], ...[7 => [3433]]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|E|'; set_error_handler('iniTwoPackTrue86', 8192);
    try { $result = $keep->__invoke(...['value' => [3449]], ...['option' => null]); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args']; $wrapper = $trace[1]['args'];
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $wrapper[0] === null ? 'N' : 'BAD';
        echo '|', $api[1][0], '|', $wrapper[1][0], '|', $result, '|', $warnings;
    }
    echo '|O|';
    try { $result = ini_set(...['option' => null], ...[[0]]); echo 'BAD'; }
    catch (Error $e) { echo $e->getMessage(), '|', $result, '|', $warnings; }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'two-pack-null-and-array-captures-survive-later-group-effects': br'''<?php
function iniTwoPackValue86() {
    global $call, $optionPack, $value, $arrayKeep, $effects;
    $earlier = [7 => $value]; echo 'P|'; $effects++;
    $optionPack = [3 => 'precision']; $arrayKeep[0] = 'pack-array86';
    $call = 'ini_get'; $value = 0; return $earlier;
}
function iniTwoPackFalse86($level, $message) {
    global $call, $value, $arrayKeep, $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array86'; $call = 'constant'; $value = 'handler-value86';
    ini_set('precision', '8'); return false;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call; $option = null; $optionPack = [3 => $option];
$part = 'captured'; $value = [$part . '-two-pack-array86']; $arrayKeep = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('iniTwoPackFalse86', 8192);
try { $result = $call(...$optionPack, ...iniTwoPackValue86()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $optionPack[3], '|', $arrayKeep[0], '|', $call, '|', $value;
    echo '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-two-pack-option-priority-before-same-owner-explicit-mixed-reception': br'''<?php
declare(strict_types=1);
function iniTwoPackStrictValue86() {
    global $call, $replacement, $optionPack, $value, $arrayKeep, $effects;
    $earlier = [9 => $value]; echo 'P|'; $effects++;
    $optionPack = [5 => 'precision']; $arrayKeep[0] = 0;
    $call = $replacement; $value = 0; return $earlier;
}
function iniTwoPackStrictTrue86($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    ini_set('precision', '8'); return true;
}
echo 'B|'; $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$option = null; $optionPack = [5 => $option]; $value = [3461]; $arrayKeep = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('iniTwoPackStrictTrue86', 8192);
try {
    try { $result = $call(...$optionPack, ...iniTwoPackStrictValue86()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $optionPack[5], '|', $arrayKeep[0], '|', $value;
    }
    echo '|E|';
    try { $result = $keep->__invoke(...[3 => null], ...['value' => []]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings; }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'B|P|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
