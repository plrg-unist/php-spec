#!/usr/bin/env python3
"""Packed INI reception holds distinct callable and shared object values."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-unpacked-stdclass-default-and-explicit-return-share-api-wrapper-value': br'''<?php
function ownedUnpackStdTrue78($level, $message) {
    global $warnings, $value, $objectKeep;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'true78'; $value = 0; return true;
}
$empty = new stdClass(); $emptyKeep = $empty;
$value = new stdClass(); $value->mark = 'initial78'; $objectKeep = $value;
$call = ini_set(...); $keep = $call; $warnings = 0; $result = 99;
echo 'B|';
try {
    try { $result = $call(...[3 => null, 7 => $empty]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|E|'; set_error_handler('ownedUnpackStdTrue78', 8192);
    try { $result = $keep->__invoke(...['value' => $value, 'option' => null]); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args']; $wrapper = $trace[1]['args'];
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $wrapper[0] === null ? 'N' : ($wrapper[0] === '' ? 'E' : 'BAD');
        echo '|', $api[1] === $objectKeep ? 'I' : 'BAD';
        echo '|', $wrapper[1] === $objectKeep ? 'I' : 'BAD';
        echo '|', $api[1]->mark, '|', $result, '|', $warnings;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'captured-owned-unpack-stdclass-before-shared-option-and-live-value-effects': br'''<?php
function ownedUnpackStdOption78() {
    global $call, $replacement, $value, $objectKeep, $effects;
    echo 'O|'; $effects++; $objectKeep->mark = 'option78';
    $call = $replacement; $value = 0; ini_set('precision', '7'); return null;
}
function ownedUnpackStdFalse78($level, $message) {
    global $call, $value, $objectKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'handler78'; $call = 'constant'; $value = 'handler-value78';
    ini_set('precision', '8'); return false;
}
echo 'B|'; $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$part = 'captured'; $value = new stdClass(); $value->mark = $part . '-owned-pack-object78'; $objectKeep = $value;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('ownedUnpackStdFalse78', 8192);
try { $result = $call(...['value' => $value, 'option' => ownedUnpackStdOption78()]); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call, '|', $value, '|', $objectKeep->mark, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-owned-unpack-stdclass-option-before-weak-explicit-mixed-value-error': br'''<?php
declare(strict_types=1);
function strictOwnedUnpackStdPack78() {
    global $call, $replacement, $value, $objectKeep, $pack, $effects;
    $earlier = $pack; echo 'P|'; $effects++; $objectKeep->mark = 'strict78';
    $call = $replacement; $value = 0; $pack = [0, 0];
    ini_set('precision', '9'); return $earlier;
}
function strictOwnedUnpackStdTrue78($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$value = new stdClass(); $value->mark = 'before78'; $objectKeep = $value;
$pack = [5 => null, 9 => $value]; $empty = new stdClass(); $emptyKeep = $empty;
$effects = 0; $warnings = 0; $result = 99; set_error_handler('strictOwnedUnpackStdTrue78', 8192);
echo 'B|';
try {
    try { $result = $call(...strictOwnedUnpackStdPack78()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $objectKeep->mark, '|', $pack[1], '|', $value, '|', ini_get('precision');
    }
    echo '|E|';
    try { $result = $keep->__invoke(...[3 => null, 'value' => $empty]); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result, '|', $warnings, '|', $effects, '|', ini_get('precision'); }
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
