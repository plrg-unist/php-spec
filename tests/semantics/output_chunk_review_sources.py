#!/usr/bin/env python3
"""Independent automatic output-handler stack, caller and ownership cases."""
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
    'lower-user-active-upper-default': (b'<?php $log="";function h($b,$p){global $log;if($p===1){$log=ob_get_level().":".ob_get_contents();echo "H";}return "L".$b;}ob_start("h",1);ob_start(null,1);echo "A";$s=ob_get_status(true);$top=ob_get_contents();ob_end_clean();ob_end_clean();echo "|".$top."|".$s[0]["buffer_used"].":".$s[0]["flags"]."|".$s[1]["buffer_used"].":".$s[1]["flags"]."|".$log;', b'LA|H|0:20593|1:53360|2:'),
    'flush-detached-active-getters': (b'<?php $log=""; function h($b,$p){global $log; if($p===1){$s=ob_get_status(); $a=ob_get_status(true); $log=ob_get_level().":".ob_get_contents().":".$s["name"].":".$s["level"].":".$a[0]["name"].":".$a[0]["level"].":".(isset($a[1])?"extra":"one");} return "L".$b;} ob_start("h",1); ob_start(); echo "A"; ob_flush(); ob_end_clean(); ob_end_clean(); echo "|".$log;', b'LA|1::default output handler:1:h:0:one'),
    'auto-alias-false-retirement': (b'<?php $log=""; class C { function h($b,$p){global $r; $r=null; return false;} function __destruct(){global $log; $log.="D".ob_get_level();} } $r=new C; $cb=[&$r,"h"]; ob_start($cb,1); unset($cb); echo "A"; echo "B"; ob_end_clean(); echo "(".$log.")";', b'AB(D1)'),
    'api-cascade-weak-owned-pop': (b'<?php declare(strict_types=1); $log=""; function h(int $b,int $p){global $log; $log.="H".$b.":".$p; return false;} class C { function __invoke($b,$p){return $b;} function __destruct(){global $log; $log.="D".ob_get_level();} } ob_start("h",1); ob_start(new C); echo "7"; $v=ob_get_flush(); ob_end_clean(); echo "|".$v."|".$log;', b'7|7|H7:1D1'),
    'busy-upper-user-next-write': (b'<?php $seen=""; $log=""; function i($b,$p){return "I".$b;} function h($b,$p){if($p===1)echo "H"; return "L".$b;} set_error_handler(function($n,$m){global $log; $log.=$m; return true;}); ob_start("h",1); ob_start("i",1); echo "A"; $s=ob_get_status(); $seen=ob_get_contents().":".$s["flags"].":".$s["buffer_used"]; echo "B"; ob_end_clean(); ob_end_clean(); echo "|".$seen."|".$log;', b'LIALIHB|H:53361:1|main(): Producing output from user output handler i is deprecated'),
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
             'tests/semantics/profile.json', 'tests/semantics/output_chunk_review_sources.py']
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
    out = args.output or Path(tempfile.mkdtemp(prefix='output-chunk-review-', dir=ROOT / '.tools'))
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
