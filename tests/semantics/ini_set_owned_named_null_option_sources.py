#!/usr/bin/env python3
"""Native-first named NULL options through retained intrinsic Closures."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-named-null-true-handlers-and-mixed-prefix': br'''<?php
function ownedNamedNullTrue65($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$call = ini_set(...); $keep = $call; $warnings = 0;
set_error_handler('ownedNamedNullTrue65', 8192);
echo 'B|', $call(value: 'literal-owned65', option: null) === false ? 'F' : 'BAD';
echo '|', $keep->__invoke(null, value: 2111) === false ? 'F' : 'BAD';
restore_error_handler(); echo '|', $warnings, '|', ini_get('precision');
''',
    'captured-owned-named-null-before-live-owner-and-option-writes': br'''<?php
function ownedNamedNullValue65() {
    global $call, $replacement, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++; ini_set('precision', '6');
    $call = $replacement; $option = 'value-option65'; $value = 'after-value65'; return $early;
}
function ownedNamedNullOption65() {
    global $call, $replacement, $option, $value, $effects;
    echo 'O|'; $effects++; ini_set('precision', '7');
    $call = $replacement; $option = 'precision'; $value = 'after-option65'; return null;
}
function ownedNamedNullFalse65($level, $message) {
    global $call, $option, $value, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8');
    $call = 'ini_get'; $option = 'precision'; $value = 'handler-owned65'; return false;
}
function ownedNamedNullCaller65() {
    global $call, $replacement, $option, $value, $effects, $warnings;
    $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
    $option = null; $part = 'captured'; $value = $part . '-owned-value65';
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('ownedNamedNullFalse65', 8192);
    try {
        $result = $call(value: ownedNamedNullValue65(), option: ownedNamedNullOption65());
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision');
        echo '|', $effects, '|', $warnings, '|', $call, '|', $option, '|', $value;
        echo '|', $call === $keep ? 'BAD' : 'D';
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep(value: '11', option: 'precision'), '|', ini_get('precision');
}
echo 'B|'; ownedNamedNullCaller65();
''',
    'strict-owned-named-call-before-weak-explicit-mixed-null': br'''<?php
declare(strict_types=1);
function strictOwnedNamedValue65() {
    global $call, $replacement, $value, $effects;
    $early = $value; echo 'V|'; $effects++; ini_set('precision', '9');
    $call = $replacement; $value = 0; return $early;
}
function strictOwnedNamedOption65() {
    global $call, $value, $effects;
    echo 'O|'; $effects++; $call = 'constant'; $value = 1; return null;
}
function strictOwnedNamedTrue65($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
function strictOwnedNamedCaller65() {
    global $call, $replacement, $value, $effects, $warnings;
    $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
    $value = 2129; $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('strictOwnedNamedTrue65', 8192);
    try {
        try { $result = $call(value: strictOwnedNamedValue65(), option: strictOwnedNamedOption65()); echo 'BAD'; }
        catch (TypeError $e) {
            echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings, '|', ini_get('precision');
        }
        echo '|E|'; $result = $keep->__invoke(null, value: 2137);
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision'), '|', $warnings, '|', $effects, '|', $value;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictOwnedNamedCaller65();
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
