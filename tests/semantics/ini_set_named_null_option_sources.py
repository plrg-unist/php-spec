#!/usr/bin/env python3
"""Native-first named NULL INI options preserve written argument order."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'named-null-literal-handler-and-positional-prefix': br'''<?php
function literalNamedNullHandler63($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
$warnings = 0; set_error_handler('literalNamedNullHandler63', 8192);
echo 'B|', ini_set(value: 'literal-value63', option: null) === false ? 'F' : 'BAD';
echo '|', ini_set(null, value: 2011) === false ? 'F' : 'BAD';
restore_error_handler(); echo '|', $warnings, '|', ini_get('precision');
''',
    'selected-reversed-named-null-false-handler-preserves-early-value': br'''<?php
function reversedNamedNullValue63() {
    global $call, $option, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++; ini_set('precision', '6');
    $call = 'constant'; $option = 'value-option63'; $value = 'after-value63'; return $earlier;
}
function reversedNamedNullOption63() {
    global $call, $option, $value, $effects;
    echo 'O|'; $effects++; ini_set('precision', '7');
    $call = 'ini_get'; $option = 'precision'; $value = 'after-option63'; return null;
}
function reversedNamedNullHandler63($level, $message) {
    global $call, $option, $value, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++; ini_set('precision', '8');
    $call = 'ini_restore'; $option = 'precision'; $value = 'handler-value63'; return false;
}
function reversedNamedNullCaller63() {
    global $call, $option, $value, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $part = 'captured'; $value = $part . '-value63';
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('reversedNamedNullHandler63', 8192);
    try {
        $result = $call(value: reversedNamedNullValue63(), option: reversedNamedNullOption63());
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision');
        echo '|', $effects, '|', $warnings, '|', $call, '|', $option, '|', $value;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; reversedNamedNullCaller63();
''',
    'strict-reversed-named-null-before-handler-after-effects': br'''<?php
declare(strict_types=1);
function strictNamedNullValue63() {
    global $call, $option, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++; ini_set('precision', '9');
    $call = 'constant'; $option = 'value-option63'; $value = 0; return $earlier;
}
function strictNamedNullOption63() {
    global $call, $option, $value, $effects;
    echo 'O|'; $effects++; $call = 'ini_get'; $option = 'precision'; $value = 1; return null;
}
function strictNamedNullHandler63($level, $message) { global $warnings; $warnings++; echo 'BAD'; }
function strictNamedNullCaller63() {
    global $call, $option, $value, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $value = 2039; $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('strictNamedNullHandler63', 8192);
    try { $result = $call(value: strictNamedNullValue63(), option: strictNamedNullOption63()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD', '|', $trace[0]['args'][1];
        echo '|', $trace[1]['function'], '|', $result, '|', $effects, '|', $warnings;
        echo '|', ini_get('precision'), '|', $call, '|', $option, '|', $value;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictNamedNullCaller63();
''',
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'B|V|O|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
