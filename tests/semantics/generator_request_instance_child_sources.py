#!/usr/bin/env python3
"""Original fatal-report child throw with ordinary storage and Weak lifetimes."""
from pathlib import Path

import generator_request_render_handler_peer_sources as previous

driver = previous.driver
ORIGINAL = Path(__file__).with_name('generator-request-instance-child-original.php')
CASES = {
    'request-fatal-instance-child-throws': (ORIGINAL.read_bytes(), b'C|FHL1:1:1:1', 255),
}
FIRST_FATAL = (
    b'Fatal error: Uncaught RequestPinException21: handler in {file}:7\n'
    b'Stack trace:\n#0 [internal function]: requestPinHandler21(Object(Exception))\n'
    b'#1 {main}\n  thrown in {file} on line 7\n'
)
SECOND_FATAL = (
    b'Fatal error: Uncaught Exception: leaf in {file}:4\n'
    b'Stack trace:\n#0 [internal function]: RequestPinLeaf21->__destruct()\n'
    b'#1 {main}\n  thrown in {file} on line 4\n'
)
NATIVE_ERROR_PREFIXES = {name: FIRST_FATAL + SECOND_FATAL for name in CASES}
EXTRA_WATCHED = previous.EXTRA_WATCHED + [
    'spec/semantics/359-instance-storage-pin.watsup',
    'tests/semantics/generator-request-instance-child-original.php',
    'tests/semantics/generator_request_instance_child_sources.py',
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
