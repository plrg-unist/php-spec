#!/usr/bin/env python3
"""Notice throws separate argument-root NOGC, child release and trace owners."""
from pathlib import Path

import function_scope as scope
from output_executor_invalid_review_sources import BASE, CYCLE_PREFIX, CYCLE_TAIL

OLD_HANDLER = b'''set_error_handler(static function ($level, $message) {
    global $weak;
    echo "H:", $level, "|", ($weak->get() === null ? "D|" : "L|"), gc_collect_cycles(), "|";
    return true;
});
'''
NOTICE_HANDLER = b'''set_error_handler(static function ($level, $message) {
    global $pendingNoticeOB12;
    echo "H:", $level, "|";
    if ($level === 8) { echo "G|", gc_collect_cycles(), "|"; throw $pendingNoticeOB12; }
    return true;
});
'''
PREFIX = CYCLE_PREFIX.replace(b'InvalidCycleOB11', b'NoticeCycleOB12').replace(
    b'invalidCycleOB11', b'noticeCycleOB12')
assert PREFIX.count(OLD_HANDLER) == 1
PREFIX = PREFIX.replace(OLD_HANDLER, NOTICE_HANDLER).replace(
    b'    public function __toString()',
    b'    public function run($a, $b, $c, $d) { echo "BAD_INVOKE|"; }\n    public function __toString()')
assert BASE.count(b'        echo "D1|";') == 1
assert BASE.count(b'echo ob_start(null) ? "T|" : "F|";') == 1

ORIGINALS = {}
for successful in (True, False):
    prefix = PREFIX
    if successful:
        prefix = prefix.replace(
            b'    public function run(',
            b'    public function __invoke($a, $b, $c, $d) { echo "BAD_INVOKE|"; }\n    public function run(')
    for array in (False, True):
        name = ('successful' if successful else 'failed') + ('-array-child' if array else '-direct')
        argument = (b'[noticeCycleOB12(), "' + (b'run' if successful else b'missing') + b'"]'
                    if array else b'noticeCycleOB12()')
        ORIGINALS[name] = BASE.replace(b'<?php\n', prefix).replace(
            b'        echo "D1|";',
            b'        global $pendingNoticeOB12;\n        echo "D1|";\n        $pendingNoticeOB12 = new Exception("notice");').replace(
            b'echo ob_start(null) ? "T|" : "F|";',
            b'try { ob_start(' + argument + b'); echo "BAD_RETURN|"; } catch (Throwable $error) { echo "CAUGHT|"; }').replace(
            b'        echo ob_get_level()', CYCLE_TAIL + b'        echo ob_get_level()')
for name in ('successful-direct', 'failed-direct'):
    ORIGINALS[name + '-new-trace'] = ORIGINALS[name].replace(
        b'throw $pendingNoticeOB12;', b'throw new Exception("notice");')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-notice-discard-review',
                                    Path(__file__), publish=False, model_seconds=240) else 1)
