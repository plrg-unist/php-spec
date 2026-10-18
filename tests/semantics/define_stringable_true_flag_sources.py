#!/usr/bin/env python3
"""Native-first Stringable define names with captured boolean-true flags."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'stringable-true-flag-fresh-duplicate-and-class-priority': br'''<?php
class TrueFlagName59 {
    public function __toString(): string {
        global $calls; echo 'S|'; $calls++;
        if ($calls === 3) { return 'A::B59'; }
        return 'STRINGTRUE59';
    }
}
$name = new TrueFlagName59; $keep = $name; $calls = 0;
echo 'B|', define($name, 1733, true) ? 'T' : 'BAD', '|', constant('STRINGTRUE59');
echo '|', define($name, 1747, true) === false ? 'F' : 'BAD', '|', constant('STRINGTRUE59');
$result = 99;
try { $result = define($name, 1769, true); echo 'BAD'; }
catch (ValueError $e) { echo '|', $e->getMessage(), '|', $result, '|', $calls; }
''',
    'stringable-throw-cancels-before-captured-true-flag-warning': br'''<?php
class CancelTrueFlagName59 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $calls, $saved;
        echo 'S|'; $calls++; define('SOURCE59CAST', 1789);
        $call = 'constant'; $name = 'STRINGTRUECANCEL59'; $value = 997; $flag = false;
        $saved = new Exception('cast59-stop'); throw $saved;
    }
}
function cancelTrueWarning59($level, $message) {
    global $warnings; echo 'BAD-W|'; $warnings++; return true;
}
function cancelTrueValue59() {
    global $call, $name, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++; $call = 'defined';
    $name = 'value-live59'; return $earlier;
}
function cancelTrueFlag59() {
    global $call, $name, $flag, $effects;
    $earlier = $flag; echo 'F|'; $effects++; $flag = false;
    $call = 'constant'; $name = 'flag-live59'; return $earlier;
}
function cancelTrueCaller59() {
    global $call, $name, $value, $flag, $calls, $saved, $warnings, $effects;
    $call = 'DeFiNe'; $name = new CancelTrueFlagName59; $keep = $name;
    $part = 'captured'; $value = $part . '-candidate59'; $flag = true;
    $calls = 0; $warnings = 0; $effects = 0; $saved = null; $result = 99;
    set_error_handler('cancelTrueWarning59');
    try { $result = $call($name, cancelTrueValue59(), cancelTrueFlag59()); echo 'BAD'; }
    catch (Exception $e) {
        echo $e === $saved ? 'I' : 'BAD', '|', $result, '|', $calls, '|', $effects, '|', $warnings;
        echo '|', $call, '|', $name, '|', $value, '|', $flag === false ? 'F' : 'BAD';
        echo '|', defined('STRINGTRUECANCEL59') === false ? 'A' : 'BAD', '|', constant('SOURCE59CAST');
    } finally { restore_error_handler(); echo '|Z'; }
}
echo 'B|'; cancelTrueCaller59();
''',
    'strict-stringable-true-flag-rejects-name-after-argument-effects': br'''<?php
declare(strict_types=1);
class StrictTrueFlagName59 {
    public function __toString(): string {
        global $calls; echo 'BAD-S|'; $calls++; return 'STRICTTRUE59';
    }
}
function strictTrueFlag59() {
    global $call, $name, $flag, $effects;
    $earlier = $flag; echo 'F|'; $effects++; $flag = false;
    $call = 'constant'; $name = 'strict-live59'; return $earlier;
}
function strictTrueCaller59() {
    global $call, $name, $flag, $calls, $effects;
    $call = 'DeFiNe'; $name = new StrictTrueFlagName59; $keep = $name;
    $flag = true; $calls = 0; $effects = 0; $result = 99;
    try { $result = $call($name, 1801, strictTrueFlag59()); echo 'BAD'; }
    catch (TypeError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === $keep ? 'O' : 'BAD', '|', $trace[0]['args'][1];
        echo '|', $trace[0]['args'][2] === true ? 'T' : 'BAD', '|', $trace[1]['function'];
        echo '|', $result, '|', $calls, '|', $effects, '|', $flag === false ? 'F' : 'BAD';
    }
}
echo 'B|'; strictTrueCaller59();
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
