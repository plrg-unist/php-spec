#!/usr/bin/env python3
"""Explicit output API receive/throw failures, stack finish and callback release."""
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
CASES = {'api-flush': (b'<?php $e=new Exception;$x=99;$log="";set_error_handler(function($n,$m){global $log;$log.="W";return true;});function h($b,$p){global $e,$log;$log.=$p;echo "H";throw $e;}ob_start("h");echo "A";try{$x=ob_flush();}catch(Exception $c){echo ($c===$e?"C":"N").":".$x.":".ob_get_level();}if(ob_get_level()){ $s=ob_get_status();echo ":".$s["flags"].":".$s["buffer_size"].":".ob_get_length();ob_end_clean();}echo "|".$log."Z";', b'AHC:99:1:45169:0:0|5Z'), 'api-clean': (b'<?php $e=new Exception;$x=99;$log="";set_error_handler(function($n,$m){global $log;$log.="W";return true;});function h($b,$p){global $e,$log;$log.=$p;echo "H";throw $e;}ob_start("h");echo "A";try{$x=ob_clean();}catch(Exception $c){echo ($c===$e?"C":"N").":".$x.":".ob_get_level();}if(ob_get_level()){ $s=ob_get_status();echo ":".$s["flags"].":".$s["buffer_size"].":".ob_get_length();ob_end_clean();}echo "|".$log."Z";', b'C:99:1:45169:0:0|3Z'), 'api-end-flush': (b'<?php $e=new Exception;$x=99;$log="";set_error_handler(function($n,$m){global $log;$log.="W";return true;});function h($b,$p){global $e,$log;$log.=$p;echo "H";throw $e;}ob_start("h");echo "A";try{$x=ob_end_flush();}catch(Exception $c){echo ($c===$e?"C":"N").":".$x.":".ob_get_level();}if(ob_get_level()){ $s=ob_get_status();echo ":".$s["flags"].":".$s["buffer_size"].":".ob_get_length();ob_end_clean();}echo "|".$log."Z";', b'AHC:99:0|9Z'), 'api-end-clean': (b'<?php $e=new Exception;$x=99;$log="";set_error_handler(function($n,$m){global $log;$log.="W";return true;});function h($b,$p){global $e,$log;$log.=$p;echo "H";throw $e;}ob_start("h");echo "A";try{$x=ob_end_clean();}catch(Exception $c){echo ($c===$e?"C":"N").":".$x.":".ob_get_level();}if(ob_get_level()){ $s=ob_get_status();echo ":".$s["flags"].":".$s["buffer_size"].":".ob_get_length();ob_end_clean();}echo "|".$log."Z";', b'C:99:0|11Z'), 'api-get-flush': (b'<?php $e=new Exception;$x=99;$log="";set_error_handler(function($n,$m){global $log;$log.="W";return true;});function h($b,$p){global $e,$log;$log.=$p;echo "H";throw $e;}ob_start("h");echo "A";try{$x=ob_get_flush();}catch(Exception $c){echo ($c===$e?"C":"N").":".$x.":".ob_get_level();}if(ob_get_level()){ $s=ob_get_status();echo ":".$s["flags"].":".$s["buffer_size"].":".ob_get_length();ob_end_clean();}echo "|".$log."Z";', b'AHC:99:0|9Z'), 'api-get-clean': (b'<?php $e=new Exception;$x=99;$log="";set_error_handler(function($n,$m){global $log;$log.="W";return true;});function h($b,$p){global $e,$log;$log.=$p;echo "H";throw $e;}ob_start("h");echo "A";try{$x=ob_get_clean();}catch(Exception $c){echo ($c===$e?"C":"N").":".$x.":".ob_get_level();}if(ob_get_level()){ $s=ob_get_status();echo ":".$s["flags"].":".$s["buffer_size"].":".ob_get_length();ob_end_clean();}echo "|".$log."Z";', b'C:99:0|11Z'), 'api-receive-trace': (b'<?php\ndeclare(strict_types=1);\nfunction h(int $b,int $p){echo "T";return $b;}\nob_start("h");echo "A";\ntry{ob_flush();}catch(TypeError $e){$a=$e->getTrace();$s=ob_get_status();echo "C:".(isset($a[0]["file"])?"F":"-").":".$a[0]["function"].":".$a[1]["function"].":".($a[1]["file"]===__FILE__?"F":"-").":".$a[1]["line"].":".$s["flags"].":".$s["buffer_size"];}\nob_end_clean();echo "Z";', b'AC:-:h:ob_flush:F:5:12401:0Z'), 'normal-upper-lower-throw': (b'<?php $e=new Exception;$log="";$report="";function l($b,$p){global $e,$log;$log.="l".$p;throw $e;}function u($b,$p){global $log;$log.="u".$p;return "X".$b;}ob_start("l",1);ob_start("u");echo "A";try{ob_flush();}catch(Exception $c){$a=ob_get_status(true);$report=($c===$e?"C":"N").":".$a[0]["flags"].":".$a[1]["flags"].":".$a[1]["buffer_used"];}ob_end_clean();ob_end_clean();echo "|".$report."|".$log."Z";', b'XA|C:12401:20593:0|u5l1u10Z')}
CONTROLS = {'api-callback-exit': b'<?php echo "P";function h($b,$p){exit("E");}ob_start("h");echo "A";ob_flush();', 'api-produced-warning-throw': b'<?php echo "P";set_error_handler(function(){throw new Exception;});function h($b,$p){echo "H";return $b;}ob_start("h");echo "A";ob_flush();'}
CONTROL_REASONS = {'api-callback-exit': 'abrupt user output-handler callback cleanup', 'api-produced-warning-throw': 'abrupt user output-handler deprecation callback cleanup'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules,
             'adapter/main.ml', 'bin/php-semantics', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe',
             'vendor/php-src/main/output.c', 'vendor/php-src/main/php_output.h',
             'vendor/php-src/Zend/zend_API.c', 'vendor/php-src/Zend/zend_vm_def.h', 'vendor/php-src/Zend/zend_execute_API.c', 'vendor/php-src/Zend/zend_objects.c',
             'tests/semantics/profile.json', 'tests/semantics/output_api_failure_sources.py']
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
    out = args.output or Path(tempfile.mkdtemp(prefix='output-api-failure-sources-', dir=ROOT / '.tools'))
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
                assert not native.stderr, (name, native.stderr)
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
