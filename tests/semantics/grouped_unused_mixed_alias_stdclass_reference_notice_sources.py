#!/usr/bin/env python3
"""Compare static-only sources with grouped unused instance declarations through a returned-value reference Notice."""
from pathlib import Path
import error_handler_run as recorder
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('grouped_unused_mixed_alias_stdclass_reference_notice_cases.json')
source.PREFIX = 'grouped-unused-mixed-alias-stdclass-reference-notice-source-'
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
