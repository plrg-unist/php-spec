#!/usr/bin/env python3
"""Native-first nested empty snapshot provenance, copies and query COW."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'mixed-nested-empty-snapshot-and-query-cow': br'''<?php
$empty = [90 => 'gone'];
unset($empty[90]);
$cell = $empty;
unset($empty);
$input = ['pooled' => [], 'head' => &$cell, 'nested' => ['again' => &$cell]];
echo 'B|';
echo define('V70_TREE', $input, false) ? 'T|' : 'BAD|';
$cell[] = 'source';
$copy = constant('V70_TREE');
echo $copy['pooled'] === [] && $copy['head'] === [] && $copy['nested']['again'] === [] ? 'empty|' : 'BAD|';
$copy['head'][] = 'head';
$copy['nested']['again'][] = 'again';
$copy['pooled'][] = 'pool';
echo $copy['head'][0], '|', $copy['nested']['again'][0], '|', $copy['pooled'][0], '|';
$peer = constant('V70_TREE');
echo $peer['pooled'] === [] && $peer['head'] === [] && $peer['nested']['again'] === [] ? 'kept|' : 'BAD|';
echo $input['head'][91] === 'source' && $input['nested']['again'][91] === 'source' ? 'history|' : 'BAD|';
unset($input, $cell, $copy, $peer);
echo 'A|';
''',
    'selected-eval-nested-empty-duplicate-and-original-trace': br'''<?php
const V70_EVAL_TARGET = 17;
$empty = [90 => 'gone'];
unset($empty[90]);
$cell = $empty;
unset($empty);
$input = ['pooled' => [], 'nested' => ['leaf' => &$cell]];
function v70Report($level, $message) {
    global $cell;
    echo 'H|', constant('V70_EVAL_TARGET'), '|';
    $cell[] = 'source';
    $probe = new Exception('probe');
    $trace = $probe->getTrace();
    $raw = $trace[1]['args'][1];
    echo $raw['pooled'] === [] ? 'pool|' : 'BAD|';
    echo $raw['nested']['leaf'][91] === 'source' ? 'source|' : 'BAD|';
    unset($probe, $trace, $raw);
    return true;
}
set_error_handler('v70Report', E_WARNING);
echo 'B|';
eval('$api = "define"; $result = $api(value: $input, constant_name: "V70_EVAL_TARGET", case_insensitive: false); echo $result ? "BAD|" : "F|"; unset($api, $result);');
restore_error_handler();
echo constant('V70_EVAL_TARGET'), '|', $input['nested']['leaf'][91], '|';
unset($input, $cell);
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
