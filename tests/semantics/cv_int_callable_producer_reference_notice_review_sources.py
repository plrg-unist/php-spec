"""Compare ordered callable/int union headers, quiet numeric-string reception and strict receive/return priority with saved originals."""
from pathlib import Path

import error_handler_run as recorder
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('cv_int_callable_producer_reference_notice_review_cases.json')
source.IMPLEMENTATION = Path(__file__)
source.PREFIX = 'cv-int-callable-producer-reference-review-source-'
source.MODEL_SECONDS, source.PROCESS_SECONDS = 180, 195


def recorded(command, directory, stem, environment, cap):
    recorder.ROOT, recorder.ENV = source.ROOT, environment
    process = recorder.recorded(list(map(str, command)), directory / stem, cap)
    return dict(process, command=process['argv'])


source.recorded = recorded

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
