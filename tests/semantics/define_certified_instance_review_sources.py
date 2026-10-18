#!/usr/bin/env python3
"""Independent certified-instance array copies and abrupt shared identity."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-instance-array-copy-throw-and-query-bucket': br'''<?php
class V73ReviewBox {
    public int $value = 0;
    public function __destruct() { echo 'D|', $this->value, '|'; }
}
const V73_REVIEW_LEFT = new V73ReviewBox();
const V73_REVIEW_RIGHT = new V73ReviewBox();
$init = V73_REVIEW_LEFT;
$init->value = 17;
$init = V73_REVIEW_RIGHT;
$init->value = 23;
unset($init);
$cell = V73_REVIEW_LEFT;
$input = ['head' => &$cell, 'nested' => ['leaf' => &$cell]];
function v73ReviewThrow(int $level, string $message): bool {
    global $cell;
    echo 'H|', $level, '|';
    $cell = V73_REVIEW_LEFT;
    $current = V73_REVIEW_RIGHT;
    $current->value = 41;
    define('V73_REVIEW_SIDE', 31);
    throw new Exception('V73_STOP');
}
$api = 'define';
echo 'B|';
echo $api(value: $input, case_insensitive: ($cell = V73_REVIEW_RIGHT) === null, constant_name: 'V73_REVIEW_TREE') ? 'T|' : 'BAD|';
$copy = constant('V73_REVIEW_TREE');
echo $copy['head'] === V73_REVIEW_RIGHT && $copy['nested']['leaf'] === V73_REVIEW_RIGHT ? 'R|' : 'BAD|';
set_error_handler('v73ReviewThrow');
$ok = 'kept';
try {
    $ok = $api(value: $input, constant_name: 'V73_REVIEW_TREE', case_insensitive: false);
    echo 'BAD|';
} catch (Exception $error) {
    echo 'E|', $error->getMessage(), '|';
    $trace = $error->getTrace();
    $raw = $trace[1]['args'][1];
    echo $trace[1]['function'], '|';
    echo $trace[1]['args'][2] === false ? 'false|' : 'BAD|';
    echo $raw['head'] === V73_REVIEW_LEFT && $raw['nested']['leaf'] === V73_REVIEW_LEFT ? 'L|' : 'BAD|';
    echo $raw['head']->value, '|';
    $row = constant('V73_REVIEW_TREE');
    echo $row['head'] === V73_REVIEW_RIGHT ? 'R|' : 'BAD|';
    echo $row['head']->value, '|';
    $slot =& $row['nested']['leaf'];
    $slot = V73_REVIEW_LEFT;
    echo $row['nested']['leaf']->value, '|';
    $again = constant('V73_REVIEW_TREE');
    echo $again['nested']['leaf'] === V73_REVIEW_RIGHT ? 'kept|' : 'BAD|';
    echo $copy['head']->value, '|', constant('V73_REVIEW_SIDE'), '|', $ok, '|';
    unset($slot, $row, $again, $trace, $raw, $error);
}
restore_error_handler();
unset($input, $cell, $copy, $api, $ok);
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
