#!/usr/bin/env python3
"""Native-first boolean ignored-warning throws and fresh registration tails."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-true-pending-registration': br'''<?php
function stopLiteralBool32($level, $message) {
    global $effect;
    echo 'H|', $level, '|', $message, '|';
    $effect = 'after';
    throw new Exception('stop');
}
function literalBoolCaller32() {
    global $effect;
    $result = 99;
    set_error_handler('stopLiteralBool32');
    try {
        $result = define('LiteralBoolTail32', 161, true);
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $effect, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'LiteralBoolTail32' ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 161 ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === true ? 'T' : 'BAD';
        echo '|', $trace[2]['function'], '|', defined('LiteralBoolTail32') ? 'T' : 'F';
        echo '|', defined('LiteralBoolTail32') ? constant('LiteralBoolTail32') : 'absent';
        echo '|', defined('literalbooltail32') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
$effect = 'before';
echo 'B|';
literalBoolCaller32();
''',
    'strict-selected-true-captured-carrier': br'''<?php
declare(strict_types=1);
function strictBoolValue32() {
    global $candidate, $flag, $call;
    echo 'V|'; $flag = false; $call = 'constant'; return $candidate;
}
function strictBoolName32() {
    global $name, $candidate, $call;
    echo 'N|'; $name = 'later'; $candidate = 'later-value'; $call = 'defined';
    return 'StrictBoolTail32';
}
function stopStrictBool32($level, $message) {
    global $name, $candidate, $flag, $call;
    echo 'H|', $level, '|', $message, '|';
    define('SiblingBoolTail32', 232);
    $name = 'handler'; $candidate = 'handler-value'; $flag = false; $call = 'constant';
    throw new Exception('strict-stop');
}
function strictBoolCaller32() {
    global $name, $candidate, $flag, $call;
    $part = 'capture'; $candidate = $part . '-value';
    $name = 'StrictBoolTail32'; $flag = true; $call = 'define'; $result = 99;
    set_error_handler('stopStrictBool32');
    try {
        $result = $call(case_insensitive: $flag, value: strictBoolValue32(), constant_name: strictBoolName32());
        echo 'BAD';
    } catch (Exception $e) {
        $trace = $e->getTrace();
        echo $name, '|', $candidate, '|', $flag === false ? 'F' : 'BAD';
        echo '|', $call, '|', $result, '|', $e->getMessage();
        echo '|', $trace[0]['function'], '|', $trace[1]['function'];
        echo '|', $trace[1]['args'][0] === 'StrictBoolTail32' ? 'N' : 'BAD';
        echo '|', $trace[1]['args'][1] === 'capture-value' ? 'V' : 'BAD';
        echo '|', $trace[1]['args'][2] === true ? 'T' : 'BAD';
        echo '|', $trace[2]['function'], '|', constant('SiblingBoolTail32');
        echo '|', defined('StrictBoolTail32') ? 'T' : 'F';
        echo '|', defined('StrictBoolTail32') ? constant('StrictBoolTail32') : 'absent';
        echo '|', defined('handler') ? 'T' : 'F';
    } finally {
        restore_error_handler();
        echo '|Z';
    }
}
echo 'B|';
strictBoolCaller32();
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
