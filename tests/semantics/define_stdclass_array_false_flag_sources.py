#!/usr/bin/env python3
"""Native-first array define snapshots after an explicit false flag."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'fresh-copy-after-flag-reference-rebind': br'''<?php
echo 'B|';
const V68_LEFT = new stdClass();
const V68_RIGHT = new stdClass();
$left = V68_LEFT;
$right = V68_RIGHT;
$left->value = 3;
$right->value = 7;
$cell = $left;
$input = [2 => &$cell, 5 => ['leaf' => &$cell]];
$input[90] = 'discard';
unset($input[90]);
echo define('V68_TREE', $input, ($cell = V68_RIGHT) === null) ? 'T|' : 'BAD|';
echo $input[2] === $right && $input[5]['leaf'] === $right ? 'R|' : 'BAD|';
$copy = constant('V68_TREE');
echo $copy[2] === $right && $copy[5]['leaf'] === $right ? 'R|' : 'BAD|';
$cell = $left;
echo $input[2] === $left && $input[5]['leaf'] === $left ? 'L|' : 'BAD|';
$copy[2]->value = 11;
echo V68_RIGHT->value, '|', V68_LEFT->value, '|';
$copy[] = 99;
echo isset($copy[6]) ? 'six|' : 'BAD|';
$input[] = 'later';
echo isset($input[91]) ? 'history|' : 'BAD|';
$bucket =& $copy[5]['leaf'];
$bucket = 23;
$again = constant('V68_TREE');
echo $again[2] === $right && $again[5]['leaf'] === $right ? 'same|' : 'BAD|';
echo $again[5]['leaf']->value, '|';
unset($bucket, $input, $cell, $copy, $again, $left, $right);
echo 'A|';
''',
    'selected-eval-duplicate-false-capture-and-trace': br'''<?php
const V68_EVAL_OLD = new stdClass();
const V68_EVAL_NEXT = new stdClass();
$old = V68_EVAL_OLD;
$next = V68_EVAL_NEXT;
$old->value = 5;
$next->value = 13;
unset($old, $next);
function v68Report($level, $message) {
    global $cell;
    echo 'H|';
    $cell = V68_EVAL_OLD;
    $probe = new Exception('probe');
    $trace = $probe->getTrace();
    $argument = $trace[1]['args'][1];
    echo $trace[1]['function'] === 'define' ? 'D|' : 'BAD|';
    echo $argument[4] === V68_EVAL_OLD && $argument[7]['leaf'] === V68_EVAL_OLD ? 'old|' : 'BAD|';
    echo $trace[1]['args'][2] === false ? 'false|' : 'BAD|';
    $old = constant('V68_EVAL_TREE');
    $old[4]->value = 19;
    $next = V68_EVAL_NEXT;
    $next->value = 23;
    unset($old, $next, $argument, $trace, $probe);
    return true;
}
echo 'B|';
echo define('V68_EVAL_TREE', [4 => V68_EVAL_OLD, 7 => ['leaf' => V68_EVAL_OLD]]) ? 'T|' : 'BAD|';
$cell = V68_EVAL_OLD;
$input = [4 => &$cell, 7 => ['leaf' => &$cell]];
set_error_handler('v68Report', E_WARNING);
eval('$api = "define"; $result = $api(value: $input, constant_name: "V68_EVAL_TREE", case_insensitive: ($cell = V68_EVAL_NEXT) === null); echo $result ? "BAD|" : "F|"; unset($api, $result);');
restore_error_handler();
echo $input[4] === V68_EVAL_OLD && $input[7]['leaf'] === V68_EVAL_OLD ? 'old|' : 'BAD|';
$old = constant('V68_EVAL_TREE');
echo $old[4] === V68_EVAL_OLD && $old[7]['leaf'] === V68_EVAL_OLD ? 'old|' : 'BAD|';
echo V68_EVAL_OLD->value, '|', V68_EVAL_NEXT->value, '|';
unset($old, $input, $cell);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
