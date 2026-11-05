#!/usr/bin/env python3
"""A failed-start Notice handler returns an object whose destructor throws."""
from pathlib import Path

import function_scope as scope

HERE = Path(__file__).resolve().parent
BASE = (HERE / 'output_executor_post_deactivate_retval.php').read_bytes()
OLD_RETURN = b'''    public function __destruct() {
        echo "R1|";
        echo ob_start() ? "RT|" : "RF|";
        echo "R2|";
    }'''
NEW_RETURN = b'''    public function __destruct() {
        echo "R1|";
        throw new Exception("retval");
    }'''
OLD_START = b'        echo ob_start() ? "DT|" : "DF|";'
assert BASE.count(OLD_RETURN) == 1 and BASE.count(OLD_START) == 1
NOARG = BASE.replace(OLD_RETURN, NEW_RETURN).replace(
    OLD_START, b'''        try { echo ob_start() ? "DT|" : "DF|"; }
        catch (Throwable $error) { echo "C:", $error->getMessage(), "|"; }''')
CALLBACK = b'''class CallbackOB13 {
    public function __invoke($a, $b, $c, $d) { echo "BAD_INVOKE|"; }
    public function __destruct() { echo "K|"; }
}
'''
OBJECT = NOARG.replace(b'class LateRetvalStartOB06', CALLBACK + b'class LateRetvalStartOB06').replace(
    b'echo ob_start() ? "DT|" : "DF|";', b'echo ob_start(new CallbackOB13) ? "DT|" : "DF|";')
ORIGINALS = {
    'noarg': NOARG,
    'object': OBJECT,
    'object-unset': OBJECT.replace(
        b'catch (Throwable $error) { echo "C:", $error->getMessage(), "|"; }',
        b'catch (Throwable $error) { echo "C:", $error->getMessage(), "|"; unset($error); echo "U|"; }'),
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-notice-retval-throw',
                                    Path(__file__), publish=False, model_seconds=120) else 1)
