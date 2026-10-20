#!/usr/bin/env python3
"""A named NULL call keeps its captured stdClass through shared writes and throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-named-null-stdclass-handler-throw-keeps-shared-object': br'''<?php
function iniNamedNullStdReviewOption72() {
    global $call, $option, $value, $objectKeep, $effects;
    echo 'O|'; $effects++; $objectKeep->mark = 'option-mark72';
    $call = 'ini_get'; $option = 'precision'; $value = 997;
    return null;
}
function iniNamedNullStdReviewDeprecated72($level, $message) {
    global $call, $option, $value, $objectKeep, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'handler-mark72';
    $call = 'constant'; $option = 'handler-option72'; $value = 123;
    ini_set('precision', '10'); define('SOURCE72PEER', 2579);
    $saved = new Exception('named-null-stdclass72-stop'); throw $saved;
}
echo 'B|';
$call = 'InI_SeT'; $keep = $call; $option = null;
$value = new stdClass(); $part = 'named'; $value->mark = $part . '-stdclass72';
$objectKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniNamedNullStdReviewDeprecated72', 8192);
try {
    $result = $call(value: $value, option: iniNamedNullStdReviewOption72()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings, '|', $objectKeep === $old ? 'S' : 'BAD';
    echo '|', $old->mark, '|', ini_get('precision'), '|', constant('SOURCE72PEER');
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
