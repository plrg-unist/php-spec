#!/usr/bin/env python3
"""A NULL-option handler throws before the captured array value is rejected."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-null-array-value-handler-throw-preserves-captured-array': br'''<?php
function iniNullArrayReviewValue69() {
    global $call, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++;
    $call = 'ini_get'; $option = 'precision'; $value = 997;
    ini_set('precision', '7'); return $early;
}
function iniNullArrayReviewDeprecated69($level, $message) {
    global $call, $option, $value, $arrayKeep, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array69';
    $call = 'constant'; $option = 'handler-option69'; $value = 123;
    ini_set('precision', '10'); define('SOURCE69PEER', 2389);
    $saved = new Exception('null-array69-stop'); throw $saved;
}
function iniNullArrayReviewCaller69() {
    global $call, $option, $value, $arrayKeep, $effects, $warnings, $saved;
    $call = 'InI_SeT'; $keep = $call; $option = null;
    $part = 'null-array'; $value = [$part . '-value69'];
    $arrayKeep = $value; $old = $value;
    $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('iniNullArrayReviewDeprecated69', 8192);
    try {
        $result = $call($option, iniNullArrayReviewValue69()); echo 'BAD';
    } catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $effects, '|', $warnings, '|', $call, '|', $option, '|', $value;
        echo '|', $arrayKeep[0], '|', $old[0], '|', ini_get('precision'), '|', constant('SOURCE69PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep('precision', '12'), '|', ini_get('precision'), '|', $result;
}
echo 'B|'; iniNullArrayReviewCaller69();
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
