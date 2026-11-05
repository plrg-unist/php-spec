#!/usr/bin/env python3
"""A returned Notice object exposes the ob_end_clean builtin trace frame."""
from pathlib import Path

import function_scope as scope
from output_executor_notice_retval_throw_sources import ORIGINALS

OLD_CALL = b'echo ob_start() ? "DT|" : "DF|";'
OLD_CATCH = b'catch (Throwable $error) { echo "C:", $error->getMessage(), "|"; }'
NEW_CATCH = b'catch (Throwable $error) { foreach ($error->getTrace() as $frame) { echo $frame["function"], "/"; } echo "C:", $error->getMessage(), "|"; }'
source = ORIGINALS['noarg']
assert source.count(OLD_CALL) == 1 and source.count(OLD_CATCH) == 1
source = source.replace(OLD_CALL, b'echo ob_end_clean() ? "DT|" : "DF|";').replace(OLD_CATCH, NEW_CATCH)
ORIGINALS = {'ob-end-clean-return-throw-trace': source}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(ORIGINALS, 'output-executor-notice-retval-throw-offkind',
                                    Path(__file__), publish=False, model_seconds=120) else 1)
