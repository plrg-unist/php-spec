#!/usr/bin/env python3
"""Native-first stored fromCallable factories retain invocation USER permission."""
from pathlib import Path

import global_constant_sources as family


DIRECT = 'stored-factory-creation-is-not-invocation-permission'
family.CASES = {
    DIRECT: br'''<?php
class V92Base {
    private static int $seed = 7;
    public static function change($value) { self::$seed = $value; }
    public static function make() { return Closure::fromCallable(...); }
    private static function read() {
        static $count = 0;
        ++$count;
        echo 'P|', self::$seed, '|', static::class, '|';
        return $count;
    }
    public static function select($factory) {
        return $factory(callback: [static::class, 'read']);
    }
}
class V92Child extends V92Base { private static int $seed = 900; }
function v92Name() {
    global $candidate, $right, $api;
    $candidate = $right;
    V92Child::change(23);
    $api = 'constant';
    echo 'N|';
    return 'V92_FACTORY';
}
function v92Duplicate($level, $message) {
    global $candidate, $made, $calls;
    ++$calls;
    V92Child::change(41);
    $made = V92Child::select($candidate);
    $candidate = null;
    echo 'H|', $level, '|', $made(), '|';
    return true;
}
$left = V92Child::make();
$right = Closure::fromCallable(...);
$candidate = $left;
$api = 'define';
$calls = 0;
echo 'B|';
$result = $api(value: $candidate, case_insensitive: false, constant_name: v92Name());
echo $result === true ? 'T|' : 'BAD|';
$stored = $api('V92_FACTORY');
echo $stored === $left && $candidate === $right ? 'same|' : 'BAD|';
$bad = 97;
try {
    $bad = $stored(callback: [V92Base::class, 'read']);
    echo 'BAD_PERMISSION|';
} catch (TypeError $error) {
    echo get_class($error), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $bad === 97 ? 'kept|' : 'BAD|';
}
unset($error, $bad);
$read = V92Child::select($stored);
echo $read(), '|';
unset($read, $right);
$api = 'define';
set_error_handler('v92Duplicate');
$result = $api('V92_FACTORY', $candidate, false);
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $candidate === null ? 'null|' : 'BAD|';
$again = constant('V92_FACTORY');
echo $again === $left ? 'same|' : 'BAD|';
$later = V92Child::select($again);
echo $made(), '|', $later(), '|', $calls, '|';
unset($stored, $again, $later, $made, $candidate, $left, $api, $calls, $result);
echo 'A|';
''',
    'stored-factory-array-query-cow-and-explicit-user-invocation': br'''<?php
class V92ArrayBase {
    private static int $seed = 7;
    public static function change($value) { self::$seed = $value; }
    private static function read() {
        static $count = 0;
        ++$count;
        echo 'S|', self::$seed, '|', static::class, '|';
        return $count;
    }
    public static function select($factory) {
        return $factory->__invoke(callback: [static::class, 'read']);
    }
    public static function direct() { return self::read(); }
}
class V92ArrayChild extends V92ArrayBase { private static int $seed = 900; }
function v92ArrayName() {
    global $input, $api;
    V92ArrayChild::change(23);
    $input[90] = 31;
    $api = 'defined';
    echo 'N|';
    return 'V92_FACTORY_ARRAY';
}
$slot = Closure::fromCallable(...);
$input = ['edge' => &$slot];
$input[90] = 0;
unset($input[90]);
$api = 'define';
echo 'B|';
$result = $api(value: $input, constant_name: v92ArrayName());
echo $result === true ? 'T|' : 'BAD|';
$slot = null;
$copy = constant('V92_FACTORY_ARRAY');
$stored = $copy['edge'];
echo !isset($copy[90]) && $input[90] === 31 ? 'split|' : 'BAD|';
echo $input['edge'] === null ? 'null|' : 'BAD|';
echo $api, '|';
$read = V92ArrayChild::select($stored);
echo $read(), '|';
unset($read);
$bucket =& $copy['edge'];
$bucket = null;
V92ArrayChild::change(41);
$again = constant('V92_FACTORY_ARRAY');
$shared = $again['edge'];
echo $copy['edge'] === null ? 'local-null|' : 'BAD|';
echo $shared === $stored ? 'same|' : 'BAD|';
$read = V92ArrayChild::select($shared);
echo $read(), '|';
$copy[] = 53;
echo isset($copy[0]) && !isset($again[0]) ? 'history|' : 'BAD|';
unset($bucket, $copy, $again, $shared, $stored, $slot, $input, $read, $api, $result);
echo 'after|', V92ArrayChild::direct(), '|A|';
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
