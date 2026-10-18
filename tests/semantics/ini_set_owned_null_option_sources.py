#!/usr/bin/env python3
"""Native-first retained intrinsic Closure NULL-option calls and weak wrappers."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'retained-intrinsic-null-default-and-true-handler': br'''<?php
function intrinsicNullTrue64($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++;
    ini_set('precision', '8'); return true;
}
$call = ini_set(...); $keep = $call; $warnings = 0;
echo 'B|', $call(null, 2071) === false ? 'F' : 'BAD', '|', ini_get('precision'), '|';
set_error_handler('intrinsicNullTrue64', 8192);
echo $keep(null, 'value64') === false ? 'F' : 'BAD';
restore_error_handler(); echo '|', $warnings, '|', ini_get('precision');
''',
    'captured-intrinsic-owner-before-value-rebinding-and-fallback': br'''<?php
function capturedIntrinsicValue64() {
    global $call, $replacement, $value, $effects;
    $early = $value; echo 'V|'; $effects++;
    $call = $replacement; $value = 'after-value64'; return $early;
}
function capturedIntrinsicNullHandler64($level, $message) {
    global $value, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    ini_set('precision', '9'); $value = 'handler-value64'; return false;
}
function capturedIntrinsicCaller64() {
    global $call, $replacement, $value, $effects, $warnings;
    $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
    $part = 'captured'; $value = $part . '-value64'; $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('capturedIntrinsicNullHandler64', 8192);
    try {
        $result = $call(null, capturedIntrinsicValue64());
        echo $result === false ? 'F' : 'BAD', '|', $call('precision');
        echo '|', $effects, '|', $warnings, '|', $value, '|', $call === $keep ? 'BAD' : 'D';
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|', $keep('precision', '10'), '|', ini_get('precision');
}
echo 'B|'; capturedIntrinsicCaller64();
''',
    'strict-intrinsic-call-before-weak-explicit-invoke-null': br'''<?php
declare(strict_types=1);
function strictIntrinsicValue64() {
    global $value, $effects;
    $early = $value; echo 'V|'; $effects++; ini_set('precision', '9'); $value = 0; return $early;
}
function strictIntrinsicNullHandler64($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8'); return true;
}
function strictIntrinsicCaller64() {
    global $value, $effects, $warnings;
    $call = ini_set(...); $keep = $call; $value = 2089; $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('strictIntrinsicNullHandler64', 8192);
    try {
        try { $result = $call(null, strictIntrinsicValue64()); echo 'BAD'; }
        catch (TypeError $e) {
            echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings, '|', ini_get('precision');
        }
        echo '|E|'; $result = $keep->__invoke(null, 2093);
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision'), '|', $warnings, '|', $effects, '|', $value;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictIntrinsicCaller64();
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
