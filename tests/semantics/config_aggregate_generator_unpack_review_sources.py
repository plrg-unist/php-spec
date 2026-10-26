#!/usr/bin/env python3
"""A returned Generator throws an Exception captured by its real Aggregate producer."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'retained-config-aggregate-generator-rethrows-producer-exception': br'''<?php
function configGeneratorSavedThrowReview91() {
    global $it, $saved, $effects;
    echo 'Y0|'; ++$effects; yield 3 => 'precision';
    echo 'Y1|'; ++$effects; $it = 17; ini_set('precision', '7');
    yield 3 => '11';
    echo 'T|'; ++$effects; throw $saved;
}
class ConfigGeneratorExceptionAggregateReview91 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $it, $aggregate, $call, $saved, $effects;
        echo 'G|'; ++$effects;
        $aggregate = 23; $call = ini_get(...); ini_set('precision', '6');
        $saved = new Exception('config-aggregate-generator-saved-before-resume91');
        return $it;
    }
}
$it = configGeneratorSavedThrowReview91(); $hold = $it;
$aggregate = new ConfigGeneratorExceptionAggregateReview91; $aggregateHold = $aggregate;
$call = ini_set(...); $keep = $call; $saved = null; $effects = 0;
$result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...$aggregate
    );
    echo 'BAD';
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', ini_get('precision'), '|', $it, '|', $aggregate;
    echo '|', $trace[0]['function'], '|', $trace[0]['class'], '|', $trace[0]['type'], '|', $trace[0]['line'], '|';
    echo $trace[0]['args'] === [] ? 'A' : 'BAD';
    echo isset($trace[1]) ? '|BAD' : '|F';
} finally { echo '|Z'; }
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
