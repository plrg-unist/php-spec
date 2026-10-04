#!/usr/bin/env python3
"""Internal-default warnings and Stringable conversion retain real callback owners."""
import argparse
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'internal-constructor-weak-stringable': b'<?php\nclass V{function __toString(){echo "T|";return "message";}}\nfunction take($e=new Exception(message:new V)){echo "F|",$e->getMessage();}\ntake();\n',
    'internal-null-message-handler-throw': b'<?php\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";throw new Exception("stop");}\nset_error_handler("h");\nfunction take($e=new Exception(message:null)){echo "BAD";}\ntry{take();}catch(Exception $e){echo "E|",$e->getMessage();}\n',
    'internal-fractional-code-warnings': b'<?php\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";return true;}\nset_error_handler("h");\nfunction fractional($e=new Exception(code:1.5)){echo "F",$e->getCode(),"|";}\nfunction numeric($e=new Exception(code:"1.5")){echo "S",$e->getCode();}\nfractional();numeric();\n',
    'internal-stringable-throw-trace': b'<?php\nclass V{function __toString(){throw new Exception("stop");}}\nfunction take($e=new Exception(message:new V)){echo "BAD";}\ntry{take();}catch(Exception $e){\n    $t=$e->getTrace();\n    echo $e->getMessage(),"|",$t[0]["function"],"|",isset($t[0]["file"])?"source":"internal","|",$t[1]["function"],"|",$t[1]["class"],"|",$t[1]["line"],"|",$t[1]["args"][0] instanceof V?"object":"other","|",$t[2]["function"];\n}\n',
    'internal-filename-stringable': b'<?php\nclass V{function __toString(){echo "T|";return "virtual.php";}}\nfunction take($e=new ErrorException(filename:new V)){echo "F|",$e->getFile();}\ntake();\n',
    'internal-effects-names-before-string': b'<?php\nclass V{function __toString(){echo "T|";return "message";}}\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";return true;}\nset_error_handler("h");\nfunction take($e=new ErrorException(message:new V,unknown:E_STRICT)){echo "BAD";}\ntry{take();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'internal-null-aborts-filename': b'<?php\nclass V{function __construct(){echo "C|";}function __toString(){echo "T|";return "virtual.php";}}\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";throw new Exception("stop");}\nset_error_handler("h");\nfunction take($e=new ErrorException(message:null,filename:new V)){echo "BAD";}\ntry{take();}catch(Exception $e){echo "E|",$e->getMessage();}\n',
    'internal-string-before-null-error-trace': b'<?php\nclass V{function __toString(){echo "T|";return "message";}}\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";throw new Exception("stop");}\nset_error_handler("h");\nfunction take($e=new Exception(message:new V,code:null)){echo "BAD";}\ntry{take();}catch(Exception $e){\n    $t=$e->getTrace();\n    echo $e->getMessage(),"|",$t[0]["function"],"|",isset($t[0]["file"])?"source":"internal","|",$t[1]["function"],"|",$t[1]["class"],"|",$t[1]["args"][0]==="message"?"string":"other","|",$t[1]["args"][0],"|",$t[1]["args"][1]===null?"null":"other";\n}\n',
    'internal-warning-string-order': b'<?php\nclass V{function __toString(){echo "T|";return "virtual.php";}}\n$i=0;\nfunction h($level,$message,$file,$line){global $i;echo "D",++$i,"|";return true;}\nset_error_handler("h");\nfunction take($e=new ErrorException(code:1.5,severity:"2.5",filename:new V,line:3.5)){echo "F|",$e->getCode(),"/",$e->getSeverity(),"/",$e->getFile(),"/",$e->getLine();}\ntake();\n',
    'internal-weak-null-strict-caller': b'<?php\ndeclare(strict_types=1);\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";return true;}\nset_error_handler("h");\neval(\'function take($e=new Exception(message:null)){echo "F|",$e->getMessage()===""?"empty":"other";}\');\ntake();\n',
    'internal-filename-owner-retirement': b'<?php\nclass V{public $text="before";function __construct(){$GLOBALS["v"]=$this;}function __toString(){echo "T",$this->text,"|";return $this->text;}}\nfunction h($level,$message,$file,$line){global $v;echo "D",func_num_args(),"|";$v->text="after";unset($GLOBALS["v"]);return true;}\nset_error_handler("h");\nfunction take($e=new ErrorException(message:null,filename:new V)){echo "F|",$e->getFile();}\ntake();\n',
    'internal-stringable-reentrant-default': b'<?php\n$i=0;\nclass V{function __toString(){global $i;++$i;echo "T",$i,"|";if($i===1){take();}return "v";}}\nfunction take($e=new Exception(message:new V)){echo "F|";}\ntake();\n',
    'internal-reentrant-handler-trace': b'<?php\n$i=0;\nclass V{function __toString(){global $i;echo "T",$i,"|";return "m".$i;}}\nfunction h($level,$message,$file,$line){global $i;++$i;echo "D",$i,"|";if($i===1){set_error_handler("h");take();}throw new Exception("stop");}\nset_error_handler("h");\nfunction take($e=new Exception(message:new V,code:null)){echo "BAD";}\ntry{take();}catch(Exception $e){$t=$e->getTrace();echo $t[1]["args"][0],"/",$t[4]["args"][0];}\n',
    'internal-private-handler-scope': b'<?php\nclass A{\n    private static function h($level,$message,$file,$line){echo "H|";return true;}\n    static function install(){set_error_handler([A::class,"h"]);}\n    static function take($e=new Exception(code:null)){echo "F";}\n}\nA::install();\ntry{A::take();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'internal-builtin-throwable-stringable': b'<?php\nfunction take($e=new Exception(message:new Exception("inner"))){$m=$e->getMessage();echo $m[0],$m[1],$m[2],$m[3],$m[4],$m[5],$m[6],$m[7],$m[8],$m[9],$m[10],$m[11],$m[12],$m[13],$m[14],$m[15];}\ntake();\n',
    'internal-null-handler-false': b'<?php\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";return false;}\nset_error_handler("h");\nerror_reporting(0);\nfunction take($e=new Exception(message:null)){echo "F|",$e->getMessage()===""?"empty":"other";}\ntake();\n',
}
EXPECTED = {
    'internal-constructor-weak-stringable': b'T|F|message',
    'internal-null-message-handler-throw': b'D4|E|stop',
    'internal-fractional-code-warnings': b'D4|F1|D4|S1',
    'internal-stringable-throw-trace': b'stop|__toString|internal|__construct|Exception|3|object|take',
    'internal-filename-stringable': b'T|F|virtual.php',
    'internal-effects-names-before-string': b'D4|E|Unknown named parameter $unknown',
    'internal-null-aborts-filename': b'C|D4|E|stop',
    'internal-string-before-null-error-trace': b'T|D4|stop|h|internal|__construct|Exception|string|message|null',
    'internal-warning-string-order': b'D1|D2|T|D3|F|1/2/virtual.php/3',
    'internal-weak-null-strict-caller': b'D4|F|empty',
    'internal-filename-owner-retirement': b'D4|Tafter|F|after',
    'internal-stringable-reentrant-default': b'T1|T2|F|F|',
    'internal-reentrant-handler-trace': b'T0|D1|T1|D2|m1/m0',
    'internal-private-handler-scope': b'H|F',
    'internal-builtin-throwable-stringable': b'Exception: inner',
    'internal-null-handler-false': b'D4|F|empty',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='internal-default-reception-', dir=ROOT / '.tools'))
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
