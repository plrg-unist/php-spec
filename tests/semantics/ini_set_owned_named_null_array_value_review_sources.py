#!/usr/bin/env python3
"""An explicit named intrinsic call retains its owner and earlier array on throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-named-null-array-throw-keeps-owner-and-captured-value': br'''<?php
declare(strict_types=1);
function iniOwnedNamedArrayReviewOption73() {
    global $call, $option, $value, $arrayKeep, $effects;
    echo 'O|'; $effects++; $arrayKeep[0] = 'option-array73';
    $call = ini_get(...); $option = 'precision'; $value = 997;
    return null;
}
function iniOwnedNamedArrayReviewDeprecated73($level, $message) {
    global $call, $option, $value, $arrayKeep, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array73';
    $call = 'constant'; $option = 'handler-option73'; $value = 123;
    ini_set('precision', '10'); define('SOURCE73PEER', 2677);
    $saved = new Exception('owned-named-array73-stop'); throw $saved;
}
echo 'B|';
$call = ini_set(...); $keep = $call; $option = null;
$part = 'owned-named'; $value = [$part . '-array73']; $arrayKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniOwnedNamedArrayReviewDeprecated73', 8192);
try {
    $result = $call->__invoke(value: $value, option: iniOwnedNamedArrayReviewOption73()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings, '|', $arrayKeep[0], '|', $old[0];
    echo '|', ini_get('precision'), '|', constant('SOURCE73PEER');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '12'), '|', ini_get('precision'), '|', $result;
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
