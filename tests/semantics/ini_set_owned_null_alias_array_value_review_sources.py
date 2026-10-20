#!/usr/bin/env python3
"""A retained setter and earlier alias array survive explicit callback reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-alias-array-throw-retains-live-reference-after-trace': br'''<?php
declare(strict_types=1);
function iniOwnedAliasArrayReviewValue82() {
    global $call, $option, $value, $arrayKeep, $leaf, $replacement, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $leaf = 'value-array82'; $arrayKeep[] = 31;
    $call = $replacement; $option = 'precision'; $value = 0; return $earlier;
}
function iniOwnedAliasArrayReviewDeprecated82($level, $message) {
    global $call, $option, $value, $arrayKeep, $leaf, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'handler-array82'; $arrayKeep[] = 37;
    $call = 'constant'; $option = 'handler-option82'; $value = 123;
    ini_set('precision', '10'); define('SOURCE82PEER', 3239);
    $saved = new Exception('owned-alias-array82-stop');
    $leaf = 'after-exception82'; throw $saved;
}
echo 'B|'; $call = ini_set(...); $keep = $call; $option = null;
$replacement = ini_get(...);
$seed = 'owned-alias-array'; $leaf = $seed . '-peer82';
$arrayKeep = [&$leaf]; $old = $arrayKeep; $value = $arrayKeep;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniOwnedAliasArrayReviewDeprecated82', 8192);
try {
    $result = $call->__invoke($option, iniOwnedAliasArrayReviewValue82()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $old[0], '|', $arrayKeep[2];
    echo '|', isset($old[1]) ? 'BAD' : 'C';
    echo '|', constant('SOURCE82PEER');
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
