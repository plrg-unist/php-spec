#!/usr/bin/env python3
"""NULL-CV original sources retain one native run and explicit prelaw mismatches."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_sources as runner
import string_offset_nested_unset_null_cv_warning_cases as cases

if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    baseline = '--baseline' in sys.argv
    if baseline:
        sys.argv.remove('--baseline')
    runner.cases = cases
    passed = runner.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'][str(own.relative_to(runner.ROOT))] = before
    for row in report['rows']:
        source = Path(row['native']['argv'][-1])
        row['native_stdout'] = str(source.with_name('native.stdout'))
        row['native_stderr'] = str(source.with_name('native.stderr'))
        if baseline:
            native, model, outcome = row['native'], row['model'], row['outcome']
            row['baseline_asserted'] = (
                native['exit'] == model['exit'] == 0 and outcome['status'] == 'normal'
                and outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
                and all(not proc['timeout'] and proc['interruption'] is None and not proc['group_after']
                        for proc in (native, model))
                and source.with_name('native.stdout').read_bytes() == cases.OUTPUTS[row['id']]
                and not source.with_name('native.stderr').read_bytes()
                and not (output.parent / row['id'] / 'model.stderr').read_bytes()
                and base64.b64decode(outcome['stdout']) != cases.OUTPUTS[row['id']]
                and not base64.b64decode(outcome['stderr']))
            row['classification'] = 'normal-mismatch' if row['baseline_asserted'] else 'unclassified'
            row['agreement_credit'] = 0
    if baseline:
        report['scope'] = 'Prelaw NORMAL/missing-H mismatch originals; all agreement credit0'
        passed = all(row['baseline_asserted'] for row in report['rows'])
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
