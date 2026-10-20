#!/usr/bin/env python3
"""Retained INI receivers preserve live element references in rejected arrays."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-null-alias-array-api-and-wrapper-see-post-trace-cell-write': br'''<?php
function ownedNullAliasArrayTrue82($level, $message) {
    global $leaf, $arrayKeep, $value, $warnings, $call, $replacement;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'true-array82'; $arrayKeep[] = 43; $value = 0; $call = $replacement;
    ini_set('precision', '9'); return true;
}
$seed = 'runtime'; $leaf = $seed . '-owned-array82';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$warnings = 0; $result = 99; echo 'B|';
try {
    try { $result = $call(null, $value); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    set_error_handler('ownedNullAliasArrayTrue82', 8192); echo '|T|';
    try { $result = $call->__invoke(null, $value); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|'; $trace = $e->getTrace();
        $leaf = 'after-error82';
        echo $trace[0]['args'][0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $trace[1]['args'][0] === null ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1][0] === 'after-error82' ? 'L' : 'BAD';
        echo '|', $trace[1]['args'][1][0] === 'after-error82' ? 'L' : 'BAD';
        echo '|', isset($trace[0]['args'][1][1]) || isset($trace[1]['args'][1][1]) ? 'BAD' : 'A';
        echo '|', $arrayKeep[1], '|', $result, '|', $warnings;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'captured-owned-null-alias-array-before-live-owner-and-cell-writes': br'''<?php
function ownedNullAliasArrayValue82() {
    global $call, $option, $value, $leaf, $arrayKeep, $effects, $replacement;
    $earlier = $value; echo 'V|'; $effects++;
    $leaf = 'value-array82'; $arrayKeep[] = 31;
    $call = $replacement; $option = 'precision'; $value = 0;
    ini_set('precision', '7'); return $earlier;
}
function ownedNullAliasArrayFalse82($level, $message) {
    global $call, $option, $value, $leaf, $arrayKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'handler-array82'; $arrayKeep[] = 37;
    $call = 'constant'; $option = 'precision'; $value = 'handler-value82';
    ini_set('precision', '8'); return false;
}
$seed = 'runtime'; $leaf = $seed . '-owned-array82';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = ini_set(...); $keep = $call; $replacement = ini_get(...); $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('ownedNullAliasArrayFalse82', 8192);
echo 'B|';
try { $result = $call($option, ownedNullAliasArrayValue82()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $old[0], '|', $arrayKeep[0], '|', $arrayKeep[1], '|', $arrayKeep[2];
    echo '|', isset($old[1]) ? 'BAD' : 'A', '|', $call, '|', $option, '|', $value, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-owned-null-alias-array-then-same-owner-explicit-weak-reception': br'''<?php
declare(strict_types=1);
function strictOwnedNullAliasArrayValue82() {
    global $call, $option, $value, $leaf, $arrayKeep, $effects, $replacement;
    $earlier = $value; echo 'V|'; $effects++;
    $leaf = 'strict-array82'; $arrayKeep[] = 31;
    $call = $replacement; $option = 'precision'; $value = 0;
    ini_set('precision', '9'); return $earlier;
}
function strictOwnedNullAliasArrayTrue82($level, $message) {
    global $warnings, $leaf;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'weak-array82'; return true;
}
$seed = 'runtime'; $leaf = $seed . '-owned-array82';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = ini_set(...); $keep = $call; $replacement = ini_get(...); $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictOwnedNullAliasArrayTrue82', 8192);
echo 'B|';
try {
    try { $result = $call($option, strictOwnedNullAliasArrayValue82()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $old[0], '|', $arrayKeep[1], '|', isset($old[1]) ? 'BAD' : 'A', '|', $value, '|', ini_get('precision');
    }
    echo '|E|';
    try { $result = $keep->__invoke(null, $old); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $warnings, '|', $old[0], '|', $arrayKeep[0], '|', $arrayKeep[1];
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
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
