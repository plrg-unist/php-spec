#!/usr/bin/env python3
"""Independent creation without invocation and saved referenced selectors."""
from pathlib import Path

import function_scope as scope

BASE = '''<?php
HEADERclass LateProbeOB10 {
    public function __destruct() {
        echo "D1|";
        echo CALL ? "T|" : "F|";
        TAIL
        echo ob_get_level(), "|D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateProbeOB10);
    return "F" . $bytes;
});
echo "X|";
'''
CALLABLE = '''class CallbackOB10 {
    public function __invoke($a, $b, $c, $d): never { throw new Exception("unexpected invocation"); }
    public function run($a, $b, $c, $d): never { throw new Exception("unexpected invocation"); }
    public function __destruct() { echo "K|"; }
}
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return true; });
'''
REBOUND = '''class CallbackRefOB10 {
    public function run($a, $b, $c, $d): never { throw new Exception("unexpected invocation"); }
    public function __destruct() { echo "K|"; }
}
$method = "run";
set_error_handler(static function ($level, $message) { global $method; echo "H:", $level, "|"; $method = 42; return true; });
'''
CYCLE = '''class CallbackCycleOB10 {
    public $self;
    public function __invoke($a, $b, $c, $d): never { throw new Exception("unexpected invocation"); }
    public function __destruct() { echo "K|"; }
}
function callbackCycleOB10() { global $weak; $c = new CallbackCycleOB10; $c->self = $c; $weak = WeakReference::create($c); return $c; }
set_error_handler(static function ($level, $message) { global $weak; echo "H:", $level, "|", ($weak->get() === null ? "D|" : "L|"), gc_collect_cycles(), "|"; return true; });
'''
ORIGINALS = {
    'required-invokable': BASE.replace('HEADER', CALLABLE).replace(
        'CALL', 'ob_start(new CallbackOB10)').replace('TAIL', '').encode(),
    'required-array': BASE.replace('HEADER', CALLABLE).replace(
        'CALL', 'ob_start([new CallbackOB10, "run"])').replace('TAIL', '').encode(),
    'referenced-selector-rebound': BASE.replace('HEADER', REBOUND).replace(
        'CALL', 'ob_start([new CallbackRefOB10, &$method])').replace(
        'TAIL', 'global $method; echo $method, "|";').replace(
        'echo "D1|";', 'global $method; echo "D1|";').encode(),
}
ORIGINALS['referenced-selector-rebound-slow'] = ORIGINALS['referenced-selector-rebound']
ORIGINALS['cycle-handler-gc'] = BASE.replace('HEADER', CYCLE).replace(
    'CALL', 'ob_start(callbackCycleOB10())').replace(
    'TAIL', 'global $weak; echo ($weak->get() === null ? "D|" : "L|"), "G|"; echo gc_collect_cycles(), "|", ($weak->get() === null ? "D|" : "L|");').encode()
ORIGINALS['cycle-without-handler-gc'] = ORIGINALS['cycle-handler-gc'].replace(
    b', gc_collect_cycles(), "|"; return true;', b'; return true;')
ORIGINALS['cycle-array-handler-gc'] = ORIGINALS['cycle-handler-gc'].replace(
    b'ob_start(callbackCycleOB10())', b'ob_start([callbackCycleOB10(), "__invoke"])')
ENVIRONMENTS = {
    'referenced-selector-rebound-slow': [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0'],
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-creation-review',
                                    Path(__file__), publish=False, model_seconds=180,
                                    request_environments=ENVIRONMENTS) else 1)
