#!/usr/bin/env python3
"""NULL INI options deprecate before rejecting captured flat array values."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'null-array-value-default-and-true-handler-convert-option-before-error': br'''<?php
function nullArrayTrue69($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
function nullArrayDefaultCaller69() {
    global $warnings;
    $warnings = 0; $result = 99;
    try { $result = ini_set(null, []); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    set_error_handler('nullArrayTrue69', 8192);
    try {
        echo '|T|';
        try { $result = ini_set(null, [2333]); echo 'BAD'; }
        catch (TypeError $e) {
            $trace = $e->getTrace(); $args = $trace[0]['args'];
            echo $e->getMessage(), '|', $args[0] === '' ? 'E' : 'BAD', '|', $args[1][0];
            echo '|', $result, '|', $warnings, '|', ini_get('precision');
        }
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; nullArrayDefaultCaller69();
''',
    'selected-null-array-value-false-handler-keeps-captured-array-after-cow': br'''<?php
function nullArrayValue69() {
    global $call, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++; ini_set('precision', '7');
    $call = 'ini_get'; $option = 'precision'; $value = 2357; return $early;
}
function nullArrayFalse69($level, $message) {
    global $call, $option, $value, $arrayKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-keep69'; $value = 'handler-value69';
    $call = 'constant'; $option = 'precision'; ini_set('precision', '8'); return false;
}
function nullArrayCaller69() {
    global $call, $option, $value, $arrayKeep, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $part = 'captured';
    $value = [$part . '-array69', 2351]; $arrayKeep = $value;
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('nullArrayFalse69', 8192);
    try {
        $result = $call($option, nullArrayValue69()); echo 'BAD';
    } catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $option, '|', $value, '|', $arrayKeep[0], '|', $arrayKeep[1], '|', ini_get('precision');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', ini_set('precision', '11'), '|', ini_get('precision');
}
echo 'B|'; nullArrayCaller69();
''',
    'strict-null-array-value-rejects-option-after-value-effects': br'''<?php
declare(strict_types=1);
function strictNullArrayValue69() {
    global $call, $option, $value, $effects;
    $early = $value; echo 'V|'; $effects++; ini_set('precision', '9');
    $call = 'constant'; $option = 'precision'; $value = 0; return $early;
}
function strictNullArrayHandler69($level, $message) {
    global $warnings;
    echo 'BAD|'; $warnings++; return true;
}
function strictNullArrayCaller69() {
    global $call, $option, $value, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $value = [2371]; $arrayKeep = $value;
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('strictNullArrayHandler69', 8192);
    try {
        $result = $call($option, strictNullArrayValue69()); echo 'BAD';
    } catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $option, '|', $value, '|', $arrayKeep[0], '|', ini_get('precision');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictNullArrayCaller69();
''',
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'B|V|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
