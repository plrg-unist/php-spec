#!/usr/bin/env python3
"""Native-first nonStringable define names fail before optional flag reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'ordinary-define-object-name-before-true-flag-warning': br'''<?php
class PlainDefineName56 {}
$name = new PlainDefineName56; $keep = $name; $result = 99;
echo 'B|';
try { $result = define($name, 1543); echo 'BAD'; }
catch (TypeError $e) { echo $e->getMessage(), '|', $e->getLine(); }
try { $result = define($name, 1549, true); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace();
    echo '|', $e->getMessage(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
    echo '|', $trace[0]['args'][1], '|', $trace[0]['args'][2] === true ? 'T' : 'BAD';
}
echo '|', $result, '|', defined('') === false ? 'E' : 'BAD';
''',
    'selected-nonstringable-define-before-null-flag-reception': br'''<?php
class SelectedPlainDefine56 {}
function plainDefineValue56() {
    global $call, $name, $value, $effects;
    $captured = $value; echo 'V|'; $effects++;
    $call = 'constant'; $name = 'value-live56'; return $captured;
}
function plainDefineFlag56() {
    global $call, $name, $value, $flag, $effects;
    echo 'F|'; $effects++; $call = 'defined'; $name = 'flag-live56';
    $value = 997; $flag = true; return null;
}
function plainDefineCaller56() {
    global $call, $name, $value, $flag, $effects;
    $call = 'DeFiNe'; $name = new SelectedPlainDefine56; $keep = $name;
    $part = 'captured'; $value = $part . '-candidate56'; $flag = null;
    $effects = 0; $result = 99;
    try { $result = $call($name, plainDefineValue56(), plainDefineFlag56()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'captured-candidate56' ? 'V' : 'BAD';
        echo '|', $trace[0]['args'][2] === null ? 'N' : 'BAD';
    }
    echo '|', $call, '|', $name, '|', $value, '|', $flag === true ? 'T' : 'BAD';
    echo '|', $effects, '|', $result;
}
echo 'B|'; plainDefineCaller56();
''',
    'strict-stdclass-define-before-third-integer-type-error': br'''<?php
declare(strict_types=1);
function plainDefineStrictFlag56() {
    global $call, $name, $effects;
    echo 'F|'; $effects++; $call = 'constant'; $name = 'strict-live56'; return 17;
}
function plainDefineStrictCaller56() {
    global $call, $name, $effects;
    $call = 'DeFiNe'; $name = new stdClass; $keep = $name;
    $effects = 0; $result = 99;
    try { $result = $call($name, 1571, plainDefineStrictFlag56()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[0]['args'][1], '|', $trace[0]['args'][2];
    }
    echo '|', $call, '|', $name, '|', $effects, '|', $result;
}
echo 'B|'; plainDefineStrictCaller56();
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
