#!/usr/bin/env python3
"""Boolean-CV originals reuse native probes; owning post-Warning states stay visible."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_sources as runner
import string_offset_nested_unset_bool_cv_warning_cases as cases

if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    runner.cases = cases
    runner.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'][str(own.relative_to(runner.ROOT))] = before
    for row in report['rows']:
        source = Path(row['native']['argv'][-1])
        row['native_stdout'] = str(source.with_name('native.stdout'))
        row['native_stderr'] = str(source.with_name('native.stderr'))
        row['category'] = ('expected-unsupported' if row['id'] in cases.UNSUPPORTED else
                           'quiet-delayed-read-control' if row['id'] == cases.QUIET_CONTROL else
                           'Boolean-CV-Warning')
        if row['id'] in cases.UNSUPPORTED:
            native, model, outcome = row['native'], row['model'], row['outcome']
            row['passed'] = (native['exit'] == 0 and not native['timeout'] and native['interruption'] is None
                and not native['group_after'] and source.with_name('native.stdout').read_bytes() == cases.OUTPUTS[row['id']]
                and not source.with_name('native.stderr').read_bytes() and model['exit'] == 1
                and not model['timeout'] and model['interruption'] is None and not model['group_after']
                and not (output.parent / row['id'] / 'model.stderr').read_bytes()
                and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
                and outcome.get('status') == 'unsupported' and outcome.get('reason') == 'post-warning Boolean CV conversion'
                and base64.b64decode(outcome['stdout']) == b'H:2:String offset cast occurred;'
                and not base64.b64decode(outcome['stderr']))
            row['agreement_credit'] = 0
    report['scope'] = ('Three Boolean-CV Warning originals, one quiet final-int delayed-read control, '
                       'and two owning post-Warning Unsupported controls with zero agreement credit.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if all(row['passed'] for row in report['rows']) else 1)
