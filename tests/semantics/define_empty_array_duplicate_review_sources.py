#!/usr/bin/env python3
"""Independent empty duplicate keeps captured input append history in its trace."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-empty-throw-trace-history-after-flag-cow': br'''<?php
const V69_REVIEW_TARGET = 17;
$input = [90 => 'discard'];
unset($input[90]);
function v69ReviewThrow(int $level, string $message): bool {
    global $input;
    echo 'H|', $level, '|', constant('V69_REVIEW_TARGET'), '|';
    echo $input[91] === 'flag' ? 'flag|' : 'BAD|';
    $input[] = 'handler';
    define('V69_REVIEW_SIDE', 31);
    throw new Exception('V69_STOP');
}
set_error_handler('v69ReviewThrow');
$api = 'define';
$ok = 'kept';
echo 'B|';
try {
    $ok = $api(value: $input, case_insensitive: ($input[] = 'flag') === null, constant_name: 'V69_REVIEW_TARGET');
    echo 'BAD|';
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo $trace[1]['function'], '|';
    echo $raw === [] ? 'empty|' : 'BAD|';
    $raw[] = 'trace';
    echo isset($raw[91]) && !isset($raw[0]) ? 'history|' : 'BAD|';
    echo $input[91] === 'flag' && $input[92] === 'handler' ? 'caller|' : 'BAD|';
    echo $trace[1]['args'][1] === [] ? 'kept-empty|' : 'BAD|';
    echo $trace[1]['args'][2] === false ? 'false|' : 'BAD|';
    echo constant('V69_REVIEW_TARGET'), '|', constant('V69_REVIEW_SIDE'), '|', $ok, '|';
    unset($trace, $raw, $error);
}
restore_error_handler();
unset($input, $api, $ok);
echo 'A|';
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
