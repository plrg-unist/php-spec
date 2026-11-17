#!/usr/bin/env python3
"""Compare independent ordinary-CV ordered String/iterable-return originals with saved native observations."""
from pathlib import Path

import error_handler_run as recorder
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('cv_union_string_iterable_return_producer_reference_notice_review_cases.json')
source.PREFIX = 'cv-union-string-iterable-return-producer-reference-notice-review-source-'
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
