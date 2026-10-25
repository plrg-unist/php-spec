#!/usr/bin/env python3
"""Normal Stringable names followed by throwing argument destructors."""
from pathlib import Path

import global_constant_sources as family

RETURN = 'owned-stringable-query-returned-name-destructor-exception'
EXPLICIT = 'owned-stringable-query-explicit-cleanup-destructor-exception'
family.CASES = {
    RETURN: br'''<?php
class V103ReturnName {
    public function __toString(): string {
        global $call, $name, $weakCall, $casts;
        ++$casts;
        $call = 'defined';
        $name = null;
        echo 'S|';
        echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
        return 'V103_RETURN';
    }
    public function __destruct() {
        global $weakCall, $drops, $provided;
        ++$drops;
        echo 'D|';
        echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
        define('V103_RETURN', 17);
        $provided = new Exception('V103_RETURN_D');
        throw $provided;
    }
}
$call = constant(...);
$weakCall = WeakReference::create($call);
$name = new V103ReturnName;
$weakName = WeakReference::create($name);
$provided = null;
$casts = 0;
$drops = 0;
$result = 97;
echo 'B|';
try {
    $result = $call($name);
    echo 'BAD_RETURN|';
} catch (Throwable $error) {
    echo $error instanceof Error ? 'Error|' : 'Exception|';
    echo $error === $provided ? 'same|' : 'other|';
    echo $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'previous|';
    $trace = $error->getTrace();
    echo isset($trace[0]) ? $trace[0]['function'] : 'noTrace';
    echo '|';
    echo isset($trace[1]) ? $trace[1]['function'] : 'noCaller';
    echo '|';
    if (isset($trace[1]['args'][0])) {
        echo $trace[1]['args'][0] instanceof V103ReturnName
            && $trace[1]['args'][0] === $weakName->get() ? 'rawO|' : 'otherArg|';
    } else { echo 'noArg|'; }
    echo isset($trace[2]) ? 'more|' : 'end|';
    echo isset($trace[0]['file']) && $trace[0]['file'] === __FILE__ ? 'file0|' : 'internal0|';
    echo isset($trace[0]['line']) ? $trace[0]['line'] : -1;
    echo '|';
    echo isset($trace[1]['file']) && $trace[1]['file'] === __FILE__ ? 'file1|' : 'internal1|';
    echo isset($trace[1]['line']) ? $trace[1]['line'] : -1;
    echo '|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakName->get() instanceof V103ReturnName ? 'nameHeld|' : 'nameGone|';
    echo $name === null ? 'null|' : 'BAD|';
    echo $call, '|', $result, '|', $casts, '|', $drops, '|';
}
unset($provided, $error, $trace);
echo $weakName->get() === null ? 'released|' : 'held|';
echo $drops, '|';
$reader = constant(...);
echo $reader('V103_RETURN'), '|';
unset($reader, $call, $weakCall, $name, $weakName, $result, $casts, $drops);
echo 'A|';
''',
    EXPLICIT: br'''<?php
declare(strict_types=1);
class V103ExplicitName {
    public function __toString(): string {
        global $call, $name, $weakCall, $casts;
        ++$casts;
        $call = 'constant';
        $name = null;
        echo 'S|';
        echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
        return 'V103_EXPLICIT';
    }
    public function __destruct() {
        global $weakCall, $drops, $provided;
        ++$drops;
        echo 'D|';
        echo $weakCall->get() instanceof Closure ? 'held|' : 'gone|';
        define('V103_EXPLICIT', 23);
        $provided = new Exception('V103_EXPLICIT_D');
        throw $provided;
    }
}
$call = defined(...);
$weakCall = WeakReference::create($call);
$name = new V103ExplicitName;
$weakName = WeakReference::create($name);
$provided = null;
$casts = 0;
$drops = 0;
$result = 97;
echo 'B|';
try {
    $result = $call->__invoke($name);
    echo 'BAD_RETURN|';
} catch (Throwable $error) {
    echo $error instanceof Error ? 'Error|' : 'Exception|';
    echo $error === $provided ? 'same|' : 'other|';
    echo $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'previous|';
    $trace = $error->getTrace();
    echo isset($trace[0]) ? $trace[0]['function'] : 'noTrace';
    echo '|';
    echo isset($trace[1]) ? $trace[1]['function'] : 'noCaller';
    echo '|';
    if (isset($trace[1]['args'][0])) {
        echo $trace[1]['args'][0] instanceof V103ExplicitName
            && $trace[1]['args'][0] === $weakName->get() ? 'rawO|' : 'otherArg|';
    } else { echo 'noArg|'; }
    echo isset($trace[2]) ? 'more|' : 'end|';
    echo isset($trace[0]['file']) && $trace[0]['file'] === __FILE__ ? 'file0|' : 'internal0|';
    echo isset($trace[0]['line']) ? $trace[0]['line'] : -1;
    echo '|';
    echo isset($trace[1]['file']) && $trace[1]['file'] === __FILE__ ? 'file1|' : 'internal1|';
    echo isset($trace[1]['line']) ? $trace[1]['line'] : -1;
    echo '|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakName->get() instanceof V103ExplicitName ? 'nameHeld|' : 'nameGone|';
    echo $name === null ? 'null|' : 'BAD|';
    echo $call, '|', $result, '|', $casts, '|', $drops, '|';
}
unset($provided, $error, $trace);
echo $weakName->get() === null ? 'released|' : 'held|';
echo $drops, '|';
$reader = constant(...);
echo $reader('V103_EXPLICIT'), '|';
unset($reader, $call, $weakCall, $name, $weakName, $result, $casts, $drops);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    name = Path(stem).name
    if name == 'model' or name.startswith('model-'):
        assert command[-2:] == ['--timeout', '45']
        limit = 180 if name == 'model' else 90
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
