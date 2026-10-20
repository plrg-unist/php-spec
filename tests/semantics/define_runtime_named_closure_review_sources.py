#!/usr/bin/env python3
"""A rejected bare named Closure retires without owning its function statics."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'named-closure-array-discard-keeps-function-static-child': br'''<?php
class V88ReviewChild {
    public int $value = 7;
    public function __destruct() {
        global $destroyed;
        $destroyed++;
        echo 'D|', $this->value, '|';
    }
}
function v88ReviewKeep($incoming = null, $release = false) {
    static $held = null;
    static $count = 0;
    $count++;
    if ($incoming !== null) { $held = $incoming; }
    if ($release) { $held = null; }
    else { $held->value = 41; }
    return $count;
}
function v88ReviewName() {
    global $child, $input, $api;
    $child = null;
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V88_REVIEW_OLD';
}
function v88ReviewReport($level, $message) {
    global $cell, $calls, $destroyed;
    $calls++;
    $value = $cell();
    $cell = null;
    echo 'H|', $level, '|', $value, '|', $destroyed, '|';
    throw new Exception('V88_STOP');
}
define('V88_REVIEW_OLD', 17);
$destroyed = 0;
$calls = 0;
$child = new V88ReviewChild();
v88ReviewKeep($child);
$cell = v88ReviewKeep(...);
$input = ['edge' => &$cell];
$input[90] = 0;
unset($input[90]);
$api = 'define';
$result = 'kept';
set_error_handler('v88ReviewReport');
echo 'B|';
try {
    $result = $api(value: $input, case_insensitive: false, constant_name: v88ReviewName());
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
    echo $child === null ? 'dropped|' : 'BAD|';
    echo $api, '|', constant('V88_REVIEW_OLD'), '|', $calls, '|', $destroyed, '|', $result, '|';
    echo $input[90], '|';
    echo !isset($args[1][90]) ? 'split|' : 'BAD|';
    $raw[] = 53;
    echo isset($raw[91]) && !isset($args[1][91]) ? 'history|' : 'BAD|';
    unset($raw, $args, $frame, $trace, $error);
}
restore_error_handler();
unset($cell, $input, $child, $api, $result, $calls);
echo v88ReviewKeep(), '|', $destroyed, '|';
echo v88ReviewKeep(null, true), '|', $destroyed, '|';
unset($destroyed);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if (Path(stem).name == 'model' and Path(stem).parent.name ==
            'named-closure-array-discard-keeps-function-static-child'):
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '90']
        timeout = 105
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
