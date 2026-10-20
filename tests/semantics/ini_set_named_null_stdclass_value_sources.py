#!/usr/bin/env python3
"""Named NULL options retain stdClass values through later shared updates."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'reversed-and-mixed-null-stdclass-values-return-through-true-handlers': br'''<?php
function namedNullStdTrue72($level, $message) {
    global $keep, $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; $keep->mark = 'true72'; return true;
}
function namedNullStdTrueCaller72() {
    global $keep, $warnings;
    $keep = new stdClass; $keep->mark = 'start72'; $empty = new stdClass;
    $warnings = 0; $result = 99; set_error_handler('namedNullStdTrue72', 8192);
    try {
        try { $result = ini_set(value: $keep, option: null); echo 'BAD'; }
        catch (TypeError $e) {
            $trace = $e->getTrace(); $args = $trace[0]['args'];
            echo $e->getMessage(), '|', $args[0] === '' ? 'E' : 'BAD';
            echo '|', $args[1] === $keep ? 'I' : 'BAD', '|', $args[1]->mark;
            echo '|', $result, '|', $warnings;
        }
        echo '|M|';
        try { $result = ini_set(null, value: $empty); echo 'BAD'; }
        catch (TypeError $e) { echo $e->getMessage(), '|', $result, '|', $warnings, '|', ini_get('precision'); }
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; namedNullStdTrueCaller72();
''',
    'selected-reversed-null-stdclass-value-preserves-shared-option-updates': br'''<?php
function namedNullStdValue72() {
    global $call, $value, $keep, $effects;
    $early = $value; echo 'V|'; $effects++; $keep->mark = 'value72';
    $call = 'ini_get'; $value = 2527; return $early;
}
function namedNullStdOption72() {
    global $call, $option, $value, $keep, $effects;
    echo 'O|'; $effects++; $keep->mark = 'option72';
    $call = 'constant'; $option = 'precision'; $value = 2531;
    ini_set('precision', '7'); return null;
}
function namedNullStdFalse72($level, $message) {
    global $call, $option, $value, $keep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++; $keep->mark = 'handler72';
    $call = 'ini_restore'; $option = 'precision'; $value = 'handler-value72';
    ini_set('precision', '8'); return false;
}
function namedNullStdCaller72() {
    global $call, $option, $value, $keep, $effects, $warnings;
    $call = 'InI_SeT'; $keepCall = $call; $option = null; $value = new stdClass;
    $part = 'captured'; $value->mark = $part . '-std72'; $keep = $value; $old = $value;
    $effects = 0; $warnings = 0; $result = 99; set_error_handler('namedNullStdFalse72', 8192);
    try { $result = $call(value: namedNullStdValue72(), option: namedNullStdOption72()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $option, '|', $value, '|', $keep === $old ? 'S' : 'BAD';
        echo '|', $old->mark, '|', ini_get('precision');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', $keepCall('precision', '11'), '|', ini_get('precision');
}
echo 'B|'; namedNullStdCaller72();
''',
    'strict-reversed-null-stdclass-value-rejects-option-after-shared-effects': br'''<?php
declare(strict_types=1);
function strictNamedStdValue72() {
    global $call, $value, $keep, $effects;
    $early = $value; echo 'V|'; $effects++; $keep->mark = 'strict-value72';
    $call = 'ini_get'; $value = 0; return $early;
}
function strictNamedStdOption72() {
    global $call, $option, $keep, $effects;
    echo 'O|'; $effects++; $keep->mark = 'strict-option72';
    $call = 'constant'; $option = 'precision'; ini_set('precision', '9'); return null;
}
function strictNamedStdHandler72($level, $message) {
    global $warnings;
    echo 'BAD|'; $warnings++; return true;
}
function strictNamedStdCaller72() {
    global $call, $option, $value, $keep, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $value = new stdClass;
    $value->mark = 'strict72'; $keep = $value; $old = $value;
    $effects = 0; $warnings = 0; $result = 99; set_error_handler('strictNamedStdHandler72', 8192);
    try { $result = $call(value: strictNamedStdValue72(), option: strictNamedStdOption72()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $option, '|', $value, '|', $keep === $old ? 'S' : 'BAD';
        echo '|', $old->mark, '|', ini_get('precision');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictNamedStdCaller72();
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
