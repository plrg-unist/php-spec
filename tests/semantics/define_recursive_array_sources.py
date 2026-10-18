#!/usr/bin/env python3
"""Native-first recursive array validation before copying or duplicate reporting."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'self-cycle-error-trace-and-acyclic-retry': br'''<?php
$input = ['empty' => [], 'tag' => 11];
$input['self'] =& $input;
$result = 99;
echo 'B|';
try {
    $result = define('V71_SELF', $input, false);
} catch (ValueError $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[0]['args'][1];
    echo $trace[0]['function'], '|';
    echo $raw['self']['tag'] === 11 ? 'cycle|' : 'BAD|';
    unset($input['self']);
    echo !isset($raw['self']['self']) ? 'broken|' : 'BAD|';
}
echo defined('V71_SELF') ? 'BAD|' : 'absent|';
echo $result === 99 ? 'kept|' : 'BAD|';
echo define('V71_SELF', $input) ? 'T|' : 'BAD|';
$copy = constant('V71_SELF');
$copy['empty'][] = 'local';
$stored = constant('V71_SELF');
echo $copy['empty'][0], '|', $stored['tag'], '|';
echo $stored['empty'] === [] ? 'kept-empty|' : 'BAD|';
unset($input, $result, $error, $trace, $raw, $copy, $stored);
echo 'A|';
''',
    'selected-eval-mutual-cycle-before-duplicate-warning': br'''<?php
const V71_OLD = 17;
$warnings = 0;
function v71Report($level, $message) {
    global $warnings;
    ++$warnings;
    echo 'H|';
    return true;
}
set_error_handler('v71Report', E_WARNING);
$left = ['tag' => 'L'];
$right = ['tag' => 'R'];
$left['peer'] =& $right;
$right['peer'] =& $left;
$result = 'kept';
echo 'B|';
try {
    eval('$api = "define"; $result = $api(value: $left, constant_name: "V71_OLD", case_insensitive: false);');
} catch (ValueError $error) {
    echo 'E|', $error->getMessage(), '|', $error->getLine(), '|';
    $trace = $error->getTrace();
    $raw = $trace[0]['args'][1];
    echo $trace[0]['function'], '|';
    echo $raw['peer']['peer']['tag'] === 'L' ? 'mutual|' : 'BAD|';
    echo $trace[0]['args'][2] === false ? 'false|' : 'BAD|';
}
echo $warnings, '|', constant('V71_OLD'), '|', $result, '|';
unset($left['peer'], $right['peer']);
unset($error, $trace, $raw);
echo $api('V71_OLD', $left, false) ? 'BAD|' : 'F|';
echo $warnings, '|', constant('V71_OLD'), '|';
restore_error_handler();
unset($left, $right, $api, $result);
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
