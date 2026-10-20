#!/usr/bin/env python3
"""Named NULL options retain earlier array values through later option effects."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'reversed-and-mixed-null-array-values-return-through-true-handlers': br'''<?php
function namedNullArrayTrue71($level, $message) {
    global $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; return true;
}
function namedNullArrayLiteralCaller71() {
    global $warnings;
    $warnings = 0; $result = 99; set_error_handler('namedNullArrayTrue71', 8192);
    try {
        try { $result = ini_set(value: [2473], option: null); echo 'BAD'; }
        catch (TypeError $e) {
            $trace = $e->getTrace(); $args = $trace[0]['args'];
            echo $e->getMessage(), '|', $args[0] === '' ? 'E' : 'BAD';
            echo '|', $args[1][0], '|', $result, '|', $warnings;
        }
        echo '|M|';
        try { $result = ini_set(null, value: []); echo 'BAD'; }
        catch (TypeError $e) { echo $e->getMessage(), '|', $result, '|', $warnings, '|', ini_get('precision'); }
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; namedNullArrayLiteralCaller71();
''',
    'selected-reversed-null-array-value-survives-later-option-cow': br'''<?php
function namedNullArrayValue71() {
    global $call, $value, $effects;
    $early = $value; echo 'V|'; $effects++; $call = 'ini_get'; $value = 2487;
    ini_set('precision', '6'); return $early;
}
function namedNullArrayOption71() {
    global $call, $option, $value, $arrayKeep, $effects;
    echo 'O|'; $effects++; $arrayKeep[0] = 'option-array71';
    $call = 'constant'; $option = 'precision'; $value = 'option-value71';
    ini_set('precision', '7'); return null;
}
function namedNullArrayFalse71($level, $message) {
    global $call, $option, $value, $arrayKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $arrayKeep[0] = 'handler-array71'; $call = 'ini_restore'; $option = 'precision';
    $value = 'handler-value71'; ini_set('precision', '8'); return false;
}
function namedNullArrayCaller71() {
    global $call, $option, $value, $arrayKeep, $effects, $warnings;
    $call = 'InI_SeT'; $keep = $call; $option = null;
    $part = 'captured'; $value = [$part . '-named-array71', 2481]; $arrayKeep = $value;
    $effects = 0; $warnings = 0; $result = 99; set_error_handler('namedNullArrayFalse71', 8192);
    try { $result = $call(value: namedNullArrayValue71(), option: namedNullArrayOption71()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $option, '|', $value, '|', $arrayKeep[0], '|', $arrayKeep[1], '|', ini_get('precision');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
}
echo 'B|'; namedNullArrayCaller71();
''',
    'strict-reversed-null-array-value-rejects-option-after-both-effects': br'''<?php
declare(strict_types=1);
function strictNamedArrayValue71() {
    global $call, $value, $effects;
    $early = $value; echo 'V|'; $effects++; $call = 'ini_get'; $value = 0;
    ini_set('precision', '6'); return $early;
}
function strictNamedArrayOption71() {
    global $call, $option, $arrayKeep, $effects;
    echo 'O|'; $effects++; $arrayKeep[0] = 0; $call = 'constant'; $option = 'precision';
    ini_set('precision', '9'); return null;
}
function strictNamedArrayHandler71($level, $message) {
    global $warnings;
    echo 'BAD|'; $warnings++; return true;
}
function strictNamedArrayCaller71() {
    global $call, $option, $value, $arrayKeep, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $value = [2491]; $arrayKeep = $value;
    $effects = 0; $warnings = 0; $result = 99; set_error_handler('strictNamedArrayHandler71', 8192);
    try { $result = $call(value: strictNamedArrayValue71(), option: strictNamedArrayOption71()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $option, '|', $value, '|', $arrayKeep[0], '|', ini_get('precision');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictNamedArrayCaller71();
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
