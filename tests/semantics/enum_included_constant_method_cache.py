#!/usr/bin/env python3
"""Original included-global method captures through the finite file provider."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_suffix('')
HASHES = {
    'main.php': '74fa388acd47a9eed08527d8f15c7d2bb43bbe505fa7c188c9ee2b7e0a00735a',
    'cold.php': '234d491032e736990b83286f6efe2b1ffebc92b98572f12446dfdc29175cd911',
    'warm.php': '12b450369cba651f0e0bf4d987482d96a01c0a83d1ddcdf7258141efcb0ebbbe',
}
EXPECTED = ('cold-enter|cold-ready|raw|query:1:IncludedConstantMethodCache142\\Target::cases|'
            'warm-enter|warm-ready|cold|query:1:IncludedConstantMethodCache142\\Target::cases|'
            'private-copy|query:1:IncludedConstantMethodCache142\\Target::cases|'
            'cold-again|query:1:IncludedConstantMethodCache142\\Target::cases|'
            'warm|query:1:IncludedConstantMethodCache142\\Target::cases|fresh|USER:OLD|'
            'query:0:OLD|shared-copy|query:1:IncludedConstantMethodCache142\\Target::cases|'
            'retire|held|query:1:IncludedConstantMethodCache142\\Target::cases|'
            'source-gone|fresh-gone|shared-gone|done|').encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def main():
    assert all(sha(SOURCES / name) == digest for name, digest in HASHES.items())
    out = Path(tempfile.mkdtemp(prefix='enum-included-constant-cache-', dir=ROOT / '.tools'))
    source = SOURCES / 'main.php'
    snapshot = {'version': 1, 'main': b64(os.fsencode(source)),
                'cwd': b64(os.fsencode(SOURCES)), 'include_path': b64(b'.:'),
                'entries': [{'caller': b64(os.fsencode(source)), 'requested': b64(name.encode()),
                             'status': 'opened', 'resolved': b64(os.fsencode(SOURCES / name)),
                             'opened': b64(os.fsencode(SOURCES / name)),
                             'source': b64((SOURCES / name).read_bytes())}
                            for name in ('cold.php', 'warm.php')]}
    snapshot_path = out / 'snapshot.json'
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + '\n')
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    profile['include_path'] = '.:'
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__),
               ROOT / 'bin/php-semantics', ROOT / 'tests/semantics/profile.json',
               ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
               ROOT / '_build/default/adapter/main.exe', snapshot_path,
               *[SOURCES / name for name in HASHES]]
    before = {str(path): sha(path) for path in watched}
    environment = dict(os.environ, LC_ALL='C', LANG='C', TZ='UTC')
    native_argv = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
    model_argv = [str(ROOT / 'bin/php-semantics'), str(source), '--file-snapshot',
                  str(snapshot_path), '--steps', '100000', '--timeout', '240']
    native = subprocess.run(native_argv, cwd=SOURCES, env=environment,
                            capture_output=True, timeout=45)
    (out / 'native.stdout').write_bytes(native.stdout)
    (out / 'native.stderr').write_bytes(native.stderr)
    started = time.monotonic()
    model = subprocess.run(model_argv, cwd=SOURCES, env=environment,
                           capture_output=True, timeout=250)
    (out / 'model.stdout').write_bytes(model.stdout)
    (out / 'model.stderr').write_bytes(model.stderr)
    actual = json.loads(model.stdout)
    stable = before == {str(path): sha(path) for path in watched}
    passed = (stable and model.returncode == 0 and not model.stderr
              and actual['status'] == 'normal' and actual['stdout'] == b64(native.stdout)
              and actual['stderr'] == b64(native.stderr) and actual['exit_status'] == native.returncode
              and native.returncode == 0 and not native.stderr and native.stdout == EXPECTED)
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'native_argv': native_argv, 'model_argv': model_argv, 'cwd': str(SOURCES),
              'environment': {key: environment[key] for key in ('LC_ALL', 'LANG', 'TZ')},
              'profile': profile, 'direct_inputs': before, 'modules': len(modules), 'stable': stable,
              'native_exit': native.returncode, 'model_exit': model.returncode,
              'model_status': actual.get('status'), 'model_reason': actual.get('reason'),
              'model_elapsed': time.monotonic() - started, 'pass': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'pass' if passed else 'fail', flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
