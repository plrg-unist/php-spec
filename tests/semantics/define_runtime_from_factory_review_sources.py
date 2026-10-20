#!/usr/bin/env python3
"""Factory creation scope does not authorize a later global callback lookup."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'published-factory-global-denial-retains-raw-receiver-trace': br'''<?php
class V92ReviewReceiver {
    private int $value = 7;
    public static function factory() { return Closure::fromCallable(...); }
    private function read() {
        global $reads;
        $reads++;
        echo 'BAD_READ|';
        return $this->value;
    }
    public function change($value) { $this->value = $value; }
    public function currentValue() { return $this->value; }
    public function __destruct() {
        global $destroyed;
        $destroyed++;
        echo 'D|', $this->value, '|';
    }
}
function v92ReviewMethod() {
    global $owner, $call;
    $owner = null;
    $call = 'defined';
    echo 'N|';
    return 'read';
}
function v92ReviewReport($level, $message) {
    global $calls;
    $calls++;
    echo 'BAD_HANDLER|';
    return true;
}
$factory = V92ReviewReceiver::factory();
echo 'B|';
$result = define('V92_REVIEW_FACTORY', $factory, false);
$call = constant('V92_REVIEW_FACTORY');
echo $result === true && $call === $factory ? 'T|same|' : 'BAD|';
unset($factory);
$owner = new V92ReviewReceiver();
$reads = 0;
$destroyed = 0;
$calls = 0;
$result = 'kept';
set_error_handler('v92ReviewReport');
try {
    $result = $call->__invoke(callback: [$owner, v92ReviewMethod()]);
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $frame = $trace[1];
    $args = $frame['args'];
    $raw = $args[0];
    $receiver = $raw[0];
    echo 'E|', $trace[0]['function'], '|', $frame['function'], '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $raw[1] === 'read' ? 'read|' : 'BAD|';
    echo $owner === null ? 'dropped|' : 'BAD|';
    echo $call, '|', $result, '|', $calls, '|', $reads, '|', $destroyed, '|';
    $receiver->change(41);
    echo $trace[0]['args'][0][0] === $receiver ? 'shared|' : 'BAD|';
    echo $trace[0]['args'][0][0]->currentValue(), '|kept-trace|';
    unset($receiver, $raw, $args, $frame, $trace, $error);
}
echo 'released|', $destroyed, '|';
restore_error_handler();
$again = constant('V92_REVIEW_FACTORY');
echo $again instanceof Closure ? 'factory|' : 'BAD|';
unset($again, $owner, $call, $result, $calls, $reads, $destroyed);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and Path(stem).parent.name ==
            'published-factory-global-denial-retains-raw-receiver-trace'):
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '120']
        timeout = 135
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
