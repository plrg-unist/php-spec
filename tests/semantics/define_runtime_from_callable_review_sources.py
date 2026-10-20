#!/usr/bin/env python3
"""A retired factory retains invocation scope without becoming a Closure owner."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'retired-factory-private-closure-copy-retires-receiver-before-catch': br'''<?php
class V91ReviewBase {
    private int $value = 7;
    private function read() {
        global $reads;
        $reads++;
        $this->value = 41;
        echo 'C|', $this->value, '|', $this->shadow(), '|', static::class, '|';
        return $this->value;
    }
    public function currentValue() { return $this->value; }
    public function capture($factory, &$saved) {
        $callback = [$this, 'read'];
        $saved = $factory(callback: $callback);
    }
}
class V91ReviewReceiver extends V91ReviewBase {
    private int $value = 97;
    public function shadow() { return $this->value; }
    public function read() { echo 'BAD_OVERRIDE|'; return $this->value; }
    public function __destruct() {
        global $destroyed;
        $destroyed++;
        echo 'D|', $this->currentValue(), '|';
    }
}
function v91ReviewName() {
    global $owner, $input, $api;
    $owner = null;
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V91_REVIEW_OLD';
}
function v91ReviewReport($level, $message) {
    global $cell, $calls;
    $calls++;
    $value = $cell();
    $cell = null;
    echo 'H|', $level, '|', $value, '|', constant('V91_REVIEW_OLD'), '|';
    throw new Exception('V91_STOP');
}
define('V91_REVIEW_OLD', 17);
$destroyed = 0;
$reads = 0;
$calls = 0;
$factory = Closure::fromCallable(...);
$owner = new V91ReviewReceiver();
$cell = null;
$owner->capture($factory, $cell);
unset($factory);
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$api = 'define';
$result = 'kept';
set_error_handler('v91ReviewReport');
echo 'B|';
try {
    $result = $api(value: $input, case_insensitive: false, constant_name: v91ReviewName());
    echo 'BAD_RETURN|';
} catch (Exception $error) {
    $trace = $error->getTrace();
    $frame = $trace[1];
    $args = $frame['args'];
    $raw = $args[1];
    echo 'E|', $error->getMessage(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $frame['function'], '|';
    echo $args[2] === false ? 'false|' : 'BAD|';
    echo $raw['edge'] === null && $cell === null ? 'null|' : 'BAD|';
    echo $owner === null ? 'dropped|' : 'BAD|';
    echo $api, '|', constant('V91_REVIEW_OLD'), '|', $calls, '|', $reads, '|', $destroyed, '|', $result, '|';
    echo $input[90], '|';
    echo !isset($args[1][90]) ? 'split|' : 'BAD|';
    $raw[] = 53;
    echo isset($raw[91]) && !isset($args[1][91]) ? 'history|' : 'BAD|';
    unset($raw, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($cell, $input, $owner, $api, $result, $calls, $reads, $destroyed);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and Path(stem).parent.name ==
            'retired-factory-private-closure-copy-retires-receiver-before-catch'):
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
