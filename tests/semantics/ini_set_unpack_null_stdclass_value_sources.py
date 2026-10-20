#!/usr/bin/env python3
"""Unpacked INI object values retain identity and live shared properties."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'unpacked-stdclass-values-default-and-selected-mixed-shared-return': br'''<?php
function unpackStdTrue77($level, $message) {
    global $warnings, $value, $objectKeep;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'true77'; $value = 0; return true;
}
$empty = new stdClass(); $emptyKeep = $empty;
$value = new stdClass(); $value->mark = 'initial77'; $objectKeep = $value;
$call = 'InI_SeT'; $keep = $call; $warnings = 0; $result = 99;
echo 'B|';
try {
    try { $result = ini_set(...[3 => null, 7 => $empty]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|M|'; set_error_handler('unpackStdTrue77', 8192);
    try { $result = $call(...[3 => null, 'value' => $value]); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args'];
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $api[1] === $objectKeep ? 'I' : 'BAD';
        echo '|', $api[1]->mark, '|', $result, '|', $warnings;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'captured-string-unpack-stdclass-before-shared-option-and-live-value-effects': br'''<?php
function unpackStdOption77() {
    global $call, $value, $objectKeep, $effects;
    echo 'O|'; $effects++; $objectKeep->mark = 'option77';
    $call = 'ini_get'; $value = 0; ini_set('precision', '7'); return null;
}
function unpackStdFalse77($level, $message) {
    global $call, $value, $objectKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'handler77'; $call = 'constant'; $value = 'handler-value77';
    ini_set('precision', '8'); return false;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call;
$part = 'captured'; $value = new stdClass(); $value->mark = $part . '-pack-object77'; $objectKeep = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('unpackStdFalse77', 8192);
try { $result = $call(...['value' => $value, 'option' => unpackStdOption77()]); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call, '|', $value, '|', $objectKeep->mark, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-string-unpack-stdclass-option-after-shared-mark-and-pack-effects': br'''<?php
declare(strict_types=1);
function strictUnpackStdPack77() {
    global $call, $value, $objectKeep, $pack, $effects;
    $earlier = $pack; echo 'P|'; $effects++; $objectKeep->mark = 'strict77';
    $call = 'ini_get'; $value = 0; $pack = [0, 0];
    ini_set('precision', '9'); return $earlier;
}
function strictUnpackStdTrue77($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
$call = 'InI_SeT'; $keep = $call;
$value = new stdClass(); $value->mark = 'before77'; $objectKeep = $value;
$pack = [5 => null, 9 => $value];
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictUnpackStdTrue77', 8192);
echo 'B|';
try { $result = $call(...strictUnpackStdPack77()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $objectKeep->mark, '|', $pack[1], '|', $value, '|', ini_get('precision');
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
