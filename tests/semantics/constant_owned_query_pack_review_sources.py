#!/usr/bin/env python3
"""Named ARRAY unpack copies an aliased query string before retiring its pack."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-query-pack-explicit-named-reference-missing'
family.CASES = {
    CASE: br'''<?php
declare(strict_types=1);
function v106ReviewPack() {
    global $call, $pack, $weakCall, $effects;
    ++$effects;
    $saved = $pack;
    $pack = null;
    $call = null;
    echo 'P|';
    echo $weakCall->get() instanceof Closure ? 'calleeHeld|' : 'calleeGone|';
    return $saved;
}
define('V106_REVIEW_RECOVERY', 23);
$part = 'V106_REVIEW';
$target = $part . '_MISSING';
$pack = ['name' => &$target];
$call = constant(...);
$weakCall = WeakReference::create($call);
$effects = 0;
$result = 97;
$rawApi = null;
$rawInvoke = null;
echo 'B|';
try {
    $result = $call->__invoke(...v106ReviewPack());
    echo 'RETURN|';
} catch (Error $error) {
    $trace = $error->getTrace();
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    echo $error->getPrevious() === null ? 'none|' : 'chained|';
    if (isset($trace[0]['args'])) {
        $rawApi = $trace[0]['args'];
        echo $trace[0]['function'], '|';
        echo isset($trace[0]['file']) && $trace[0]['file'] === __FILE__ ? 'apiFile|' : 'noApiFile|';
        echo isset($trace[0]['line']) ? $trace[0]['line'] : 'internal';
        echo '|';
        if (isset($rawApi[0])) { echo $rawApi[0] === 'V106_REVIEW_MISSING' ? 'api0|' : 'apiOther|'; }
        elseif (isset($rawApi['name'])) { echo $rawApi['name'] === 'V106_REVIEW_MISSING' ? 'apiName|' : 'apiOther|'; }
        else { echo 'noApiValue|'; }
    } else { echo 'noApi|'; }
    if (isset($trace[1]['args'])) {
        $rawInvoke = $trace[1]['args'];
        echo $trace[1]['function'], '|';
        echo isset($trace[1]['class']) ? $trace[1]['class'] : 'noClass';
        echo '|';
        echo isset($trace[1]['type']) ? $trace[1]['type'] : 'noType';
        echo '|';
        echo isset($trace[1]['file']) && $trace[1]['file'] === __FILE__ ? 'invokeFile|' : 'noInvokeFile|';
        echo isset($trace[1]['line']) ? $trace[1]['line'] : 'internal';
        echo '|';
        if (isset($rawInvoke[0])) { echo $rawInvoke[0] === 'V106_REVIEW_MISSING' ? 'invoke0|' : 'invokeOther|'; }
        elseif (isset($rawInvoke['name'])) { echo $rawInvoke['name'] === 'V106_REVIEW_MISSING' ? 'invokeName|' : 'invokeOther|'; }
        else { echo 'noInvokeValue|'; }
    } else { echo 'noWrapper|'; }
    echo isset($trace[2]) ? 'more|' : 'end|';
    echo $call === null && $pack === null ? 'currentNull|' : 'changed|';
    echo $weakCall->get() === null ? 'calleeGone|' : 'calleeHeld|';
    echo $result, '|', $effects, '|';
    $target = 'changed-after-pack';
    echo (isset($rawApi[0]) && $rawApi[0] === 'V106_REVIEW_MISSING') || (isset($rawApi['name']) && $rawApi['name'] === 'V106_REVIEW_MISSING') ? 'apiKept|' : 'apiChanged|';
    echo (isset($rawInvoke[0]) && $rawInvoke[0] === 'V106_REVIEW_MISSING') || (isset($rawInvoke['name']) && $rawInvoke['name'] === 'V106_REVIEW_MISSING') ? 'invokeKept|' : 'invokeChanged|';
    echo $target, '|';
    unset($error, $trace, $target);
    echo (isset($rawApi[0]) && $rawApi[0] === 'V106_REVIEW_MISSING') || (isset($rawApi['name']) && $rawApi['name'] === 'V106_REVIEW_MISSING') ? 'apiHeld|' : 'apiGone|';
    unset($rawApi);
    echo (isset($rawInvoke[0]) && $rawInvoke[0] === 'V106_REVIEW_MISSING') || (isset($rawInvoke['name']) && $rawInvoke['name'] === 'V106_REVIEW_MISSING') ? 'invokeHeld|' : 'invokeGone|';
    unset($rawInvoke);
}
$reader = constant(...);
echo $reader('V106_REVIEW_RECOVERY'), '|';
unset($reader, $call, $pack, $weakCall, $part, $effects, $result, $rawApi, $rawInvoke, $target);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).parent.name == CASE and Path(stem).name in ('model', 'model-' + CASE):
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '90' if Path(stem).name != 'model' else '180']
        timeout = 105 if Path(stem).name != 'model' else 195
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
