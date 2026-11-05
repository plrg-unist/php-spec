#!/usr/bin/env python3
"""Independent object-result owners, cast throws and late reference-string reads."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import output_api_failure_sources as common

ROOT = common.ROOT
CASES = {'raw-invokable-owner-after-route': (b'<?php echo "P";class H{function __invoke($b,$p){return $this;}function _'
                                     b'_toString(){return "H";}function __destruct(){echo "D".ob_get_level();}}'
                                     b'ob_start(new H);echo "A";$x=ob_get_flush();echo "|".$x.":".ob_get_level('
                                     b');',
                                     b'PHD0|A:0'),
 'reference-string-late-cleanup-throw': (b'<?php echo "P";$s="H";$x=99;class D{function __destruct(){global $s;'
                                         b'$s="J";throw new Exception("E");}}class T{function &__toString(){glo'
                                         b'bal $s;$d=new D;return $s;}}function h($b,$p){return new T;}ob_start'
                                         b'("h");echo "A";try{$x=ob_get_flush();}catch(Exception $c){echo "|".$'
                                         b'x.":".$s.":".$c->getMessage().":".ob_get_level();}',
                                         b'PJ|99:J:E:0'),
 'body-throw-object-release-replaces-vm': (b'<?php\necho "P";$x=99;$once=true;$deprecations=0;\nclass T{functio'
                                           b'n __toString(){throw new Exception("E");}function __destruct(){e'
                                           b'cho "D";throw new Exception("F");}}\nset_error_handler(function()'
                                           b'{global $deprecations;$deprecations++;return true;});\nfunction h'
                                           b'($b,$p){global $once;if($once){$once=false;return new T;}return '
                                           b'"";}\nob_start("h",1);\ntry{$x=print "A";}catch(Exception $c){$s=o'
                                           b'b_get_status();$t=$c->getTrace();$p=$c->getPrevious();$u=$p->get'
                                           b'Trace();$report=$x.":".$c->getMessage().":".$p->getMessage().":"'
                                           b'.$s["flags"].":".$t[0]["function"].":".(isset($t[0]["file"])?"F"'
                                           b':"I").":".(isset($t[0]["line"])?$t[0]["line"]:-1).":".$u[0]["fun'
                                           b'ction"].":".(isset($u[0]["file"])?"F":"I").":".(isset($u[0]["lin'
                                           b'e"])?$u[0]["line"]:-1);}\n$y=print "B";$s=ob_get_status();ob_end_'
                                           b'clean();echo "|".$report.":".$y.":".$s["flags"].":".$deprecation'
                                           b's;\n',
                                           b'P|99:F:E:53361:__destruct:F:7:__toString:F:7:1:20593:1'),
 'unique-reference-object-gc-transfer': (b'<?php echo "P";$log="";class T{function __toString(){global $log;$lo'
                                         b'g.="S".gc_collect_cycles();return "H";}function __destruct(){global '
                                         b'$log;$s=ob_get_status();$log.="D".$s["flags"];}}function &h($b,$p){$'
                                         b'r=new T;return $r;}ob_start("h");echo "A";$x=ob_get_flush();echo "|"'
                                         b'.$x.":".$log;',
                                         b'PH|A:S0D113')}

CASES['deprecation-retval-object-api-trace'] = (
    b'<?php\necho "P";$x=99;$log="";\nclass R{function __destruct(){echo "W";throw new Exception("E");}}\nclass T{function __toString(){global $log;$log.="S";return "H";}function __destruct(){global $log;$s=ob_get_status();$log.="D".$s["flags"];}}\nfunction h($b,$p){echo "Q";return new T;}set_error_handler(function(){return new R;});\nob_start("h");echo "A";\ntry{$x=ob_get_flush();}catch(Exception $c){$t=$c->getTrace();echo "|".$x.":".$log.":".ob_get_level().":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[1]["function"])?$t[1]["function"]:"missing").":".(isset($t[1]["file"])&&$t[1]["file"]===__FILE__?"F":"N").":".(isset($t[1]["line"])?$t[1]["line"]:-1);}\n',
    b'PW|99:D113:0:__destruct:I:ob_get_flush:F:7')

CASES['deprecation-retval-quiet-object-api-trace'] = (
    b'<?php\necho "P";$x=99;$log="";\nclass R{function __destruct(){echo "W";throw new Exception("E");}}\nclass T{function __toString(){global $log;$log.="S";return "H";}}\nfunction h($b,$p){echo "Q";return new T;}set_error_handler(function(){return new R;});\nob_start("h");echo "A";\ntry{$x=ob_get_flush();}catch(Exception $c){$t=$c->getTrace();echo "|".$x.":".$log.":".ob_get_level().":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[1]["function"])?$t[1]["function"]:"missing").":".(isset($t[1]["file"])&&$t[1]["file"]===__FILE__?"F":"N").":".(isset($t[1]["line"])?$t[1]["line"]:-1);}\n',
    b'PW|99::0:__destruct:I:ob_get_flush:F:7')
SLOW_CASES = {'deprecation-retval-object-api-trace'}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_object_conversion_review_sources.py'] = common.sha(Path(__file__))
    for name in ('vendor/php-src/Zend/zend_operators.c', 'vendor/php-src/Zend/zend_operators.h',
                 'vendor/php-src/Zend/zend_object_handlers.c', 'vendor/php-src/Zend/zend_objects_API.c',
                 'vendor/php-src/Zend/zend_objects_API.h'):
        inputs[name] = common.sha(ROOT / name)
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else [name for name in CASES if name not in SLOW_CASES]
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-object-conversion-review-', dir=ROOT / '.tools'))
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
