#!/usr/bin/env python3
"""Retained checked-source state mutations at the public call resume boundary.

The literal source contexts are semantic filename/argv facts; no fixture reads
those paths. Native/source agreement is tested separately by function_calls.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import static_types as types

ROOT = Path(__file__).resolve().parents[2]


def main(catalogue=None, campaign="function-call-protocol"):
    before = types.syntax_validation.implementation_fingerprint()
    if catalogue is None:
        catalogue = ROOT / 'tests/semantics/function_call_protocol_cases.json'
    cases = json.loads(catalogue.read_text())
    out = Path(tempfile.mkdtemp(prefix=campaign+'-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [*modules, runner, Path(__file__), catalogue]}
    (out / 'inputs.json').write_text(json.dumps({'closure': before, 'direct': inputs}, indent=2))
    for name in inputs:
        target = out / 'original-inputs' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    records = []
    print(out, flush=True)
    for name, case in cases.items():
        directory = out / name.replace('/', '-')
        directory.mkdir()
        fixture = directory / 'case.watsup'
        source = case['fixture']
        if not case.get('bool'):
            source = source.replace('$main', '$subject')
            source += '\ndec $main() : bool\ndef $main() = true\n  -- if S = $subject()\n'
            if case['completion'] in ('NORMAL',):
                source += '  -- if S.COMPLETION = NORMAL\n'
            elif case['completion'] == 'UNSUPPORTED':
                source += '  -- if S.COMPLETION = UNSUPPORTED text\n  -- if S.TODO = eps\n'
            elif case['completion'] == 'STATICERROR':
                source += '  -- if S.COMPLETION = STATICERROR text z\n'
            elif case['completion'] == 'THROWN':
                source += '  -- if S.COMPLETION = THROWN text n_message* z\n'
            else:
                raise AssertionError(case['completion'])
        fixture.write_text(source)
        command = [str(runner), *map(str, modules), str(fixture)]
        (directory / 'command.json').write_text(json.dumps(command))
        try:
            result = subprocess.run(command, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired as error:
            (directory / 'stdout').write_bytes(error.stdout or b'')
            (directory / 'stderr').write_bytes(error.stderr or b'')
            (directory / 'status.json').write_text(json.dumps({'status': 'timeout', 'seconds': 300}))
            raise
        (directory / 'stdout').write_bytes(result.stdout)
        (directory / 'stderr').write_bytes(result.stderr)
        (directory / 'status.json').write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
        row = {'id': name, 'pass': result.returncode == 0 and result.stdout.strip() == b'true' and not result.stderr,
               'original_fixture_sha256': case['original_sha256']}
        records.append(row)
        (out / 'results.json').write_text(json.dumps(records, indent=2))
        print(name, row['pass'], flush=True)
        assert row['pass'], result
    assert before == types.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'inputs': inputs, 'raw': str(out), 'cases': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    (ROOT / 'coverage/semantics' / (campaign+'.json')).write_text(json.dumps(report, indent=2))
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
