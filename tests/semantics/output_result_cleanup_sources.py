#!/usr/bin/env python3
"""Normal output-handler results followed by argument cleanup Throwables."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import output_api_failure_sources as common

ROOT = common.ROOT
CASES = {'api-normal-result-argv-throw': (b'<?php $e=new Exception;$x=99;$log="";$once=false;set_error_handler(function(){global $log;$log.="W";return true;});class D{function __destruct(){global $e;echo "D".ob_get_level();throw $e;}}function h(&$b,$p){global $once;if(!$once){$once=true;$b=new D;}return "X";}ob_start("h");echo "A";try{$x=ob_flush();}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$x.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$report."|".$log."Z";', b'X|C:99:20593:0|WWZ'), 'normal-null-cleanup-throw': (b'<?php $e=new Exception;$x=99;$log="";$once=false;set_error_handler(function(){global $log;$log.="W";return true;});class D{function __destruct(){global $e;echo "D".ob_get_level();throw $e;}}function h(&$b,$p){global $once;if(!$once){$once=true;$b=new D;}return null;}ob_start("h");echo "A";try{$x=ob_flush();}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$x.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$report."|".$log."Z";', b'|C:99:20593:0|WWZ'), 'body-throw-null-result': (b'<?php $e=new Exception;$x=99;$log="";$once=false;set_error_handler(function(){global $log;$log.="W";return true;});class D{function __destruct(){global $e;echo "D".ob_get_level();throw $e;}}function h(&$b,$p){global $once;if(!$once){$once=true;$b=new D;}throw $GLOBALS["e"];}ob_start("h");echo "A";try{$x=ob_flush();}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$x.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$report."|".$log."Z";', b'AD1|C:99:45169:0|WZ'), 'false-result-cleanup-throw': (b'<?php $e=new Exception;$x=99;$log="";$once=false;set_error_handler(function(){global $log;$log.="W";return true;});class D{function __destruct(){global $e;echo "D".ob_get_level();throw $e;}}function h(&$b,$p){global $once;if(!$once){$once=true;$b=new D;}return false;}ob_start("h");echo "A";try{$x=ob_flush();}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$x.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$report."|".$log."Z";', b'AD1|C:99:12401:0|WZ'), 'vm-print-cleanup-throw': (b'<?php $e=new Exception;$x=99;$log="";$once=false;set_error_handler(function($n){global $log;$log.="W".$n.";";return true;});class D{function __destruct(){global $e;echo "D".ob_get_level();throw $e;}}function h(&$b,$p){global $once;if(!$once){$once=true;$b=new D;}return "X";}ob_start("h",1);try{$x=print "A";}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$x.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$report."|".$log."Z";', b'X|C:99:20593:0|W2;W2;Z'), 'unset-wrapper-during-body': (b'<?php $log="";$inside="";set_error_handler(function($n){global $log;$log.=($n===2?"W":"P");return true;});class D{function __destruct(){echo "D".ob_get_level();}}function h(&$b,$p){global $inside;$b=new D;unset($b);$inside=ob_get_contents();return "X";}ob_start("h");echo "A";$copy=ob_get_flush();echo "|".$copy."|".$inside."|".$log."Z";', b'X|A|AD1|WPZ'), 'pending-default-deprecation': (b'<?php $e=new Exception;$x=99;$log="";$once=false;set_error_handler(function(){global $log;$log.="W";return true;},2);error_reporting(32767);class D{function __destruct(){global $e;echo "D".ob_get_level();throw $e;}}function h(&$b,$p){global $once;if(!$once){$once=true;$b=new D;}return "X";}ob_start("h");echo "A";try{$x=ob_flush();}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$x.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$report."|".$log."Z";', b'X|C:99:20593:0|WWZ')}
STDERR = {'pending-default-deprecation': b'Deprecated: ob_flush(): Producing output from user output handler h is deprecated in {FILE} on line 1\n'}
CONTROLS = {
    'byref-variadic-ownership': b'<?php echo "P";set_error_handler(function(){return true;});function h(&...$a){return "X";}ob_start("h");echo "A";ob_end_clean();',
    'nonscalar-result-cleanup-throw': b'<?php echo "P";$e=new Exception;set_error_handler(function(){return true;});class D{function __destruct(){global $e;throw $e;}}function h(&$b,$p){$b=new D;return [];}ob_start("h");echo "A";try{ob_end_clean();}catch(Exception $c){}',
}
CONTROL_REASONS = {
    'byref-variadic-ownership': 'by-reference variadic output-handler argument ownership',
    'nonscalar-result-cleanup-throw': 'non-scalar user output-handler return conversion',
}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_result_cleanup_sources.py'] = common.sha(Path(__file__))
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES) + list(CONTROLS)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES or name in CONTROLS for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-result-cleanup-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': common.PROFILE, 'selected': selected,
              'records': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source, expected = CASES[name] if name in CASES else (CONTROLS[name], None)
            path = directory / 'source.php'; path.write_bytes(source)
            native = common.run([str(ROOT / '.tools/php/bin/php'), '-n', *common.FLAGS, str(path)], directory, 'native', 10)
            if name in CASES:
                assert native.returncode == 0 and native.stdout == expected, (name, native.stdout, native.stderr)
                assert native.stderr == STDERR.get(name, b'').replace(b'{FILE}', str(path).encode()), (name, native.stderr)
            modeled = common.run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '60'], directory, 'model', 90)
            assert not modeled.stderr, (name, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            if name in CASES:
                assert modeled.returncode == 0 and outcome['status'] == 'normal' and outcome['reason'] is None, (name, outcome)
                assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
                assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
                assert outcome['exit_status'] == native.returncode
            else:
                assert modeled.returncode == 1 and outcome['status'] == 'unsupported', (name, outcome)
                assert outcome['reason'] == CONTROL_REASONS[name], (name, outcome)
                assert base64.b64decode(outcome['stdout'], validate=True) == b'P', (name, outcome)
                assert base64.b64decode(outcome['stderr'], validate=True) == b'', (name, outcome)
            report['records'].append({'case': name, 'source_sha256': common.sha(path),
                                      'stdout_sha256': hashlib.sha256(native.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest(), 'native_credit': name in CASES,
                                      'status': outcome['status']})
            print(name, outcome['status'], flush=True)
        report.update(passed=True, completed=True)
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
