#!/usr/bin/env python3
"""Inactive handler creation, saved selection and ordinary argument cleanup."""
from pathlib import Path

import function_scope as scope

HERE = Path(__file__).resolve().parent
BASE = (HERE / 'output_executor_post_deactivate_explicit.php').read_bytes()
ORIGINALS = {
    'closure': (HERE / 'output_executor_post_deactivate_callable.php').read_bytes(),
    'named-function': BASE.replace(b'<?php\n',
        b'<?php\nfunction inactiveHandlerOB10($bytes, $phase) { echo "BAD|"; return $bytes; }\n').replace(
        b'ob_start(null)', b'ob_start("inactiveHandlerOB10")'),
    'required-signature': BASE.replace(b'<?php\n',
        b'<?php\nfunction inactiveRequiredOB10($a, $b, $c, $d) { echo "BAD|"; }\n').replace(
        b'ob_start(null)', b'ob_start(callback: "inactiveRequiredOB10", chunk_size: 2, flags: 3)'),
    'internal-noargs': BASE.replace(b'ob_start(null)', b'ob_start("ob_get_level")'),
    'invokable-temporary': BASE.replace(b'<?php\n',
        b'<?php\nclass InactiveCallbackOB10 { function __invoke($bytes) { echo "BAD|"; return $bytes; } function __destruct() { echo "C|"; } }\n').replace(
        b'ob_start(null)', b'ob_start(new InactiveCallbackOB10)'),
    'array-receiver-temporary': BASE.replace(b'<?php\n',
        b'<?php\nclass InactiveArrayOB10 { function run($bytes) { echo "BAD|"; return $bytes; } function __destruct() { echo "C|"; } }\n').replace(
        b'ob_start(null)', b'ob_start(...["callback" => [new InactiveArrayOB10, "run"]])'),
}
HANDLER = b'<?php\nset_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return true; });\n'
ORIGINALS['handled-invokable'] = ORIGINALS['invokable-temporary'].replace(b'<?php\n', HANDLER)
ORIGINALS['handled-array'] = ORIGINALS['array-receiver-temporary'].replace(b'<?php\n', HANDLER)
ORIGINALS['invokable-slow'] = ORIGINALS['invokable-temporary']
ORIGINALS['array-slow'] = ORIGINALS['array-receiver-temporary']
ORIGINALS['selector-changed-before-creation'] = BASE.replace(b'<?php\n', b'''<?php
class BeforeCreationOB10 { function run($bytes) { echo "BAD|"; return $bytes; } function __destruct() { echo "C|"; } }
$method = 42;
set_error_handler(static function ($level, $message) { global $method; echo "H:", $level, "|"; if ($level === 8192) { $method = "run"; } return true; });
''').replace(b'echo "D1|";', b'global $method; echo "D1|";').replace(
    b'ob_start(null)', b'ob_start([new BeforeCreationOB10, &$method], null)')
ORIGINALS['argument-cleanup-throw'] = ORIGINALS['invokable-temporary'].replace(
    b'echo "C|";', b'echo "C|"; throw new Exception("cleanup");').replace(
    b'echo ob_start(new InactiveCallbackOB10) ? "T|" : "F|";',
    b'try { echo ob_start(new InactiveCallbackOB10) ? "T|" : "F|"; } catch (Exception $error) { echo "E:", $error->getMessage(), "|"; }')
ORIGINALS['receiver-rebound-during-notice'] = BASE.replace(b'<?php\n', b'''<?php
class ReboundReceiverOB10 { function run($bytes) { echo "BAD|"; return $bytes; } function __destruct() { echo "C|"; } }
set_error_handler(static function ($level, $message) { global $receiver; echo "H1|"; $receiver = null; echo "H2|"; return true; });
''').replace(b'echo "D1|";', b'global $receiver; $receiver = new ReboundReceiverOB10; echo "D1|";').replace(
    b'ob_start(null)', b'ob_start([&$receiver, "run"])')
ORIGINALS['notice-handler-throw'] = ORIGINALS['invokable-temporary'].replace(b'<?php\n', b'''<?php
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; throw new Exception("notice"); });
''').replace(b'echo ob_start(new InactiveCallbackOB10) ? "T|" : "F|";',
    b'try { echo ob_start(new InactiveCallbackOB10) ? "T|" : "F|"; } catch (Exception $error) { echo "E:", $error->getMessage(), "|"; }')
ORIGINALS['closure-lifetime-byref'] = BASE.replace(b'<?php\n', b'''<?php
class CapturedChildOB10 { function __destruct() { echo "C|"; } }
function capturedCallbackOB10() { $child = new CapturedChildOB10; return static function ($bytes) use (&$child) { echo "BAD|"; return $bytes; }; }
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return true; });
''').replace(b'ob_start(null)', b'ob_start(capturedCallbackOB10())')
ORIGINALS['closure-lifetime-method'] = BASE.replace(b'<?php\n', b'''<?php
class CapturedMethodOB10 { function run($a, $b, $c, $d) { echo "BAD|"; } function __destruct() { echo "C|"; } }
function methodCallbackOB10() { $receiver = new CapturedMethodOB10; return $receiver->run(...); }
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return true; });
''').replace(b'ob_start(null)', b'ob_start(methodCallbackOB10())')
ORIGINALS['notice-return-callable'] = (HERE / 'output_executor_post_deactivate_retval.php').read_bytes().replace(b'<?php\n', b'''<?php
class ReturnedCallbackOB10 { function __invoke($a, $b, $c, $d) { echo "BAD|"; } function __destruct() { echo "C|"; } }
''').replace(b'echo ob_start() ? "RT|"', b'echo ob_start(new ReturnedCallbackOB10) ? "RT|"')
SLOW = [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']
ENVIRONMENTS = {'invokable-slow': SLOW, 'array-slow': SLOW}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-creation',
                                    Path(__file__), publish=False, model_seconds=120,
                                    request_environments=ENVIRONMENTS) else 1)
