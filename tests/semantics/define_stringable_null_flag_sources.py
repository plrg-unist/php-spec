#!/usr/bin/env python3
"""Native-first Stringable define names followed by captured NULL flag reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'stringable-null-flag-fresh-duplicate-and-class-priority': br'''<?php
class NullFlagName60 {
    public function __toString(): string {
        global $calls; echo 'S|'; $calls++;
        if ($calls === 3) { return 'A::NULL60'; }
        return 'STRINGNULL60';
    }
}
$name = new NullFlagName60; $keep = $name; $calls = 0;
echo 'B|', define($name, 1807, null) ? 'T' : 'BAD', '|', constant('STRINGNULL60');
echo '|', define($name, 1811, null) === false ? 'F' : 'BAD', '|', constant('STRINGNULL60'), '|';
$result = 99;
try { $result = define($name, 1817, null); echo 'BAD'; }
catch (ValueError $e) { echo 'E|', $e->getMessage(), '|', $result, '|', $calls; }
''',
    'selected-stringable-null-flag-handler-installs-duplicate-after-conversion': br'''<?php
class CapturedNullFlagName60 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $calls;
        echo 'S|'; $calls++; $call = 'constant'; $name = 'cast-live60';
        $value = 997; $flag = true; $part = 'CAPTURE'; return $part . 'NULL60';
    }
}
function capturedNullValue60() {
    global $call, $name, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++; $call = 'defined';
    $name = 'value-live60'; return $earlier;
}
function capturedNullFlag60() {
    global $call, $name, $flag, $effects;
    $earlier = $flag; echo 'F|'; $effects++; $flag = true;
    $call = 'constant'; $name = 'flag-live60'; return $earlier;
}
function capturedNullWarning60($level, $message) {
    global $call, $name, $value, $flag, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    if ($warnings === 1) {
        define('CAPTURENULL60', 1823); $call = 'defined'; $name = 'handler-live60';
        $value = 991; $flag = true; return true;
    }
    return false;
}
function capturedNullCaller60() {
    global $call, $name, $value, $flag, $calls, $warnings, $effects;
    $call = 'DeFiNe'; $name = new CapturedNullFlagName60; $keep = $name;
    $part = 'captured'; $value = $part . '-candidate60'; $flag = null;
    $calls = 0; $warnings = 0; $effects = 0; $result = 99;
    set_error_handler('capturedNullWarning60');
    try {
        $result = $call($name, capturedNullValue60(), capturedNullFlag60());
        echo $result === false ? 'F' : 'BAD', '|', constant('CAPTURENULL60');
        echo '|', $calls, '|', $effects, '|', $warnings, '|', $call, '|', $name;
        echo '|', $value, '|', $flag === true ? 'T' : 'BAD';
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; capturedNullCaller60();
''',
    'strict-stringable-null-flag-rejects-name-after-argument-effects': br'''<?php
declare(strict_types=1);
class StrictNullFlagName60 {
    public function __toString(): string {
        global $calls; echo 'BAD-S|'; $calls++; return 'STRICTNULL60';
    }
}
function strictNullFlag60() {
    global $call, $name, $flag, $effects;
    $earlier = $flag; echo 'F|'; $effects++; $flag = true;
    $call = 'constant'; $name = 'strict-live60'; return $earlier;
}
function strictNullCaller60() {
    global $call, $name, $flag, $calls, $effects;
    $call = 'DeFiNe'; $name = new StrictNullFlagName60; $keep = $name;
    $flag = null; $calls = 0; $effects = 0; $result = 99;
    try { $result = $call($name, 1847, strictNullFlag60()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD', '|', $trace[0]['args'][1];
        echo '|', $trace[0]['args'][2] === null ? 'N' : 'BAD', '|', $trace[1]['function'];
        echo '|', $result, '|', $calls, '|', $effects, '|', $flag === true ? 'T' : 'BAD';
    }
}
echo 'B|'; strictNullCaller60();
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
