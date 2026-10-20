#!/usr/bin/env python3
"""A changed raw reference leaf retires before the retained DEFINE callee."""
from pathlib import Path

import global_constant_sources as family

CASE = 'owned-define-raw-reference-leaf-before-callee-retirement'
family.CASES = {
    CASE: br'''<?php
const V94_ORDER_OLD = 17;
class V94OrderLeaf {
    public int $value = 41;
    function __destruct() {
        global $weak;
        echo 'D|', $this->value, '|';
        echo $weak->get() instanceof Closure ? 'held|' : 'gone|';
    }
}
class V94OrderBox {
    public $leaf;
}
function v94OrderDrop() {
    global $call, $source;
    $call = null;
    $source = null;
    echo 'N|';
    return false;
}
function v94OrderReport($level, $message) {
    global $box;
    $box->leaf = new V94OrderLeaf;
    $box->leaf->value = 53;
    $box = null;
    echo 'H|', $level, '|';
    return true;
}
$box = new V94OrderBox;
$box->leaf = new V94OrderLeaf;
$source = ['leaf' => &$box->leaf];
$call = define(...);
$weak = WeakReference::create($call);
set_error_handler('v94OrderReport');
echo 'B|';
$result = $call('V94_ORDER_OLD', $source, v94OrderDrop());
restore_error_handler();
echo $result === false ? 'F|' : 'BAD|';
echo $weak->get() === null ? 'gone|' : 'BAD|';
echo constant('V94_ORDER_OLD'), '|A|';
unset($box, $call, $source, $weak, $result);
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint
family_recorded = family.recorder.recorded


def recorded(command, stem, timeout):
    if Path(stem).name == 'model' and Path(stem).parent.name == CASE:
        assert command[-2:] == ['--timeout', '45']
        command = [*command[:-1], '120']
        timeout = 135
    return family_recorded(command, stem, timeout)


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint
family.recorder.recorded = recorded

if __name__ == '__main__':
    family.main()
