#!/usr/bin/env python3
"""Native-first file registration at recorded compiler-diagnostic boundaries."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import static_types as types
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
b64 = lambda data: base64.b64encode(data).decode()
CHILD = b"<?php\nuse Foo;\necho 'B|';return 7;\n"


def cases():
    rows = {}
    for kind in ['include', 'require', 'include_once', 'require_once']:
        prefix = "<?php\n$calls=0;$held=new Exception('held');\n"
        suffix = "restore_error_handler();echo 'after:',include_once __DIR__.'/unit.php','|calls:',$calls;\n"
        nested = "function notice($level,$message,$file,$line){global $calls,$held;++$calls;echo 'H:',$level,'|';echo 'inner:',include_once __DIR__.'/unit.php','|';return true;}\n"
        throwing = "function notice($level,$message,$file,$line){global $calls,$held;++$calls;echo 'H:',$level,'|';throw $held;}\n"
        entry = "set_error_handler('notice');\ntry{$v=" + kind + " __DIR__.'/unit.php';echo 'outer:',$v,'|';}catch(Exception $e){echo $e===$held?'same|':'BAD|';}\n"
        inner = '1' if kind.endswith('_once') else 'B|7'
        rows[kind + '-nested'] = (prefix + nested + entry + suffix, CHILD,
                                  'H:2|inner:' + inner + '|B|outer:7|after:1|calls:1', 0, 'normal')
        rows[kind + '-throw'] = (prefix + throwing + entry + suffix, CHILD,
                                 'H:2|same|after:1|calls:1', 0, 'normal')
        shutdown = "function finish(){echo 'S|',include_once __DIR__.'/unit.php','|';}\nregister_shutdown_function('finish');\n"
        exiting = "function notice($level,$message,$file,$line){echo 'H:',$level,'|';exit(7);}\n"
        fatal = "function notice($level,$message,$file,$line){echo 'H:',$level,'|';trigger_error('stop',256);}\n"
        tail = "set_error_handler('notice');echo 'A|';" + kind + " __DIR__.'/unit.php';echo 'BAD';\n"
        rows[kind + '-exit'] = (prefix + shutdown + exiting + tail, CHILD,
                                'A|H:2|S|1|', 7, 'explicit_exit')
        body = '1' if kind.endswith('_once') else 'B|7'
        rows[kind + '-fatal'] = (prefix + shutdown + fatal + tail, CHILD,
                                 'A|H:2|S|' + body + '|', 255, 'php_error')
    main, _, _, code, status = rows['include-nested']
    rows['include-repeated'] = (main, CHILD.replace(b'use Foo;', b'use Foo;\nuse Bar;'),
        'H:2|inner:B|7|H:2|inner:1|B|outer:7|after:1|calls:2', code, status)
    main, _, expected, code, status = rows['include-throw']
    rows['include-throw-repeated'] = (main, CHILD.replace(b'use Foo;', b'use Foo;\ndeclare(unknown=1);\nuse Bar;'),
                                     expected, code, status)
    main, _, expected, code, status = rows['include-exit']
    rows['include-exit-repeated'] = (main, CHILD.replace(b'use Foo;', b'use Foo;\ndeclare(unknown=1);\nuse Bar;'),
                                    expected, code, status)
    rows['body-once'] = ("<?php echo include __DIR__.'/unit.php';echo '|',include_once __DIR__.'/unit.php';\n",
        b"<?php echo 'B|',include_once __FILE__,'|';return 7;\n", 'B|1|7|1', 0, 'normal')
    main, child, _, code, status = rows['include-nested']
    rows['include-return'] = (main.replace("echo 'inner:',include_once __DIR__.'/unit.php','|';", ''),
        child, 'H:2|B|outer:7|after:1|calls:1', code, status)
    return rows


def inputs():
    paths = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths += [ROOT / name for name in ['spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json',
        'adapter/main.ml', '_build/default/adapter/main.exe', 'bin/php-semantics', '.tools/php/bin/php',
        '.tools/php-file.so', 'frontend/worker.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php',
        'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json',
        'tests/semantics/static_types.py', 'tests/semantics/typed_static_invoke_set_protocol.py', Path(__file__).relative_to(ROOT)]]
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def snapshot(directory):
    main = directory / 'main.php'
    child = directory / 'unit.php'
    entries = []
    for caller, requested in [(main, child), (child, child)]:
        entries.append({'caller': b64(os.fsencode(caller)), 'requested': b64(os.fsencode(requested)),
            'cwd': b64(os.fsencode(directory)), 'include_path': b64(b'.:'), 'status': 'opened',
            'resolved': b64(os.fsencode(child)), 'opened': b64(os.fsencode(child)), 'source': b64(child.read_bytes())})
    path = directory / 'snapshot.json'
    path.write_text(json.dumps({'version': 2, 'main': b64(os.fsencode(main)), 'cwd': b64(os.fsencode(directory)),
        'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': entries}, indent=2) + '\n')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['native', 'model'], required=True)
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    assert args.attempt > 0
    run_label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    selection = {name: row for name, row in cases().items() if not args.case or name in args.case}
    assert selection and set(args.case) <= selection.keys(), 'unknown or empty selection'
    out = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='file-notice-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    print(out, flush=True)
    before = inputs()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(
                  ['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(), 'records': [], 'result': 'fail'}
    if args.phase == 'native':
        runtime = process([str(types.PHP), '-n', *types.FLAGS, '-r',
            'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,get_loaded_extensions(),ini_get_all(null,false)]);'],
            out / ('runtime' if args.attempt == 1 else 'runtime-' + str(args.attempt)), 10, ROOT)
        identity = json.loads(runtime.stdout)
        assert runtime.returncode == 0 and not runtime.stderr and identity[:4] == ['8.5.10', 'cli', 8, False]
        assert all(identity[5][key] == value for key, value in types.PROFILE.items())
        report['runtime'] = identity
    try:
        for name, (source, child, expected, exit_status, status) in selection.items():
            directory = out / name
            if args.phase == 'native':
                directory.mkdir()
                (directory / 'main.php').write_bytes(source.encode())
                (directory / 'unit.php').write_bytes(child)
                snapshot(directory)
                result = process([str(types.PHP), '-n', *types.FLAGS, str(directory / 'main.php')],
                                 directory / 'native', 30, directory)
                passed = result.returncode == exit_status and result.stdout == expected.encode()
                actual = None
            else:
                assert (directory / 'main.php').read_bytes() == source.encode()
                assert (directory / 'unit.php').read_bytes() == child
                native = directory / 'native'
                assert json.loads((native / 'process.json').read_text())['exit_status'] == exit_status
                assert (native / 'stdout').read_bytes() == expected.encode()
                result = process([str(ROOT / 'bin/php-semantics'), str(directory / 'main.php'),
                    '--file-snapshot', str(directory / 'snapshot.json'), '--steps', '100000', '--timeout', '60'],
                    directory / run_label, 90, directory)
                actual = json.loads(result.stdout)
                passed = (result.returncode == 0 and not result.stderr and actual.get('frontend') == 'accepted'
                    and actual.get('checked') == 'program' and actual.get('status') == status
                    and actual.get('exit_status') == exit_status
                    and actual.get('stdout') == b64((native / 'stdout').read_bytes())
                    and actual.get('stderr') == b64((native / 'stderr').read_bytes()))
            row = {'id': name, 'pass': passed, 'expected_status': status, 'actual': actual,
                   'source_sha256': hashlib.sha256((directory / 'main.php').read_bytes()).hexdigest(),
                   'child_sha256': hashlib.sha256(child).hexdigest(),
                   'snapshot_sha256': hashlib.sha256((directory / 'snapshot.json').read_bytes()).hexdigest()}
            report['records'].append(row)
            print(name, passed, flush=True)
            if not passed:
                break
        report['result'] = 'pass' if all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == inputs()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (run_label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
