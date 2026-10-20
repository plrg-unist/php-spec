#!/usr/bin/env python3
"""An earlier array keeps its shared reference through callback trace creation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-null-alias-array-throw-retains-live-reference-after-trace': br'''<?php
function iniAliasArrayReviewValue81() {
    global $call, $option, $value, $arrayKeep, $leaf, $effects;
    $earlier = $value; echo 'V|'; $effects++;
    $leaf = 'value-array81'; $arrayKeep[] = 31;
    $call = 'ini_get'; $option = 'precision'; $value = 0; return $earlier;
}
function iniAliasArrayReviewDeprecated81($level, $message) {
    global $call, $option, $value, $arrayKeep, $leaf, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $leaf = 'handler-array81'; $arrayKeep[] = 37;
    $call = 'constant'; $option = 'handler-option81'; $value = 123;
    ini_set('precision', '10'); define('SOURCE81PEER', 3179);
    $saved = new Exception('alias-null-array81-stop');
    $leaf = 'after-exception81'; throw $saved;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call; $option = null;
$seed = 'alias-null-array'; $leaf = $seed . '-peer81';
$arrayKeep = [&$leaf]; $old = $arrayKeep; $value = $arrayKeep;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniAliasArrayReviewDeprecated81', 8192);
try {
    $result = $call($option, iniAliasArrayReviewValue81()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $old[0], '|', $arrayKeep[2];
    echo '|', isset($old[1]) ? 'BAD' : 'C';
    echo '|', constant('SOURCE81PEER');
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
