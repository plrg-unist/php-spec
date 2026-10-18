#!/usr/bin/env python3
"""A NULL option deprecation throw preserves captured values and caller effects."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-null-option-deprecation-throw-retains-request-value': br'''<?php
function iniNullReviewValue62() {
    global $call, $option, $value, $effects;
    echo 'V|'; $effects++;
    $captured = $value;
    $call = 'constant'; $option = 'precision'; $value = 'after-value62';
    return $captured;
}
function iniNullReviewDeprecated62($level, $message) {
    global $call, $option, $value, $deprecations, $saved;
    echo 'D|', $level, '|', $message, '|'; $deprecations++;
    $call = 'ini_get'; $option = 'precision'; $value = 'handler-value62';
    ini_set('precision', '8');
    define('SOURCE62PEER', 2003);
    $saved = new Exception('deprecated62-stop'); throw $saved;
}
function iniNullReviewCaller62() {
    global $call, $option, $value, $effects, $deprecations, $saved;
    $call = 'InI_SeT'; $option = null;
    $part = 'captured'; $value = $part . '-value62';
    $effects = 0; $deprecations = 0; $saved = null; $result = 99;
    set_error_handler('iniNullReviewDeprecated62', 8192);
    try { $result = $call($option, iniNullReviewValue62()); echo 'BAD'; }
    catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $effects, '|', $deprecations, '|', $call;
        echo '|', $option, '|', $value, '|', ini_get('precision');
        echo '|', constant('SOURCE62PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|', $call($option), '|', $result;
}
echo 'B|'; iniNullReviewCaller62();
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
