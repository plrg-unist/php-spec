#!/usr/bin/env python3
"""Independent invalid-output lookup, cleanup order and pending diagnostics."""
from pathlib import Path

import function_scope as scope

HERE = Path(__file__).resolve().parent
BASE = (HERE / 'output_executor_post_deactivate_explicit.php').read_bytes()
CYCLE_PREFIX = b'''<?php
class InvalidCycleOB11 {
    public $self;
    public function __toString() { echo "BAD_STRING|"; return "missing"; }
    public function __destruct() { echo "K|"; }
}
function invalidCycleOB11() {
    global $weak;
    $c = new InvalidCycleOB11;
    $c->self = $c;
    $weak = WeakReference::create($c);
    return $c;
}
set_error_handler(static function ($level, $message) {
    global $weak;
    echo "H:", $level, "|", ($weak->get() === null ? "D|" : "L|"), gc_collect_cycles(), "|";
    return true;
});
'''
CYCLE_TAIL = b'''        global $weak;
        echo ($weak->get() === null ? "D|" : "L|"), "G|";
        echo gc_collect_cycles(), "|", ($weak->get() === null ? "D|" : "L|");
        $survivor = $weak->get();
        if ($survivor !== null) { $survivor->self = null; }
        unset($survivor);
        $weak = null;
'''
REBOUND_PREFIX = b'''<?php
class InvalidReboundOB11 {
    public function run($a, $b, $c, $d) { echo "BAD_INVOKE|"; }
    public function __destruct() { echo "K|"; }
}
$method = "missing";
set_error_handler(static function ($level, $message) {
    global $method;
    echo "H:", $level, "|";
    if ($level === 2) { $method = "run"; }
    return true;
});
'''
REPLACING_PREFIX = b'''<?php
class ReplacingWarningOB11 {
    public function __invoke($level, $message) {
        echo "A:", $level, "|";
        restore_error_handler();
        set_error_handler(static function ($level, $message) { echo "B:", $level, "|"; return true; });
        return true;
    }
    public function __destruct() { echo "C|"; }
}
'''
PENDING_BASE = b'''<?php
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; if ($level === 2) { throw new Exception("warning"); } return true; }, 2);
class LateProbeOB10 {
    public function __destruct() {
        echo "D1|";
        try { echo ob_start(42) ? "T|" : "F|"; } catch (Throwable $e) { echo "C:", $e->getMessage(), "|"; }

        echo ob_get_level(), "|D2|";
    }
}
ob_start(function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new LateProbeOB10);
    return "F" . $bytes;
});
echo "X|";
'''

# Retain the original fixture's padded blank line.
PENDING_BASE = PENDING_BASE.replace(b'\n\n', b'\n        \n')

ORIGINALS = {
    'invalid-direct-cycle': BASE.replace(b'<?php\n', CYCLE_PREFIX).replace(
        b'ob_start(null)', b'ob_start(invalidCycleOB11())').replace(
        b'        echo ob_get_level()', CYCLE_TAIL + b'        echo ob_get_level()'),
    'invalid-array-child-cycle': BASE.replace(b'<?php\n', CYCLE_PREFIX).replace(
        b'ob_start(null)', b'ob_start([invalidCycleOB11(), "missing"])').replace(
        b'        echo ob_get_level()', CYCLE_TAIL + b'        echo ob_get_level()'),
    'invalid-selector-becomes-valid': BASE.replace(b'<?php\n', REBOUND_PREFIX).replace(
        b'        echo "D1|";', b'        global $method; echo "D1|";').replace(
        b'ob_start(null)', b'ob_start([new InvalidReboundOB11, &$method])').replace(
        b'        echo ob_get_level()', b'        echo $method, "|";\n        echo ob_get_level()'),
    'warning-handler-created-late': BASE.replace(b'<?php\n', REPLACING_PREFIX).replace(
        b'        echo "D1|";\n', b'        echo "D1|";\n        set_error_handler(new ReplacingWarningOB11);\n').replace(
        b'ob_start(null)', b'ob_start(42)'),
    'warning-throw-notice-mask-excluded': PENDING_BASE,
    'warning-throw-notice-suppressed': PENDING_BASE.replace(b'ob_start(42)', b'@ob_start(42)'),
}
ORIGINALS['invalid-direct-cycle-warning-throw'] = ORIGINALS['invalid-direct-cycle'].replace(
    b'    echo "H:", $level, "|", ($weak->get() === null ? "D|" : "L|"), gc_collect_cycles(), "|";\n    return true;',
    b'    echo "H:", $level, "|G|", gc_collect_cycles(), "|";\n    if ($level === 2) { throw new Exception("warning"); }\n    return true;').replace(
    b'echo ob_start(invalidCycleOB11()) ? "T|" : "F|";',
    b'try { ob_start(invalidCycleOB11()); echo "BAD_RETURN|"; } catch (Throwable $error) { echo "CAUGHT|"; }')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-invalid-review',
                                    Path(__file__), publish=False, model_seconds=180) else 1)
