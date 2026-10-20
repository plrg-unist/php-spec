#!/usr/bin/env python3
"""Retained INI_SET owners and shared stdClass values survive NULL reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-stdclass-values-default-and-explicit-return-keep-shared-trace-value': br'''<?php
function ownedStdclassTrue74($level, $message) {
    global $objectKeep, $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'true74'; return true;
}
$call = ini_set(...); $keep = $call; $value = new stdClass();
$value->mark = 'initial74'; $objectKeep = $value; $warnings = 0; $result = 99;
echo 'B|';
try {
    try { $result = $call(null, $value); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    echo '|T|'; set_error_handler('ownedStdclassTrue74', 8192);
    try { $result = $keep->__invoke(value: $value, option: null); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace(); $api = $trace[0]['args']; $wrapper = $trace[1]['args'];
        echo $e->getMessage(), '|', $api[0] === '' ? 'E' : 'BAD';
        echo '|', $trace[1]['function'] === '__invoke' ? 'W' : 'BAD';
        echo '|', $wrapper[0] === null ? 'N' : ($wrapper[0] === '' ? 'E' : 'BAD');
        echo '|', $api[1] === $objectKeep ? 'I' : 'BAD', '|', $wrapper[1] === $objectKeep ? 'I' : 'BAD';
        echo '|', $api[1]->mark, '|', $wrapper[1]->mark, '|', $result, '|', $warnings;
    }
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'captured-owned-stdclass-before-option-shared-write-and-live-owner-replacement': br'''<?php
function ownedStdclassOption74() {
    global $call, $replacement, $option, $value, $objectKeep, $effects;
    echo 'O|'; $effects++; $objectKeep->mark = 'option74';
    $call = $replacement; $option = 'precision'; $value = 0;
    ini_set('precision', '7'); return null;
}
function ownedStdclassFalse74($level, $message) {
    global $call, $option, $value, $objectKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'handler74'; $call = 'constant'; $option = 'precision';
    $value = 'handler-value74'; ini_set('precision', '8'); return false;
}
echo 'B|';
$call = ini_set(...); $keep = $call; $replacement = ini_get(...); $option = null;
$part = 'owned'; $value = new stdClass(); $value->mark = $part . '-stdclass74';
$objectKeep = $value; $old = $value; $effects = 0; $warnings = 0; $result = 99;
set_error_handler('ownedStdclassFalse74', 8192);
try { $result = $call(value: $value, option: ownedStdclassOption74()); echo 'BAD'; }
catch (TypeError $e) {
    echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
    echo '|', $call, '|', $option, '|', $value, '|', $old === $objectKeep ? 'S' : 'BAD';
    echo '|', $old->mark, '|', $objectKeep->mark, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep(value: '11', option: 'precision'), '|', ini_get('precision');
''',
    'strict-owned-stdclass-option-before-weak-explicit-mixed-value-rejection': br'''<?php
declare(strict_types=1);
function strictOwnedStdclassValue74() {
    global $call, $replacement, $value, $objectKeep, $effects;
    $earlier = $value; echo 'V|'; $effects++; $objectKeep->mark = 'strict-value74';
    $call = $replacement; $value = 0; ini_set('precision', '9'); return $earlier;
}
function strictOwnedStdclassTrue74($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$value = new stdClass(); $value->mark = 'strict74'; $objectKeep = $value; $old = $value;
$empty = new stdClass(); $effects = 0; $warnings = 0; $result = 99;
set_error_handler('strictOwnedStdclassTrue74', 8192); echo 'B|';
try {
    try { $result = $call(null, strictOwnedStdclassValue74()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $old === $objectKeep ? 'S' : 'BAD', '|', $old->mark, '|', $value, '|', ini_get('precision');
    }
    echo '|E|';
    try { $result = $keep->__invoke(null, value: $empty); echo 'BAD'; }
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
