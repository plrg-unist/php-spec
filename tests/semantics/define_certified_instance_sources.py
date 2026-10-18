#!/usr/bin/env python3
"""Native-first define of completed user-instance donors and duplicate captures."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'completed-instance-publication-and-property-alias': br'''<?php
class V73Built {
    public int $value = 0;
    public function __construct() { echo 'C|'; $this->value = 5; }
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
echo 'B|';
const V73_DONOR = new V73Built();
$donor = V73_DONOR;
echo define(value: $donor, constant_name: 'V73_ROW', case_insensitive: false) ? 'T|' : 'BAD|';
$first = constant('V73_ROW');
echo $first === $donor && $first === V73_DONOR ? 'same|' : 'BAD|';
$slot =& $first->value;
$slot = 11;
unset($slot, $donor, $first);
$again = constant(name: 'V73_ROW');
echo $again->value, '|', V73_DONOR->value, '|';
unset($again);
echo 'A|';
''',
    'selected-eval-instance-duplicate-and-normal-handler': br'''<?php
class V73EvalBox {
    public int $value = 0;
    public function __construct() { $this->value = 3; }
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
echo 'B|';
const V73_EVAL_OLD = new V73EvalBox();
const V73_EVAL_NEXT = new V73EvalBox();
$old = V73_EVAL_OLD;
$next = V73_EVAL_NEXT;
$old->value = 7;
$next->value = 23;
unset($old, $next);
$api = 'define';
echo $api(value: V73_EVAL_OLD, constant_name: 'V73_EVAL_ROW') ? 'T|' : 'BAD|';
function v73Report($level, $message) {
    $old = constant('V73_EVAL_ROW');
    $next = V73_EVAL_NEXT;
    $old->value = 13;
    $next->value = 29;
    define('V73_SIDE', 19);
    echo 'H|';
    return true;
}
set_error_handler('v73Report', E_WARNING);
eval('$api = "define"; $candidate = V73_EVAL_NEXT; $result = $api(value: $candidate, constant_name: "V73_EVAL_ROW", case_insensitive: false); echo $result ? "BAD|" : "F|"; unset($candidate, $result);');
restore_error_handler();
$held = constant('V73_EVAL_ROW');
echo $held === V73_EVAL_OLD ? 'old|' : 'BAD|';
echo $held->value, '|', V73_EVAL_NEXT->value, '|', constant('V73_SIDE'), '|';
unset($held, $api);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|C|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
