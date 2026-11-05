#!/usr/bin/env python3
"""Frozen failed lookup, Warning/Notice order and real argument cleanup."""
from pathlib import Path

import function_scope as scope
from output_executor_creation_sources import ORIGINALS as CREATED
from output_executor_reception_sources import ORIGINALS as RECEIVED

HERE = Path(__file__).resolve().parent
BASE = (HERE / 'output_executor_post_deactivate_explicit.php').read_bytes()
HANDLED = b'''<?php
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return true; });
'''
ORIGINALS = {
    'default-int': (HERE / 'output_executor_post_deactivate_invalid_ob08.php').read_bytes(),
    'published-after-warning': BASE.replace(b'<?php\n', b'''<?php
set_error_handler(static function ($level, $message) {
    echo "H:", $level, ":", $message, "|";
    if ($level === 2) { function appearedAfterWarningOB11() { echo "FN|"; } }
    return true;
});
''').replace(b'ob_start(null)', b'ob_start("appearedAfterWarningOB11")').replace(
        b'echo ob_get_level(), "|D2|";', b'appearedAfterWarningOB11(); echo ob_get_level(), "|D2|";'),
    'invalid-object': BASE.replace(b'<?php\n', HANDLED + b'''class InvalidObjectOB11 {
    function __toString() { echo "BAD_STRING|"; return "ob_get_level"; }
    function __destruct() { echo "C|"; }
}
''').replace(b'ob_start(null)', b'ob_start(new InvalidObjectOB11)'),
    'invalid-array-method': BASE.replace(b'<?php\n', HANDLED + b'''class InvalidMethodOB11 {
    function run($bytes) { echo "BAD_INVOKE|"; return $bytes; }
    function __destruct() { echo "C|"; }
}
''').replace(b'ob_start(null)', b'ob_start(...["callback" => [new InvalidMethodOB11, "missing"], "flags" => 3])'),
}
THROW = b'''<?php
set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; throw new Exception("warning"); });
'''
ORIGINALS['warning-throw-all-mask'] = BASE.replace(b'<?php\n', THROW).replace(
    b'echo ob_start(null) ? "T|" : "F|";',
    b'try { ob_start(42); echo "BAD_RETURN|"; } catch (Exception $error) { echo "E:", $error->getMessage(), "|"; }')
ORIGINALS['warning-return-object'] = ORIGINALS['invalid-object'].replace(
    b'set_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return true; });',
    b'class WarningReturnOB11 { function __destruct() { echo "R|"; } }\nset_error_handler(static function ($level, $message) { echo "H:", $level, "|"; return new WarningReturnOB11; });')
ORIGINALS['warning-return-destructor-throw'] = ORIGINALS['warning-return-object'].replace(
    b'echo "R|";', b'echo "R|"; throw new Exception("warning-result");').replace(
    b'echo ob_start(new InvalidObjectOB11) ? "T|" : "F|";',
    b'try { ob_start(new InvalidObjectOB11); echo "BAD_RETURN|"; } catch (Exception $error) { echo "E:", $error->getMessage(), "|"; }')
ORIGINALS['argument-cleanup-throw'] = ORIGINALS['invalid-object'].replace(
    b'echo "C|";', b'echo "C|"; throw new Exception("cleanup");').replace(
    b'echo ob_start(new InvalidObjectOB11) ? "T|" : "F|";',
    b'try { ob_start(new InvalidObjectOB11); echo "BAD_RETURN|"; } catch (Exception $error) { echo "E:", $error->getMessage(), "|"; }')
ORIGINALS['warning-throw-owning'] = ORIGINALS['invalid-object'].replace(
    HANDLED, THROW).replace(
    b'echo ob_start(new InvalidObjectOB11) ? "T|" : "F|";',
    b'try { ob_start(new InvalidObjectOB11); echo "BAD_RETURN|"; } catch (Exception $error) { echo "E:", $error->getMessage(), "|"; }')
ORIGINALS['warning-retires-array-receiver'] = BASE.replace(b'<?php\n', b'''<?php
class RetiredFailureReceiverOB11 { function run($bytes) { echo "BAD_INVOKE|"; return $bytes; } function __destruct() { echo "C|"; } }
set_error_handler(static function ($level, $message) { global $receiver; echo "H:", $level, ":", $message, "|"; if ($level === 2) { $receiver = null; } return true; });
''').replace(b'echo "D1|";', b'global $receiver; $receiver = new RetiredFailureReceiverOB11; echo "D1|";').replace(
    b'ob_start(null)', b'ob_start([&$receiver, "missing"])')
ORIGINALS['type-error-before-lookup'] = RECEIVED['nonnull-type-error']
ORIGINALS['successful-byref-closure'] = CREATED['closure-lifetime-byref']

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-invalid',
                                    Path(__file__), publish=False, model_seconds=150) else 1)
