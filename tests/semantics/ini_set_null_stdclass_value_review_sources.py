#!/usr/bin/env python3
"""A NULL-option handler keeps the shared stdClass value through a throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-null-stdclass-value-handler-throw-preserves-shared-object': br'''<?php
function iniNullStdReviewValue70() {
    global $call, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++;
    $call = 'ini_get'; $option = 'precision'; $value = 997;
    ini_set('precision', '7'); return $early;
}
function iniNullStdReviewDeprecated70($level, $message) {
    global $call, $option, $value, $objectKeep, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $objectKeep->mark = 'handler-mark70';
    $call = 'constant'; $option = 'handler-option70'; $value = 123;
    ini_set('precision', '10'); define('SOURCE70PEER', 2459);
    $saved = new Exception('null-stdclass70-stop'); throw $saved;
}
function iniNullStdReviewCaller70() {
    global $call, $option, $value, $objectKeep, $effects, $warnings, $saved;
    $call = 'InI_SeT'; $keep = $call; $option = null;
    $value = new stdClass(); $part = 'stdclass'; $value->mark = $part . '-mark70';
    $objectKeep = $value; $old = $value;
    $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('iniNullStdReviewDeprecated70', 8192);
    try {
        $result = $call($option, iniNullStdReviewValue70()); echo 'BAD';
    } catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $effects, '|', $warnings, '|', $call, '|', $option, '|', $value;
        echo '|', $objectKeep === $old ? 'S' : 'BAD', '|', $objectKeep->mark, '|', $old->mark;
        echo '|', ini_get('precision'), '|', constant('SOURCE70PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep('precision', '12'), '|', ini_get('precision'), '|', $result;
}
echo 'B|'; iniNullStdReviewCaller70();
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
