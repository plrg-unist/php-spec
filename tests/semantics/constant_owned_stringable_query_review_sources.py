#!/usr/bin/env python3
"""Explicit Stringable query errors retain the wrapper object after callee death."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-stringable-query-explicit-missing-error-and-raw-retention'
family.CASES = {
    CASE: br'''<?php
declare(strict_types=1);
class V102ReviewName {
    public function __toString(): string {
        global $call, $name, $weakCall, $casts;
        ++$casts;
        $call = null;
        $name = null;
        echo 'S|';
        echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'BAD_GONE|';
        return 'V102_REVIEW_MISSING';
    }
    public function __destruct() {
        global $weakCall, $drops;
        ++$drops;
        echo 'D|';
        echo $weakCall->get() === null ? 'calleeGone|' : 'BAD_HELD|';
    }
}
$casts = 0;
$drops = 0;
$call = constant(...);
$weakCall = WeakReference::create($call);
$name = new V102ReviewName;
$weakName = WeakReference::create($name);
$result = 97;
echo 'B|';
try {
    $result = $call->__invoke($name);
    echo 'BAD_RETURN|';
} catch (Error $error) {
    $trace = $error->getTrace();
    $rawApi = $trace[0]['args'];
    $rawInvoke = $trace[1]['args'];
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|', $trace[1]['function'], '|';
    echo $rawApi[0] === 'V102_REVIEW_MISSING' ? 'apiS|' : 'BAD|';
    echo $rawInvoke[0] instanceof V102ReviewName ? 'invokeObject|' : 'BAD|';
    echo $rawInvoke[0] === $weakName->get() ? 'same|' : 'BAD|';
    echo $call === null && $name === null ? 'currentNull|' : 'BAD|';
    echo $result, '|', $casts, '|', $drops, '|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'BAD_HELD|';
    echo $weakName->get() instanceof V102ReviewName ? 'traceHeld|' : 'BAD_GONE|';
    unset($error, $trace);
    echo $weakName->get() instanceof V102ReviewName ? 'rawHeld|' : 'BAD_GONE|';
    echo $drops, '|';
    unset($rawInvoke);
    echo $weakName->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $drops, '|', $rawApi[0], '|';
    unset($rawApi);
}
unset($call, $name, $weakCall, $weakName, $casts, $drops, $result);
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
