#!/usr/bin/env python3
"""Deep-array originals; execute native once and reuse its exact observations."""
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_sources as runner
import string_offset_nested_unset_bool_cv_deep_array_post_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    passed = runner.main()
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['scope'] = ('Fresh deep-array Unsupported baseline/source0' if '--baseline' in sys.argv else
                       'Production-SL deep-array postvalue originals with saved native observations')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
