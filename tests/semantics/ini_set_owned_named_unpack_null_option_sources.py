#!/usr/bin/env python3
"""Native-first named/mixed unpack through retained NULL-option INI Closures."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'owned-named-unpack-null-true-handlers-and-mixed-pack': br'''<?php
function ownedNamedUnpackTrue67($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$call = ini_set(...); $keep = $call; $warnings = 0;
set_error_handler('ownedNamedUnpackTrue67', 8192);
echo 'B|', $call(...['value' => 2237, 'option' => null]) === false ? 'F' : 'BAD';
echo '|', $keep->__invoke(...[null, 'value' => 2243]) === false ? 'F' : 'BAD';
restore_error_handler(); echo '|', $warnings, '|', ini_get('precision');
''',
    'captured-owned-named-unpack-before-later-array-option-effects': br'''<?php
function ownedNamedUnpackValue67() {
    global $call, $replacement, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++; ini_set('precision', '6');
    $call = $replacement; $option = 'value-option67'; $value = 'after-value67'; return $early;
}
function ownedNamedUnpackOption67() {
    global $call, $option, $value, $effects;
    echo 'O|'; $effects++; ini_set('precision', '7');
    $call = 'constant'; $option = 'precision'; $value = 'after-option67'; return null;
}
function ownedNamedUnpackFalse67($level, $message) {
    global $call, $option, $value, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8');
    $call = 'ini_get'; $option = 'precision'; $value = 'handler-named-pack67'; return false;
}
function ownedNamedUnpackCaller67() {
    global $call, $replacement, $option, $value, $effects, $warnings;
    $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
    $option = null; $part = 'captured'; $value = $part . '-named-pack67';
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('ownedNamedUnpackFalse67', 8192);
    try {
        $result = $call(...['value' => ownedNamedUnpackValue67(), 'option' => ownedNamedUnpackOption67()]);
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision');
        echo '|', $effects, '|', $warnings, '|', $call, '|', $option, '|', $value;
        echo '|', $call === $keep ? 'BAD' : 'D';
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep(...['option' => 'precision', 'value' => '11']), '|', ini_get('precision');
}
echo 'B|'; ownedNamedUnpackCaller67();
''',
    'strict-owned-named-unpack-before-weak-explicit-forward-pack': br'''<?php
declare(strict_types=1);
function strictOwnedNamedUnpackValue67() {
    global $call, $replacement, $value, $effects;
    $early = $value; echo 'V|'; $effects++; ini_set('precision', '9');
    $call = $replacement; $value = 0; return $early;
}
function strictOwnedNamedUnpackOption67() {
    global $call, $value, $effects;
    echo 'O|'; $effects++; $call = 'constant'; $value = 1; return null;
}
function strictOwnedNamedUnpackTrue67($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
function strictOwnedNamedUnpackCaller67() {
    global $call, $replacement, $value, $effects, $warnings;
    $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
    $value = 2273; $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('strictOwnedNamedUnpackTrue67', 8192);
    try {
        try { $result = $call(...['value' => strictOwnedNamedUnpackValue67(), 'option' => strictOwnedNamedUnpackOption67()]); echo 'BAD'; }
        catch (TypeError $e) {
            echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings, '|', ini_get('precision');
        }
        echo '|E|'; $result = $keep->__invoke(...['option' => null, 'value' => 2281]);
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision'), '|', $warnings, '|', $effects, '|', $value;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictOwnedNamedUnpackCaller67();
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
