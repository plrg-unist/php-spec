#!/usr/bin/env python3
"""Prepared internal default constructors: lossless scalar, hole and trace paths."""
import argparse
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'internal-default-basic': b'<?php function f(Exception $x=new Exception(message:"m",code:7)){echo $x->getMessage(),"|",$x->getCode(),"|",$x->getLine();}f();\n',
    'inherited-internal-all-values': b'<?php class C extends Exception{}function h($a,$b,$c,$d){echo "D|";return true;}set_error_handler("h");function f($x=new C(missing:1,code:E_STRICT)){echo "BAD";}try{f();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'internal-strict-definition': b'<?php declare(strict_types=1);\nfunction take($e=new Exception(message:7)){echo "BAD";}\ntry{take();}catch(TypeError $e){echo "E";}\n',
    'internal-strict-caller-weak-default': b'<?php declare(strict_types=1);\neval(\'function take($e=new Exception(message:7,code:"8")){echo $e->getMessage(),"/",$e->getCode();}\');\ntake();\n',
    'internal-weak-caller-strict-default': b'<?php\neval(\'declare(strict_types=1);function take($e=new Exception(message:7)){echo "BAD";}\');\ntry{take();}catch(TypeError $e){echo "E";}\n',
    'internal-named-hole-previous': b'<?php\nfunction take($e=new Exception(previous:new Exception("inner"))){echo $e->getMessage(),"/",$e->getCode(),"/",$e->getPrevious()->getMessage();}\ntake();\n',
    'internal-errorexception-fields': b'<?php\nfunction take($e=new ErrorException(previous:new Exception("inner"),line:19,filename:"virtual.php",severity:4,code:7,message:"outer")){echo $e->getMessage(),"/",$e->getCode(),"/",$e->getSeverity(),"/",$e->getFile(),"/",$e->getLine(),"/",$e->getPrevious()->getMessage();}\ntake();\n',
    'internal-extra-values-before-arity': b'<?php\nfunction h($level,$message,$file,$line){echo "D|";return true;}\nset_error_handler("h");\nfunction take($e=new Exception("m",7,null,E_STRICT)){echo "BAD";}\ntry{take();}catch(ArgumentCountError $e){echo "E|",$e->getMessage();}\n',
    'internal-default-type-error-trace-core': b'<?php\nfunction take(\n    $e =\n        new Exception(code:"bad")\n){echo "BAD";}\ntry{take();}catch(TypeError $e){\n    $t=$e->getTrace();\n    $n=0;foreach($t[0]["args"] as $arg){$n=$n+1;}\n    echo $e->getLine(),"|",$t[0]["function"],"|",$t[0]["class"],"|",$t[0]["line"],"|",$t[1]["function"],"|",$t[1]["line"],"|",$n,"|",$t[0]["args"][0]===""?"empty":"other","|",$t[0]["args"][1];\n}\n',
    'internal-strict-null-message': b'<?php declare(strict_types=1);\nfunction h($level,$message,$file,$line){echo "D|";return true;}\nset_error_handler("h");\nfunction take($e=new Exception(message:null)){echo "BAD";}\ntry{take();}catch(TypeError $e){echo "E";}\n',
    'internal-strict-null-code': b'<?php declare(strict_types=1);\nfunction h($level,$message,$file,$line){echo "D|";return true;}\nset_error_handler("h");\nfunction take($e=new Exception(code:null)){echo "BAD";}\ntry{take();}catch(TypeError $e){echo "E";}\n',
    'internal-strict-null-severity': b'<?php declare(strict_types=1);\nfunction h($level,$message,$file,$line){echo "D|";return true;}\nset_error_handler("h");\nfunction take($e=new ErrorException(severity:null)){echo "BAD";}\ntry{take();}catch(TypeError $e){echo "E";}\n',
    'internal-nullable-line': b'<?php declare(strict_types=1);\nfunction take($e=new ErrorException(filename:"virtual.php",line:null)){echo $e->getFile(),"/",$e->getLine(),"/",$e->getSeverity();}\ntake();\n',
    'inherited-internal-omitted-message': b'<?php\nclass C extends Exception{protected $message="seed";}\nfunction omitted($e=new C()){echo $e->getMessage(),"|";}\nfunction previous($e=new C(previous:new Exception("inner"))){echo $e->getMessage(),"/",$e->getPrevious()->getMessage();}\nomitted();previous();\n',
    'affected-direct-default-constructor': b'<?php class A{function __construct(){echo "C",func_num_args(),"|";}function __toString(){echo "T",func_num_args(),"|";return "s";}}class S extends A{}function take(string $s=new A){echo "F",func_num_args(),"|",$s;}take();',
    'internal-coerced-message-error-trace': b'<?php\nfunction take($e=new Exception(message:7,code:"bad")){echo "BAD";}\ntry{take();}catch(TypeError $e){$t=$e->getTrace();echo $t[0]["args"][0]==="7"?"string":"other","|",$t[0]["args"][0];}\n',
    'internal-coerced-filename-error-trace': b'<?php\nfunction take($e=new ErrorException(filename:7,line:"bad")){echo "BAD";}\ntry{take();}catch(TypeError $e){$t=$e->getTrace();echo $t[0]["args"][3]==="7"?"string":"other","|",$t[0]["args"][3];}\n',
}
EXPECTED = {
    'internal-default-basic': b'm|7|1',
    'inherited-internal-all-values': b'D|E|Unknown named parameter $missing',
    'internal-strict-definition': b'E',
    'internal-strict-caller-weak-default': b'7/8',
    'internal-weak-caller-strict-default': b'E',
    'internal-named-hole-previous': b'/0/inner',
    'internal-errorexception-fields': b'outer/7/4/virtual.php/19/inner',
    'internal-extra-values-before-arity': b'D|E|Exception::__construct() expects at most 3 arguments, 4 given',
    'internal-default-type-error-trace-core': b'3|__construct|Exception|3|take|6|2|empty|bad',
    'internal-strict-null-message': b'E',
    'internal-strict-null-code': b'E',
    'internal-strict-null-severity': b'E',
    'internal-nullable-line': b'virtual.php/0/1',
    'inherited-internal-omitted-message': b'seed|/inner',
    'affected-direct-default-constructor': b'C0|T0|F0|s',
    'internal-coerced-message-error-trace': b'string|7',
    'internal-coerced-filename-error-trace': b'string|7',
}
OWNER_SOURCE = b'<?php\nfunction take(Exception $e=new Exception(previous:new Exception("inner"),code:7,message:"outer")){echo $e->getMessage(),"/",$e->getCode(),"/",$e->getPrevious()->getMessage();}\ntake();\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='internal-default-constructors-', dir=ROOT / '.tools'))
    report = {'passed': False, 'completed': False, 'before': before,
              'profile': cross.invoke.types.PROFILE, 'selected': selected, 'records': []}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source = directory / 'source.php'; source.write_bytes(CASES[name])
            row = {'case': name, 'source_sha256': cross.invoke.sha(source), 'completed': False}
            report['records'].append(row)
            row['outcome'] = cross.source({'abrupt': False, 'expected_exit_status': 0,
                'expected_stdout': EXPECTED[name].decode()}, directory, source)
            row['completed'] = True
            print(name, row['outcome']['status'], flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(args.freeze)
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
