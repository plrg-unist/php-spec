#!/usr/bin/env python3
"""Independent positional reference variadics, repeated payloads and EXTRA owners."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('iterator_call_unpack_reference_positional_variadic_review_cases.json')
source.PREFIX = 'iterator-reference-positional-variadic-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
