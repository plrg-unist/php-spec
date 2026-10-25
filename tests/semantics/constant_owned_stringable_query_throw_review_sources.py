#!/usr/bin/env python3
"""A pending destructor Exception meets ordinary missing-constant lookup."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-stringable-query-destructor-missing-error-previous'
family.CASES = {
    CASE: br'''<?php
class V103ReviewName {
    public function __toString(): string {
        global $call, $name, $weakCall, $casts;
        ++$casts;
        $call = null;
        $name = null;
        echo 'S|';
        echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
        return 'V103_REVIEW_MISSING';
    }
    public function __destruct() {
        global $weakCall, $drops, $made;
        ++$drops;
        echo 'D|';
        echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
        define('V103_REVIEW_RECOVERY', 23);
        $made = new Exception('V103_REVIEW_STOP');
        throw $made;
    }
}
$casts = 0;
$drops = 0;
$made = null;
$call = constant(...);
$weakCall = WeakReference::create($call);
$name = new V103ReviewName;
$weakName = WeakReference::create($name);
$result = 97;
$rawPrior = null;
echo 'B|';
try {
    $result = $call($name);
    echo 'RETURN|';
} catch (Throwable $error) {
    $trace = $error->getTrace();
    $previous = $error->getPrevious();
    echo $error instanceof Error ? 'Error|' : 'Exception|';
    echo $error->getMessage(), '|', $error->getLine(), '|';
    if (isset($trace[0])) {
        echo $trace[0]['function'], '|';
        echo isset($trace[0]['file']) ? ($trace[0]['file'] === __FILE__ ? 'file|' : 'otherFile|') : 'noFile|';
        echo isset($trace[0]['line']) ? $trace[0]['line'] : 'internal';
        echo '|';
        echo isset($trace[0]['args'][0]) && $trace[0]['args'][0] === 'V103_REVIEW_MISSING' ? 'apiS|' : 'noApiS|';
    } else { echo 'noPrimaryFrame|'; }
    if (isset($trace[1])) {
        echo $trace[1]['function'], '|';
        echo isset($trace[1]['file']) ? ($trace[1]['file'] === __FILE__ ? 'file|' : 'otherFile|') : 'noFile|';
        echo isset($trace[1]['line']) ? $trace[1]['line'] : 'internal';
        echo '|';
    } else { echo 'noPrimarySecond|'; }
    if ($previous instanceof Exception) {
        echo $previous === $made ? 'samePrevious|' : 'differentPrevious|';
        echo $previous->getMessage(), '|', $previous->getLine(), '|';
        echo $previous->getPrevious() === null ? 'none|' : 'chained|';
        $previousTrace = $previous->getTrace();
        if (isset($previousTrace[0])) {
            echo $previousTrace[0]['function'], '|';
            echo isset($previousTrace[0]['file']) ? ($previousTrace[0]['file'] === __FILE__ ? 'file|' : 'otherFile|') : 'noFile|';
            echo isset($previousTrace[0]['line']) ? $previousTrace[0]['line'] : 'internal';
            echo '|';
        } else { echo 'noDestructorFrame|'; }
        if (isset($previousTrace[1]['args'][0])) {
            echo $previousTrace[1]['function'], '|';
            echo isset($previousTrace[1]['file']) ? ($previousTrace[1]['file'] === __FILE__ ? 'file|' : 'otherFile|') : 'noFile|';
            echo isset($previousTrace[1]['line']) ? $previousTrace[1]['line'] : 'internal';
            echo '|';
            $rawPrior = $previousTrace[1]['args'];
            echo $rawPrior[0] instanceof V103ReviewName ? 'rawO|' : 'other|';
            echo $rawPrior[0] === $weakName->get() ? 'sameObject|' : 'differentObject|';
        } else { echo 'noRawFrame|'; }
        echo isset($previousTrace[2]) ? 'more|' : 'end|';
    } else { echo 'noPrevious|'; }
    echo $call === null && $name === null ? 'currentNull|' : 'changed|';
    echo $result, '|', $casts, '|', $drops, '|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $weakName->get() instanceof V103ReviewName ? 'traceHeld|' : 'nameGone|';
    unset($error, $trace, $previous, $previousTrace, $made);
    echo $weakName->get() instanceof V103ReviewName ? 'rawHeld|' : 'nameGone|';
    echo $drops, '|';
    unset($rawPrior);
    echo $weakName->get() === null ? 'gone|' : 'held|';
    echo $drops, '|';
}
$reader = constant(...);
echo $reader('V103_REVIEW_RECOVERY'), '|';
unset($reader, $call, $name, $weakCall, $weakName, $casts, $drops, $result, $rawPrior, $made);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    stem = Path(stem)
    if stem.parent.name == CASE and stem.name in ('model', 'model-' + CASE):
        assert command[-2:] == ['--timeout', '45']
        limit = 180 if stem.name == 'model' else 90
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
