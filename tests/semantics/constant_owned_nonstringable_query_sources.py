#!/usr/bin/env python3
"""Captured nonStringable query names retain raw TypeError arguments."""
from pathlib import Path

import global_constant_sources as family

STRICT = 'owned-nonstringable-query-strict-stdclass-trace'
EXPLICIT = 'owned-nonstringable-query-explicit-raw-wrapper-retirement'
family.CASES = {
    STRICT: br'''<?php
declare(strict_types=1);
function v104StrictArgument() {
    global $call, $name, $weakCall, $effects;
    ++$effects;
    $saved = $name;
    $call = 'defined';
    $name = null;
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
    return $saved;
}
define('V104_STRICT_RECOVERY', 17);
$call = constant(...);
$weakCall = WeakReference::create($call);
$name = new stdClass;
$weakName = WeakReference::create($name);
$effects = 0;
$result = 97;
echo 'B|';
try {
    $result = $call(v104StrictArgument());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $raw = $trace[0]['args'];
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|';
    echo $raw[0] instanceof stdClass && $raw[0] === $weakName->get() ? 'rawO|' : 'BAD|';
    echo $trace[0]['file'] === __FILE__ ? 'file|' : 'BAD|';
    echo $trace[0]['line'], '|';
    echo isset($trace[1]) ? 'more|' : 'end|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakName->get() instanceof stdClass ? 'nameHeld|' : 'nameGone|';
    echo $name === null ? 'null|' : 'BAD|';
    echo $call, '|', $result, '|', $effects, '|';
}
unset($error, $trace);
echo $weakName->get() instanceof stdClass ? 'rawHeld|' : 'BAD|';
unset($raw);
echo $weakName->get() === null ? 'released|' : 'BAD|';
$reader = constant(...);
echo $reader('V104_STRICT_RECOVERY'), '|';
unset($reader, $call, $weakCall, $name, $weakName, $result, $effects);
echo 'A|';
''',
    EXPLICIT: br'''<?php
declare(strict_types=1);
class V104ExplicitName {
    public function __destruct() {
        global $weakCall, $drops;
        ++$drops;
        echo 'D|';
        echo $weakCall->get() === null ? 'gone|' : 'held|';
        define('V104_EXPLICIT_RECOVERY', 23);
    }
}
function v104ExplicitArgument() {
    global $call, $name, $weakCall, $effects;
    ++$effects;
    $saved = $name;
    $call = 'constant';
    $name = null;
    echo 'N|';
    echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
    return $saved;
}
$call = defined(...);
$weakCall = WeakReference::create($call);
$name = new V104ExplicitName;
$weakName = WeakReference::create($name);
$effects = 0;
$drops = 0;
$result = 97;
echo 'B|';
try {
    $result = $call->__invoke(v104ExplicitArgument());
    echo 'BAD_RETURN|';
} catch (TypeError $error) {
    $trace = $error->getTrace();
    $rawApi = $trace[0]['args'];
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'BAD|';
    echo $trace[0]['function'], '|';
    echo $rawApi[0] instanceof V104ExplicitName && $rawApi[0] === $weakName->get() ? 'apiO|' : 'BAD|';
    echo $trace[0]['file'] === __FILE__ ? 'apiFile|' : 'BAD|';
    echo $trace[0]['line'], '|';
    if (isset($trace[1]['args'][0])) {
        $rawInvoke = $trace[1]['args'];
        echo $trace[1]['function'], '|', $trace[1]['class'], '|', $trace[1]['type'], '|';
        echo $rawInvoke[0] === $weakName->get() ? 'invokeO|' : 'BAD|';
        echo $trace[1]['file'] === __FILE__ ? 'invokeFile|' : 'BAD|';
        echo $trace[1]['line'], '|';
    } else { echo 'noWrapper|'; }
    echo isset($trace[2]) ? 'more|' : 'end|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakName->get() instanceof V104ExplicitName ? 'nameHeld|' : 'nameGone|';
    echo $name === null ? 'null|' : 'BAD|';
    echo $call, '|', $result, '|', $effects, '|', $drops, '|';
}
unset($error, $trace, $rawApi);
echo $weakName->get() instanceof V104ExplicitName ? 'wrapperHeld|' : 'BAD|';
echo $drops, '|';
unset($rawInvoke);
echo $weakName->get() === null ? 'released|' : 'BAD|';
echo $drops, '|';
$reader = constant(...);
echo $reader('V104_EXPLICIT_RECOVERY'), '|';
unset($reader, $call, $weakCall, $name, $weakName, $result, $effects, $drops);
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
