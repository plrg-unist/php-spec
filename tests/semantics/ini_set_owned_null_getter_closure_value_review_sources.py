#!/usr/bin/env python3
"""A held setter and rejected getter value survive same-getter callee rebinding."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-null-getter-throw-keeps-both-callables': br'''<?php
declare(strict_types=1);
function iniOwnedGetterClosureReviewValue80() {
    global $call, $option, $value, $getterKeep, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $call = $getterKeep; $option = 'precision'; $value = 0; return $earlier;
}
function iniOwnedGetterClosureReviewDeprecated80($level, $message) {
    global $call, $option, $value, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $call = 'constant'; $option = 'handler-option80'; $value = 123;
    ini_set('precision', '10'); define('SOURCE80PEER', 3119);
    $saved = new Exception('owned-null-getter-closure80-stop'); throw $saved;
}
echo 'B|'; $call = ini_set(...); $keep = $call; $option = null;
$value = ini_get(...); $getterKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniOwnedGetterClosureReviewDeprecated80', 8192);
try {
    $result = $call->__invoke($option, iniOwnedGetterClosureReviewValue80()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $getterKeep === $old ? 'S' : 'BAD';
    echo '|', constant('SOURCE80PEER');
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
