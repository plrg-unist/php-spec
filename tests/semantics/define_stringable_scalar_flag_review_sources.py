#!/usr/bin/env python3
"""A captured request-zero flag reaches the duplicate created during the cast."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-stringable-request-zero-duplicate-throw-retains-key': br'''<?php
class StringScalarReviewName61 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $casts;
        echo 'S|'; $casts++;
        define('STRINGQUIET61PEER', 1901);
        $call = 'constant'; $name = 'cast-name61';
        $value = 'cast-value61'; $flag = 'cast-flag61';
        $part = 'STRINGQUIET'; return $part . '61PEER';
    }
}
function stringScalarReviewWarning61($level, $message) {
    global $call, $name, $value, $flag, $warnings, $saved;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $call = 'defined'; $name = 'handler-name61';
    $value = 'handler-value61'; $flag = 'handler-flag61';
    define('SOURCE61PEER', 1957);
    $saved = new Exception('duplicate61-stop'); throw $saved;
}
function stringScalarReviewCaller61() {
    global $call, $name, $value, $flag, $casts, $warnings, $saved;
    $call = 'DeFiNe'; $name = new StringScalarReviewName61(); $keep = $name;
    $part = 'captured'; $value = $part . '-value61';
    $left = '00'; $mask = '0'; $flag = $left & $mask;
    $casts = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('stringScalarReviewWarning61');
    try { $result = $call($name, $value, $flag); echo 'BAD'; }
    catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $casts, '|', $warnings, '|', $call, '|', $name;
        echo '|', $value, '|', $flag;
        echo '|', constant('STRINGQUIET61PEER'), '|', constant('SOURCE61PEER');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|', $result;
}
echo 'B|'; stringScalarReviewCaller61();
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
