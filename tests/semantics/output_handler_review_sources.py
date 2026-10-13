#!/usr/bin/env python3
"""Independent explicit output-handler entry, buffering and lifetime cases."""
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
    'internal-weak-entry': (b'<?php declare(strict_types=1); function h(int $b,int $p){return "I".$b.":".$p;} ob_start("h"); echo "7"; ob_end_flush(); echo "Z";', b'I7:9Z'),
    'internal-builtin-trace': (b'<?php $log=""; function h($b,$p){global $log; $e=new Exception; $a=$e->getTrace(); $log=(isset($a[0]["file"])?"F":"-")."|".$a[0]["function"]."|".$a[1]["function"]; return $b;} ob_start("h"); echo "A"; ob_end_flush(); echo $log;', b'A-|h|ob_end_flush'),
    'byref-copy-and-frozen-getter': (b'<?php $log=""; set_error_handler(function($n,$m){global $log; $s=ob_get_status(); $log.=$n.":".ob_get_contents().":".$s["flags"]."|"; return true;}); function h(&$b,$p){$b="X";return $b;} ob_start("h"); echo "A"; $v=ob_get_flush(); echo "(".$v."/".$log.")";', b'X(A/2:A:113|)'),
    'produced-live-getters': (b'<?php $log=""; function h($b,$p){global $log; echo "H"; $s=ob_get_status(); $log=ob_get_length().":".ob_get_contents().":".$s["flags"]; return "X".$b;} ob_start("h"); echo "A"; ob_end_flush(); echo "(".$log.")";', b'XA(2:AH:32881)'),
    'false-forwards-live-buffer': (b'<?php function h($b,$p){echo "H";return false;} ob_start("h"); echo "A"; ob_flush(); $s=ob_get_status(); echo "B"; ob_end_flush(); echo ":".$s["flags"].":".$s["buffer_size"]."Z";', b'AHB:12401:0Z'),
    'deprecation-handler-bypass': (b'<?php $log=""; set_error_handler(function($n,$m){global $log; $s=ob_get_status(); $log=$s["flags"].":".ob_get_contents(); echo "E"; return true;}); function h($b,$p){echo "H"; return "X".$b;} ob_start("h"); echo "A"; ob_end_flush(); echo "(".$log.")";', b'EXA(8305:AH)'),
    'lower-default-produced-flag': (b'<?php set_error_handler(function(){echo "E";return true;}); function h($b,$p){echo "H";return "X".$b;} ob_start(); ob_start("h"); echo "A"; ob_end_flush(); $s=ob_get_status(); ob_flush(); $a=ob_get_status(); ob_end_clean(); echo ":".$s["flags"].":".$a["flags"];', b'EXA:32880:53360'),
    'alias-receiver-return-timing': (b'<?php $log=""; class C { function h($b,$p){global $r; $r=null; return "X".$b;} function __destruct(){global $log; $log.="D".ob_get_level();} } $r=new C; $cb=[&$r,"h"]; ob_start($cb); unset($cb); echo "A"; ob_end_flush(); echo "(".$log.")";', b'XA(D1)'),
    'raw-callable-owns-receiver': (b'<?php $log=""; class C { function h($b,$p){return "X".$b;} function __destruct(){global $log; $log.="D".ob_get_level();} } $r=new C; $cb=[$r,"h"]; ob_start($cb); unset($r,$cb); echo "A"; ob_end_flush(); echo "(".$log.")";', b'XA(D0)'),
}
CONTROLS = {
    'automatic-handler-chunk': b'<?php echo "P"; function h($b,$p){return "X".$b;} ob_start("h",1); echo "A"; ob_end_flush();',
    'request-end-handler-drain': b'<?php echo "P"; function h($b,$p){return "X".$b;} ob_start("h"); echo "A";',
    'nonscalar-handler-result': b'<?php echo "P"; function h($b,$p){return [];} ob_start("h"); echo "A"; ob_end_flush(); echo "Z";',
    'handler-stack-mutation': b'<?php echo "P"; function h($b,$p){ob_clean(); return $b;} ob_start("h"); echo "A"; ob_end_flush(); echo "Z";',
}
CONTROL_REASONS = {
    'automatic-handler-chunk': 'automatic user output-handler chunk dispatch',
    'request-end-handler-drain': 'request-end user output-handler callback drain',
    'nonscalar-handler-result': 'non-scalar user output-handler return conversion',
    'handler-stack-mutation': 'output-buffer mutation from a running user handler',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules,
             'adapter/main.ml', 'bin/php-semantics', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe',
             'vendor/php-src/main/output.c', 'vendor/php-src/main/php_output.h',
             'vendor/php-src/Zend/zend_API.c', 'tests/semantics/profile.json',
             'tests/semantics/output_handler_review_sources.py']
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
    out = args.output or Path(tempfile.mkdtemp(prefix='output-handler-review-', dir=ROOT / '.tools'))
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
                assert modeled.returncode == 0 and outcome['status'] == 'normal', (name, outcome)
                assert outcome['reason'] is None
                assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
                assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
                assert outcome['exit_status'] == native.returncode
            else:
                assert modeled.returncode == 1 and outcome['status'] == 'unsupported', (name, outcome)
                assert base64.b64decode(outcome['stdout'], validate=True) == b'P', (name, outcome)
                assert base64.b64decode(outcome['stderr'], validate=True) == b'', (name, outcome)
                assert outcome['reason'] == CONTROL_REASONS[name], (name, outcome)
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
