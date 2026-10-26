#!/usr/bin/env python3
"""Temporary INPUT retirement preserves the real storage pin and Dtor throw."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'temporary-generator-return-dtor-throw-precedes-config-api': br'''<?php
class ConfigGeneratorStorageThrowReview96 {
    public function __destruct() {
        global $watchGenerator, $watchReturn, $saved, $call, $effects;
        echo 'D|'; ++$effects;
        echo $watchGenerator->get() !== null ? 'G|' : 'BAD|';
        echo $watchReturn->get() !== null ? 'V|' : 'BAD|';
        $call = ini_get(...); ini_set('precision', '6');
        $saved = new Exception('config-generator-storage96');
        throw $saved;
    }
}
function configGeneratorStorageBodyReview96() {
    global $watchReturn, $effects;
    echo 'Y0|'; ++$effects; yield 3 => 'precision';
    echo 'Y1|'; ++$effects; yield 3 => '8';
    echo 'F|'; ++$effects;
    $payload = new ConfigGeneratorStorageThrowReview96();
    $watchReturn = WeakReference::create($payload);
    return $payload;
}
function configGeneratorStorageFactoryReview96() {
    global $watchGenerator;
    echo 'P|'; $generator = configGeneratorStorageBodyReview96();
    $watchGenerator = WeakReference::create($generator);
    return $generator;
}
$watchGenerator = null; $watchReturn = null; $saved = null; $effects = 0;
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...configGeneratorStorageFactoryReview96()
    );
    echo 'BAD';
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', ini_get('precision');
    echo '|', $trace[0]['function'], '|', $trace[0]['class'], '|', $trace[0]['type'], '|', $trace[0]['line'];
    echo $trace[0]['args'] === [] ? '|A' : '|BAD';
    echo isset($trace[1]) ? '|BAD' : '|N';
    echo $watchGenerator->get() === null ? '|gD' : '|BAD';
    echo $watchReturn->get() === null ? '|vD' : '|BAD';
}
echo '|L|', $call('precision'), '|R|', $keep('precision', '9'), '|', ini_get('precision'), '|', $result;
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
