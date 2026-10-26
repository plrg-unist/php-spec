#!/usr/bin/env python3
"""Advanced Generator rewind fails before inspecting its non-string current."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'advanced-config-generator-rewind-error-precedes-current-send': br'''<?php
function configGeneratorInitialReview95() {
    global $effects;
    echo 'Y0|'; ++$effects; ini_set('precision', '6'); yield 3 => 'precision';
    echo 'Y1|'; ++$effects; yield 3 => 17;
    echo 'F|'; ++$effects;
}
$effects = 0; $generator = configGeneratorInitialReview95();
$watch = WeakReference::create($generator);
$generator->current(); $generator->next();
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...$generator
    );
    echo 'BAD';
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo 'X|', $e->getMessage(), '|', $e->getLine();
    echo '|', $result, '|', $effects, '|', ini_get('precision'), '|', $generator->current();
    echo isset($trace[0]) ? '|BAD' : '|N';
    echo $watch->get() === $generator ? '|H|' : '|BAD|';
}
$generator->next();
$generator = null;
echo $watch->get() === null ? 'D' : 'BAD';
echo '|R|', $keep('precision', '9'), '|', ini_get('precision'), '|', $result, '|', $effects;
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
