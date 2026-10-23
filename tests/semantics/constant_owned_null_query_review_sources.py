#!/usr/bin/env python3
"""A captured NULL query retains its owner until a real handler throws."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-null-query-explicit-handler-throw-and-reader-recovery'
family.CASES = {
    CASE: br'''<?php
declare(strict_types=1);
function v101ReviewName() {
    global $call, $name, $weak, $arguments;
    ++$arguments;
    $saved = $name;
    $call = 'defined';
    $name = 'V101_ARGUMENT';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
function v101ReviewStop($level, $message, $file, $line) {
    global $call, $name, $weak, $calls, $held;
    ++$calls;
    $call = null;
    $name = 'V101_HANDLER';
    echo 'H|', $level, '|', $message, '|', $line, '|';
    echo $file === __FILE__ ? 'file|' : 'BAD|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    define('', 23);
    $held = new Exception('V101_STOP');
    throw $held;
}
function v101ReviewRecoveryName() {
    global $call, $weakRead;
    $call = null;
    echo 'R|';
    echo $weakRead->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return '';
}
$call = constant(...);
$weak = WeakReference::create($call);
$name = null;
$arguments = 0;
$calls = 0;
$held = null;
$result = 97;
set_error_handler('v101ReviewStop');
echo 'B|';
try {
    $result = $call->__invoke(name: v101ReviewName());
    echo 'BAD_RETURN|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $rawApi = $trace[1]['args'];
    $rawInvoke = $trace[2]['args'];
    echo 'E|', $error === $held ? 'same|' : 'BAD|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $error->getMessage(), '|', $error->getLine(), '|';
    echo $trace[0]['function'], '|', $trace[1]['function'], '|', $trace[2]['function'], '|';
    echo $trace[0]['args'][0] === 8192 ? 'level|' : 'BAD|';
    echo $rawApi[0] === null && $rawInvoke[0] === null ? 'rawN|' : 'BAD|';
    echo $rawApi === $rawInvoke ? 'rawsame|' : 'BAD|';
    echo $result, '|', $arguments, '|', $calls, '|', $name, '|';
    echo $call === null ? 'null|' : 'BAD|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    restore_error_handler();
    $call = constant(...);
    $weakRead = WeakReference::create($call);
    $recovered = $call(name: v101ReviewRecoveryName());
    echo $recovered, '|';
    echo $call === null ? 'null|' : 'BAD|';
    echo $weakRead->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $rawApi[0] === null && $rawInvoke[0] === null ? 'keptN|' : 'BAD|';
}
unset($error, $held, $trace, $rawApi, $rawInvoke);
unset($call, $name, $weak, $weakRead, $arguments, $calls, $result, $recovered);
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
