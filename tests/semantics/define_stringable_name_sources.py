#!/usr/bin/env python3
"""Native-first Stringable define names convert before registration or duplication."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'weak-stringable-define-names-fresh-then-duplicate': br'''<?php
class StringDefineName55 {
    public function __toString(): string {
        global $calls;
        echo 'S|'; $calls++; return 'STRINGDEFINE55';
    }
}
$name = new StringDefineName55; $keep = $name; $calls = 0;
echo 'B|', define($name, 1481) ? 'T' : 'BAD', '|', constant('STRINGDEFINE55');
echo '|', define($name, 1487, false) ? 'BAD' : 'F', '|', constant('STRINGDEFINE55'), '|', $calls;
''',
    'selected-stringable-name-callback-installs-duplicate-key': br'''<?php
function defineStringWarning55($level, $message) {
    global $saved, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++; $saved = new Exception('duplicate55'); throw $saved;
}
class CapturedStringDefine55 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $calls;
        echo 'S|'; $calls++; define('CAPTUREDEFINE55', 1493);
        $call = 'constant'; $name = 'cast-live55'; $value = 997; $flag = true;
        $prefix = 'CAPTURE'; return $prefix . 'DEFINE55';
    }
}
function captureDefineValue55() {
    global $call, $name, $value, $effects;
    $captured = $value; echo 'V|'; $effects++; $call = 'defined';
    $name = 'value-live55'; return $captured;
}
function capturedDefineCaller55() {
    global $call, $name, $value, $flag, $calls, $effects, $saved, $warnings;
    $call = 'DeFiNe'; $name = new CapturedStringDefine55; $keep = $name;
    $part = 'captured'; $value = $part . '-candidate55'; $flag = false;
    $calls = 0; $effects = 0; $warnings = 0; $saved = null; $result = 99;
    set_error_handler('defineStringWarning55');
    try { $result = $call($name, captureDefineValue55(), $flag); echo 'BAD'; }
    catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD';
        echo '|', $result, '|', $calls, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $name, '|', $value, '|', $flag === true ? 'T' : 'BAD';
        echo '|', constant('CAPTUREDEFINE55');
    } finally { echo '|Z'; }
}
echo 'B|'; capturedDefineCaller55();
''',
    'strict-stringable-define-rejects-before-name-method': br'''<?php
declare(strict_types=1);
class StrictStringDefine55 {
    public function __toString(): string { echo 'BAD'; return 'WRONG55'; }
}
function strictStringDefineValue55() {
    global $call, $name, $value, $effects;
    $captured = $value; echo 'V|'; $effects++;
    $call = 'defined'; $name = 'strict-live55'; $value = 997; return $captured;
}
function strictStringDefineCaller55() {
    global $call, $name, $value, $effects;
    $call = 'DeFiNe'; $name = new StrictStringDefine55; $keep = $name;
    $value = 1507; $effects = 0; $result = 99;
    try { $result = $call($name, strictStringDefineValue55(), false); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[0]['args'][1], '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
        echo '|', $trace[1]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
    }
    echo '|', $call, '|', $name, '|', $value, '|', $effects, '|', $result;
}
echo 'B|'; strictStringDefineCaller55();
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
