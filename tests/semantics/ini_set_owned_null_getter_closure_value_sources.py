#!/usr/bin/env python3
"""Retained setters reject getter Closure values without invoking them."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-null-getter-default-and-explicit-true-keep-both-callables': br'''<?php
function ownedNullGetterTrue80($level, $message) {
    global $warnings, $call, $getterKeep, $value;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $call = $getterKeep; $value = 0;
    ini_set('precision', '9'); return true;
}
$call = ini_set(...); $keep = $call;
$getterName = 'InI_GeT'; $value = $getterName(...); $getterKeep = $value;
$warnings = 0; $result = 99; echo 'B|';
try {
    try { $result = $call(null, $value); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    set_error_handler('ownedNullGetterTrue80', 8192); echo '|T|';
    try { $result = $call->__invoke(null, $value); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|'; $trace = $e->getTrace();
        echo $trace[0]['args'][0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $trace[1]['args'][0] === null ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1] === $getterKeep ? 'I' : 'BAD';
        echo '|', $trace[1]['args'][1] === $getterKeep ? 'I' : 'BAD';
        echo '|', $result, '|', $warnings, '|', $value;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|G|', $getterKeep('precision'), '|R|', $keep('precision', '11'), '|', $getterKeep('precision');
''',
    'captured-owned-null-getter-before-live-callee-becomes-value': br'''<?php
function ownedNullGetterValue80() {
    global $call, $option, $value, $getterKeep, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $call = $getterKeep; $option = 'precision'; $value = 0;
    ini_set('precision', '7'); return $earlier;
}
function ownedNullGetterFalse80($level, $message) {
    global $call, $option, $value, $getterKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $call = $getterKeep; $option = 'precision'; $value = 'handler-value80';
    ini_set('precision', '8'); return false;
}
$call = ini_set(...); $keep = $call; $value = ini_get(...); $getterKeep = $value; $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('ownedNullGetterFalse80', 8192);
echo 'B|';
try { $result = $call($option, ownedNullGetterValue80()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call === $getterKeep ? 'G' : 'BAD', '|', $option, '|', $value, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|G|', $getterKeep('precision'), '|R|', $keep('precision', '11'), '|', $getterKeep('precision');
''',
    'strict-owned-null-getter-ordinary-then-same-owner-explicit-weak': br'''<?php
declare(strict_types=1);
function strictOwnedNullGetterValue80() {
    global $call, $option, $value, $getterKeep, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $call = $getterKeep; $option = 'precision'; $value = 0;
    ini_set('precision', '9'); return $earlier;
}
function strictOwnedNullGetterTrue80($level, $message) {
    global $call, $getterKeep, $value, $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $call = $getterKeep; $value = 0;
    ini_set('precision', '10'); return true;
}
$call = ini_set(...); $keep = $call; $value = ini_get(...); $getterKeep = $value; $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictOwnedNullGetterTrue80', 8192);
echo 'B|';
try {
    try { $result = $call($option, strictOwnedNullGetterValue80()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call === $getterKeep ? 'G' : 'BAD', '|', $value, '|', ini_get('precision');
    }
    echo '|M|';
    try { $result = $keep->__invoke(null, $getterKeep); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings; }
} finally { restore_error_handler(); echo '|Z'; }
echo '|G|', $getterKeep('precision'), '|R|', $keep('precision', '12'), '|', $getterKeep('precision');
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
