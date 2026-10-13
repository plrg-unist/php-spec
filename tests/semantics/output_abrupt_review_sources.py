#!/usr/bin/env python3
"""Independent automatic output-handler exception, argv and receiver cleanup."""
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
    'argv-destructor-replaces-error': (b'<?php $e=new Exception("E");$f=new Exception("F");set_error_handler(function(){return true;});class D{function __destruct(){global $f;echo "D".ob_get_level();throw $f;}}function h(&$b,$p){global $e;$b=new D;throw $e;}ob_start("h",1);try{echo "A";}catch(Exception $c){$s=ob_get_status();echo ($c===$f?"S":"N").($c->getPrevious()===$e?"P":"N").":".$s["flags"].":".$s["buffer_used"].":".$s["buffer_size"];}ob_end_clean();echo "Z";', b'AD1SP:45169:0:0Z'),
    'alias-receiver-unwind-output': (b'<?php $e=new Exception("E");$log="";class C{function h($b,$p){global $r,$e;$r=null;throw $e;}function __destruct(){global $log;$s=ob_get_status();$log=$s["flags"].":".$s["buffer_used"];echo "D".ob_get_level();}}$r=new C;$cb=[&$r,"h"];ob_start($cb,1);unset($cb);try{echo "A";}catch(Exception $c){$s=ob_get_status();echo ($c===$e?"C":"N")."|".$log."|".$s["flags"];}ob_end_clean();echo "Z";', b'AD1C|113:1|45169Z'),
    'lower-below-threshold-resume': (b'<?php $e=new Exception("E");$log="";function l($b,$p){global $log;$log.=$p.":".$b.";";return "L".$b;}function h($b,$p){global $e;throw $e;}ob_start("l",10);echo "B";ob_start("h",1);try{echo "A";}catch(Exception $c){$a=ob_get_status(true);echo "C";}ob_end_clean();$lower=ob_get_contents();ob_end_flush();echo "|".$lower."|".$a[0]["buffer_used"].":".$a[0]["flags"]."|".$log;', b'LBAC|BAC|2:113|9:BAC;'),
    'normal-stringable-producer-release': (b'<?php $x=99;function h($b,$p){return $b;}class C{function __toString(){return "A";}function __destruct(){global $x;echo "D".ob_get_level().":".$x.";";}}ob_start("h",1);$x=print new C;ob_end_clean();echo ":".$x."Z";', b'AD1:99;:1Z'),
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
             'vendor/php-src/Zend/zend_execute_API.c',
             'tests/semantics/profile.json', 'tests/semantics/output_abrupt_review_sources.py']
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
    out = args.output or Path(tempfile.mkdtemp(prefix='output-abrupt-review-', dir=ROOT / '.tools'))
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
