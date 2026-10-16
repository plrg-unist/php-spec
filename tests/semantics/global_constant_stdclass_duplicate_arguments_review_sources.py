#!/usr/bin/env python3
"""Independent rejected array roots, escaped leaf identity and fresh retry."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'escaped-leaf-array-and-fresh-retry': br'''<?php
class V64ReviewPrior {
    public function __destruct() { echo 'prior|'; }
}
class V64ReviewEscaped {
    public int $value = 7;
    public function __construct() { $GLOBALS['v64_review_escape'] = $this; }
    public function __destruct() { echo 'escaped:', $this->value, '|'; }
}
class V64ReviewLast {
    public function __destruct() { echo 'last|'; }
}
echo 'B|';
try {
    eval('const V64_REVIEW_BAD = new stdClass(keep: new V64ReviewPrior(), keep: [NAN, [new V64ReviewEscaped(), new V64ReviewLast()]], late: new V64ReviewPrior());');
} catch (Error $e) {
    echo 'E|', $e->getMessage(), '|';
}
$held = $GLOBALS['v64_review_escape'];
unset($GLOBALS['v64_review_escape']);
$held->value = 41;
unset($held, $e);
echo defined('V64_REVIEW_BAD') ? 'BAD|' : 'absent|';
eval('const V64_REVIEW_BAD = new stdClass(only: 23);');
$retry = constant('V64_REVIEW_BAD');
echo isset($retry->value) ? 'BAD|' : 'empty|';
unset($retry);
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
