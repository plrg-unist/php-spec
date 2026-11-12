"""Compare grouped static sources, higher item indices, an INITIAL hole and singleton COW."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import error_handler_run as recorder

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('grouped_static_alias_stdclass_reference_notice_review_cases.json')
CASES = {row['id']: row['source'].encode() for row in json.loads(CATALOGUE.read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    row, = json.loads(CATALOGUE.read_bytes())
    source = Path(native['command'][-1])
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    runtime = digest(ROOT / '.tools/php/bin/php')
    assert native['mode'] == 'native-only' and native['passed']
    assert native['id'] == row['id'] and native['profile'] == profile
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == runtime
    assert runtime == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert source.read_bytes() == CASES[row['id']]
    assert digest(source) == native['source_sha256'] == row['source_sha256']
    assert native['exit'] == row['native_exit'] == 0
    assert source.with_name('native.stdout').read_bytes() == native['stdout'].encode() == row['native_stdout'].encode()
    assert source.with_name('native.stderr').read_bytes() == native['stderr'].encode() == row['native_stderr'].encode()
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    paths = modules + [ROOT / name for name in (
        'spec/semantics/modules.json', 'tests/semantics/profile.json', 'bin/php-semantics',
        '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/error_handler_run.py')]
    paths += [Path(__file__), CATALOGUE, provenance, source,
              source.with_name('native.stdout'), source.with_name('native.stderr')]
    fingerprints = lambda: {str(path): digest(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    out = args.output or Path(tempfile.mkdtemp(prefix='grouped-static-alias-stdclass-reference-review-source-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    print(out, flush=True)
    # The original native source filename and process cwd are preserved.
    recorder.ROOT = Path(native['cwd'])
    process = recorder.recorded([str(ROOT / 'bin/php-semantics'), str(source),
        '--steps', '100000', '--timeout', '180'], out / 'model', 195)
    try:
        outcome = json.loads((out / 'model.stdout').read_bytes())
    except ValueError:
        outcome = {}
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
              and not (out / 'model.stderr').read_bytes() and stable and head_stable
              and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
              and outcome.get('status') == 'normal' and outcome.get('exit_status') == 0
              and outcome.get('reason') is None
              and base64.b64decode(outcome.get('stdout', '')) == native['stdout'].encode()
              and base64.b64decode(outcome.get('stderr', '')) == native['stderr'].encode())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable,
        'module_count': len(modules), 'mode': 'SL/cache=false/det=true',
        'compiler': {'spectec_commit': 'da36ac3c434cd291940293a63da64544307730a3', 'ocaml': '5.1.0'},
        'profile': profile, 'runtime_sha256': runtime,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
        'native_provenance': str(provenance), 'native_reused': True,
        'source': str(source), 'source_sha256': row['source_sha256'], 'id': row['id'],
        'process': process, 'outcome': outcome, 'source_agreements': int(passed), 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(row['id'], passed, outcome.get('status'), flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
