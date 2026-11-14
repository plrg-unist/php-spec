#!/usr/bin/env python3
"""Check raw ordered callable/array union producer headers against saved native originals."""
from pathlib import Path

import error_handler_run as recorder
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('cv_array_callable_producer_reference_notice_cases.json')
source.PREFIX = 'cv-array-callable-producer-reference-notice-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS, source.PROCESS_SECONDS = 180, 195
source.__doc__ = __doc__


def recorded(command, directory, stem, environment, cap):
    recorder.ROOT, recorder.ENV = source.ROOT, environment
    process = recorder.recorded(list(map(str, command)), directory / stem, cap)
    return dict(process, command=process['argv'])


source.recorded = recorded

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
