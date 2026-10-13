#!/usr/bin/env python3
"""Independent explicit output API failure and handler ownership cases."""
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
    'popped-zoh-destructor-replaces-error': (b'<?php $e=new Exception("E");$f=new Exception("F");$log="";function l($b,$p){global $log;$log.="L";return "L".$b;}class C{function __invoke($b,$p){global $e;throw $e;}function __destruct(){global $f;echo "D".ob_get_level();throw $f;}}ob_start("l",1);ob_start(new C);echo "A";try{ob_end_flush();}catch(Exception $c){$s=ob_get_status();echo ($c===$f?"F":"N").($c->getPrevious()===$e?"P":"N").":".$s["flags"];}ob_end_clean();echo "|".$log."Z";', b'AD1FP:12401|Z'),
    'clean-argv-replacement-retains-lower': (b'<?php $e=new Exception("E");$f=new Exception("F");$log="";set_error_handler(function(){return true;});class D{function __destruct(){global $f,$log;$log.="D".ob_get_level();echo "D".ob_get_level();throw $f;}}function h(&$b,$p){global $e;$b=new D;throw $e;}ob_start();echo "B";ob_start("h");echo "A";try{ob_clean();}catch(Exception $c){$s=ob_get_status();$x=($c===$f?"F":"N").($c->getPrevious()===$e?"P":"N").":".ob_get_level().":".$s["flags"].":".$s["buffer_used"].":".$s["buffer_size"];}ob_end_clean();$raw=ob_get_clean();echo $raw."|".$log."|".$x."Z";', b'B|D2|FP:2:45169:0:0Z'),
    'flush-alias-receiver-unwind': (b'<?php $e=new Exception("E");$log="";class C{function h($b,$p){global $r,$e;$r=null;throw $e;}function __destruct(){global $log;$s=ob_get_status();$log=$s["flags"].":".$s["buffer_used"];echo "D".ob_get_level();}}ob_start(null,1);$r=new C;$cb=[&$r,"h"];ob_start($cb);unset($cb);echo "A";try{ob_flush();}catch(Exception $c){$a=ob_get_status(true);$x=($c===$e?"C":"N")."|".$log."|".$a[1]["flags"].":".$a[1]["buffer_used"]."|".$a[0]["flags"].":".$a[0]["buffer_used"];}ob_end_clean();ob_end_clean();echo "|".$x."Z";', b'AD2|C|113:1|45169:0|20592:0Z'),
    'popped-zoh-echo-crosses-lower-threshold': (b'<?php $e=new Exception("E");$f=new Exception("F");$log="";function l($b,$p){global $log;$log.="L";return "L".$b;}class C{function __invoke($b,$p){global $e;throw $e;}function __destruct(){global $f;echo "D".ob_get_level();throw $f;}}ob_start("l",3);ob_start(new C);echo "A";try{ob_end_flush();}catch(Exception $c){$s=ob_get_status();echo ($c===$f?"F":"N").($c->getPrevious()===$e?"P":"N").":".$s["flags"];}ob_end_clean();echo "|".$log."Z";', b'LAD1LFP:20593|LLLZ'),
    'get-clean-zoh-fresh-throw-trace': (b'<?php\n$e=new Exception("E");$x=99;\nclass C{\nfunction __invoke($b,$p){global $e;throw $e;}\nfunction __destruct(){echo "D".ob_get_level();throw new Exception("F");}\n}\nob_start(new C);\necho "A";\ntry{$x=ob_get_clean();}catch(Exception $c){$t=$c->getTrace();echo $t[0]["function"].":".$t[1]["function"].":".($t[1]["file"]===__FILE__?"F":"N").":".$t[1]["line"].":".($c->getPrevious()===$e?"P":"N");}\necho ":".$x."Z";', b'D0__destruct:ob_get_clean:F:9:P:99Z'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules,
             'adapter/main.ml', 'bin/php-semantics', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe',
             'vendor/php-src/main/output.c', 'vendor/php-src/main/php_output.h',
             'vendor/php-src/Zend/zend_API.c', 'vendor/php-src/Zend/zend_vm_def.h',
             'vendor/php-src/Zend/zend_execute_API.c', 'vendor/php-src/Zend/zend_objects.c',
             'tests/semantics/profile.json', 'tests/semantics/output_api_failure_review_sources.py']
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
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected)
    assert all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-api-failure-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': PROFILE, 'selected': selected, 'records': [],
              'completed': False, 'passed': False}
    print(out, flush=True)
    try:
        for name in selected:
            source, expected = CASES[name]
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(source)
            native = run([str(ROOT / '.tools/php/bin/php'), '-n', *FLAGS, str(path)], directory, 'native', 10)
            assert native.stdout == expected and native.stderr == b'' and native.returncode == 0, (name, native.stdout, native.stderr, native.returncode)
            modeled = run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '60'], directory, 'model', 90)
            assert not modeled.stderr, (name, modeled.stdout, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            assert modeled.returncode == 0 and outcome['status'] == 'normal', (name, outcome)
            assert outcome['reason'] is None
            assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
            assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
            assert outcome['exit_status'] == native.returncode
            report['records'].append({'case': name, 'source_sha256': sha(path), 'status': outcome['status'],
                                      'native_credit': True, 'native_exit': native.returncode,
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
