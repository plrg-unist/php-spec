#!/usr/bin/env python3
"""An ignored-flag handler throw still publishes the converted captured value."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-stringable-true-warning-throw-still-registers-captured-value': br'''<?php
class StringTrueReviewName59 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $casts;
        echo 'S|'; $casts++;
        $call = 'constant'; $name = 'cast-name59';
        $value = 'cast-value59'; $flag = false;
        $part = 'STRINGFLAG'; return $part . '59PEER';
    }
}
function stringTrueReviewWarning59($level, $message) {
    global $call, $name, $value, $flag, $warnings, $saved;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $call = 'defined'; $name = 'handler-name59';
    $value = 'handler-value59'; $flag = false;
    define('SOURCE59PEER', 1777);
    $saved = new Exception('ignored59-stop'); throw $saved;
}
function stringTrueReviewCaller59() {
    global $call, $name, $value, $flag, $casts, $warnings, $saved;
    $call = 'DeFiNe'; $name = new StringTrueReviewName59(); $keep = $name;
    $part = 'captured'; $value = $part . '-value59'; $flag = true;
    $casts = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('stringTrueReviewWarning59');
    try { $result = $call($name, $value, $flag); echo 'BAD'; }
    catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $casts, '|', $warnings, '|', $call, '|', $name;
        echo '|', $value, '|', $flag === false ? 'F' : 'BAD';
        echo '|', constant('STRINGFLAG59PEER'), '|', constant('SOURCE59PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|', $result;
}
echo 'B|'; stringTrueReviewCaller59();
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
