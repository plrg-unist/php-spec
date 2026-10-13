#!/usr/bin/env python3
"""Automatic output-handler receive/throw failures, live bytes and caller cleanup."""
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
CASES = {'strict-receive': (b'<?php\ndeclare(strict_types=1);\nfunction h(int $b,int $p){return $b;}\nob_start("h",1)'
                    b';\ntry{echo "7";}catch(TypeError $e){$a=$e->getTrace();$s=ob_get_status();echo "C:".('
                    b'$a[0]["file"]===__FILE__?"F":"-").":".$a[0]["line"].":".$s["flags"].":".$s["buffer_s'
                    b'ize"].":".ob_get_length();}\nob_end_clean();echo "Z";',
                    b'7C:F:5:12401:0:0Z'),
 'throw-identity': (b'<?php $e=new Exception("E");function h($b,$p){global $e;throw $e;}ob_start("h",1);tr'
                    b'y{echo "A";}catch(Exception $c){$s=ob_get_status();echo ($c===$e?"S":"N").":".$s["fl'
                    b'ags"].":".$s["buffer_size"].":".ob_get_length();}ob_end_clean();echo "Z";',
                    b'AS:12401:0:0Z'),
 'throw-produced': (b'<?php $log="";set_error_handler(function($n,$m){global $log;$log.=$m;return true;});'
                    b'function h($b,$p){echo "H";throw new Exception("E");}ob_start("h",1);try{echo "A";}c'
                    b'atch(Exception $e){$s=ob_get_status();echo "C:".$s["flags"].":".ob_get_length();}ob_'
                    b'end_clean();echo "|".$log;',
                    b'AHC:45169:0|'),
 'print-capture': (b'<?php $v="A";$x=99;function h($b,$p){global $v;$v="B";throw new Exception;}ob_start("h",'
                   b'1);try{$x=print $v;echo "T";}catch(Exception $e){}ob_end_clean();echo "|".$x.":".$v;',
                   b'A|99:B'),
 'inline-interruption': (b'<?php function h($b,$p){throw new Exception;}ob_start("h",1);try{?>A<?php echo "'
                         b'T";}catch(Exception $e){echo "C";}ob_end_clean();echo "Z";',
                         b'ACZ'),
 'lower-pending': (b'<?php $log="";function l($b,$p){global $log;$log.="L";return "X".$b;}function u($b,$p){t'
                   b'hrow new Exception;}ob_start("l",1);ob_start("u",1);try{echo "A";}catch(Exception $e){$a'
                   b'=ob_get_status(true);echo "C:".$a[0]["flags"].":".$a[1]["flags"];}ob_end_clean();ob_end_'
                   b'clean();echo "|".$log;',
                   b'AC:12401:12401|'),
 'reference-argument-cleanup': (b'<?php $e=new Exception;set_error_handler(function(){return true;});class'
                                b' C{function __destruct(){echo "D".ob_get_level();}}function h(&$b,$p){gl'
                                b'obal $e;$b=new C;throw $e;}ob_start("h",1);try{echo "A";}catch(Exception'
                                b' $c){echo ($c===$e?"C":"N");}ob_end_clean();echo "Z";',
                                b'AD1CZ')}
CASES["owned-stringable-producer"] = (b'<?php $e=new Exception;$x=99;function h($b,$p){global $e;throw $e;}class C{function __toString(){return "A";}function __destruct(){echo "D".ob_get_level();}}ob_start("h",1);try{$x=print new C;}catch(Exception $c){echo ($c===$e?"C":"N");}ob_end_clean();echo ":".$x."Z";', b"AD1C:99Z")
CONTROLS = {'callback-exit': b'<?php echo "P";function h($b,$p){exit("E");}ob_start("h",1);echo "A";ob_end_clean();',
 'reference-warning-throw': b'<?php echo "P";set_error_handler(function(){throw new Exception;});function '
                            b'h(&$b,$p){return $b;}ob_start("h",1);try{echo "A";}catch(Exception $e){echo '
                            b'"C";}ob_end_clean();',
 'produced-warning-throw': b'<?php echo "P";set_error_handler(function(){throw new Exception;});function h($b'
                           b',$p){echo "H";return $b;}ob_start("h",1);try{echo "A";}catch(Exception $e){echo '
                           b'"C";}ob_end_clean();'}
CONTROL_REASONS = {'callback-exit': 'abrupt user output-handler callback cleanup',
 'reference-warning-throw': 'abrupt user output-handler callback cleanup',
 'produced-warning-throw': 'abrupt user output-handler deprecation callback cleanup'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules,
             'adapter/main.ml', 'bin/php-semantics', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe',
             'vendor/php-src/main/output.c', 'vendor/php-src/main/php_output.h',
             'vendor/php-src/Zend/zend_API.c', 'vendor/php-src/Zend/zend_vm_def.h', 'vendor/php-src/Zend/zend_execute_API.c',
             'tests/semantics/profile.json', 'tests/semantics/output_abrupt_sources.py']
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
    out = args.output or Path(tempfile.mkdtemp(prefix='output-abrupt-sources-', dir=ROOT / '.tools'))
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
