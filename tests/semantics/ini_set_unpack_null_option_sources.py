#!/usr/bin/env python3
"""Native-first NULL-option INI calls through direct and selected unpacking."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'direct-unpack-null-default-and-named-mixed-true-handlers': br'''<?php
function unpackNullTrue68($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
echo 'B|', ini_set(...[3 => null, 7 => 2293]) === false ? 'F' : 'BAD';
$warnings = 0; set_error_handler('unpackNullTrue68', 8192);
try {
    echo '|', ini_set(...['value' => 2297, 'option' => null]) === false ? 'F' : 'BAD';
    echo '|', ini_set(...[null, 'value' => 2309]) === false ? 'F' : 'BAD';
    echo '|', $warnings, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
''',
    'captured-selected-unpack-null-before-later-array-option-effects': br'''<?php
function unpackNullValue68() {
    global $call, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++; ini_set('precision', '6');
    $call = 'ini_get'; $option = 'value-option68'; $value = 'after-value68'; return $early;
}
function unpackNullOption68() {
    global $call, $option, $value, $effects;
    echo 'O|'; $effects++; ini_set('precision', '7');
    $call = 'constant'; $option = 'precision'; $value = 'after-option68'; return null;
}
function unpackNullFalse68($level, $message) {
    global $call, $option, $value, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8');
    $call = 'ini_get'; $option = 'precision'; $value = 'handler-unpack68'; return false;
}
function unpackNullCaller68() {
    global $call, $option, $value, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $part = 'captured'; $value = $part . '-unpack68';
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('unpackNullFalse68', 8192);
    try {
        $result = $call(...['value' => unpackNullValue68(), 'option' => unpackNullOption68()]);
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision');
        echo '|', $effects, '|', $warnings, '|', $call, '|', $option, '|', $value;
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', ini_set(...['value' => '11', 'option' => 'precision']), '|', ini_get('precision');
}
echo 'B|'; unpackNullCaller68();
''',
    'strict-selected-unpack-null-keeps-early-numeric-api-value': br'''<?php
declare(strict_types=1);
function strictUnpackNullPack68() {
    global $call, $value, $effects, $pack;
    $early = $value; echo 'P|'; $effects++; ini_set('precision', '9');
    $call = 'constant'; $value = 0; $pack = [5 => null, 9 => $early]; return $pack;
}
function strictUnpackNullHandler68($level, $message) {
    global $warnings;
    echo 'BAD|'; $warnings++; return true;
}
function strictUnpackNullCaller68() {
    global $call, $value, $effects, $warnings, $pack;
    $call = 'InI_SeT'; $value = 2321; $effects = 0; $warnings = 0; $result = 99; $pack = [];
    set_error_handler('strictUnpackNullHandler68', 8192);
    try {
        try { $result = $call(...strictUnpackNullPack68()); echo 'BAD'; }
        catch (TypeError $e) {
            $trace = $e->getTrace(); $args = $trace[0]['args'];
            echo $e->getMessage(), '|', $args[0] === null ? 'N' : 'BAD', '|', $args[1];
            echo '|', $result, '|', $effects, '|', $warnings, '|', $call, '|', $value, '|', ini_get('precision');
        }
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictUnpackNullCaller68();
''',
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'B|V|O|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
