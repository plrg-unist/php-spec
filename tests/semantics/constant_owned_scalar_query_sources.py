#!/usr/bin/env python3
"""Captured scalar query names convert after argument effects, without CV writes."""
from pathlib import Path

import global_constant_sources as family

LATE = 'owned-scalar-query-late-int-and-empty-bool'
MISSING = 'owned-scalar-query-ordinary-false-error'
family.CASES = {
    LATE: br'''<?php
function v100IntName(&$call, &$other, &$name, $weak) {
    $saved = $name;
    $call = $other;
    $other = null;
    $name = 404;
    define('37', 137);
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
function v100EmptyName(&$call, &$name, $weak) {
    $saved = $name;
    $call = 'constant';
    $name = true;
    define('', 101);
    echo 'F|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
$call = constant(...);
$other = defined(...);
$weakRead = WeakReference::create($call);
$weakHas = WeakReference::create($other);
$name = 37;
$result = 97;
echo 'B|';
$result = $call(name: v100IntName($call, $other, $name, $weakRead));
echo $result, '|';
echo $weakRead->get() === null ? 'gone|' : 'BAD_HELD|';
echo $other === null ? 'null|' : 'BAD|';
echo $name, '|';
$name = false;
$result = $call(constant_name: v100EmptyName($call, $name, $weakHas));
echo $result === true ? 'T|' : 'BAD|';
echo $weakHas->get() === null ? 'gone|' : 'BAD_HELD|';
echo $name === true ? 'T|' : 'BAD|';
echo constant(''), '|';
unset($call, $other, $name, $result, $weakRead, $weakHas);
echo 'A|';
''',
    MISSING: br'''<?php
function v100MissingName() {
    global $call, $name, $weak, $calls;
    $saved = $name;
    $call = null;
    $name = true;
    ++$calls;
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
$call = constant(...);
$name = false;
$weak = WeakReference::create($call);
$calls = 0;
$result = 97;
echo 'B|';
try {
    $result = $call(name: v100MissingName());
    echo 'BAD_RETURN|';
} catch (Error $error) {
    $trace = $error->getTrace();
    $raw = $trace[0]['args'];
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|';
    echo $raw[0] === '' ? 'S|' : 'BAD|';
    echo $result, '|', $calls, '|';
    echo $weak->get() === null ? 'gone|' : 'BAD_HELD|';
    echo $name === true ? 'T|' : 'BAD|';
    echo $call === null ? 'null|' : 'BAD|';
    unset($raw, $trace, $error);
}
unset($call, $name, $weak, $calls, $result);
echo 'A|';
''',
}
family.BASELINE = ('class constant value query', b'B|N|held|')
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
