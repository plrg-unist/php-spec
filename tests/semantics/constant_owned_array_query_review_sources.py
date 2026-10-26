#!/usr/bin/env python3
"""A captured ARRAY query keeps DIRECT snapshots and shared scalar references."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-array-query-weak-defined-reference-cow'
family.CASES = {
    CASE: br'''<?php
function v105ReviewArgument() {
    global $call, $name, $cell, $weakCall, $effects;
    ++$effects;
    $saved = $name;
    $name['plain'] = 29;
    $cell = 31;
    $call = 'constant';
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    return $saved;
}
define('V105_REVIEW_RECOVERY', 23);
$plain = 17;
$cell = 19;
$name = ['plain' => $plain, 'alias' => &$cell];
$call = defined(...);
$weakCall = WeakReference::create($call);
$effects = 0;
$result = 97;
echo 'B|';
try {
    $result = $call(v105ReviewArgument());
    echo 'RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    echo 'T|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'chained|';
    if (isset($trace[0]['args'][0])) {
        $rawArgs = $trace[0]['args'];
        $copy = $rawArgs[0];
        echo $trace[0]['function'], '|';
        echo isset($trace[0]['file']) && $trace[0]['file'] === __FILE__ ? 'file|' : 'noFile|';
        echo isset($trace[0]['line']) ? $trace[0]['line'] : 'internal';
        echo '|';
        echo isset($trace[1]) ? 'more|' : 'end|';
        echo $rawArgs[0]['plain'], '|', $rawArgs[0]['alias'], '|';
        echo $name['plain'], '|', $name['alias'], '|', $cell, '|';
        echo $call, '|', $result, '|', $effects, '|';
        echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
        $copy['plain'] = 47;
        $copy['alias'] = 53;
        echo $rawArgs[0]['plain'], '|', $rawArgs[0]['alias'], '|';
        echo $copy['plain'], '|', $copy['alias'], '|';
        echo $name['plain'], '|', $name['alias'], '|', $cell, '|';
        unset($error, $trace);
        echo $rawArgs[0]['plain'], '|', $rawArgs[0]['alias'], '|';
        unset($rawArgs);
        $cell = 59;
        echo $copy['plain'], '|', $copy['alias'], '|';
        echo $name['plain'], '|', $name['alias'], '|', $cell, '|';
    } else { echo 'noApi|'; }
}
unset($error, $trace, $rawArgs, $copy, $name, $cell);
$reader = constant(...);
echo $reader('V105_REVIEW_RECOVERY'), '|';
unset($reader, $call, $weakCall, $plain, $effects, $result);
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
