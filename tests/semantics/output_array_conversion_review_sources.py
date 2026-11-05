#!/usr/bin/env python3
"""Independent array-result owners, warning/callee throws and child traces."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import output_api_failure_sources as common

ROOT = common.ROOT
CASES = {
    'fresh-warning-retval-api-trace': (
        b'<?php\necho "P";$x=99;$log="";\nclass D{function __destruct(){global $log;$s=ob_get_status();$log="D".$s["flags"].":".ob_get_contents();echo "D";throw new Exception("F");}}\nset_error_handler(function(){return new D;});\nfunction h($b,$p){return [];}\nob_start("h");echo "A";\ntry{$x=ob_get_flush();}catch(Exception $c){$t=$c->getTrace();echo "|".$x.":".$log.":".ob_get_level().":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[1]["function"])?$t[1]["function"]:"missing").":".(isset($t[1]["file"])&&$t[1]["file"]===__FILE__?"F":"N").":".(isset($t[1]["line"])?$t[1]["line"]:-1).":".($c->getPrevious()===null?"0":"P");}\n',
        b'PArray|99:D113:A:0:__destruct:I:ob_get_flush:F:7:0'),
    'fresh-array-child-vm-flags-and-trace': (
        b'<?php\necho "P";$x=99;$once=true;$warnings=0;$deprecations=0;\nclass D{function __destruct(){echo "D";throw new Exception("F");}}\nset_error_handler(function($n){global $warnings,$deprecations;if($n===2){$warnings++;}else{$deprecations++;}return true;});\nfunction h($b,$p){global $once;if($once){$once=false;return [new D];}return "";}\nob_start("h",1);\ntry{$x=print "A";}catch(Exception $c){$t=$c->getTrace();$s=ob_get_status();$report=$x.":".$c->getMessage().":".$s["flags"].":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[0]["line"])?$t[0]["line"]:-1).":".(isset($t[1])?"E":"-");}\n$y=print "B";$s=ob_get_status();ob_end_clean();echo "|".$report.":".$y.":".$s["flags"].":".$warnings.":".$deprecations;\n',
        b'PArray|99:F:53361:__destruct:F:7:-:1:20593:1:1'),
    'callee-array-owner-then-child-replacement': (
        b'<?php echo "P";$x=99;$log="";$n=0;class D{function __destruct(){global $log;$log.="D";throw new Exception("E");}}class C{function __destruct(){global $log;$log.="C";throw new Exception("F");}}set_error_handler(function(){global $n;$n++;return true;});function h($b,$p){$a=[new C];$d=new D;return $a;}ob_start("h");echo "A";try{$x=ob_get_flush();}catch(Exception $c){echo "|".$x.":".$log.":".$n.":".$c->getMessage().":".$c->getPrevious()->getMessage().":".ob_get_level();}',
        b'PArray|99:DC:0:F:E:0'),
    'reference-array-capture-before-warning': (
        b'<?php\necho "P";$x=99;\nclass D{function __destruct(){throw new Exception("F");}}\n$r=[new D];set_error_handler(function(){global $r;$r=false;throw new Exception("E");});\nfunction &h($b,$p){global $r;return $r;}\nob_start("h");echo "A";\ntry{$x=ob_get_flush();}catch(Exception $c){$t=$c->getTrace();echo "|".$x.":".$c->getMessage().":".$c->getPrevious()->getMessage().":".($r===false?"F":"N").":".ob_get_level().":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[1]["function"])?$t[1]["function"]:"missing").":".(isset($t[1]["file"])&&$t[1]["file"]===__FILE__?"F":"N").":".(isset($t[1]["line"])?$t[1]["line"]:-1);}\n',
        b'PArray|99:F:E:F:0:__destruct:I:ob_get_flush:F:7'),
}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_array_conversion_review_sources.py'] = common.sha(Path(__file__))
    for name in ('vendor/php-src/Zend/zend_operators.c', 'vendor/php-src/Zend/zend_operators.h'):
        inputs[name] = common.sha(ROOT / name)
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-array-conversion-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': common.PROFILE, 'selected': selected,
              'records': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
            native = common.run([str(ROOT / '.tools/php/bin/php'), '-n', *common.FLAGS, str(path)], directory, 'native', 10)
            assert native.returncode == 0 and native.stdout == expected and not native.stderr, (name, native.stdout, native.stderr)
            modeled = common.run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '90'], directory, 'model', 120)
            assert not modeled.stderr, (name, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            assert modeled.returncode == 0 and outcome['status'] == 'normal' and outcome['reason'] is None, (name, outcome)
            assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
            assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
            assert outcome['exit_status'] == native.returncode
            report['records'].append({'case': name, 'source_sha256': common.sha(path),
                                      'stdout_sha256': hashlib.sha256(native.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest(),
                                      'native_credit': True, 'status': outcome['status']})
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
