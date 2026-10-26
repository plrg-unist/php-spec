#!/usr/bin/env python3
"""Captured array query TypeErrors preserve snapshots and wrapper COW."""
from pathlib import Path

import global_constant_sources as family

STRICT = 'owned-array-query-strict-captured-direct-cow'
EXPLICIT = 'owned-array-query-explicit-api-wrapper-cow'
family.CASES = {
    STRICT: br'''<?php
declare(strict_types=1);
function v105StrictArgument() {
    global $call, $name, $weakCall, $effects;
    ++$effects;
    $saved = $name;
    $name['plain'] = 'strict-live';
    $call = 'defined';
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
    return $saved;
}
define('V105_STRICT_RECOVERY', 17);
$part = 'strict';
$number = 17;
$name = ['plain' => $part . '-old', 3 => $number];
$snapshot = $name;
$call = constant(...);
$weakCall = WeakReference::create($call);
$effects = 0;
$result = 97;
echo 'B|';
try {
    $result = $call(v105StrictArgument());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $rawArgs = $trace[0]['args'];
    $raw = $rawArgs[0];
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|', $trace[0]['line'], '|';
    echo $trace[0]['file'] === __FILE__ ? 'file|' : 'BAD|';
    echo isset($trace[1]) ? 'more|' : 'end|';
    echo $raw['plain'], '|', $raw[3], '|', $name['plain'], '|', $snapshot['plain'], '|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $call, '|', $result, '|', $effects, '|';
    $raw['plain'] = 'strict-raw';
    echo $raw['plain'], '|', $name['plain'], '|', $snapshot['plain'], '|';
    echo $trace[0]['args'][0]['plain'], '|';
}
unset($error, $trace, $rawArgs, $name, $snapshot);
echo 'R|', $raw['plain'], '|', $raw[3], '|';
unset($raw);
$reader = constant(...);
echo $reader('V105_STRICT_RECOVERY'), '|';
unset($reader, $call, $weakCall, $part, $number, $result, $effects);
echo 'A|';
''',
    EXPLICIT: br'''<?php
declare(strict_types=1);
function v105ExplicitArgument() {
    global $call, $name, $weakCall, $effects;
    ++$effects;
    $saved = $name;
    $call = null;
    $name = null;
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
    return $saved;
}
define('V105_EXPLICIT_RECOVERY', 23);
$part = 'explicit';
$flag = false;
$name = ['plain' => $part . '-old', 5 => $flag];
$call = defined(...);
$weakCall = WeakReference::create($call);
$effects = 0;
$result = 97;
echo 'B|';
try {
    $result = $call->__invoke(v105ExplicitArgument());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $rawApiArgs = $trace[0]['args'];
    $api = $rawApiArgs[0];
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|', $trace[0]['line'], '|';
    echo $trace[0]['file'] === __FILE__ ? 'apiFile|' : 'BAD|';
    if (isset($trace[1]['args'][0])) {
        $rawInvokeArgs = $trace[1]['args'];
        $invoke = $rawInvokeArgs[0];
        echo $trace[1]['function'], '|', $trace[1]['class'], '|', $trace[1]['type'], '|';
        echo $trace[1]['line'], '|';
        echo $trace[1]['file'] === __FILE__ ? 'invokeFile|' : 'BAD|';
        echo $invoke['plain'], '|';
    } else { echo 'noWrapper|'; }
    echo isset($trace[2]) ? 'more|' : 'end|';
    echo $api['plain'], '|';
    echo $api[5] === false ? 'F|' : 'BAD|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $call === null && $name === null ? 'currentNull|' : 'BAD|';
    echo $result, '|', $effects, '|';
    $api['plain'] = 'explicit-api';
    if (isset($rawInvokeArgs)) {
        $invoke[5] = true;
        echo $api['plain'], '|', $invoke['plain'], '|';
        echo $api[5] === false && $invoke[5] === true ? 'FT|' : 'BAD|';
        echo $trace[0]['args'][0]['plain'], '|';
        echo $trace[1]['args'][0][5] === false ? 'traceF|' : 'BAD|';
    }
}
unset($error, $trace, $rawApiArgs, $rawInvokeArgs);
echo 'R|', $api['plain'], '|';
if (isset($invoke)) { echo $invoke['plain'], '|'; }
unset($api);
if (isset($invoke)) { echo 'I|', $invoke['plain'], '|'; }
unset($invoke);
$reader = constant(...);
echo $reader('V105_EXPLICIT_RECOVERY'), '|';
unset($reader, $call, $weakCall, $part, $flag, $result, $effects);
echo 'A|';
''',
}
family.BASELINE = ('class constant value query', b'B|N|held|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name in family.CASES:
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '180']
        timeout = 195
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
