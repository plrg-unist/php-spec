#!/usr/bin/env python3
"""A Generator-method throw retires its receiver pin before saved-callee recovery."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'aggregate-generator-method-terminal-throw-keeps-real-receiver-and-trace': br'''<?php
class ConfigAggregateGeneratorMethodReview93 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $aggregate, $hold, $call, $saved, $effects;
        echo 'Y0|'; ++$effects; $aggregate = 23; $call = ini_get(...);
        ini_set('precision', '6'); echo $this === $hold ? 'S|' : 'BAD|';
        $saved = new Exception('aggregate-generator-method93');
        yield 3 => 'precision';
        echo 'Y1|'; ++$effects; ini_set('precision', '7'); yield 3 => '11';
        echo 'T|'; ++$effects; throw $saved;
    }
}
$aggregate = new ConfigAggregateGeneratorMethodReview93(); $hold = $aggregate;
$watch = WeakReference::create($aggregate);
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
    echo '|', $result, '|', $effects, '|', ini_get('precision'), '|', $aggregate;
    echo '|', $trace[0]['function'], '|', $trace[0]['class'], '|', $trace[0]['type'], '|', $trace[0]['line'];
    echo $trace[0]['args'] === [] ? '|A' : '|BAD';
    echo isset($trace[1]) ? '|BAD' : '|F';
    echo $watch->get() === $hold ? '|H' : '|BAD';
}
$hold = null; echo $watch->get() === null ? '|D' : '|BAD';
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
