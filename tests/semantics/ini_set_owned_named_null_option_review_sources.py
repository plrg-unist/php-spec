#!/usr/bin/env python3
"""Named intrinsic invocation keeps numeric wrapper trace slots and early captures."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-named-null-throw-keeps-numeric-wrapper-args': br'''<?php
declare(strict_types=1);
function iniOwnedNamedReviewValue65() {
    global $call, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++;
    $call = ini_get(...); $option = 'value-option65'; $value = 'value-live65';
    return $early;
}
function iniOwnedNamedReviewOption65() {
    global $call, $option, $value, $effects;
    echo 'O|'; $effects++; ini_set('precision', '7');
    $call = 'constant'; $option = 'option-live65'; $value = 'option-value65';
    return null;
}
function iniOwnedNamedReviewDeprecated65($level, $message) {
    global $call, $option, $value, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $call = 'ini_get'; $option = 'precision'; $value = 'handler-value65';
    ini_set('precision', '10'); define('SOURCE65PEER', 2131);
    $saved = new Exception('named-owned65-stop'); throw $saved;
}
function iniOwnedNamedReviewCaller65() {
    global $call, $option, $value, $effects, $warnings, $saved;
    $call = ini_set(...); $keep = $call; $option = 'initial-option65';
    $part = 'named-owned'; $value = $part . '-value65';
    $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('iniOwnedNamedReviewDeprecated65', 8192);
    try {
        $result = $call->__invoke(value: iniOwnedNamedReviewValue65(), option: iniOwnedNamedReviewOption65());
        echo 'BAD';
    } catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        $trace = $e->getTrace(); $args = $trace[2]['args'];
        echo '|', $args[0] === null ? 'N' : 'BAD', '|', $args[1];
        echo '|', $result, '|', $effects, '|', $warnings, '|', $call;
        echo '|', $option, '|', $value, '|', ini_get('precision');
        echo '|', constant('SOURCE65PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep('precision', '12'), '|', ini_get('precision'), '|', $result;
}
echo 'B|'; iniOwnedNamedReviewCaller65();
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
