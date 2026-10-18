#!/usr/bin/env python3
"""Reversed named INI arguments keep the early value through a deprecation throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-reversed-named-null-option-throw-keeps-early-request': br'''<?php
function iniNamedReviewValue63() {
    global $call, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++;
    $call = 'ini_get'; $option = 'value-option63'; $value = 'value-live63';
    return $early;
}
function iniNamedReviewOption63() {
    global $call, $option, $value, $effects;
    echo 'O|'; $effects++; ini_set('precision', '7');
    $call = 'ini_restore'; $option = 'option-live63'; $value = 'option-value63';
    return null;
}
function iniNamedReviewDeprecated63($level, $message) {
    global $call, $option, $value, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $call = 'ini_get'; $option = 'precision'; $value = 'handler-value63';
    ini_set('precision', '10'); define('SOURCE63PEER', 2053);
    $saved = new Exception('named63-stop'); throw $saved;
}
function iniNamedReviewCaller63() {
    global $call, $option, $value, $effects, $warnings, $saved;
    $call = 'InI_SeT'; $option = 'initial-option63';
    $part = 'early'; $value = $part . '-value63';
    $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('iniNamedReviewDeprecated63', 8192);
    try {
        $result = $call(value: iniNamedReviewValue63(), option: iniNamedReviewOption63());
        echo 'BAD';
    } catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $effects, '|', $warnings, '|', $call;
        echo '|', $option, '|', $value, '|', ini_get('precision');
        echo '|', constant('SOURCE63PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|', $call($option), '|', $result;
}
echo 'B|'; iniNamedReviewCaller63();
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
