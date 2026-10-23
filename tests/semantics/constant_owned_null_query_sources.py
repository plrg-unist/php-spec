#!/usr/bin/env python3
"""Captured NULL query names retain callees through reception callbacks."""
from pathlib import Path

import global_constant_sources as family

RETURN = 'owned-null-query-returning-handler-and-late-lookup'
STRICT = 'owned-null-query-strict-and-explicit-default-error'
family.CASES = {
    RETURN: br'''<?php
function v101NullName(&$call, &$name, $weak) {
    $saved = $name;
    $call = null;
    $name = 'argument';
    echo 'N|';
    echo $weak->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
function v101PublishEmpty($level, $message, $file, $line) {
    global $call, $name, $weakCurrent, $hits;
    ++$hits;
    echo 'H|', $level, '|', $message, '|', $line, '|';
    echo $weakCurrent->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    if (!defined('')) { define('', 101); }
    $call = 'constant';
    $name = 'handler';
    return true;
}
$call = constant(...);
$weakRead = WeakReference::create($call);
$weakCurrent = $weakRead;
$name = null;
$hits = 0;
set_error_handler('v101PublishEmpty');
echo 'B|';
$result = $call(name: v101NullName($call, $name, $weakRead));
echo $result, '|';
echo $weakRead->get() === null ? 'gone|' : 'BAD_HELD|';
echo $name, '|', $call, '|', $hits, '|';
$call = defined(...);
$weakHas = WeakReference::create($call);
$weakCurrent = $weakHas;
$name = null;
$result = $call(constant_name: v101NullName($call, $name, $weakHas));
echo $result === true ? 'T|' : 'BAD|';
echo $weakHas->get() === null ? 'gone|' : 'BAD_HELD|';
echo $name, '|', $call, '|', $hits, '|', constant(''), '|';
restore_error_handler();
unset($call, $name, $hits, $result, $weakCurrent, $weakRead, $weakHas);
echo 'A|';
''',
    STRICT: br'''<?php
declare(strict_types=1);
function v101StrictName() {
    global $call, $name, $weakCurrent, $calls;
    ++$calls;
    $saved = $name;
    $call = null;
    $name = 'argument';
    echo 'N|';
    echo $weakCurrent->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    return $saved;
}
function v101DefaultNull($level, $message, $file, $line) {
    global $call, $name, $weakCurrent, $hits;
    ++$hits;
    echo 'H|', $level, '|', $message, '|', $line, '|';
    echo $weakCurrent->get() instanceof Closure ? 'held|' : 'BAD_GONE|';
    $call = 'defined';
    $name = 'handler';
    return false;
}
$call = constant(...);
$weakStrict = WeakReference::create($call);
$weakCurrent = $weakStrict;
$name = null;
$calls = 0;
$hits = 0;
$result = 97;
set_error_handler('v101DefaultNull');
echo 'B|';
try {
    $result = $call(name: v101StrictName());
    echo 'BAD_RETURN|';
} catch (TypeError $typeError) {
    $typeTrace = $typeError->getTrace();
    echo 'T|', $typeError->getMessage(), '|', $typeError->getLine(), '|';
    echo $typeTrace[0]['function'], '|';
    echo $typeTrace[0]['args'][0] === null ? 'rawN|' : 'BAD|';
    echo $call === null ? 'null|' : 'BAD|';
    echo $name, '|', $result, '|', $calls, '|', $hits, '|';
    echo $weakStrict->get() === null ? 'gone|' : 'BAD_HELD|';
}
$call = constant(...);
$weakExplicit = WeakReference::create($call);
$weakCurrent = $weakExplicit;
$name = null;
try {
    $result = $call->__invoke(name: v101StrictName());
    echo 'BAD_RETURN|';
} catch (Error $error) {
    $trace = $error->getTrace();
    $rawApi = $trace[0]['args'];
    $rawInvoke = $trace[1]['args'];
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|', $trace[1]['function'], '|';
    echo $rawApi[0] === '' ? 'apiS|' : 'BAD|';
    echo $rawInvoke[0] === null ? 'invokeN|' : 'BAD|';
    echo $rawApi !== $rawInvoke ? 'distinct|' : 'BAD|';
    echo $typeTrace[0]['args'][0] === null ? 'keptN|' : 'BAD|';
    echo $name, '|', $call, '|', $result, '|', $calls, '|', $hits, '|';
    echo $weakExplicit->get() === null ? 'gone|' : 'BAD_HELD|';
}
restore_error_handler();
unset($call, $name, $calls, $hits, $result, $weakCurrent, $weakStrict, $weakExplicit);
unset($typeError, $typeTrace, $error, $trace, $rawApi, $rawInvoke);
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
