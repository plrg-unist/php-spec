#!/usr/bin/env python3
"""A NULL-flag deprecation throw cancels registration after name conversion."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-stringable-null-deprecation-throw-cancels-captured-value': br'''<?php
class StringNullReviewName60 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $casts;
        echo 'S|'; $casts++;
        $call = 'constant'; $name = 'cast-name60';
        $value = 'cast-value60'; $flag = true;
        $part = 'STRINGNULL'; return $part . '60PEER';
    }
}
function stringNullReviewDeprecated60($level, $message) {
    global $call, $name, $value, $flag, $deprecations, $saved;
    echo 'D|', $level, '|', $message, '|'; $deprecations++;
    $call = 'defined'; $name = 'handler-name60';
    $value = 'handler-value60'; $flag = true;
    define('SOURCE60PEER', 1877);
    $saved = new Exception('deprecated60-stop'); throw $saved;
}
function stringNullReviewCaller60() {
    global $call, $name, $value, $flag, $casts, $deprecations, $saved;
    $call = 'DeFiNe'; $name = new StringNullReviewName60(); $keep = $name;
    $part = 'captured'; $value = $part . '-value60'; $flag = null;
    $casts = 0; $deprecations = 0; $saved = null; $result = 99;
    set_error_handler('stringNullReviewDeprecated60');
    try { $result = $call($name, $value, $flag); echo 'BAD'; }
    catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $casts, '|', $deprecations, '|', $call, '|', $name;
        echo '|', $value, '|', $flag === true ? 'T' : 'BAD';
        echo '|', defined('STRINGNULL60PEER') ? 'BAD' : 'A';
        echo '|', constant('SOURCE60PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|', $result;
}
echo 'B|'; stringNullReviewCaller60();
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
