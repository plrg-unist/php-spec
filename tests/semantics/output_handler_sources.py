#!/usr/bin/env python3
"""Chunk0 explicit user output handlers: native-first original-byte checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
FLAGS = [arg for key, value in PROFILE.items() for arg in ('-d', key + '=' + value)]
CASES = {
    'phase-sequence': (b'<?php $log=""; function h($b,$p){global $log;$log.=$p.";";return $p.":".$b;} ob_start("h");echo "A";ob_flush();echo "B";ob_clean();echo "C";ob_end_flush();echo $log;', b'5:A8:C5;2;8;'),
    'first-clean': (b'<?php $log="";function h($b,$p){global $log;$log.=$p.";";return $p.$b;}ob_start("h");echo "A";ob_clean();echo "B";ob_flush();ob_end_flush();echo "|".$log;', b'4B8|3;4;8;'),
    'get-clean-snapshot': (b'<?php $log="";function h($b,$p){global $log;$log=$p;return "X".$b;}ob_start("h");echo "A";$v=ob_get_clean();echo $v.":".$log;', b'A:11'),
    'scalar-results': (b'<?php $v=true;$n=0;function h($b,$p){global $v,$n;$n=$n+1;return $v;}ob_start("h");echo "A";ob_end_flush();$v=null;ob_start("h");echo "B";ob_end_flush();$v=42;ob_start("h");echo "C";ob_end_flush();$v="Q\\0R";ob_start("h");echo "D";ob_end_flush();echo ":".$n;', b'42Q\x00R:4'),
    'false-disable': (b'<?php $n=0;function h($b,$p){global $n;$n=$n+1;return false;}ob_start("h");echo "A";ob_flush();echo "B";ob_clean();$s=ob_get_status();ob_end_flush();echo ":".$n.":".$s["flags"].":".$s["buffer_used"];', b'AB:1:12401:0'),
    'empty-calls': (b'<?php $log="";function h($b,$p){global $log;$log.=$p.";";return "E".$p;}ob_start("h");ob_end_flush();ob_start("h");ob_flush();ob_end_clean();echo ":".$log;', b'E9E5:9;5;10;'),
    'nested-users': (b'<?php function i($b,$p){return "I".$b;}function o($b,$p){return "O".$b;}ob_start("o");ob_start("i");echo "A";ob_flush();echo "B";ob_end_flush();ob_end_flush();', b'OIAIB'),
    'lower-default-chunk': (b'<?php function h($b,$p){return $b."X";}ob_start(null,3);ob_start("h");echo "A";ob_end_flush();echo "B";$s=ob_get_status();ob_end_flush();echo $s["flags"].":".$s["buffer_used"];', b'AXB20592:0'),
    'callable-name-spelling': (b'<?php function Handler($b,$p){return $b;}class C{static function H($b,$p){return $b;}}ob_start("hAnDlEr");$a=ob_get_status();$l=ob_list_handlers();ob_end_clean();ob_start(["c","h"]);$s=ob_get_status();ob_end_clean();echo $a["name"].":".$l[0].":".$s["name"].":".$s["type"];', b'hAnDlEr:hAnDlEr:c::h:1'),
    'invokable-handler': (b'<?php class C{function __invoke($b,$p){return "X".$b;}}$c=new C;ob_start($c);echo "A";$s=ob_get_status();ob_end_flush();echo ":".$s["name"].":".$s["type"];', b'XA:C::__invoke:1'),
    'closure-handler': (b'<?php $prefix="C";$cb=function($b,$p)use($prefix){return $prefix.$b;};ob_start($cb);echo "A";ob_end_flush();echo "Z";', b'CAZ'),
    'negative-chunk-wide-flags': (b'<?php function h($b,$p){return $p.$b;}ob_start("h",-2,4294967408);$s=ob_get_status();echo "A";ob_end_flush();echo ":".$s["flags"].":".$s["chunk_size"];', b'9A:113:0'),
    'named-unpack-selection': (b'<?php function h($b,$p){return $p.$b;}ob_start(flags:112,callback:"h",chunk_size:0);echo "N";ob_end_flush();$f="ob_start";$f(...["callback"=>"h","chunk_size"=>0]);echo "U";ob_end_flush();', b'9N9U'),
    'produced-api-lines': (b'<?php\nfunction h($b,$p){echo "H";return $b;}\nob_start("h");\necho "A";\nob_flush();\nob_end_clean();', b'A'),
    'lower-default-running-threshold': (b'<?php $seen="";function h($b,$p){echo "H";return "X".$b;}function eh($n,$m){global $seen;echo "E";$a=ob_get_status(true);$seen=$a[0]["buffer_used"].":".$a[0]["flags"];return true;}set_error_handler("eh");ob_start(null,1);ob_start("h");echo "A";ob_end_flush();$s=ob_get_status();ob_end_clean();echo "|".$seen."|".$s["buffer_used"].":".$s["flags"];', b'EXA|1:32880|0:53360'),
    'default-none-routing': (b'<?php ob_start();echo "A";ob_start(null,3);echo "BCD";ob_end_flush();$s=ob_get_clean();echo $s;', b'ABCD'),
}
CONTROLS = {
    'invalid-callback': b'<?php echo "P";ob_start("");echo "Z";',
    'builtin-callback': b'<?php echo "P";ob_start("strlen");echo "A";ob_end_flush();',
    'callback-throw': b'<?php echo "P";function h($b,$p){throw new Exception("E");}ob_start("h");echo "A";ob_end_flush();',
    'callback-exit': b'<?php echo "P";function h($b,$p){exit("E");}ob_start("h");echo "A";ob_end_flush();',
    'handler-fiber-switch': b'<?php echo "P";function h($b,$p){$f=new Fiber(function(){});$f->start();return $b;}ob_start("h");echo "A";ob_end_flush();',
}
CONTROL_REASONS = {
    'invalid-callback': 'invalid output-handler Warning and Notice',
    'builtin-callback': 'user output-handler outside admitted callable forms',
    'callback-throw': 'abrupt user output-handler callback cleanup',
    'callback-exit': 'abrupt user output-handler callback cleanup',
    'handler-fiber-switch': 'Fiber switching from a user output handler',
}
CONTROL_PREFIX = {}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules,
             'adapter/main.ml', 'bin/php-semantics', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe',
             'vendor/php-src/main/output.c', 'vendor/php-src/main/php_output.h',
             'vendor/php-src/Zend/zend_API.c',
             'tests/semantics/profile.json', 'tests/semantics/output_handler_sources.py']
    return {name: sha(ROOT / name) for name in names}


def run(argv, directory, name, timeout):
    environment = {'LC_ALL': 'C', 'TZ': 'UTC', 'PATH': '/usr/bin:/bin'}
    (directory / (name + '.command.json')).write_text(json.dumps(
        {'argv': argv, 'cwd': str(directory), 'env': environment}) + '\n')
    result = subprocess.run(argv, cwd=directory, env=environment,
                            capture_output=True, timeout=timeout)
    for channel, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (directory / (name + '.' + channel)).write_bytes(raw)
    (directory / (name + '.exit')).write_text(str(result.returncode) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES) + list(CONTROLS)
    assert selected and len(set(selected)) == len(selected)
    assert all(name in CASES or name in CONTROLS for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-handler-sources-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': PROFILE, 'selected': selected, 'records': [],
              'completed': False, 'passed': False}
    print(out, flush=True)
    try:
        for name in selected:
            source = CASES[name][0] if name in CASES else CONTROLS[name]
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(source)
            native = run([str(ROOT / '.tools/php/bin/php'), '-n', *FLAGS, str(path)], directory, 'native', 10)
            if name in CASES:
                assert native.stdout == CASES[name][1], (name, native.stdout, CASES[name][1])
                assert native.returncode == 0, (name, native.returncode, native.stderr)
            modeled = run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '60'], directory, 'model', 90)
            assert not modeled.stderr, (name, modeled.stdout, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            if name in CASES:
                status = 'normal'
                assert modeled.returncode == 0 and outcome['status'] == status, (name, outcome)
                assert outcome['reason'] is None
                assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
                assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
                assert outcome['exit_status'] == native.returncode
            else:
                assert modeled.returncode == 1 and outcome['status'] == 'unsupported', (name, outcome)
                assert base64.b64decode(outcome['stdout'], validate=True) == CONTROL_PREFIX.get(name, b'P'), (name, outcome)
                assert base64.b64decode(outcome['stderr'], validate=True) == b'', (name, outcome)
                assert CONTROL_REASONS[name] in outcome['reason'], (name, outcome)
            report['records'].append({'case': name, 'source_sha256': sha(path), 'status': outcome['status'],
                                      'native_credit': name in CASES, 'native_exit': native.returncode,
                                      'stdout_sha256': hashlib.sha256(native.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest()})
            print(name, outcome['status'], flush=True)
        report.update(completed=True, passed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
