#!/usr/bin/env python3
"""Captured Stringable names distinguish conversion, lookup and object cleanup."""
from pathlib import Path

import global_constant_sources as family

ORDER = 'owned-stringable-query-ordinary-and-explicit-destruction'
STRICT = 'owned-stringable-query-strict-raw-object-retirement'
family.CASES = {
    ORDER: br'''<?php
class V102Name {
    public function __toString(): string {
        global $call, $name, $weak, $strings, $key;
        ++$strings;
        $saved = $key;
        $call = 'constant';
        $name = null;
        echo 'S|';
        echo $weak->get() instanceof Closure ? 'held|' : 'gone|';
        return $saved;
    }
    public function __destruct() {
        global $weak, $deaths, $key;
        ++$deaths;
        echo 'D|';
        echo $weak->get() instanceof Closure ? 'held|' : 'gone|';
        define($key, 17);
        $key = 'afterD';
    }
}
$strings = 0;
$deaths = 0;
$call = constant(...);
$weak = WeakReference::create($call);
$name = new V102Name;
$weakName = WeakReference::create($name);
$key = 'V102_ORDINARY';
$result = 97;
echo 'B|';
$result = $call($name);
echo $result, '|';
echo $weak->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $weakName->get() === null ? 'nameGone|' : 'nameHeld|';
echo $name === null ? 'null|' : 'BAD|';
echo $key, '|', $strings, '|', $deaths, '|';
$call = defined(...);
$weak = WeakReference::create($call);
$name = new V102Name;
$weakName = WeakReference::create($name);
$key = 'V102_EXPLICIT';
$result = $call->__invoke($name);
echo $result === false ? 'F|' : 'T|';
echo $weak->get() === null ? 'calleeGone|' : 'calleeHeld|';
echo $weakName->get() === null ? 'nameGone|' : 'nameHeld|';
echo $name === null ? 'null|' : 'BAD|';
echo $key, '|', $strings, '|', $deaths, '|';
echo defined('V102_EXPLICIT') ? 'lateT|' : 'lateF|';
echo constant('V102_EXPLICIT'), '|';
unset($call, $weak, $name, $weakName, $key, $result, $strings, $deaths);
echo 'A|';
''',
    STRICT: br'''<?php
declare(strict_types=1);
class V102StrictName {
    public function __toString(): string {
        echo 'BAD_STRING|';
        return 'V102_STRICT';
    }
    public function __destruct() {
        global $weak, $deaths;
        ++$deaths;
        echo 'D|';
        echo $weak->get() instanceof Closure ? 'held|' : 'gone|';
        define('V102_STRICT', 23);
    }
}
function v102StrictArgument() {
    global $call, $name, $weak, $effects;
    ++$effects;
    $saved = $name;
    $call = 'constant';
    $name = null;
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'gone|';
    return $saved;
}
$call = defined(...);
$weak = WeakReference::create($call);
$name = new V102StrictName;
$weakName = WeakReference::create($name);
$effects = 0;
$deaths = 0;
$result = 97;
echo 'B|';
try {
    $result = $call(v102StrictArgument());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|';
    echo $trace[0]['args'][0] === $weakName->get() ? 'rawO|' : 'BAD|';
    echo $weak->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakName->get() instanceof V102StrictName ? 'nameHeld|' : 'nameGone|';
    echo $name === null ? 'null|' : 'BAD|';
    echo $call, '|', $result, '|', $effects, '|', $deaths, '|';
}
echo 'X|';
unset($error, $trace);
echo $weakName->get() === null ? 'nameGone|' : 'nameHeld|';
$reader = constant(...);
echo $reader('V102_STRICT'), '|';
unset($reader, $call, $weak, $name, $weakName, $result, $effects, $deaths);
echo 'A|';
''',
}
family.BASELINE = ('class constant value query', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name in family.CASES:
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
