#!/usr/bin/env python3
"""NULL-option INI calls reject retained stdClass values after deprecation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'null-stdclass-value-default-and-true-handler-preserve-live-object': br'''<?php
function nullStdTrue70($level, $message) {
    global $keep, $warnings;
    echo 'H|', $level, '|', $message, '|'; $warnings++; $keep->mark = 'true70'; return true;
}
function nullStdDefaultCaller70() {
    global $keep, $warnings;
    $keep = new stdClass; $warnings = 0; $result = 99;
    try { $result = ini_set(null, $keep); echo 'BAD'; }
    catch (TypeError $e) { echo $e->getMessage(), '|', $result; }
    $keep->mark = 'start70'; set_error_handler('nullStdTrue70', 8192);
    try {
        echo '|T|';
        try { $result = ini_set(null, $keep); echo 'BAD'; }
        catch (TypeError $e) {
            $trace = $e->getTrace(); $args = $trace[0]['args'];
            echo $e->getMessage(), '|', $args[0] === '' ? 'E' : 'BAD';
            echo '|', $args[1] === $keep ? 'I' : 'BAD', '|', $args[1]->mark;
            echo '|', $result, '|', $warnings, '|', ini_get('precision');
        }
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; nullStdDefaultCaller70();
''',
    'selected-null-stdclass-value-false-handler-sees-shared-property-writes': br'''<?php
function nullStdValue70() {
    global $call, $option, $value, $keep, $effects;
    $early = $value; echo 'V|'; $effects++; $keep->mark = 'value70';
    $call = 'ini_get'; $option = 'precision'; $value = 2423;
    ini_set('precision', '7'); return $early;
}
function nullStdFalse70($level, $message) {
    global $call, $option, $value, $keep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++; $keep->mark = 'handler70';
    $value = 'handler-value70'; $call = 'constant'; $option = 'precision';
    ini_set('precision', '8'); return false;
}
function nullStdCaller70() {
    global $call, $option, $value, $keep, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $value = new stdClass;
    $part = 'captured'; $value->mark = $part . '-std70'; $keep = $value;
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('nullStdFalse70', 8192);
    try { $result = $call($option, nullStdValue70()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $option, '|', $value, '|', $keep->mark, '|', ini_get('precision');
    } finally { restore_error_handler(); echo '|Z'; }
    echo '|R|', ini_set('precision', '11'), '|', ini_get('precision');
}
echo 'B|'; nullStdCaller70();
''',
    'strict-null-stdclass-value-rejects-option-after-shared-property-effect': br'''<?php
declare(strict_types=1);
function strictNullStdValue70() {
    global $call, $option, $value, $keep, $effects;
    $early = $value; echo 'V|'; $effects++; $keep->mark = 'strict-value70';
    $call = 'constant'; $option = 'precision'; $value = 0;
    ini_set('precision', '9'); return $early;
}
function strictNullStdHandler70($level, $message) {
    global $warnings;
    echo 'BAD|'; $warnings++; return true;
}
function strictNullStdCaller70() {
    global $call, $option, $value, $keep, $effects, $warnings;
    $call = 'InI_SeT'; $option = null; $value = new stdClass;
    $value->mark = 'strict70'; $keep = $value;
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('strictNullStdHandler70', 8192);
    try { $result = $call($option, strictNullStdValue70()); echo 'BAD'; }
    catch (TypeError $e) {
        echo $e->getMessage(), '|', $result, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $option, '|', $value, '|', $keep->mark, '|', ini_get('precision');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; strictNullStdCaller70();
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
