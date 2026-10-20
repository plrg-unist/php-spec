#!/usr/bin/env python3
"""A saved pack preserves object identity while shared property writes stay live."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-unpack-null-stdclass-throw-keeps-shared-object': br'''<?php
function iniUnpackStdclassReviewPack77() {
    global $call, $value, $objectKeep, $pack, $effects;
    $earlier = $pack; echo 'P|'; $effects++; $objectKeep->mark = 'pack-mark77';
    $call = 'ini_get'; $value = 997; return $earlier;
}
function iniUnpackStdclassReviewDeprecated77($level, $message) {
    global $call, $value, $objectKeep, $pack, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $pack['value'] = 0; $pack['option'] = 'precision'; $objectKeep->mark = 'handler-mark77';
    $call = 'constant'; $value = 123;
    ini_set('precision', '10'); define('SOURCE77PEER', 2939);
    $saved = new Exception('unpack-stdclass77-stop'); throw $saved;
}
echo 'B|';
$call = 'InI_SeT'; $keep = $call;
$part = 'unpack-stdclass'; $value = new stdClass(); $value->mark = $part . '-peer77';
$objectKeep = $value; $pack = ['value' => $value, 'option' => null]; $packOld = $pack;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniUnpackStdclassReviewDeprecated77', 8192);
try {
    $result = $call(...iniUnpackStdclassReviewPack77()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $packOld['value'] === $objectKeep ? 'S' : 'BAD';
    echo '|', $packOld['value']->mark, '|', $pack['value'];
    echo '|', ini_get('precision'), '|', constant('SOURCE77PEER');
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
