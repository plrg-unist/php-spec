#!/usr/bin/env python3
"""Owned numeric unpack keeps captured values through NULL-option cancellation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'strict-explicit-owned-unpack-null-keeps-captured-numeric-args': br'''<?php
declare(strict_types=1);
function iniOwnedUnpackReviewPack66() {
    global $call, $pack, $value, $effects;
    $early = $value; echo 'V|'; $effects++;
    $pack = [3 => null, 7 => $early];
    $call = ini_get(...); $value = 'after-value66';
    ini_set('precision', '7'); return $pack;
}
function iniOwnedUnpackReviewDeprecated66($level, $message) {
    global $call, $pack, $value, $warnings, $saved;
    echo 'D|', $level, '|', $message, '|'; $warnings++;
    $pack[3] = 'precision'; $pack[7] = 'handler-pack66';
    $call = 'constant'; $value = 'handler-value66';
    ini_set('precision', '10'); define('SOURCE66PEER', 2197);
    $saved = new Exception('unpack-owned66-stop'); throw $saved;
}
function iniOwnedUnpackReviewCaller66() {
    global $call, $pack, $value, $effects, $warnings, $saved;
    $call = ini_set(...); $keep = $call; $pack = [];
    $part = 'unpack-owned'; $value = $part . '-value66';
    $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('iniOwnedUnpackReviewDeprecated66', 8192);
    try {
        $result = $call->__invoke(...iniOwnedUnpackReviewPack66()); echo 'BAD';
    } catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        $trace = $e->getTrace(); $args = $trace[2]['args'];
        echo '|', $args[0] === null ? 'N' : 'BAD', '|', $args[1];
        echo '|', $result, '|', $effects, '|', $warnings, '|', $call, '|', $value;
        echo '|', $pack[3], '|', $pack[7], '|', ini_get('precision'), '|', constant('SOURCE66PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep('precision', '12'), '|', ini_get('precision'), '|', $result;
}
echo 'B|'; iniOwnedUnpackReviewCaller66();
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
