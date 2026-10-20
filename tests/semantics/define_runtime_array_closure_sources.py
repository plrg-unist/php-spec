#!/usr/bin/env python3
"""Native-first array-selected Closure VALUES after callable-array retirement."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'array-closure-selected-receiver-and-normal-duplicate': br'''<?php
class V89Base {
    private int $value = 7;
    public function change($value) { $this->value = $value; }
    public function read() {
        static $count = 0;
        ++$count;
        echo 'C|', $this->value, '|', static::class, '|';
        return $count;
    }
    public function other() { echo 'BAD_METHOD|'; }
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
class V89Child extends V89Base { private int $value = 100; }
function v89Name() {
    global $candidate, $right, $owner, $receiver, $method, $source, $other, $api;
    $candidate = $right;
    $owner->change(23);
    $owner = null;
    $receiver = $other;
    $method = 'other';
    $source = null;
    $receiver = null;
    $api = 'constant';
    echo 'N|';
    return 'V89_ARRAY_CLOSURE';
}
function v89Duplicate($level, $message) {
    global $candidate, $other, $calls;
    ++$calls;
    $other->change(41);
    echo 'H|', $level, '|', $candidate(), '|';
    $candidate = null;
    return true;
}
$owner = new V89Child();
$receiver = $owner;
$method = 'read';
$source = [&$receiver, &$method];
$left = $source(...);
$other = new V89Child();
$other->change(100);
$otherSource = [$other, 'read'];
$right = $otherSource(...);
unset($otherSource);
$candidate = $left;
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api(value: $candidate, case_insensitive: false, constant_name: v89Name());
echo $result === true ? 'T|' : 'BAD|';
$stored = $api('V89_ARRAY_CLOSURE');
echo $stored === $left && $candidate === $right ? 'same|' : 'BAD|';
echo $source === null && $receiver === null && $method === 'other' ? 'retired|' : 'BAD|';
echo $stored(), '|', $right(), '|';
$api = 'define';
set_error_handler('v89Duplicate');
$result = $api('V89_ARRAY_CLOSURE', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === null ? 'null|' : 'BAD|';
$again = constant('V89_ARRAY_CLOSURE');
echo $again === $left ? 'same|' : 'BAD|';
echo $again(), '|', $calls, '|';
unset($stored, $again, $candidate, $left, $right, $other, $owner, $receiver, $method, $source, $api, $calls, $result);
echo 'A|';
''',
    'static-array-closure-snapshot-query-cow-and-shared-method-static': br'''<?php
class V89ArrayBase {
    private static int $seed = 7;
    public static function change($value) { self::$seed = $value; }
    public static function read() {
        static $count = 0;
        ++$count;
        echo 'S|', self::$seed, '|', static::class, '|';
        return $count;
    }
}
class V89ArrayChild extends V89ArrayBase { private static int $seed = 900; }
function v89ArrayName() {
    global $input, $api;
    V89ArrayChild::change(23);
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V89_STATIC_ARRAY_CLOSURE';
}
$class = V89ArrayChild::class;
$method = 'read';
$source = [&$class, &$method];
$slot = $source(...);
$source = null;
$class = V89ArrayBase::class;
$method = 'absent';
$input = ['edge' => &$slot];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v89ArrayName());
echo $result === true ? 'T|' : 'BAD|';
$slot = null;
$copy = constant('V89_STATIC_ARRAY_CLOSURE');
$stored = $copy['edge'];
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge'] === null ? 'null|' : 'BAD|';
echo $api, '|';
echo $source === null && $class === V89ArrayBase::class && $method === 'absent' ? 'retired|' : 'BAD|';
echo $stored(), '|';
$bucket =& $copy['edge'];
$bucket = null;
V89ArrayChild::change(41);
$again = constant('V89_STATIC_ARRAY_CLOSURE');
$shared = $again['edge'];
echo $copy['edge'] === null ? 'local-null|' : 'BAD|';
echo $shared === $stored ? 'same|' : 'BAD|';
echo $shared(), '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($bucket, $copy, $again, $shared, $stored, $slot, $input, $class, $method, $source, $api, $result);
echo 'after|', V89ArrayChild::read(), '|A|';
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
