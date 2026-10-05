#!/usr/bin/env python3
"""Independent ordinary-source Generator send/throw counterexamples."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from generator_review import run

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'send-fresh-target': (b'<?php\nfunction seq(){echo "B";$x=yield 1;echo $x;yield $x+1;return 9;}$g=seq();echo "C";echo $g->send(4),":",$g->current(),":",$g->key();$g->next();echo ":",$g->getReturn();', b'CB45:5:1:9'),
    'send-paused-expression': (b'<?php\nfunction seq(){echo "B";$x=yield 1;$y=yield $x;return $y;}$g=seq();echo $g->current(),":",$g->send(7),":",$g->current();echo $g->send(8)===null?"N":"X";echo $g->getReturn();', b'B1:7:7N8'),
    'next-yield-null': (b'<?php\nfunction seq(){$x=yield 1;echo $x===null?"N":"X";yield 2;}$g=seq();echo $g->current();$g->next();echo $g->current();$g->next();', b'1N2'),
    'send-ignored-result': (b'<?php\nfunction seq(){yield 1;echo "B";yield 2;}$g=seq();echo $g->send([9]);echo $g->send(8)===null?"N":"X";echo $g->getReturn()===null?"R":"X";', b'B2NR'),
    'send-fresh-empty-and-closed': (b'<?php\nfunction value(){echo "A";return 3;}function seq(){if(false)yield 1;echo "E";return 8;}$g=seq();echo "C";echo $g->send(value())===null?"N":"X";echo $g->send(value())===null?"N":"X";echo $g->getReturn();', b'CAENAN8'),
    'send-eager-scalar-capture': (b'<?php\n$v=4;$alias=&$v;function seq(){echo "B";$GLOBALS["v"]=9;$x=yield 1;echo $x;yield 2;}$g=seq();echo "C";echo $g->send($v),":",$v;$g->next();', b'CB42:9'),
    'send-array-reference-copy': (b'<?php\n$r=4;$a=[&$r];function seq(){$GLOBALS["r"]=9;$x=yield 1;yield $x;return $x;}$g=seq();$v=$g->send($a);$a[1]=8;echo $v[0],":",isset($g->current()[1])?"X":"N";$r=6;$g->next();echo ":",$g->getReturn()[0],":",isset($g->getReturn()[1])?"X":"N";', b'9:N:6:N'),
    'send-object-identity': (b'<?php\nclass Box{public $n=4;}$o=new Box;function seq(){$GLOBALS["o"]->n=9;$x=yield 1;yield $x;return $x;}$g=seq();echo $g->send($o)===$o?"I":"X";echo $g->current()->n;$g->next();echo $g->getReturn()===$o?"R":"X";', b'I9R'),
    'throw-fresh-catch': (b'<?php\nfunction seq(){echo "B";try{yield 1;}catch(Exception $e){echo $e->getMessage();yield 2;}return 8;}$g=seq();echo "C";echo $g->throw(new Exception("E"));$g->next();echo $g->getReturn();', b'CBE28'),
    'throw-paused-catch': (b'<?php\nfunction seq(){try{$x=yield 1;echo "X";}catch(Exception $e){echo $e->getMessage();yield 2;}yield 3;}$g=seq();echo $g->current();echo $g->throw(new Exception("E")),":",$g->key();$g->next();echo $g->current();$g->next();', b'1E2:13'),
    'throw-error-is-Throwable': (b'<?php\nfunction seq(){try{yield 1;}catch(Exception $e){echo "X";}catch(Error $e){echo $e->getMessage();yield 2;}}$g=seq();echo $g->throw(new Error("E"));$g->next();', b'E2'),
    'throw-closed-same-object': (b'<?php\nfunction seq(){yield 1;return 7;}$g=seq();$g->next();$e=new Exception("E");try{$g->throw($e);}catch(Exception $x){echo $x===$e?"I":"X";echo $x->getPrevious()===null?"N":"X";}echo $g->getReturn();', b'IN7'),
    'throw-fresh-empty-same-object': (b'<?php\nfunction seq(){if(false)yield 1;echo "B";return 7;}$g=seq();$e=new Exception("E");echo "C";try{$g->throw($e);}catch(Exception $x){echo $x===$e?"I":"X";}echo $g->getReturn();', b'CBI7'),
    'throw-fresh-initialization-exception': (b'<?php\nfunction seq(){echo "B";throw new Exception("initial");yield 1;}$g=seq();$e=new Exception("input");echo "C";try{$g->throw($e);}catch(Exception $x){echo $x===$e?"I":"X";echo ":",$x->getMessage(),":";echo $x->getPrevious()===null?"N":$x->getPrevious()->getMessage();}echo $g->valid()?"T":"F";', b'CBI:input:initialF'),
    'send-fresh-initialization-exception': (b'<?php\nfunction seq($p){throw new Exception("initial");yield 1;}function resume($g){$g->send(7);}$g=seq(3);try{resume($g);}catch(Exception $e){echo $e->getMessage(),":";foreach($e->getTrace() as $r){echo $r["function"],";";}}echo $g->valid()?"T":"F";', b'initial:seq;send;resume;F'),
    'throw-rethrow-live-resumer-trace': (b'<?php\nfunction seq($p){try{yield 1;}catch(Exception $e){throw new Exception("inner");}}function resume($g){$g->throw(new Exception("input"));}$g=seq(3);$g->current();try{resume($g);}catch(Exception $e){foreach($e->getTrace() as $r){echo $r["function"],":";if($r["function"]==="seq"){echo $r["args"][0];}elseif($r["function"]==="throw"){echo $r["args"][0]->getMessage();}echo ";";}}', b'seq:3;throw:input;resume:;'),
    'send-body-error-live-resumer-trace': (b'<?php\nfunction seq($p){$x=yield 1;throw new Exception("inner");}function resume($g){$g->send(7);}$g=seq(3);$g->current();try{resume($g);}catch(Exception $e){foreach($e->getTrace() as $r){echo $r["function"],":";if($r["function"]==="seq"||$r["function"]==="send"){echo $r["args"][0];}echo ";";}}', b'seq:3;send:7;resume:;'),
    'throw-finally-suspends': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";$x=yield 2;echo $x;}}$g=seq();$e=new Exception("E");echo $g->current(),"|";echo $g->throw($e),"|";try{$g->send("S");}catch(Exception $x){echo $x===$e?"I":"X";}echo $g->valid()?"T":"F";', b'1|F2|SIF'),
    'send-arity-eager-errors': (b'<?php\nfunction value($v){echo $v;return $v;}function seq(){echo "B";yield 1;}$g=seq();try{$g->send();}catch(ArgumentCountError $e){echo "Z";}try{$g->send(value(3),value(4));}catch(ArgumentCountError $e){$t=$e->getTrace();echo $t[0]["function"],":",$t[0]["args"][0],":",$t[0]["args"][1];}echo $g->current();$g->next();', b'Z34send:3:4B1'),
    'throw-type-validation-before-init': (b'<?php\nfunction seq(){echo "B";yield 1;}$g=seq();try{$g->throw(new stdClass);}catch(TypeError $e){echo "T";}try{$g->throw(null);}catch(TypeError $e){echo "N";}echo $g->current();$g->next();', b'TNB1'),
    'send-two-yield-expression': (b'<?php\nfunction seq(){$x=(yield 1)+(yield 2);return $x;}$g=seq();echo $g->send(5);echo $g->send(7)===null?"N":"X";echo $g->getReturn();', b'2N12'),
    'send-argument-throw-keeps-paused': (b'<?php\nfunction argument(){echo "A";throw new Exception("E");}function seq(){$x=yield 1;echo $x;yield 2;}$g=seq();echo $g->current();try{$g->send(argument());}catch(Exception $e){echo "E";foreach($e->getTrace() as $r){echo $r["function"],";";}}echo $g->current(),":",$g->key();echo $g->send(8);$g->next();', b'1AEargument;1:082'),
    'reentrant-send-throw': (b'<?php\nfunction seq(){$x=yield 1;try{$GLOBALS["g"]->send(4);}catch(Error $e){echo "S";}try{$GLOBALS["g"]->throw(new Exception("E"));}catch(Error $e){echo "T";}echo $x,":",$GLOBALS["g"]->current();yield 3;}$g=seq();echo $g->send(2);$g->next();', b'ST2:13'),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['pin', 'native', 'full'], default='full')
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES)
    assert names and len(set(names)) == len(names) and all(n in CASES for n in names)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    php = ROOT / '.tools/php/bin/php'
    flags = [v for key, value in profile.items() for v in ['-d', f'{key}={value}']]
    directory = Path(tempfile.mkdtemp(prefix='generator-effects-review-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'mode': args.mode, 'records': [], 'agreements': 0,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'tools': {'php_sha256': hashlib.sha256(php.read_bytes()).hexdigest(),
                        'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    print(directory, flush=True)
    try:
        (directory / 'candidate.diff').write_bytes(subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT))
        (directory / 'case-fixture.py').write_bytes(Path(__file__).read_bytes())
        identity = run([str(php), '-n', *flags, '-r', 'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,get_loaded_extensions(),ini_get_all(null,false)]);'], directory / 'runtime', 10)
        assert identity.returncode == 0 and not identity.stderr
        report['runtime'] = json.loads(identity.stdout)
        assert report['runtime'][:4] == ['8.5.10', 'cli', 8, False]
        assert all(report['runtime'][5][key] == value for key, value in profile.items())
        if args.mode == 'full':
            report['tools']['adapter_sha256'] = hashlib.sha256((ROOT / '_build/default/adapter/main.exe').read_bytes()).hexdigest()
        for name in names:
            case = directory / name
            case.mkdir()
            source, expected = CASES[name]
            path = case / 'source.php'
            path.write_bytes(source)
            row = {'id': name, 'source_sha256': hashlib.sha256(source).hexdigest()}
            report['records'].append(row)
            native = run([str(php), '-n', *flags, str(path)], case / 'native', 10)
            row.update(native_exit=native.returncode, native_stdout=base64.b64encode(native.stdout).decode(), native_stderr=base64.b64encode(native.stderr).decode())
            assert native.returncode == 0 and not native.stderr, (name, native)
            if args.mode != 'pin':
                assert expected is not None and native.stdout == expected, (name, native.stdout, expected)
            if args.mode == 'full':
                model = run([str(ROOT / 'bin/php-semantics'), str(path), '--steps', '100000', '--timeout', '60'], case / 'model', 90)
                row['model_exit'] = model.returncode
                assert not model.stderr, (name, model.stderr)
                observation = json.loads(model.stdout)
                row['model_status'] = observation['status']
                assert model.returncode == 0 and observation['status'] == 'normal', (name, observation)
                assert observation['frontend'] == 'accepted' and observation['checked'] == 'program'
                assert observation['reason'] is None and observation['diagnostic'] is None
                assert observation['exit_status'] == native.returncode
                assert base64.b64decode(observation['stdout'], validate=True) == native.stdout
                assert base64.b64decode(observation['stderr'], validate=True) == native.stderr
                report['agreements'] += 1
            row['passed'] = True
            print(name, repr(native.stdout), 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(directory / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()
