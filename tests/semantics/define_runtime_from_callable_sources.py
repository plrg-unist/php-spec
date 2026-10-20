#!/usr/bin/env python3
"""Native-first fromCallable VALUES with saved private USER selection."""
from pathlib import Path

import global_constant_sources as family


DIRECT = 'from-private-method-closure-and-normal-duplicate'
family.CASES = {
    DIRECT: br'''<?php
class V91Base {
    private int $value = 7;
    public function change($value) { $this->value = $value; }
    private function read() {
        static $count = 0;
        ++$count;
        echo 'P|', $this->value, '|', static::class, '|';
        return $count;
    }
    public function make() {
        $receiver = $this;
        $method = 'read';
        $callback = [&$receiver, &$method];
        $made = Closure::fromCallable($callback);
        $method = 'gone';
        $receiver = null;
        unset($callback);
        return $made;
    }
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
class V91Child extends V91Base {
    private int $value = 100;
    public function read() { echo 'BAD_CHILD|'; return 900; }
}
function v91Name() {
    global $candidate, $right, $owner, $api;
    $candidate = $right;
    $owner->change(23);
    $owner = null;
    $api = 'constant';
    echo 'N|';
    return 'V91_FROM_CLOSURE';
}
function v91Duplicate($level, $message) {
    global $candidate, $other, $calls;
    ++$calls;
    $other->change(41);
    echo 'H|', $level, '|', $candidate(), '|';
    $candidate = null;
    return true;
}
$owner = new V91Child();
$left = $owner->make();
$other = new V91Child();
$other->change(100);
$right = $other->make();
$candidate = $left;
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api(value: $candidate, case_insensitive: false, constant_name: v91Name());
echo $result === true ? 'T|' : 'BAD|';
$stored = $api('V91_FROM_CLOSURE');
echo $stored === $left && $candidate === $right ? 'same|' : 'BAD|';
echo $owner === null ? 'dropped|' : 'BAD|';
echo $stored(), '|', $right(), '|';
$api = 'define';
set_error_handler('v91Duplicate');
$result = $api('V91_FROM_CLOSURE', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === null ? 'null|' : 'BAD|';
$again = constant('V91_FROM_CLOSURE');
echo $again === $left ? 'same|' : 'BAD|';
echo $again(), '|', $calls, '|';
unset($stored, $again, $candidate, $left, $right, $other, $owner, $api, $calls, $result);
echo 'A|';
''',
    'from-private-static-closure-snapshot-query-cow-and-method-static': br'''<?php
class V91ArrayBase {
    private static int $seed = 7;
    public static function change($value) { self::$seed = $value; }
    private static function read() {
        static $count = 0;
        ++$count;
        echo 'S|', self::$seed, '|', static::class, '|';
        return $count;
    }
    public static function make() {
        $class = static::class;
        $method = 'read';
        $callback = [&$class, &$method];
        $made = Closure::fromCallable($callback);
        $class = 'V91ArrayBase';
        $method = 'gone';
        unset($callback);
        return $made;
    }
    public static function direct() { return self::read(); }
}
class V91ArrayChild extends V91ArrayBase { private static int $seed = 900; }
function v91ArrayName() {
    global $input, $api;
    V91ArrayChild::change(23);
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V91_STATIC_FROM_CLOSURE';
}
$slot = V91ArrayChild::make();
$input = ['edge' => &$slot];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v91ArrayName());
echo $result === true ? 'T|' : 'BAD|';
$slot = null;
$copy = constant('V91_STATIC_FROM_CLOSURE');
$stored = $copy['edge'];
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge'] === null ? 'null|' : 'BAD|';
echo $api, '|';
echo $stored(), '|';
$bucket =& $copy['edge'];
$bucket = null;
V91ArrayChild::change(41);
$again = constant('V91_STATIC_FROM_CLOSURE');
$shared = $again['edge'];
echo $copy['edge'] === null ? 'local-null|' : 'BAD|';
echo $shared === $stored ? 'same|' : 'BAD|';
echo $shared(), '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($bucket, $copy, $again, $shared, $stored, $slot, $input, $api, $result);
echo 'after|', V91ArrayChild::direct(), '|A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|N|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name in family.CASES:
        assert command[-2:] == ['--timeout', '45']
        limit = 120 if Path(stem).parent.name == DIRECT else 90
        command = [*command[:-1], str(limit)]
        timeout = limit + 15
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
