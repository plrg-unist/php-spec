#!/usr/bin/env python3
"""A Stringable query throw preserves the raw receiver and its original API call."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-stringable-query-throw-keeps-raw-object-api-trace': br'''<?php
class QueryStringReviewThrow53 {
    public function __toString(): string {
        global $call, $name, $calls, $saved;
        echo 'S|'; $calls++; $call = 'defined'; $name = 'live-name53';
        define('SOURCE53PEER', 1433);
        $saved = new Exception('query53-stop');
        throw $saved;
    }
}
function queryStringReviewCaller53() {
    global $call, $name, $calls, $saved;
    $call = 'CoNsTaNt'; $name = new QueryStringReviewThrow53(); $keep = $name;
    $calls = 0; $saved = null; $result = 99;
    try {
        $result = $call($name);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $e === $saved ? 'I' : 'BAD', '|', $e->getMessage();
        echo '|', $result, '|', $calls, '|', $call, '|', $name;
        echo '|', $trace[0]['function'], '|', $trace[0]['class'], '|', $trace[0]['type'];
        echo '|', $trace[0]['args'] === [] ? 'E' : 'BAD';
        echo '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === $keep ? 'O' : 'BAD';
        echo '|', $trace[2]['function'], '|', $e->getPrevious() === null ? 'P' : 'BAD';
        echo '|', constant('SOURCE53PEER'), '|', $result;
    } finally { echo '|Z'; }
}
echo 'B|'; queryStringReviewCaller53();
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
