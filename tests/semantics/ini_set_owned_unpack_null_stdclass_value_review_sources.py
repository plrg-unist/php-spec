#!/usr/bin/env python3
"""The held INI receiver and unpacked object survive shared writes and throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-unpack-null-stdclass-throw-keeps-shared-value': br'''<?php
declare(strict_types=1);
function iniOwnedUnpackStdclassReviewPack78() {
    global $call, $replacement, $value, $objectKeep, $pack, $effects;
    $earlier = $pack; echo 'P|'; $effects++; $objectKeep->mark = 'pack-mark78';
    $call = $replacement; $value = 997; return $earlier;
}
function iniOwnedUnpackStdclassReviewDeprecated78($level, $message) {
    global $call, $value, $objectKeep, $pack, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $pack['value'] = 0; $pack['option'] = 'precision'; $objectKeep->mark = 'handler-mark78';
    $call = 'constant'; $value = 123;
    ini_set('precision', '10'); define('SOURCE78PEER', 2999);
    $saved = new Exception('owned-unpack-stdclass78-stop'); throw $saved;
}
echo 'B|';
$call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$part = 'owned-unpack-stdclass'; $value = new stdClass(); $value->mark = $part . '-peer78';
$objectKeep = $value; $pack = ['value' => $value, 'option' => null]; $packOld = $pack;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniOwnedUnpackStdclassReviewDeprecated78', 8192);
try {
    $result = $call->__invoke(...iniOwnedUnpackStdclassReviewPack78()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $packOld['value'] === $objectKeep ? 'S' : 'BAD';
    echo '|', $packOld['value']->mark, '|', $pack['value'];
    echo '|', ini_get('precision'), '|', constant('SOURCE78PEER');
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
