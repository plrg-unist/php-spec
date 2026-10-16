#!/usr/bin/env python3
"""Native-first rejected current stdClass argument objects and array roots."""
from pathlib import Path

import global_constant_stdclass_arguments_review_sources as previous

family = previous.family
original = family.CASES['named-value-destructors-and-duplicate-cutoff']
family.CASES = {
    'duplicate-current-object': original,
    'duplicate-current-nested-array': br'''<?php
class V64Prior {
    public function __destruct() { echo 'prior|'; }
}
class V64Current {
    public function __destruct() { echo 'current|'; }
}
echo 'B|';
try {
    eval('const V64_DUPLICATE = new stdClass(keep: new V64Prior(), keep: [NAN, [new V64Current()]], late: new V64Prior());');
} catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|';
}
echo defined('V64_DUPLICATE') ? 'BAD|' : 'absent|';
unset($e);
echo 'A|';
''',
}
family.BASELINE = ('global constant internal or Throwable initializer', b'B|first|second|ready|41|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
