#!/usr/bin/env python3
"""Compare supplied FLOAT formals with raw INT defaults and separate existing controls."""
from pathlib import Path

import supplied_optional_int_default_producer_reference_notice_sources as implementation

source = implementation.source
source.CASES = Path(__file__).with_name('supplied_optional_float_int_default_producer_reference_notice_cases.json')
source.PREFIX = 'supplied-optional-float-int-default-reference-notice-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
