#!/usr/bin/env python3
"""Check independent enum fronts using frozen sources and retained native bytes."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sources', type=Path, required=True,
                    help='frozen source packet containing case directories and native outputs')
parser.add_argument('--output', type=Path, required=True,
                    help='new directory for checked fixtures, raw streams and the report')
parser.add_argument('--cpu', type=int, required=True,
                    help='CPU already selected by taskset for this process and its children')
parser.add_argument('--case', action='append', required=True, choices=(
    'identity-alias', 'deferred-backing-priority', 'identity-alias-duplicate',
    'weak-parser-order', 'parsed-argument-trace'))
args = parser.parse_args()
SOURCES = args.sources.resolve()
OUT = args.output.resolve()
SELECTED = args.case
import enum_core_review_protocol as case_review
import enum_generated_review_protocol as generated_review
from recorded_worker import Worker
import static_types as types

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def folder(name):
    if name == 'identity-alias-duplicate':
        name = 'identity-alias'
    return SOURCES / name

def receipt(name, filename):
    direct = folder(name) / filename
    return direct if direct.exists() else folder(name).parent / filename

assert os.sched_getaffinity(0) == {args.cpu}
OUT.mkdir()
modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).splitlines()
paths = [Path(__file__), Path(generated_review.__file__), Path(case_review.__file__), ROOT / 'spec/semantics/modules.json',
         ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/static_types.py',
         ROOT / 'tests/semantics/profile.json', ROOT / 'frontend/worker.php',
         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
         ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
paths += [ROOT / p for p in changed if (ROOT / p).is_file()]
paths += [ROOT / 'spec/semantics/436-enum-compiler.watsup', ROOT / 'spec/semantics/437-enum-runtime.watsup']
paths += [folder(name) / p for name in SELECTED for p in ('main.php', 'native.stdout')]
paths += [receipt(name, p) for name in SELECTED for p in ('freeze.json', 'native-report.json')]
before = {str(p): sha(p) for p in paths}
report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'sources': str(SOURCES),
          'affinity': sorted(os.sched_getaffinity(0)), 'module_count': len(modules),
          'inputs': before, 'selected': SELECTED, 'records': [], 'result': 'fail'}
snapshots = OUT / 'tested-inputs'
snapshots.mkdir()
for p in [Path(__file__), Path(generated_review.__file__), Path(case_review.__file__), *(ROOT / p for p in changed),
          ROOT / 'spec/semantics/436-enum-compiler.watsup', ROOT / 'spec/semantics/437-enum-runtime.watsup']:
    if p.is_file():
        target = snapshots / (p.relative_to(ROOT) if p.is_relative_to(ROOT) else p.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(p.read_bytes())
frontend = adapter = None
try:
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], OUT / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], OUT / 'adapter')
    for name in SELECTED:
        review = generated_review if name in ('weak-parser-order', 'parsed-argument-trace') else case_review
        source = folder(name) / 'main.php'
        freeze = json.loads(receipt(name, 'freeze.json').read_text())
        if 'cases' in freeze:
            source_id = 'identity-alias' if name == 'identity-alias-duplicate' else name
            freeze, = [row for row in freeze['cases'] if row['id'] == source_id]
        assert sha(source) == freeze['source_sha256']
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        checks = (review.duplicate_assertions(checked['fixture'], source, (source.parent / 'native.stdout').read_bytes())
                  if name == 'identity-alias-duplicate' else
                  review.assertions(name, checked['fixture'], source, (source.parent / 'native.stdout').read_bytes()))
        target = OUT / name
        target.mkdir()
        (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (target / 'protocol.watsup').write_text(review.PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join(('  -- ' if x.startswith('PhpStep:') else '  -- if ') + x + '\n' for x in checks))
    adapter.close(); adapter = None
    frontend.close(); frontend = None
    for name in SELECTED:
        target = OUT / name
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                   *map(str, modules), str(target / 'protocol.watsup')]
        (target / 'command.json').write_text(json.dumps({'argv': command, 'cwd': str(ROOT), 'timeout': 180}) + '\n')
        start = time.monotonic()
        child = subprocess.Popen(command, cwd=ROOT, env=types.ENV, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, start_new_session=True)
        timeout = False
        try:
            stdout, stderr = child.communicate(timeout=180)
        except subprocess.TimeoutExpired:
            timeout = True
            os.killpg(child.pid, signal.SIGKILL)
            stdout, stderr = child.communicate()
        try:
            os.killpg(child.pid, 0)
            alive = True
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            alive = False
        (target / 'stdout').write_bytes(stdout)
        (target / 'stderr').write_bytes(stderr)
        passed = child.returncode == 0 and stdout == b'true\n' and not stderr and not timeout and not alive
        row = {'case': name, 'exit': child.returncode, 'timeout': timeout, 'group_alive_after': alive,
               'seconds': round(time.monotonic() - start, 3), 'passed': passed,
               'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0}
        (target / 'process.json').write_text(json.dumps(row, indent=2) + '\n')
        report['records'].append(row)
        print(json.dumps(row), flush=True)
        if not passed:
            break
    report['result'] = 'pass' if len(report['records']) == len(SELECTED) and all(x['passed'] for x in report['records']) else 'fail'
finally:
    try:
        if adapter:
            adapter.close()
    finally:
        if frontend:
            frontend.close()
    report['stable_inputs'] = before == {str(p): sha(p) for p in paths}
    if not report['stable_inputs']:
        report['result'] = 'fail'
    (OUT / 'check-report.json').write_text(json.dumps(report, indent=2) + '\n')
raise SystemExit(0 if report['result'] == 'pass' else 1)
