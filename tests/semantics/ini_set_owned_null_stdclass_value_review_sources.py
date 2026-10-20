#!/usr/bin/env python3
"""An intrinsic owner and shared stdClass survive a named NULL handler throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-null-stdclass-throw-keeps-owner-and-shared-value': br'''<?php
declare(strict_types=1);
function iniOwnedNullStdReviewOption74() {
    global $call, $option, $value, $objectKeep, $effects;
    echo 'O|'; $effects++; $objectKeep->mark = 'option-mark74';
    $call = ini_get(...); $option = 'precision'; $value = 997;
    return null;
}
function iniOwnedNullStdReviewDeprecated74($level, $message) {
    global $call, $option, $value, $objectKeep, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'handler-mark74';
    $call = 'constant'; $option = 'handler-option74'; $value = 123;
    ini_set('precision', '10'); define('SOURCE74PEER', 2731);
    $saved = new Exception('owned-null-stdclass74-stop'); throw $saved;
}
echo 'B|';
$call = ini_set(...); $keep = $call; $option = null;
$value = new stdClass(); $part = 'owned'; $value->mark = $part . '-stdclass-peer74';
$objectKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniOwnedNullStdReviewDeprecated74', 8192);
try {
    $result = $call->__invoke(value: $value, option: iniOwnedNullStdReviewOption74()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings, '|', $objectKeep === $old ? 'S' : 'BAD';
    echo '|', $old->mark, '|', ini_get('precision'), '|', constant('SOURCE74PEER');
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
