#!/usr/bin/env python3
"""Native-first immutable and mutable empty-array duplicate definitions."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-empty-shared-pool-and-normal-handler': br'''<?php
const V69_LITERAL_TARGET = 17;
$input = [];
function v69Literal($level, $message) {
    global $input;
    echo 'H|', $level, '|';
    $probe = new Exception('probe');
    $trace = $probe->getTrace();
    $raw = $trace[1]['args'][1];
    echo $raw === [] ? 'empty|' : 'BAD|';
    $input[] = 'handler';
    echo isset($input[0]) ? 'zero|' : 'BAD|';
    unset($probe, $trace, $raw);
    return true;
}
set_error_handler('v69Literal', E_WARNING);
echo 'B|';
$result = define('V69_LITERAL_TARGET', []);
restore_error_handler();
echo $result ? 'BAD|' : 'F|';
echo constant('V69_LITERAL_TARGET'), '|', $input[0], '|';
unset($input, $result);
echo 'A|';
''',
    'selected-eval-mutable-empty-and-default-warning': br'''<?php
const V69_EVAL_TARGET = 23;
$input = [90 => 'gone'];
unset($input[90]);
function v69Mutable($level, $message) {
    global $input;
    echo 'H|';
    $input[] = 'handler';
    $probe = new Exception('probe');
    $trace = $probe->getTrace();
    $raw = $trace[1]['args'][1];
    echo $raw === [] ? 'empty|' : 'BAD|';
    $raw[] = 'trace';
    echo isset($raw[91]) ? 'history|' : 'BAD|';
    echo $input[91] === 'handler' ? 'caller|' : 'BAD|';
    unset($probe, $trace, $raw);
    return false;
}
set_error_handler('v69Mutable', E_WARNING);
echo 'B|';
eval('$api = "define"; $result = $api("V69_EVAL_TARGET", $input, false); echo $result ? "BAD|" : "F|"; unset($api, $result);');
restore_error_handler();
echo constant('V69_EVAL_TARGET'), '|', $input[91], '|';
unset($input);
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
