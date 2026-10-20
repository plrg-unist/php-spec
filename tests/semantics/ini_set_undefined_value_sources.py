#!/usr/bin/env python3
"""An undefined INI VALUE sends NULL despite assignments in its Warning handler."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-ini-undefined-value-warning-then-null-deprecated-keeps-fallback': br'''<?php
function iniUndefinedValueReturning85($level, $message) {
    global $call, $option, $missing, $warningKeep, $warnings, $deprecations;
    if ($level === 2) {
        echo 'W|', $level, '|', $message, '|'; $warnings++;
        $missing = [51]; $warningKeep = $missing;
        $call = 'ini_get'; $option = 'precision'; return true;
    }
    echo 'D|', $level, '|', $message, '|'; $deprecations++;
    $missing[0] = 53; $call = 'constant'; $option = 'changed';
    ini_set('precision', '8'); return false;
}
echo 'B|'; $call = 'InI_SeT'; $keep = $call; $option = null;
$warnings = 0; $deprecations = 0; $warningKeep = null; $result = 99;
set_error_handler('iniUndefinedValueReturning85', 8194);
try {
    $result = $call($option, $missing); echo $result === false ? 'F' : 'BAD';
} catch (TypeError $e) { echo 'TYPE|', $e->getMessage(); }
finally { restore_error_handler(); echo '|Z'; }
echo '|', $warnings, '|', $deprecations, '|', $missing[0], '|', $warningKeep[0];
echo '|', $call, '|', $option, '|', ini_get('precision');
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-owned-ini-undefined-value-warning-before-null-option-type-error': br'''<?php
declare(strict_types=1);
function iniUndefinedValueStrict85($level, $message) {
    global $call, $replacement, $option, $missing, $warningKeep, $warnings;
    echo 'W|', $level, '|', $message, '|'; $warnings++;
    $missing = [61]; $warningKeep = $missing;
    $call = $replacement; $option = 'precision';
    ini_set('precision', '9'); return true;
}
echo 'B|'; $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$option = null; $warnings = 0; $warningKeep = null; $result = 99;
set_error_handler('iniUndefinedValueStrict85', 8194);
try { $result = $call($option, $missing); echo 'BAD'; }
catch (TypeError $e) {
    $trace = $e->getTrace(); $args = $trace[0]['args'];
    echo $e->getMessage(), '|', $trace[0]['function'] === 'ini_set' ? 'I' : 'BAD';
    echo '|', $args[0] === null ? 'N' : 'BAD';
    echo '|', $args[1] === null ? 'N' : 'BAD';
    echo '|', $result, '|', $warnings, '|', $missing[0];
    echo '|', $call === $replacement ? 'G' : 'BAD';
    echo '|', $option, '|', ini_get('precision');
} finally { restore_error_handler(); echo '|Z'; }
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
    'strict-explicit-ini-undefined-value-false-warning-then-weak-null-reception': br'''<?php
declare(strict_types=1);
function iniUndefinedValueExplicit85($level, $message) {
    global $call, $replacement, $option, $missing, $warningKeep, $warnings, $deprecations;
    if ($level === 2) {
        echo 'W|', $level, '|', $message, '|'; $warnings++;
        $missing = [67]; $warningKeep = $missing;
        $call = $replacement; $option = 'precision'; return false;
    }
    echo 'D|', $level, '|', $message, '|'; $deprecations++;
    $missing[0] = 69; ini_set('precision', '10'); return true;
}
echo 'B|'; $call = ini_set(...); $keep = $call; $replacement = ini_get(...);
$option = null; $warnings = 0; $deprecations = 0; $warningKeep = null; $result = 99;
set_error_handler('iniUndefinedValueExplicit85', 8194);
try {
    $result = $call->__invoke($option, $missing); echo $result === false ? 'F' : 'BAD';
} catch (TypeError $e) { echo 'TYPE|', $e->getMessage(); }
finally { restore_error_handler(); echo '|Z'; }
echo '|', $warnings, '|', $deprecations, '|', $missing[0], '|', $warningKeep[0];
echo '|', $call === $replacement ? 'G' : 'BAD';
echo '|', $option, '|', ini_get('precision');
echo '|R|', $keep('precision', '11'), '|', ini_get('precision');
''',
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
