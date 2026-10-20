#!/usr/bin/env python3
"""A rejected private array retires its child before the captured DEFINE owner."""
from pathlib import Path

import global_constant_sources as family


CASE = 'owned-define-array-duplicate-child-before-callee-retirement'
family.CASES = {
    CASE: br'''<?php
const V94_REVIEW_ARRAY = 17;
class V94ReviewPayload {
    public int $value = 7;
    function __destruct() {
        global $weak, $destroyed;
        ++$destroyed;
        echo 'D|', $this->value, '|';
        echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    }
}
function v94ReviewFlag() {
    global $call, $source, $weak;
    $call = 'defined';
    $source[90] = 90;
    unset($source['leaf']);
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return false;
}
function v94ReviewReport($level, $message) {
    global $slot, $calls, $weak, $chosen;
    ++$calls;
    $slot->value = 41;
    $slot = null;
    echo 'H|', $level, '|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    $chosen = new Exception('STOP');
    throw $chosen;
}
$slot = new V94ReviewPayload;
$source = ['leaf' => &$slot];
$call = define(...);
$weak = WeakReference::create($call);
$calls = 0;
$destroyed = 0;
$result = 97;
$chosen = null;
set_error_handler('v94ReviewReport');
echo 'B|';
try {
    $result = $call->__invoke('V94_REVIEW_ARRAY', $source, v94ReviewFlag());
    echo 'BAD_RETURN|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $rawApi = $trace[1]['args'];
    $rawInvoke = $trace[2]['args'];
    echo 'E|', $error === $chosen ? 'same|' : 'BAD|';
    echo $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|', $trace[1]['function'], '|', $trace[2]['function'], '|';
    echo $rawApi[0], '|';
    echo $rawApi[1]['leaf'] === null ? 'null|' : 'BAD|';
    echo $rawApi[2] === false ? 'false|' : 'BAD|';
    echo $rawInvoke === $rawApi ? 'rawsame|' : 'BAD|';
    echo $call, '|', $source[90], '|', $result, '|', $calls, '|', $destroyed, '|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    unset($rawInvoke, $rawApi, $trace, $error, $chosen);
}
restore_error_handler();
echo constant('V94_REVIEW_ARRAY'), '|A|';
unset($weak, $call, $source, $slot, $calls, $destroyed, $result);
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name == CASE:
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '150']
        timeout = 165
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
