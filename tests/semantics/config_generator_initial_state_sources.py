#!/usr/bin/env python3
"""CONFIG observes native Generator acquisition and first-yield history."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'cached-first-generator-config-reuses-value-and-retires-data': br'''<?php
function configGeneratorCached95() {
    global $generator;
    echo 'Y0|'; yield 3 => 'precision';
    echo 'Y1|'; $generator = 17; ini_set('precision', '7'); yield 3 => '8';
    echo 'F|'; ini_set('precision', '6');
}
$generator = configGeneratorCached95(); $watch = WeakReference::create($generator);
$result = 99; echo 'B|';
echo 'C|', $generator->current(), '|U|';
$result = ini_set(...$generator);
echo 'A|', $result, '|', ini_get('precision'), '|', $generator;
echo $watch->get() === null ? '|D' : '|BAD';
''',
    'closed-generator-config-rejects-before-iterator-data': br'''<?php
function configGeneratorClosed95() {
    echo 'Y0|'; yield 3 => 'precision';
    echo 'F|'; ini_set('precision', '6');
}
$generator = configGeneratorClosed95(); $watch = WeakReference::create($generator);
$result = 99; echo 'B|'; $generator->next();
echo $generator->valid() ? 'BAD|' : 'C|';
try {
    $result = ini_set(
        ...$generator
    );
    echo 'BAD';
} catch (Exception $e) {
    echo 'E|', get_class($e), '|', $e->getMessage(), '|', $e->getLine();
    echo $e->getTrace() === [] ? '|T' : '|BAD';
    echo '|', $result, '|', ini_get('precision');
    echo $watch->get() !== null ? '|H' : '|BAD';
}
unset($generator); echo $watch->get() === null ? '|D' : '|BAD';
echo '|R|', ini_set('precision', '9'), '|', ini_get('precision');
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
