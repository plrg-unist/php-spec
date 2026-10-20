#!/usr/bin/env python3
"""Reversed named unpack retains normalized owned INI arguments through a throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-named-unpack-null-retains-numeric-wrapper-args': br'''<?php
declare(strict_types=1);
function iniOwnedNamedUnpackReviewPack67() {
    global $call, $pack, $value, $effects;
    $early = $value; echo 'P|'; $effects++;
    $pack = ['value' => $early, 'option' => null];
    $call = ini_get(...); $value = 'after-value67';
    ini_set('precision', '7'); return $pack;
}
function iniOwnedNamedUnpackReviewDeprecated67($level, $message) {
    global $call, $pack, $value, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $pack['option'] = 'precision'; $pack['value'] = 'handler-pack67';
    $call = 'constant'; $value = 'handler-value67';
    ini_set('precision', '10'); define('SOURCE67PEER', 2251);
    $saved = new Exception('named-unpack-owned67-stop'); throw $saved;
}
function iniOwnedNamedUnpackReviewCaller67() {
    global $call, $pack, $value, $effects, $warnings, $saved;
    $call = ini_set(...); $keep = $call; $pack = [];
    $part = 'named-unpack-owned'; $value = $part . '-value67';
    $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('iniOwnedNamedUnpackReviewDeprecated67', 8192);
    try {
        $result = $call->__invoke(...iniOwnedNamedUnpackReviewPack67()); echo 'BAD';
    } catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $effects, '|', $warnings, '|', $call, '|', $value;
        echo '|', $pack['option'], '|', $pack['value'], '|', ini_get('precision'), '|', constant('SOURCE67PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep('precision', '12'), '|', ini_get('precision'), '|', $result;
}
echo 'B|'; iniOwnedNamedUnpackReviewCaller67();
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
