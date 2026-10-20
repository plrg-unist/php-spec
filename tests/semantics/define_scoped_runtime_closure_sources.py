#!/usr/bin/env python3
"""Native-first scoped REAL Closure values with lexical/called scope."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'scoped-real-closure-private-access-and-normal-duplicate': br'''<?php
class V87Base {
    private int $value = 7;
    public function change($value) { $this->value = $value; }
    public function make() {
        return function () {
            static $count = 0;
            ++$count;
            echo 'C|', $this->value, '|', static::class, '|';
            return $count;
        };
    }
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
class V87Child extends V87Base { private int $value = 100; }
function v87Name() {
    global $candidate, $right, $owner, $api;
    $candidate = $right;
    $owner->change(23);
    $owner = null;
    $api = 'constant';
    echo 'N|';
    return 'V87_SCOPED';
}
function v87Duplicate($level, $message) {
    global $candidate, $other, $calls;
    $calls++;
    $other->change(41);
    echo 'H|', $level, '|', $candidate(), '|';
    $candidate = null;
    return true;
}
$owner = new V87Child();
$left = $owner->make();
$other = new V87Child();
$other->change(100);
$right = $other->make();
$candidate = $left;
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api(value: $candidate, case_insensitive: false, constant_name: v87Name());
echo $result === true ? 'T|' : 'BAD|';
$stored = $api('V87_SCOPED');
echo $stored === $left && $candidate === $right ? 'same|' : 'BAD|';
echo $stored(), '|', $left(), '|', $right(), '|';
$api = 'define';
set_error_handler('v87Duplicate');
$result = $api('V87_SCOPED', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === null ? 'null|' : 'BAD|';
$again = constant('V87_SCOPED');
echo $again === $left ? 'same|' : 'BAD|';
echo $again(), '|', $left(), '|', $calls, '|';
unset($stored, $again, $candidate, $left, $right, $other, $owner, $api, $calls, $result);
echo 'A|';
''',
    'scoped-static-real-closure-array-snapshot-and-query-cow': br'''<?php
class V87ArrayBase {
    private static int $seed = 7;
    public static function change($value) { self::$seed = $value; }
    public static function make() {
        return static function () {
            static $count = 0;
            ++$count;
            echo 'S|', self::$seed, '|', static::class, '|';
            return $count;
        };
    }
}
class V87ArrayChild extends V87ArrayBase { private static int $seed = 900; }
function v87ArrayName() {
    global $input, $api;
    V87ArrayChild::change(23);
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V87_SCOPED_ARRAY';
}
$slot = V87ArrayChild::make();
$input = ['edge' => &$slot];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v87ArrayName());
echo $result === true ? 'T|' : 'BAD|';
$slot = null;
$copy = constant('V87_SCOPED_ARRAY');
$stored = $copy['edge'];
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge'] === null ? 'null|' : 'BAD|';
echo $api, '|', $stored(), '|';
$bucket =& $copy['edge'];
$bucket = null;
V87ArrayChild::change(41);
$again = constant('V87_SCOPED_ARRAY');
$shared = $again['edge'];
echo $copy['edge'] === null ? 'local-null|' : 'BAD|';
echo $shared === $stored ? 'same|' : 'BAD|';
echo $shared(), '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($bucket, $copy, $again, $shared, $stored, $slot, $input, $api, $result);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|N|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name in family.CASES:
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
