#!/usr/bin/env python3
"""Source/native declaration notices and file/eval publication ordering."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import user_iterator as iterator

ROOT = Path(__file__).resolve().parents[2]
METHODS = '\n'.join(iterator.METHODS.values())
BARE = METHODS.replace(':mixed', '').replace(':void', '').replace(':bool', '')
CURRENT = METHODS.replace('current():mixed', 'current()')
HANDLER = 'function notice($level,$message,$file,$line){echo $level,":",$message,";";return true;} set_error_handler("notice");'
PARENT = 'abstract class ParentIt implements Iterator {}'


def cls(name='It', methods=CURRENT, parent='', interfaces='Iterator'):
    return ('class ' + name + (' extends ' + parent if parent else '') +
            (' implements ' + interfaces if interfaces else '') +
            '{public $i=0;\n' + methods + '\n}')


def literal(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"


def php(text):
    return ('<?php\n' + text).encode()


def fatal_formatter(body):
    code = (cls('A', parent='ParentIt', interfaces='') + '\n' +
            cls('B', CURRENT.replace('next():void', 'next($x):void'), parent='ParentIt', interfaces='') + 'echo "BAD";')
    return php(PARENT + '\nclass NoticeException extends Exception {function __toString():string {' + body + '}}\n' +
               'function notice(){echo "H";throw new NoticeException("handler");}set_error_handler("notice");\n' +
               'try{eval(' + literal(code) + ');}catch(Exception $e){echo "caught";}echo "BAD";')


CASES = {
    'runtime-order': {'source': php(HANDLER + '\nif(true){' + cls(methods=BARE) + '}echo "D";')},
    'runtime-readiness': {'source': php('function notice($l,$m,$f,$n){echo "H";foreach(new It as $k=>$v){echo $k,":",$v;break;}return true;}set_error_handler("notice");\nif(true){' + cls() + '}echo "D";')},
    'runtime-throw-eligible-tail': {'source': php('function notice(){echo "H";throw new Exception("x");}set_error_handler("notice");try{if(true){' + cls(methods=BARE) + '}}catch(Exception $e){echo "C";}echo (new It) instanceof Traversable?"1":"0";')},
    'runtime-throw-ineligible-tail': {'source': php('function notice(){echo "H";set_error_handler("notice",E_WARNING);throw new Exception("x");}set_error_handler("notice");try{if(true){' + cls(methods=BARE) + '}}catch(Exception $e){echo "C";}echo (new It) instanceof Iterator?"1":"0";')},
    'runtime-prefix-hard': {'source': php(HANDLER + '\nif(true){' + cls(methods=CURRENT.replace('next():void', 'next($x):void')) + '}')},
    'runtime-prefix-constant': {'source': php('interface HasC {public const int C=1;}\n' + HANDLER + '\necho "B";try{if(true){' + cls(methods='public const string C="x";\n' + CURRENT, interfaces='Iterator,HasC') + '}}catch(CompileError $e){echo "caught";}echo "BAD";')},
    'runtime-constant-first': {'source': php('interface HasC {public const int C=1;}\n' + HANDLER + '\necho "B";try{if(true){' + cls(methods='public const string C="x";\n' + CURRENT, interfaces='HasC,Iterator') + '}}catch(CompileError $e){echo "caught";}echo "BAD";')},
    'source-erases-prototype': {'source': php(HANDLER + '\ninterface Seq extends Iterator {function current();}\n' + cls(methods=BARE, interfaces='Seq') + 'echo "D";')},
    'direct-restores-first': {'source': php(HANDLER + '\ninterface Seq extends Iterator {function current();}\n' + cls(methods=BARE, interfaces='Iterator,Seq') + 'echo "D";')},
    'direct-restores-last': {'source': php(HANDLER + '\ninterface Seq extends Iterator {function current();}\n' + cls(methods=BARE, interfaces='Seq,Iterator') + 'echo "D";')},
    'suppressor-global': {'source': php(HANDLER + '\n' + cls(methods=CURRENT.replace('function current()', '#[ReturnTypeWillChange] function current()')) + 'echo "D";')},
    'suppressor-import': {'source': php('namespace Box;use ReturnTypeWillChange as Quiet;\n' + cls(methods=CURRENT.replace('function current()', '#[Quiet] function current()'), interfaces='\\Iterator') + 'echo "D";')},
    'runtime-eval-direct': {'source': php(HANDLER + '\neval(' + literal(cls()) + ');echo "D";')},
    'early-file-later-ready': {'source': php('function notice($l,$m,$f,$n){echo "H";foreach(new B as $k=>$v){echo $k,":",$v;break;}return true;}set_error_handler("notice");\n' + PARENT + '\ninclude __DIR__."/unit.php";echo "D";'), 'unit': php(cls('A', parent='ParentIt', interfaces='') + '\n' + cls('B', parent='ParentIt', interfaces='') + 'echo "U";')},
    'early-file-throw-published': {'source': php('function notice(){echo "H";throw new Exception("x");}set_error_handler("notice");\n' + PARENT + '\ntry{include __DIR__."/unit.php";}catch(Exception $e){echo "C";}echo (new A) instanceof Iterator?"1":"0";echo (new B) instanceof Iterator?"1":"0";'), 'unit': php(cls('A', parent='ParentIt', interfaces='') + '\n' + cls('B', parent='ParentIt', interfaces='') + 'echo "BAD";')},
    'early-file-mixed-warnings': {'source': php(HANDLER + '\n' + PARENT + '\ninclude __DIR__."/unit.php";echo "D";'), 'unit': php(cls('A', parent='ParentIt', interfaces='') + '\nclass W {protected function __invoke(){}}\n' + cls('B', parent='ParentIt', interfaces='') + 'echo "U";')},
    'early-file-mixed-fatal-prefix': {'source': php(HANDLER + '\n' + PARENT + '\ninclude __DIR__."/unit.php";echo "BAD";'), 'unit': php(cls('A', parent='ParentIt', interfaces='') + '\nclass W {protected function __invoke(){}}\n' + cls('B', CURRENT.replace('next():void', 'next($x):void'), parent='ParentIt', interfaces='') + 'echo "BAD";')},
    'early-eval-per-class': {'source': php(HANDLER + '\n' + PARENT + '\neval(' + literal(cls('A', parent='ParentIt', interfaces='') + cls('B', parent='ParentIt', interfaces='')) + ');echo "D";')},
    'early-eval-fatal-prefix': {'source': php(HANDLER + '\n' + PARENT + '\neval(' + literal(cls('B', CURRENT.replace('next():void', 'next($x):void'), parent='ParentIt', interfaces='')) + ');')},
    'early-eval-success-before-fatal': {'source': php(HANDLER + '\n' + PARENT + '\neval(' + literal(cls('A', parent='ParentIt', interfaces='') + cls('B', CURRENT.replace('next():void', 'next($x):void'), parent='ParentIt', interfaces='')) + ');')},
    'early-eval-compiler-warning': {'source': php(HANDLER + '\neval(' + literal('class W {protected function __invoke(){}}') + ');echo "D";')},
    'early-eval-throw-publications': {'source': php('function notice(){echo "H";throw new Exception("held");}set_error_handler("notice");\n' + PARENT + '\ntry{eval(' + literal(cls('A', parent='ParentIt', interfaces='') + cls('B', parent='ParentIt', interfaces='') + 'echo "BAD";') + ');}catch(Exception $e){echo "C:",$e->getMessage(),";";}echo (new A) instanceof Iterator?"A":"a";echo (new B) instanceof Iterator?"B":"b";')},
    'early-eval-exit-publications': {'source': php('function notice(){echo "H";exit(7);}function finish(){echo "S";try{new A;echo "A";}catch(Throwable $e){echo "a";}try{new B;echo "B";}catch(Throwable $e){echo "b";}}register_shutdown_function("finish");set_error_handler("notice");\n' + PARENT + '\neval(' + literal(cls('A', parent='ParentIt', interfaces='') + cls('B', parent='ParentIt', interfaces='') + 'echo "BAD";') + ');echo "BAD";')},
    'early-eval-user-fatal-stops': {'source': php('function notice(){echo "H";trigger_error("stop",256);}function finish(){echo "S";try{new A;echo "A";}catch(Throwable $e){echo "a";}try{new B;echo "B";}catch(Throwable $e){echo "b";}}register_shutdown_function("finish");set_error_handler("notice");\n' + PARENT + '\neval(' + literal(cls('A', parent='ParentIt', interfaces='') + cls('B', parent='ParentIt', interfaces='') + 'echo "BAD";') + ');echo "BAD";')},
    'early-eval-formatter-exit': {'source': fatal_formatter('echo "F";exit(7);')},
    'early-eval-formatter-throw': {'source': fatal_formatter('echo "F";throw new Exception("secondary");')},
    'early-eval-formatter-recorded-read': {'source': fatal_formatter('echo "F";echo $missing;return "formatted";')},
    'early-eval-formatter-user-fatal': {'source': fatal_formatter('echo "F";trigger_error("nested",256);return "formatted";')},
    'early-eval-formatter-nested-hard': {'source': fatal_formatter('echo "F";eval(' + literal(cls('InnerBad', CURRENT.replace('next():void', 'next($x):void'), parent='ParentIt', interfaces='')) + ');return "formatted";')},
    'early-eval-formatter-file-hard': {'source': fatal_formatter('echo "F";include __DIR__."/unit.php";return "formatted";'),
                                       'unit': php(cls('InnerBad', CURRENT.replace('next():void', 'next($x):void'), parent='ParentIt', interfaces=''))},
}


def b64(data):
    return base64.b64encode(data).decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES)
    assert names and len(set(names)) == len(names) and all(name in CASES for name in names)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    out = Path(tempfile.mkdtemp(prefix='iterator-notices-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, Path(__file__), ROOT / 'spec/semantics/modules.json',
              ROOT / '_build/default/adapter/main.exe', iterator.driver.types.PHP]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    report = {'result': 'fail', 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': iterator.driver.types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'inputs': before, 'selected': names, 'records': []}
    (out / 'candidate.diff').write_bytes(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT))
    try:
        report['runtime'] = iterator.runtime(out)
        for name in names:
            case = CASES[name]
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(case['source'])
            command = [str(ROOT / 'bin/php-semantics'), str(path), '--steps', '100000', '--timeout', '240']
            if 'unit' in case:
                unit = directory / 'unit.php'
                unit.write_bytes(case['unit'])
                snapshot = {'version': 1, 'main': b64(os.fsencode(path)), 'cwd': b64(os.fsencode(directory)),
                            'include_path': b64(b'.:'), 'entries': [{'caller': b64(os.fsencode(path)),
                            'requested': b64(os.fsencode(unit)), 'status': 'opened', 'resolved': b64(os.fsencode(unit)),
                            'opened': b64(os.fsencode(unit)), 'source': b64(case['unit'])}]}
                snapshot_path = directory / 'snapshot.json'
                snapshot_path.write_text(json.dumps(snapshot, indent=2) + '\n')
                command += ['--file-snapshot', str(snapshot_path)]
            native_command = [str(iterator.driver.types.PHP), '-n', *iterator.driver.types.FLAGS, str(path)]
            native = iterator.process(native_command, directory / 'native', 10, directory)
            model = iterator.process(command, directory / 'model', 270, directory)
            row = {'id': name, 'source_sha256': hashlib.sha256(case['source']).hexdigest(),
                   'native_command': native_command, 'model_command': command, 'cwd': str(directory),
                   'native_exit': native.returncode, 'model_exit': model.returncode}
            report['records'].append(row)
            assert model.returncode == 0 and not model.stderr, (name, model.stderr)
            observation = json.loads(model.stdout)
            row['status'] = observation['status']
            assert observation['status'] in ['normal', 'php_error', 'static_rejection', 'explicit_exit'], observation
            assert observation['exit_status'] == native.returncode, (name, observation, native.stderr)
            assert base64.b64decode(observation['stdout'], validate=True) == native.stdout, (name, observation, native.stdout)
            assert base64.b64decode(observation['stderr'], validate=True) == native.stderr, (name, observation, native.stderr)
            row['passed'] = True
            print(name, 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['stable_inputs'] = before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()
