#!/usr/bin/env python3
"""Rejected array values retain live primitive reference cells across callbacks."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'null-alias-array-default-and-returned-trace-sees-later-cell-write': br'''<?php
function nullAliasArrayTrue81($level, $message) {
    global $leaf, $arrayKeep, $value, $warnings, $call;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'true-array81'; $arrayKeep[] = 41; $value = 0; $call = 'ini_get';
    ini_set('precision', '9'); return true;
}
$seed = 'runtime'; $leaf = $seed . '-array81';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = 'InI_SeT'; $keep = $call; $warnings = 0; $result = 99; echo 'B|';
try {
    try { $result = ini_set(null, $value); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    set_error_handler('nullAliasArrayTrue81', 8192); echo '|T|';
    try { $result = $call(null, $value); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|'; $trace = $e->getTrace();
        $leaf = 'after-error81';
        echo $trace[0]['args'][0] === '' ? 'E' : 'BAD';
        echo '|', $trace[0]['args'][1][0] === 'after-error81' ? 'L' : 'BAD';
        echo '|', isset($trace[0]['args'][1][1]) ? 'BAD' : 'A';
        echo '|', $old[0], '|', $arrayKeep[0], '|', $arrayKeep[1];
        echo '|', $result, '|', $warnings, '|', $value;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'captured-null-alias-array-before-reference-write-and-live-value-rebinding': br'''<?php
function nullAliasArrayValue81() {
    global $call, $option, $value, $leaf, $arrayKeep, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $leaf = 'value-array81'; $arrayKeep[] = 31;
    $call = 'ini_get'; $option = 'precision'; $value = 0;
    ini_set('precision', '7'); return $earlier;
}
function nullAliasArrayFalse81($level, $message) {
    global $call, $option, $value, $leaf, $arrayKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'handler-array81'; $arrayKeep[] = 37;
    $call = 'constant'; $option = 'precision'; $value = 'handler-value81';
    ini_set('precision', '8'); return false;
}
$seed = 'runtime'; $leaf = $seed . '-array81';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = 'InI_SeT'; $keep = $call; $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('nullAliasArrayFalse81', 8192);
echo 'B|';
try { $result = $call($option, nullAliasArrayValue81()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $old[0], '|', $arrayKeep[0], '|', $arrayKeep[1], '|', $arrayKeep[2];
    echo '|', isset($old[1]) ? 'BAD' : 'A', '|', $call, '|', $option, '|', $value, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-null-alias-array-rejects-option-after-shared-cell-and-container-effects': br'''<?php
declare(strict_types=1);
function strictNullAliasArrayValue81() {
    global $call, $option, $value, $leaf, $arrayKeep, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $leaf = 'strict-array81'; $arrayKeep[] = 31;
    $call = 'ini_get'; $option = 'precision'; $value = 0;
    ini_set('precision', '9'); return $earlier;
}
function strictNullAliasArrayTrue81($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$seed = 'runtime'; $leaf = $seed . '-array81';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$call = 'InI_SeT'; $keep = $call; $option = null;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictNullAliasArrayTrue81', 8192);
echo 'B|';
try { $result = $call($option, strictNullAliasArrayValue81()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $old[0], '|', $arrayKeep[1], '|', isset($old[1]) ? 'BAD' : 'A', '|', $value, '|', ini_get('precision');
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
