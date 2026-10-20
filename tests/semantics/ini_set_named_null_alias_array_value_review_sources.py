#!/usr/bin/env python3
"""A named array capture preserves its shape and later shared cell writes."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-named-alias-array-throw-retains-cell-after-option-effects': br'''<?php
function iniNamedAliasArrayReviewOption83() {
    global $call, $option, $value, $arrayKeep, $leaf, $effects;
    $earlier = $option; echo 'O|'; $effects++;
    $leaf = 'option-array83'; $arrayKeep[] = 31;
    $call = 'ini_get'; $option = 'precision'; $value = 0; return $earlier;
}
function iniNamedAliasArrayReviewDeprecated83($level, $message) {
    global $call, $option, $value, $arrayKeep, $leaf, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'handler-array83'; $arrayKeep[] = 37;
    $call = 'constant'; $option = 'handler-option83'; $value = 123;
    ini_set('precision', '10'); define('SOURCE83PEER', 3299);
    $saved = new Exception('named-alias-array83-stop');
    $leaf = 'after-exception83'; throw $saved;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call; $option = null;
$seed = 'named-alias-array'; $leaf = $seed . '-peer83';
$value = [&$leaf]; $arrayKeep = $value; $old = $value;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniNamedAliasArrayReviewDeprecated83', 8192);
try {
    $result = $call(value: $value, option: iniNamedAliasArrayReviewOption83()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $old[0], '|', $arrayKeep[2];
    echo '|', isset($old[1]) ? 'BAD' : 'C';
    echo '|', constant('SOURCE83PEER');
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
