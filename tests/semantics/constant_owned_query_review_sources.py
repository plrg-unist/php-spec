#!/usr/bin/env python3
"""A captured CONSTANT callee raises its own Error before later reader recovery."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-query-explicit-missing-error-and-reader-recovery'
family.CASES = {
    CASE: br'''<?php
function v99ReviewName() {
    global $call, $name, $weak, $calls;
    ++$calls;
    $saved = $name;
    $call = 'defined';
    $name = 'V99_REVIEW_REBOUND';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
function v99ReviewRecoveryName() {
    global $call, $weakAgain;
    $call = null;
    echo 'R|';
    echo $weakAgain->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return 'V99_REVIEW_LATE';
}
$call = constant(...);
$weak = WeakReference::create($call);
$name = 'V99_REVIEW_MISSING';
$calls = 0;
$result = 97;
echo 'B|';
try {
    $result = $call->__invoke(v99ReviewName());
    echo 'BAD_RETURN|';
} catch (Error $error) {
    $trace = $error->getTrace();
    $rawApi = $trace[0]['args'];
    $rawInvoke = $trace[1]['args'];
    echo 'E|', $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|', $trace[1]['function'], '|';
    echo $rawApi[0], '|';
    echo $rawInvoke === $rawApi ? 'rawsame|' : 'BAD|';
    echo $name, '|', $call, '|', $result, '|', $calls, '|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    echo defined('V99_REVIEW_MISSING') ? 'BAD_DEFINED|' : 'absent|';
    define('V99_REVIEW_LATE', 23);
    $call = constant(...);
    $weakAgain = WeakReference::create($call);
    $recovered = $call(v99ReviewRecoveryName());
    echo $recovered, '|';
    echo $call === null ? 'null|' : 'BAD|';
    echo $weakAgain->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $rawApi[0], '|';
    unset($rawApi, $rawInvoke, $trace, $error);
}
echo 'A|';
unset($call, $name, $weak, $weakAgain, $calls, $result, $recovered);
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
