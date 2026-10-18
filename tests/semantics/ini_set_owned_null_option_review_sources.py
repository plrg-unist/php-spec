#!/usr/bin/env python3
"""A retained intrinsic Closure keeps raw NULL captures across explicit invocation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-null-option-throw-keeps-original-closure': br'''<?php
declare(strict_types=1);
function iniOwnedReviewValue64() {
    global $call, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++;
    $call = ini_get(...); $option = 'value-option64'; $value = 'value-live64';
    return $early;
}
function iniOwnedReviewDeprecated64($level, $message) {
    global $call, $option, $value, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $call = 'constant'; $option = 'handler-option64'; $value = 'handler-value64';
    ini_set('precision', '10'); define('SOURCE64PEER', 2099);
    $saved = new Exception('owned64-stop'); throw $saved;
}
function iniOwnedReviewCaller64() {
    global $call, $option, $value, $effects, $warnings, $saved;
    $call = ini_set(...); $keep = $call; $option = null;
    $part = 'owned'; $value = $part . '-value64';
    $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('iniOwnedReviewDeprecated64', 8192);
    try {
        $result = $call->__invoke($option, iniOwnedReviewValue64());
        echo 'BAD';
    } catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $effects, '|', $warnings, '|', $call;
        echo '|', $option, '|', $value, '|', ini_get('precision');
        echo '|', constant('SOURCE64PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep('precision', '11'), '|', ini_get('precision'), '|', $result;
}
echo 'B|'; iniOwnedReviewCaller64();
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
