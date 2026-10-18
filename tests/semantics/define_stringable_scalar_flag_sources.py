#!/usr/bin/env python3
"""Native-first Stringable names with captured quiet nonboolean define flags."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'stringable-quiet-flags-fresh-duplicates-and-infinite-class-priority': br'''<?php
class QuietFlagName61 {
    public function __toString(): string {
        global $calls; echo 'S|'; $calls++;
        if ($calls === 4) { return 'A::QUIET61'; }
        return 'STRINGQUIET61';
    }
}
$name = new QuietFlagName61; $keep = $name; $calls = 0;
echo 'B|', define($name, 1907, 0) ? 'T' : 'BAD', '|', constant('STRINGQUIET61');
echo '|', define($name, 1913, -0.0) === false ? 'F' : 'BAD', '|', constant('STRINGQUIET61');
echo '|', define($name, 1919, '0') === false ? 'F' : 'BAD', '|', constant('STRINGQUIET61'), '|';
$result = 99;
try { $result = define($name, 1921, INF); echo 'BAD'; }
catch (ValueError $e) { echo 'E|', $e->getMessage(), '|', $result, '|', $calls; }
''',
    'selected-stringable-truthy-request-flag-before-live-zero-and-duplicate': br'''<?php
class CapturedScalarFlagName61 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $calls;
        echo 'S|'; $calls++; $call = 'constant'; $name = 'cast-live61';
        $value = 997; $flag = '0'; $part = 'CAPTURE'; return $part . 'QUIET61';
    }
}
function capturedScalarValue61() {
    global $call, $name, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++; $call = 'defined';
    $name = 'value-live61'; return $earlier;
}
function capturedScalarFlag61() {
    global $call, $name, $flag, $effects;
    $earlier = $flag; echo 'F|'; $effects++; $flag = '0';
    $call = 'constant'; $name = 'flag-live61'; return $earlier;
}
function capturedScalarWarning61($level, $message) {
    global $call, $name, $value, $flag, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    if ($warnings === 1) {
        define('CAPTUREQUIET61', 1931); $call = 'defined'; $name = 'handler-live61';
        $value = 991; $flag = '0'; return true;
    }
    return false;
}
function capturedScalarCaller61() {
    global $call, $name, $value, $flag, $calls, $warnings, $effects;
    $call = 'DeFiNe'; $name = new CapturedScalarFlagName61; $keep = $name;
    $part = 'captured'; $value = $part . '-candidate61';
    $left = 'fal'; $flag = $left . 'se';
    $calls = 0; $warnings = 0; $effects = 0; $result = 99;
    set_error_handler('capturedScalarWarning61');
    try {
        $result = $call($name, capturedScalarValue61(), capturedScalarFlag61());
        echo $result === false ? 'F' : 'BAD', '|', constant('CAPTUREQUIET61');
        echo '|', $calls, '|', $effects, '|', $warnings, '|', $call, '|', $name;
        echo '|', $value, '|', $flag === '0' ? 'S0' : 'BAD';
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; capturedScalarCaller61();
''',
    'strict-stringable-quiet-flag-rejects-name-before-nonbool-flag': br'''<?php
declare(strict_types=1);
class StrictScalarFlagName61 {
    public function __toString(): string {
        global $calls; echo 'BAD-S|'; $calls++; return 'STRICTQUIET61';
    }
}
function strictScalarFlag61() {
    global $call, $name, $flag, $effects;
    $earlier = $flag; echo 'F|'; $effects++; $flag = 0;
    $call = 'constant'; $name = 'strict-live61'; return $earlier;
}
function strictScalarCaller61() {
    global $call, $name, $flag, $calls, $effects;
    $call = 'DeFiNe'; $name = new StrictScalarFlagName61; $keep = $name;
    $flag = 1; $calls = 0; $effects = 0; $result = 99;
    try { $result = $call($name, 1961, strictScalarFlag61()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD', '|', $trace[0]['args'][1];
        echo '|', $trace[0]['args'][2] === 1 ? 'I1' : 'BAD', '|', $trace[1]['function'];
        echo '|', $result, '|', $calls, '|', $effects, '|', $flag === 0 ? 'I0' : 'BAD';
    }
}
echo 'B|'; strictScalarCaller61();
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
