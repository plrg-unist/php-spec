#!/usr/bin/env python3
"""Strict captured queries and distinct converted API/raw wrapper arguments."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-scalar-query-strict-and-explicit-trace-recovery'
family.CASES = {
    CASE: br'''<?php
declare(strict_types=1);
function v100ReviewStrictName() {
    global $call, $name, $weakStrict, $calls;
    ++$calls;
    $saved = $name;
    $call = null;
    $name = 911;
    echo 'S|';
    echo $weakStrict->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
function v100ReviewFloatName() {
    global $call, $name, $weakFloat, $calls;
    ++$calls;
    $saved = $name;
    $call = 'defined';
    $name = 0.0;
    echo 'F|';
    echo $weakFloat->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
function v100ReviewRecoveryName() {
    global $call, $weakRead;
    $call = null;
    echo 'R|';
    echo $weakRead->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return '2.5';
}
$call = defined(...);
$weakStrict = WeakReference::create($call);
$name = true;
$calls = 0;
$result = 97;
echo 'B|';
try {
    $result = $call(constant_name: v100ReviewStrictName());
    echo 'BAD_RETURN|';
} catch (TypeError $strictError) {
    $strictTrace = $strictError->getTrace();
    echo 'T|', $strictError->getMessage(), '|', $strictError->getLine(), '|';
    echo $strictError->getPrevious() === null ? 'none|' : 'BAD|';
    echo $strictTrace[0]['function'], '|';
    echo $strictTrace[0]['args'][0] === true ? 'rawT|' : 'BAD|';
    echo $call === null ? 'null|' : 'BAD|';
    echo $name === 911 ? 'currentI|' : 'BAD|';
    echo $result, '|', $calls, '|';
    echo $weakStrict->get() === null ? 'gone|' : 'BAD_HELD|';
}
$call = constant(...);
$weakFloat = WeakReference::create($call);
$name = 37.5;
try {
    $result = $call->__invoke(name: v100ReviewFloatName());
    echo 'BAD_RETURN|';
} catch (Error $floatError) {
    $floatTrace = $floatError->getTrace();
    $rawApi = $floatTrace[0]['args'];
    $rawInvoke = $floatTrace[1]['args'];
    echo 'E|', $floatError->getMessage(), '|', $floatError->getLine(), '|';
    echo $floatError->getPrevious() === null ? 'none|' : 'BAD|';
    echo $floatTrace[0]['function'], '|', $floatTrace[1]['function'], '|';
    echo $rawApi[0] === '37.5' ? 'apiS|' : 'BAD|';
    echo $rawInvoke[0] === 37.5 ? 'invokeD|' : 'BAD|';
    echo $rawApi !== $rawInvoke ? 'distinct|' : 'BAD|';
    echo $strictTrace[0]['args'][0] === true ? 'stillT|' : 'BAD|';
    echo $call, '|';
    echo $name === 0.0 ? 'currentD|' : 'BAD|';
    echo $result, '|', $calls, '|';
    echo $weakFloat->get() === null ? 'gone|' : 'BAD_HELD|';
    define('2.5', 23);
    $call = constant(...);
    $weakRead = WeakReference::create($call);
    $recovered = $call(name: v100ReviewRecoveryName());
    echo $recovered, '|';
    echo $call === null ? 'null|' : 'BAD|';
    echo $weakRead->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $rawApi[0] === '37.5' && $rawInvoke[0] === 37.5 ? 'kept|' : 'BAD|';
}
unset($strictError, $strictTrace, $floatError, $floatTrace, $rawApi, $rawInvoke);
unset($call, $name, $weakStrict, $weakFloat, $weakRead, $calls, $result, $recovered);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name == CASE:
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
