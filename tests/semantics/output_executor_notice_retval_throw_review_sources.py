#!/usr/bin/env python3
"""A returned Notice value throws after GC, before VM argument cleanup."""
from pathlib import Path

import function_scope as scope
from output_executor_notice_discard_review_sources import ORIGINALS as OB12


OLD_HANDLER = b'''set_error_handler(static function ($level, $message) {
    global $pendingNoticeOB12;
    echo "H:", $level, "|";
    if ($level === 8) { echo "G|", gc_collect_cycles(), "|"; throw $pendingNoticeOB12; }
    return true;
});'''
RETURNED_HANDLER = b'''class NoticeReturnedThrowOB13 {
    public function __destruct() {
        global $pendingNoticeOB12;
        echo "R|G|", gc_collect_cycles(), "|";
        throw $pendingNoticeOB12;
    }
}
set_error_handler(static function ($level, $message) {
    echo "H:", $level, "|";
    if ($level === 8) { return new NoticeReturnedThrowOB13; }
    return true;
});'''

ORIGINALS = {}
for name in ('successful-direct', 'failed-direct', 'successful-array-child'):
    source = OB12[name]
    assert source.count(OLD_HANDLER) == 1
    ORIGINALS['retval-precreated-' + name] = source.replace(OLD_HANDLER, RETURNED_HANDLER)


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-notice-retval-throw-review',
                                    Path(__file__), publish=False, model_seconds=240) else 1)
