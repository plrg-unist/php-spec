#!/usr/bin/env python3
"""Original-source include/require comparisons through a finite file snapshot."""
import base64
import errno
import hashlib
import json
import locale
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / 'tests/semantics/profile.json'
locale.setlocale(locale.LC_ALL, 'C')
STREAM_MISSING = os.strerror(errno.ENOENT).encode()
CASES = {
    'return7': (b"<?php echo include 'one.php';", {'one.php': b'<?php return 7;'}, ['one.php']),
    'fallthrough': (b"<?php echo include 'one.php';", {'one.php': b'<?php echo "C";'}, ['one.php']),
    'once-main': (b'<?php echo include_once __FILE__;', {}, ['__FILE__']),
    'missing-include': (b"<?php echo 'A'; echo include 'missing.php'; echo 'B';", {}, ['missing.php']),
    'missing-require': (b"<?php echo 'A'; try { require 'missing.php'; } catch (Error $e) { echo 'C'; }", {}, ['missing.php']),
    'nested': (b"<?php echo include 'one.php';", {'one.php': b"<?php echo 'C'; return include 'two.php';", 'two.php': b'<?php return 7;'}, ['one.php', 'two.php']),
    'parse-reject': (b"<?php try { include 'bad.php'; } catch (ParseError $e) { echo 'C'; } echo 'D';", {'bad.php': b'<?php echo ;'}, ['bad.php']),
    'compile-reject': (b"<?php try { include 'bad.php'; } catch (CompileError $e) { echo 'C'; } echo 'D';", {'bad.php': b'<?php class A { final abstract private function f(); }'}, ['bad.php']),
    'static-fatal': (b"<?php echo 'A'; try { include 'bad.php'; } catch (CompileError $e) { echo 'C'; } echo 'D';", {'bad.php': b'<?php echo 1; namespace N;'}, ['bad.php']),
    'once-bad-retry': (b"<?php try { include_once 'bad.php'; } catch (ParseError $e) { echo 'C'; } echo include_once 'bad.php';", {'bad.php': b'<?php echo ;'}, ['bad.php']),
    'ordinary-bad-twice': (b"<?php try { include 'bad.php'; } catch (ParseError $e) { echo 'C'; } try { include 'bad.php'; } catch (ParseError $e) { echo 'C'; }", {'bad.php': b'<?php echo ;'}, ['bad.php']),
    'uncaught-parse': (b"<?php include 'bad.php';", {'bad.php': b'<?php echo ;'}, ['bad.php']),
    'uncaught-compile': (b"<?php include 'bad.php';", {'bad.php': b'<?php class A { final abstract private function f(); }'}, ['bad.php']),
    'finally-return': (b"<?php try { echo include 'one.php'; } finally { echo 'F'; }", {'one.php': b'<?php return 7;'}, ['one.php']),
    'function-frame': (b"<?php function f() { return include 'one.php'; } echo f();", {'one.php': b'<?php return 7;'}, ['one.php']),
    'class-scope': (b"<?php class C { function f() { return include 'one.php'; } } echo (new C)->f();", {'one.php': b'<?php return self::class;'}, ['one.php']),
    'file-eval-file': (b"<?php echo include 'one.php';", {'one.php': b'''<?php function f(){ return eval('return include "two.php";'); } return f();''', 'two.php': b'<?php return 7;'}, ['one.php', 'two.php']),
    'ordinary-then-once': (b"<?php echo include 'one.php'; echo include_once 'one.php';", {'one.php': b"<?php echo 'X';"}, ['one.php']),
    'require-once-success-skip': (b"<?php echo require_once 'one.php'; echo require_once 'one.php';", {'one.php': b"<?php echo 'X'; return 7;"}, ['one.php']),
    'alias-once': (b"<?php echo include_once 'one.php'; echo include_once 'alias.php';", {'one.php': b"<?php echo 'X';"}, ['one.php', 'alias.php']),
    'recursive-once': (b"<?php echo include_once 'one.php';", {'one.php': b'<?php echo "X"; echo include_once __FILE__;'}, ['one.php', '__SELF_ONE__']),
    'once-compile-retry': (b"<?php try { include_once 'bad.php'; } catch (CompileError $e) { echo 'C'; } echo include_once 'bad.php';", {'bad.php': b'<?php class A { final abstract private function f(); }'}, ['bad.php']),
    'caller-variables': (b"<?php $x=3; include 'one.php'; echo $x;", {'one.php': b'<?php $x=7;'}, ['one.php']),
    'caller-receiver': (b"<?php class C { public $x=7; function f(){return include 'one.php';} } echo (new C)->f();", {'one.php': b'<?php return $this->x;'}, ['one.php']),
    'declaration-publication': (b"<?php include 'one.php'; echo f();", {'one.php': b'<?php function f(){return 7;}'}, ['one.php']),
    'own-namespace': (b"<?php echo include 'one.php';", {'one.php': b'<?php namespace N; return __NAMESPACE__;'}, ['one.php']),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree

def main():
    out = Path(tempfile.mkdtemp(prefix='include-execution-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
               ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
               ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php',
               ROOT / 'frontend/target.php', ROOT / 'frontend/SourcePrinter.php',
               ROOT / 'frontend/encoding.php', ROOT / 'frontend/wire.php',
               ROOT / 'spec/schema.json', ROOT / 'spec/php.watsup', ROOT / 'adapter/main.ml',
               ROOT / 'frontend/wire.py', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', PROFILE, Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    vendor_before = vendor_identity()
    profile = json.loads(PROFILE.read_text())
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    environment = os.environ.copy()
    environment['LC_ALL'] = 'C'
    records = []
    for name, (source, files, requested_paths) in CASES.items():
        directory = out / name
        directory.mkdir()
        main_path = directory / 'main.php'
        main_path.write_bytes(source)
        for filename, data in files.items():
            (directory / filename).write_bytes(data)
        if name == 'alias-once':
            (directory / 'alias.php').symlink_to('one.php')
        main_bytes = os.fsencode(main_path.resolve())
        entries = []
        for filename in requested_paths:
            caller = main_bytes if filename not in {'two.php', '__SELF_ONE__'} else os.fsencode((directory / 'one.php').resolve())
            if name == 'file-eval-file' and filename == 'two.php':
                caller += b"(1) : eval()'d code"
            requested = main_bytes if filename == '__FILE__' else (caller if filename == '__SELF_ONE__' else filename.encode())
            if filename == 'missing.php':
                fact = {'status': 'missing', 'stream_error': b64(STREAM_MISSING)}
            else:
                opened = main_path if filename == '__FILE__' else (directory / 'one.php' if filename == '__SELF_ONE__' else directory / filename)
                opened_bytes = os.fsencode(opened.resolve())
                fact = {'status': 'opened', 'resolved': b64(opened_bytes),
                        'opened': b64(opened_bytes), 'source': b64(opened.read_bytes())}
            entries.append({'caller': b64(caller), 'requested': b64(requested), **fact})
        snapshot = {'version': 1, 'main': b64(main_bytes),
                    'cwd': b64(os.fsencode(ROOT.resolve())),
                    'include_path': b64(b'.:'), 'entries': entries}
        snapshot_path = directory / 'snapshot.json'
        snapshot_path.write_text(json.dumps(snapshot, sort_keys=True) + '\n')
        model_command = [str(ROOT / 'bin/php-semantics'), str(main_path),
                         '--file-snapshot', str(snapshot_path), '--steps', '100000', '--timeout', '60']
        native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(main_path)]
        model = subprocess.run(model_command, cwd=ROOT, env=environment, capture_output=True, timeout=90)
        native = subprocess.run(native_command, cwd=ROOT, env=environment, capture_output=True, timeout=30)
        for label, result in [('model', model), ('native', native)]:
            (directory / (label + '.stdout')).write_bytes(result.stdout)
            (directory / (label + '.stderr')).write_bytes(result.stderr)
        try:
            outcome = json.loads(model.stdout)
            matching = (base64.b64decode(outcome.get('stdout', '')) == native.stdout
                        and base64.b64decode(outcome.get('stderr', '')) == native.stderr
                        and outcome.get('exit_status') == native.returncode
                        and outcome.get('status') in {'normal', 'php_error', 'static_rejection'})
        except (ValueError, KeyError):
            outcome = {}
            matching = False
        records.append({'case': name, 'result': 'pass' if matching else 'fail',
                        'source_sha256': digest(main_path), 'snapshot_sha256': digest(snapshot_path),
                        'children_sha256': {filename: digest(directory / filename) for filename in files},
                        'model_command': model_command, 'native_command': native_command,
                        'model_process_exit': model.returncode, 'native_exit': native.returncode,
                        'model_status': outcome.get('status'),
                        'model_stdout_sha256': digest(directory / 'model.stdout'),
                        'model_stderr_sha256': digest(directory / 'model.stderr'),
                        'native_stdout_sha256': digest(directory / 'native.stdout'),
                        'native_stderr_sha256': digest(directory / 'native.stderr')})
        print(name, matching, flush=True)
    after = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    assert before == after, 'watched inputs changed during source campaign'
    assert vendor_before == vendor_identity()
    passed = all(row['result'] == 'pass' for row in records)
    report = {'result': 'pass' if passed else 'fail', 'exact': sum(row['result'] == 'pass' for row in records),
              'total': len(records), 'inputs': before, 'vendor_parser_tree': vendor_before,
              'cwd': str(ROOT.resolve()), 'include_path': b64(b'.:'),
              'stream_error_fact': {'class': 'ENOENT', 'bytes': b64(STREAM_MISSING),
                                    'source': 'os.strerror(errno.ENOENT), fixed before native/model runs'},
              'locale': {'LC_ALL': 'C'},
              'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
