#!/usr/bin/env python3
"""Exact include-origin first-class method capture on the current file provider."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import tempfile

import static_types as types

ROOT = Path(__file__).resolve().parents[2]
MAIN = b"<?php\nrequire __DIR__ . '/include-first-class-lib.php';\n$callable = IncludedCapture::make();\necho $callable();\n"
LIB = (b'<?php\nclass IncludedCapture {\n'
       b"    private static function value(): string { return 'I'; }\n"
       b'    public static function make(): Closure { return self::value(...); }\n}\n')
MAIN_SHA = 'a87223af14c317ba9072207e03b6c1a95e2f900aac10d4fd1e6d7daba72c5ad4'
LIB_SHA = '679ef518ab7172928a84e4fdbd60f5bae84d19d1ffeb213bc7ff86a343c61d7e'
RAW_SHA = 'b91463b2a045000ae57b286d7227b6a610c42fb59ceffb03117a83f5c48a424a'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(value):
    return base64.b64encode(value).decode()


def run():
    assert hashlib.sha256(MAIN).hexdigest() == MAIN_SHA
    assert hashlib.sha256(LIB).hexdigest() == LIB_SHA
    before = types.syntax_validation.implementation_fingerprint()
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__),
               ROOT / 'bin/php-semantics', ROOT / 'tests/semantics/profile.json',
               ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so']
    direct = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='first-class-include-', dir=ROOT / '.tools'))
    main = out / 'main.php'
    lib = out / 'include-first-class-lib.php'
    main.write_bytes(MAIN)
    lib.write_bytes(LIB)
    main_bytes = os.fsencode(main.resolve())
    lib_bytes = os.fsencode(lib.resolve())
    snapshot = {'version': 1, 'main': b64(main_bytes),
                'cwd': b64(os.fsencode(ROOT.resolve())),
                'include_path': b64(b'.:'),
                'entries': [{'caller': b64(main_bytes), 'requested': b64(lib_bytes),
                             'status': 'opened', 'resolved': b64(lib_bytes),
                             'opened': b64(lib_bytes), 'source': b64(LIB)}]}
    snapshot_path = out / 'snapshot.json'
    snapshot_path.write_text(json.dumps(snapshot, sort_keys=True) + '\n')
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    environment = os.environ.copy()
    environment.update(LC_ALL='C', TZ='UTC')
    model = subprocess.run([str(ROOT / 'bin/php-semantics'), str(main),
                            '--file-snapshot', str(snapshot_path), '--steps', '100000',
                            '--timeout', '60'], cwd=ROOT, env=environment,
                           capture_output=True, timeout=90)
    native = subprocess.run([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(main)],
                            cwd=ROOT, env=environment, capture_output=True, timeout=30)
    (out / 'model.stdout').write_bytes(model.stdout)
    (out / 'model.stderr').write_bytes(model.stderr)
    (out / 'native.stdout').write_bytes(native.stdout)
    (out / 'native.stderr').write_bytes(native.stderr)
    actual = json.loads(model.stdout)
    passed = (model.returncode == 0 and not model.stderr and actual['status'] == 'normal'
              and actual['stdout'] == b64(native.stdout)
              and actual['stderr'] == b64(native.stderr)
              and actual['exit_status'] == native.returncode
              and native.stdout == b'I' and not native.stderr and native.returncode == 0)
    stable = (before == types.syntax_validation.implementation_fingerprint()
              and direct == {str(path.relative_to(ROOT)): digest(path) for path in watched})
    report = {'result': 'pass' if passed and stable else 'fail', 'stable': stable,
              'native_raw_archive_sha256': RAW_SHA, 'main_sha256': MAIN_SHA,
              'lib_sha256': LIB_SHA, 'snapshot_sha256': digest(snapshot_path),
              'fingerprint': before, 'direct_inputs': direct,
              'model': actual, 'native': {'stdout': b64(native.stdout),
                                         'stderr': b64(native.stderr),
                                         'exit_status': native.returncode}}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], flush=True)
    assert report['result'] == 'pass'


if __name__ == '__main__':
    run()
