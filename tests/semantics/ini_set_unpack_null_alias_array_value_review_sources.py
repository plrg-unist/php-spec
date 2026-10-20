#!/usr/bin/env python3
"""A saved unpack pack keeps an earlier array with a live shared reference."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-unpack-alias-array-throw-keeps-old-pack-and-live-cell': br'''<?php
function iniUnpackAliasArrayReviewPack84() {
    global $call, $option, $value, $arrayKeep, $leaf, $pack, $effects;
    $earlier = $pack; echo 'P|'; $effects++;
    $leaf = 'pack-array84'; $arrayKeep[] = 31;
    $call = 'ini_get'; $option = 'precision'; $value = 0; return $earlier;
}
function iniUnpackAliasArrayReviewDeprecated84($level, $message) {
    global $call, $option, $value, $arrayKeep, $leaf, $pack, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $pack['value'] = 0; $pack['option'] = 'precision';
    $leaf = 'handler-array84'; $arrayKeep[] = 37;
    $call = 'constant'; $option = 'handler-option84'; $value = 123;
    ini_set('precision', '10'); define('SOURCE84PEER', 3359);
    $saved = new Exception('unpack-alias-array84-stop');
    $leaf = 'after-exception84'; throw $saved;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call; $option = null;
$seed = 'unpack-alias-array'; $leaf = $seed . '-peer84';
$value = [&$leaf]; $arrayKeep = $value;
$pack = ['value' => $value, 'option' => $option]; $packOld = $pack;
$effects = 0; $warnings = 0; $saved = null; $result = 99;
set_error_handler('iniUnpackAliasArrayReviewDeprecated84', 8192);
try {
    $result = $call(...iniUnpackAliasArrayReviewPack84()); echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $warnings;
    echo '|', $packOld['value'][0], '|', $arrayKeep[2], '|', $pack['value'];
    echo '|', isset($packOld['value'][1]) ? 'BAD' : 'C';
    echo '|', constant('SOURCE84PEER');
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
