#!/usr/bin/env python3
"""Original reference-cell child throw during fatal exception release."""
from pathlib import Path

import generator_request_instance_child_sources as previous

driver = previous.driver
ORIGINAL = Path(__file__).with_name('generator-request-reference-child-original.php')
CASES = {
    'request-fatal-reference-child-throws': (ORIGINAL.read_bytes(), b'C|FHL1:1:1:1', 255),
}
FIRST_FATAL = previous.FIRST_FATAL.replace(b'RequestPinException21', b'RequestRefPinException22').replace(b'requestPinHandler21', b'requestRefPinHandler22')
SECOND_FATAL = previous.SECOND_FATAL.replace(b'RequestPinLeaf21', b'RequestRefPinLeaf22')
NATIVE_ERROR_PREFIXES = {name: FIRST_FATAL + SECOND_FATAL for name in CASES}
EXTRA_WATCHED = previous.EXTRA_WATCHED + [
    'tests/semantics/generator-request-reference-child-original.php',
    'tests/semantics/generator_request_reference_child_sources.py',
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
