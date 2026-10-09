#!/usr/bin/env python3
"""Fatal-release array child and an external shared-array owner control."""
from pathlib import Path

import generator_request_instance_child_sources as previous

driver = previous.driver
ORIGINAL = Path(__file__).with_name('generator-request-array-child-original.php')
SHARED = Path(__file__).with_name('generator-request-array-child-shared-original.php')
CASES = {
    'request-fatal-array-child-throws': (ORIGINAL.read_bytes(), b'C|FHL1:1:1:1', 255),
    'request-fatal-shared-array-child': (SHARED.read_bytes(), b'C|FH', 255),
}
FIRST_FATAL = previous.FIRST_FATAL.replace(b'RequestPinException21', b'RequestArrayPinException23').replace(b'requestPinHandler21', b'requestArrayPinHandler23')
SECOND_FATAL = previous.SECOND_FATAL.replace(b'RequestPinLeaf21', b'RequestArrayPinLeaf23')
NATIVE_ERROR_PREFIXES = {
    'request-fatal-array-child-throws': FIRST_FATAL + SECOND_FATAL,
    'request-fatal-shared-array-child': FIRST_FATAL,
}
EXTRA_WATCHED = previous.EXTRA_WATCHED + [
    'spec/semantics/36-arrays.watsup',
    'tests/semantics/generator-request-array-child-original.php',
    'tests/semantics/generator-request-array-child-shared-original.php',
    'tests/semantics/generator_request_array_child_sources.py',
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
