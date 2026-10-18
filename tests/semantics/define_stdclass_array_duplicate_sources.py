#!/usr/bin/env python3
"""Native-first duplicate array snapshots and original API argument ownership."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'reference-candidate-and-normal-handler-trace': br'''<?php
const V67_OLD = new stdClass();
const V67_LEFT = new stdClass();
const V67_RIGHT = new stdClass();
$old = V67_OLD;
$left = V67_LEFT;
$right = V67_RIGHT;
$old->value = 3;
$left->value = 7;
$right->value = 11;
unset($old, $left, $right);
function v67Normal($level, $message) {
    global $cell;
    echo 'H|', $level, '|';
    $old = constant('V67_TREE');
    echo $old[2] === V67_OLD ? 'old|' : 'BAD|';
    $cell = V67_RIGHT;
    $probe = new Exception('probe');
    $trace = $probe->getTrace();
    $argument = $trace[1]['args'][1];
    echo $trace[1]['function'] === 'define' ? 'D|' : 'BAD|';
    echo $argument[2] === V67_RIGHT && $argument[5]['leaf'] === V67_RIGHT ? 'right|' : 'BAD|';
    $old[2]->value = 17;
    $left = V67_LEFT;
    $left->value = 13;
    unset($old, $left, $argument, $trace, $probe);
    return true;
}
echo 'B|';
echo define('V67_TREE', [2 => V67_OLD, 5 => ['leaf' => V67_OLD]]) ? 'T|' : 'BAD|';
$cell = V67_LEFT;
$input = [2 => &$cell, 5 => ['leaf' => &$cell]];
$input[90] = 'discard';
unset($input[90]);
set_error_handler('v67Normal', E_WARNING);
$result = define('V67_TREE', $input);
restore_error_handler();
echo $result ? 'BAD|' : 'F|';
echo $input[2] === V67_RIGHT && $input[5]['leaf'] === V67_RIGHT ? 'right|' : 'BAD|';
$old = constant('V67_TREE');
echo $old[2] === V67_OLD && $old[5]['leaf'] === V67_OLD ? 'old|' : 'BAD|';
echo V67_OLD->value, '|', V67_LEFT->value, '|', V67_RIGHT->value, '|';
unset($old, $result, $input, $cell);
echo 'A|';
''',
    'selected-eval-default-warning-and-old-array': br'''<?php
const V67_EVAL_OLD = new stdClass();
const V67_EVAL_NEXT = new stdClass();
$old = V67_EVAL_OLD;
$next = V67_EVAL_NEXT;
$old->value = 11;
$next->value = 29;
unset($old, $next);
function v67Report($level, $message) {
    echo 'H|';
    $old = constant('V67_EVAL_TREE');
    $old[4]->value = 19;
    return false;
}
echo 'B|';
echo define('V67_EVAL_TREE', [4 => V67_EVAL_OLD, 7 => ['leaf' => V67_EVAL_OLD]]) ? 'T|' : 'BAD|';
set_error_handler('v67Report', E_WARNING);
eval('$api = "define"; $result = $api("V67_EVAL_TREE", [4 => V67_EVAL_NEXT, 7 => ["leaf" => V67_EVAL_NEXT]]); echo $result ? "BAD|" : "F|"; unset($api, $result);');
restore_error_handler();
$old = constant('V67_EVAL_TREE');
echo $old[4] === V67_EVAL_OLD && $old[7]['leaf'] === V67_EVAL_OLD ? 'old|' : 'BAD|';
echo V67_EVAL_OLD->value, '|', V67_EVAL_NEXT->value, '|';
unset($old);
echo 'A|';
''',
}
family.BASELINE = ('dynamic constant call domain', b'B|T|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
