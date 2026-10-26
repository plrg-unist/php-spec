#!/usr/bin/env python3
"""A captured weak query rejects ordinary toString and retains its raw argument."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-nonstringable-query-weak-defined-raw-retention'
family.CASES = {
    CASE: br'''<?php
class V104ReviewName {
    public function toString(): string {
        global $methodCalls;
        ++$methodCalls;
        echo 'BAD_METHOD|';
        return 'TRUE';
    }
    public function __destruct() {
        global $drops, $weakCall;
        ++$drops;
        echo 'D|';
        echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
        define('V104_REVIEW_RECOVERY', 23);
    }
}
function v104ReviewArgument() {
    global $call, $name, $weakCall, $effects;
    ++$effects;
    $raw = $name;
    $call = null;
    $name = null;
    echo 'A|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    return $raw;
}
$methodCalls = 0;
$effects = 0;
$drops = 0;
$call = defined(...);
$weakCall = WeakReference::create($call);
$name = new V104ReviewName;
$weakName = WeakReference::create($name);
$result = 97;
$rawArgs = null;
echo 'B|';
try {
    $result = $call(v104ReviewArgument());
    echo 'RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    echo 'T|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'chained|';
    if (isset($trace[0]['args'][0])) {
        $rawArgs = $trace[0]['args'];
        echo $trace[0]['function'], '|';
        echo isset($trace[0]['file']) && $trace[0]['file'] === __FILE__ ? 'file|' : 'noFile|';
        echo isset($trace[0]['line']) ? $trace[0]['line'] : 'internal';
        echo '|';
        echo $rawArgs[0] instanceof V104ReviewName ? 'rawObject|' : 'other|';
        echo $rawArgs[0] === $weakName->get() ? 'same|' : 'different|';
    } else { echo 'noApi|'; }
    echo isset($trace[1]) ? 'more|' : 'end|';
    echo $call === null && $name === null ? 'currentNull|' : 'changed|';
    echo $result, '|', $effects, '|', $methodCalls, '|', $drops, '|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakName->get() instanceof V104ReviewName ? 'traceHeld|' : 'nameGone|';
    unset($error, $trace);
    echo $weakName->get() instanceof V104ReviewName ? 'rawHeld|' : 'nameGone|';
    echo $drops, '|';
    unset($rawArgs);
    echo $weakName->get() === null ? 'gone|' : 'held|';
    echo $drops, '|', $methodCalls, '|';
}
$reader = constant(...);
echo $reader('V104_REVIEW_RECOVERY'), '|';
unset($reader, $call, $name, $weakCall, $weakName, $methodCalls, $effects, $drops, $result, $rawArgs);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).parent.name == CASE and Path(stem).name in ('model', 'model-' + CASE):
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '90' if Path(stem).name != 'model' else '180']
        timeout = 105 if Path(stem).name != 'model' else 195
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
