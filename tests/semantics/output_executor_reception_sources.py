#!/usr/bin/env python3
"""Default-handler argument reception after output deactivation."""
from pathlib import Path

import function_scope as scope

HERE = Path(__file__).resolve().parent
BASE = (HERE / 'output_executor_post_deactivate_explicit.php').read_bytes()
HANDLED = (HERE / 'output_executor_post_deactivate_handled_ob08.php').read_bytes()
RETVAL = (HERE / 'output_executor_post_deactivate_retval.php').read_bytes()
ORIGINALS = {
    'named-null': BASE.replace(b'ob_start(null)', b'ob_start(callback: null)'),
    'unpacked-null': BASE.replace(b'ob_start(null)', b'ob_start(...[null])'),
    'dynamic-unpacked-null': BASE.replace(b'echo ob_start(null)',
        b'$start = "ob_start"; $arguments = ["callback" => null]; echo $start(...$arguments)'),
    'unpacked-named-options': BASE.replace(b'ob_start(null)',
        b'ob_start(...["flags" => -1, "callback" => null, "chunk_size" => -3])'),
    'default-named-options': BASE.replace(b'ob_start(null)',
        b'ob_start(flags: 5, chunk_size: 2)'),
    'weak-options': BASE.replace(b'ob_start(null)', b'ob_start(null, "3", true)'),
    'deprecated-options': BASE.replace(b'ob_start(null)', b'ob_start(null, null, 1.5)'),
    'handled-named-options': HANDLED.replace(b'ob_start(null)',
        b'ob_start(callback: null, flags: 31)'),
    'retval-unpacked-options': RETVAL.replace(b'ob_start()',
        b'ob_start(...["chunk_size" => 2, "callback" => null])'),
    'final-retained-named-null': (HERE / 'output_executor_post_deactivate_named_ob08.php').read_bytes(),
    'final-retval-type-error': RETVAL.replace(b'echo ob_start() ? "RT|" : "RF|";',
        b'try { ob_start(42, []); } catch (TypeError $error) { echo $error->getMessage(), "|"; }'),
}
for name, call, kind, strict in (
    ('type-error', b'ob_start(null, [])', b'TypeError', False),
    ('count-error', b'ob_start(null, 0, 112, 4)', b'ArgumentCountError', False),
    ('strict-type-error', b'ob_start(null, "3")', b'TypeError', True),
    ('nonnull-type-error', b'ob_start(42, [])', b'TypeError', False),
):
    source = BASE.replace(b'echo ob_start(null) ? "T|" : "F|";',
        b'try { ' + call + b'; } catch (' + kind +
        b' $error) { echo $error->getMessage(), "|"; }')
    ORIGINALS[name] = source.replace(b'<?php\n', b'<?php\ndeclare(strict_types=1);\n') if strict else source
SLOW = [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one', b'USE_ZEND_ALLOC=0']
ORIGINALS['unpacked-options-slow'] = ORIGINALS['unpacked-named-options']
ORIGINALS['retval-options-slow'] = ORIGINALS['retval-unpacked-options']
ENVIRONMENTS = {'unpacked-options-slow': SLOW, 'retval-options-slow': SLOW}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-reception',
                                    Path(__file__), publish=False, model_seconds=120,
                                    request_environments=ENVIRONMENTS) else 1)
