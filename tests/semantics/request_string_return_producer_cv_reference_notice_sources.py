#!/usr/bin/env python3
"""Compare request-string snapshots, cancellation and bounded nested arrays before Notices."""
from pathlib import Path

import error_handler_run as recorder
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('request_string_return_producer_cv_reference_notice_cases.json')
source.PREFIX = 'request-string-return-producer-cv-reference-notice-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 180
source.PROCESS_SECONDS = 195
source.__doc__ = __doc__


def recorded(command, directory, stem, environment, cap):
    recorder.ROOT = source.ROOT
    recorder.ENV = environment
    process = recorder.recorded(list(map(str, command)), directory / stem, cap)
    return dict(process, command=process['argv'])


source.recorded = recorded

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
