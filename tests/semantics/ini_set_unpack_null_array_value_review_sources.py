#!/usr/bin/env python3
"""A selected unpacked INI call keeps its earlier inner array through a throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-unpack-null-array-throw-keeps-inner-snapshot': br'''<?php
function iniUnpackArrayReviewPack76() {
    global $call, $value, $arrayKeep, $pack, $effects;
    $earlier = $pack; echo 'P|'; $effects++; $arrayKeep[0] = 'pack-array76';
    $call = 'ini_get'; $value = 997; return $earlier;
}
function iniUnpackArrayReviewDeprecated76($level, $message) {
    global $call, $value, $arrayKeep, $pack, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $pack['value'] = [0]; $pack['option'] = 'precision'; $arrayKeep[0] = 'handler-array76';
    $call = 'constant'; $value = 123;
    ini_set('precision', '10'); define('SOURCE76PEER', 2879);
    $saved = new Exception('unpack-array76-stop'); throw $saved;
}
echo 'B|';
$call = 'InI_SeT'; $keep = $call;
$part = 'unpack-array'; $value = [$part . '-peer76']; $arrayKeep = $value;
$pack = ['value' => $value, 'option' => null]; $packOld = $pack;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniUnpackArrayReviewDeprecated76', 8192);
try {
    $result = $call(...iniUnpackArrayReviewPack76()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings, '|', $arrayKeep[0];
    echo '|', $pack['value'][0], '|', $packOld['value'][0];
    echo '|', ini_get('precision'), '|', constant('SOURCE76PEER');
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
