#!/usr/bin/env python3
"""Native-first two-slot ini_set NULL options and deprecation continuations."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'ordinary-null-ini-set-default-and-precision-recovery': br'''<?php
echo 'B|', ini_set(null, 1973) === false ? 'F' : 'BAD', '|', ini_get('precision');
echo '|R|', ini_set('precision', '12'), '|', ini_get('precision');
''',
    'selected-null-option-handler-preserves-captures-and-precision': br'''<?php
function setNullOptionValue62() {
    global $call, $option, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++; ini_set('precision', '6');
    $call = 'ini_get'; $option = 'precision'; $value = 'value-live62'; return $earlier;
}
function setNullOptionHandler62($level, $message) {
    global $call, $option, $value, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    ini_set('precision', '8'); $call = 'ini_restore';
    $option = 'precision'; $value = 'handler-value62'; return true;
}
function selectedNullSetCaller62() {
    global $call, $option, $value, $effects, $warnings;
    $call = 'InI_SeT'; $option = null;
    $part = 'captured'; $value = $part . '-value62';
    $effects = 0; $warnings = 0; $result = 99;
    set_error_handler('setNullOptionHandler62');
    try {
        $result = $call($option, setNullOptionValue62());
        echo $result === false ? 'F' : 'BAD', '|', ini_get('precision');
        echo '|', $effects, '|', $warnings, '|', $call, '|', $option, '|', $value;
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; selectedNullSetCaller62();
''',
    'strict-null-ini-set-option-before-value-after-effects': br'''<?php
declare(strict_types=1);
function strictSetNullValue62() {
    global $call, $option, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++; ini_set('precision', '9');
    $call = 'ini_get'; $option = 'precision'; $value = 0; return $earlier;
}
function strictNullSetCaller62() {
    global $call, $option, $value, $effects;
    $call = 'InI_SeT'; $option = null; $value = 1987; $effects = 0; $result = 99;
    try { $result = $call($option, strictSetNullValue62()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === null ? 'N' : 'BAD', '|', $trace[0]['args'][1];
        echo '|', $trace[1]['function'], '|', $result, '|', $effects, '|', ini_get('precision');
        echo '|', $call, '|', $option, '|', $value;
    }
}
echo 'B|'; strictNullSetCaller62();
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
