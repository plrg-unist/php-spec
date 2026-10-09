#!/usr/bin/env python3
"""Fatal-release array reference child and a genuine global reference owner."""
from pathlib import Path

import generator_request_instance_child_sources as previous

driver = previous.driver
ORIGINAL = Path(__file__).with_name('generator-request-array-reference-child-original.php')
GLOBAL = Path(__file__).with_name('generator-request-array-reference-child-global-original.php')
CASES = {
    'request-fatal-array-reference-child-throws': (ORIGINAL.read_bytes(), b'C|FHL1:1:1:1', 255),
    'request-fatal-global-reference-array-child': (GLOBAL.read_bytes(), b'C|FH', 255),
}
FIRST_FATAL = previous.FIRST_FATAL.replace(b'RequestPinException21', b'RequestArrayRefPinException24').replace(b'requestPinHandler21', b'requestArrayRefPinHandler24')
SECOND_FATAL = previous.SECOND_FATAL.replace(b'RequestPinLeaf21', b'RequestArrayRefPinLeaf24')
NATIVE_ERROR_PREFIXES = {
    'request-fatal-array-reference-child-throws': FIRST_FATAL + SECOND_FATAL,
    'request-fatal-global-reference-array-child': FIRST_FATAL,
}
EXTRA_WATCHED = previous.EXTRA_WATCHED + [
    '.tools/php-file.so',
    'spec/semantics/36-arrays.watsup',
    'spec/semantics/37-array-locations.watsup',
    'spec/semantics/76-globals.watsup',
    'spec/semantics/81-global-frames.watsup',
    'tests/semantics/generator-request-array-reference-child-original.php',
    'tests/semantics/generator-request-array-reference-child-global-original.php',
    'tests/semantics/generator_request_array_reference_child_sources.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.EXPECTED_STATUSES = {name: 'php_error' for name in CASES}
    driver.NATIVE_ERROR_PREFIXES = NATIVE_ERROR_PREFIXES
    driver.WATCHED += EXTRA_WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
