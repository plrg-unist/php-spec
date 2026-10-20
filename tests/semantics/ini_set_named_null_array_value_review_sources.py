#!/usr/bin/env python3
"""A reversed named NULL call retains its earlier array through effects and throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-named-null-array-handler-throw-preserves-earlier-array': br'''<?php
function iniNamedNullArrayReviewOption71() {
    global $call, $option, $value, $arrayKeep, $effects;
    echo 'O|'; $effects++; $arrayKeep[0] = 'option-array71';
    $call = 'ini_get'; $option = 'precision'; $value = 997;
    return null;
}
function iniNamedNullArrayReviewDeprecated71($level, $message) {
    global $call, $option, $value, $arrayKeep, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array71';
    $call = 'constant'; $option = 'handler-option71'; $value = 123;
    ini_set('precision', '10'); define('SOURCE71PEER', 2513);
    $saved = new Exception('named-null-array71-stop'); throw $saved;
}
echo 'B|';
$call = 'InI_SeT'; $keep = $call; $option = null;
$part = 'named'; $value = [$part . '-array71']; $arrayKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniNamedNullArrayReviewDeprecated71', 8192);
try {
    $result = $call(value: $value, option: iniNamedNullArrayReviewOption71()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings, '|', $arrayKeep[0], '|', $old[0];
    echo '|', ini_get('precision'), '|', constant('SOURCE71PEER');
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
