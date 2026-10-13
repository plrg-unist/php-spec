#!/usr/bin/env python3
"""Automatic positive chunks: original native/model bytes, phases and continuations."""
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
CASES = {'whole-buffer-phases': (b'<?php $log="";function h($b,$p){global $log;$log.=$p.":".$b.";";return "X".$b;}ob_start("h",3);echo "abcdef";echo "gh";ob_end_flush();echo "|".$log;', b'XabcdefXgh|1:abcdef;8:gh;'),
 'source-file-line-trace': (b'<?php\n$log="";\nfunction h($b,$p){global $log;$e=new Exception;$a=$e->getTrace();$log.=(isset($a[0]["file"])&&$a[0]["file"]===__FILE__?"F":"-").":".($a[0]["line"]??0).":".$a[0]["functio'
                            b'n"].":".($a[1]["function"]??"-").";";return $b;}\nob_start("h",1);\necho "A";\nob_end_clean();\necho "|".$log;',
                            b'A|F:5:h:-;-:0:h:ob_end_clean;'),
 'print-inline-continuation': (b'<?php\n$log="";function h($b,$p){global $log;$e=new Exception;$a=$e->getTrace();$log.=$b.":".($a[0]["line"]??0).";";return $b;}\nob_start("h",1);\n$x=print "P";\n?>H<?php ob_end_clean('
                               b');echo "|".$x.":".$log;',
                               b'PH|1:P:4;H:5;:0;'),
 'weak-typed-false-disable': (b'<?php $log="";function h(int $b,int $p){global $log;$log="I".$b.":".$p;return false;}ob_start("h",1);echo "7";ob_end_clean();echo "|".$log;', b'7|I7:1'),
 'false-live-forwarding': (b'<?php $log="";set_error_handler(function($n,$m){global $log;$log=$m;return true;});function h($b,$p){echo "H";return false;}ob_start("h",1);echo "A";echo "B";ob_end_clean();echo "|".$log;',
                           b'AHB|main(): Producing output from user output handler h is deprecated'),
 'lower-user-cascade': (b'<?php $log="";function i($b,$p){global $log;$log.="i".$p.";";return "I".$b;}function o($b,$p){global $log;$log.="o".$p.";";return "O".$b;}ob_start("o",2);ob_start("i",1);echo "A";ob_end_clean('
                        b');ob_end_clean();echo "|".$log;',
                        b'OIA|i1;o1;i10;o10;'),
 'produced-source-and-api-lines': (b'<?php\n$log="";function h($b,$p){echo "H";return "X".$b;}\nset_error_handler(function($n,$m,$f,$l){global $log;$log.=$m.":".$l.";";echo "E";return true;});\nob_start("h",1);\necho '
                                   b'"A";\nob_end_clean();\necho "|".$log;',
                                   b'EXAE|main(): Producing output from user output handler h is deprecated:5;ob_end_clean(): Producing output from user output handler h is deprecated:6;'),
 'cv-capture-print-result': (b'<?php $v="A";function h($b,$p){global $v;$v="B";return $b;}ob_start("h",1);$n=print $v;ob_end_clean();echo ":".$n.":".$v;', b'A:1:B')}
CONTROLS = {'strict-failing-receive': b'<?php declare(strict_types=1);echo "P";function h(int $b,int $p){return $b;}ob_start("h",1);try{echo "7";}catch(TypeError $e){echo "C";}ob_end_clean();',
 'callback-throw': b'<?php echo "P";function h($b,$p){throw new Exception("E");}ob_start("h",1);echo "A";ob_end_clean();',
 'callback-exit': b'<?php echo "P";function h($b,$p){exit("E");}ob_start("h",1);echo "A";ob_end_clean();'}
CONTROL_REASONS = {'strict-failing-receive': 'abrupt user output-handler callback cleanup', 'callback-throw': 'abrupt user output-handler callback cleanup', 'callback-exit': 'abrupt user output-handler callback cleanup'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules,
             'adapter/main.ml', 'bin/php-semantics', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe',
             'vendor/php-src/main/output.c', 'vendor/php-src/main/php_output.h',
             'vendor/php-src/Zend/zend_API.c', 'vendor/php-src/Zend/zend_vm_def.h', 'vendor/php-src/Zend/zend_execute_API.c',
             'tests/semantics/profile.json', 'tests/semantics/output_chunk_sources.py']
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
    out = args.output or Path(tempfile.mkdtemp(prefix='output-chunk-sources-', dir=ROOT / '.tools'))
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
                assert base64.b64decode(outcome['stdout'], validate=True) == b'P', (name, outcome)
                assert base64.b64decode(outcome['stderr'], validate=True) == b'', (name, outcome)
                assert CONTROL_REASONS[name] == outcome['reason'], (name, outcome)
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
