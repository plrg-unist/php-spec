#!/usr/bin/env python3
"""Native-first Stringable define names reach class-name ValueError after casting."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'stringable-class-define-name-errors-after-conversion': br'''<?php
class StringClassName57 {
    public function __toString(): string {
        global $calls; echo 'S|'; $calls++; return 'Missing57::VALUE';
    }
}
$name = new StringClassName57; $keep = $name; $calls = 0; $result = 99;
echo 'B|';
try { $result = define($name, 1601); echo 'BAD'; }
catch (ValueError $e) {
    $trace = $e->getTrace();
    echo $e->getMessage(), '|', $trace[0]['function'];
    echo '|', $trace[0]['args'][0] === 'Missing57::VALUE' ? 'N' : 'BAD';
    echo '|', $trace[0]['args'][1], '|', $result, '|', $calls;
}
''',
    'selected-stringable-class-name-keeps-earlier-candidate-and-false': br'''<?php
class CapturedStringClass57 {
    public function __toString(): string {
        global $call, $name, $value, $flag, $calls;
        echo 'S|'; $calls++; $call = 'constant'; $name = 'cast-live57';
        $value = 997; $flag = true; $part = 'Captured57:'; return $part . ':VALUE';
    }
}
function stringClassValue57() {
    global $call, $name, $value, $effects;
    $earlier = $value; echo 'V|'; $effects++; $call = 'defined';
    $name = 'value-live57'; return $earlier;
}
function stringClassCaller57() {
    global $call, $name, $value, $flag, $calls, $effects;
    $call = 'DeFiNe'; $name = new CapturedStringClass57; $keep = $name;
    $part = 'captured'; $value = $part . '-candidate57'; $flag = false;
    $calls = 0; $effects = 0; $result = 99;
    try { $result = $call($name, stringClassValue57(), $flag); echo 'BAD'; }
    catch (ValueError $e) {
        $trace = $e->getTrace();
        echo $e->getMessage(), '|', $trace[0]['function'];
        echo '|', $trace[0]['args'][0] === 'Captured57::VALUE' ? 'N' : 'BAD';
        echo '|', $trace[0]['args'][1] === 'captured-candidate57' ? 'V' : 'BAD';
        echo '|', $trace[0]['args'][2] === false ? 'F' : 'BAD';
        echo '|', $result, '|', $calls, '|', $effects;
    }
    echo '|', $call, '|', $name, '|', $value, '|', $flag === true ? 'T' : 'BAD';
}
echo 'B|'; stringClassCaller57();
''',
    'bare-class-name-error-recovers-with-global-stringable-definition': br'''<?php
class RecoverStringClass57 {
    public function __toString(): string {
        global $calls; echo 'S|'; $calls++;
        if ($calls === 1) { return '::'; }
        return 'STRINGCLASSRECOVERY57';
    }
}
$name = new RecoverStringClass57; $keep = $name; $calls = 0; $result = 99;
echo 'B|';
try { $result = define($name, 1621, false); echo 'BAD'; }
catch (ValueError $e) { echo $e->getMessage(), '|', $result; }
echo '|', define($name, 1637) ? 'T' : 'BAD', '|', constant('STRINGCLASSRECOVERY57'), '|', $calls;
''',
}
family.BASELINE = ('Stringable define global name', b'B|S|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
