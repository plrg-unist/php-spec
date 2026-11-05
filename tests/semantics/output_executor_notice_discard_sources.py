#!/usr/bin/env python3
"""A consumed Closure keeps only borrowed capture metadata after Notice throw."""
from pathlib import Path

import function_scope as scope
from output_executor_creation_sources import ORIGINALS as CREATED

ORIGINALS = {
    'factory-byref-closure': CREATED['closure-lifetime-byref'].replace(
        b'set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return true; });',
        b'set_error_handler(static function ($level, $message) { global $pendingNoticeOB12; echo "H:", $level, "|"; throw $pendingNoticeOB12; });').replace(
        b'        echo "D1|";',
        b'        global $pendingNoticeOB12; echo "D1|"; $pendingNoticeOB12 = new Exception("notice");').replace(
        b'echo ob_start(capturedCallbackOB10()) ? "T|" : "F|";',
        b'try { ob_start(capturedCallbackOB10()); echo "BAD_RETURN|"; } catch (Throwable $error) { echo "E:", $error->getMessage(), "|"; }'),
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-notice-discard',
                                    Path(__file__), publish=False,
                                    model_seconds=180) else 1)
