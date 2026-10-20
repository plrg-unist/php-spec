#!/usr/bin/env python3
"""A rejected callable value stays captured while the callback throws."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-null-getter-closure-throw-keeps-captured-value-callable': br'''<?php
function iniGetterClosureReviewValue79() {
    global $call, $option, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $call = 'ini_get'; $option = 'precision'; $value = 0; return $earlier;
}
function iniGetterClosureReviewDeprecated79($level, $message) {
    global $call, $option, $value, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $call = 'constant'; $option = 'handler-option79'; $value = 123;
    ini_set('precision', '10'); define('SOURCE79PEER', 3059);
    $saved = new Exception('null-getter-closure79-stop'); throw $saved;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call; $option = null;
$value = ini_get(...); $getterKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniGetterClosureReviewDeprecated79', 8192);
try {
    $result = $call($option, iniGetterClosureReviewValue79()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $getterKeep === $old ? 'S' : 'BAD';
    echo '|', constant('SOURCE79PEER');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $getterKeep('precision'), '|', $keep('precision', '12');
echo '|', $getterKeep('precision'), '|', $result;
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
