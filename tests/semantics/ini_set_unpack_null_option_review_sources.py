#!/usr/bin/env python3
"""A selected INI callee retains normalized unpacked arguments through a throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-unpack-null-deprecated-throw-preserves-callee-and-request-value': br'''<?php
function iniUnpackReviewPack68() {
    global $call, $pack, $value, $effects;
    $early = $value; echo 'P|'; $effects++;
    $pack = ['value' => $early, 'option' => null];
    $call = 'ini_get'; $value = 'after-value68';
    ini_set('precision', '7'); return $pack;
}
function iniUnpackReviewDeprecated68($level, $message) {
    global $call, $pack, $value, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $pack['option'] = 'precision'; $pack['value'] = 'handler-pack68';
    $call = 'constant'; $value = 'handler-value68';
    ini_set('precision', '10'); define('SOURCE68PEER', 2311);
    $saved = new Exception('unpack-null68-stop'); throw $saved;
}
function iniUnpackReviewCaller68() {
    global $call, $pack, $value, $effects, $warnings, $saved;
    $call = 'InI_SeT'; $keep = $call; $pack = [];
    $part = 'unpack'; $value = $part . '-value68';
    $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('iniUnpackReviewDeprecated68', 8192);
    try {
        $result = $call(...iniUnpackReviewPack68()); echo 'BAD';
    } catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $effects, '|', $warnings, '|', $call, '|', $value;
        echo '|', $pack['option'], '|', $pack['value'], '|', ini_get('precision'), '|', constant('SOURCE68PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep(...['option' => 'precision', 'value' => '12']), '|', ini_get('precision'), '|', $result;
}
echo 'B|'; iniUnpackReviewCaller68();
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
