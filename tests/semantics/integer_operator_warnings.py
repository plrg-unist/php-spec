#!/usr/bin/env python3
"""Original scalar integer operators across conversion callbacks."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import ENV, recorded

ROOT = Path(__file__).resolve().parents[2]
OPERATORS = ('%', '<<', '>>', '&', '|', '^')
CASES = {}

for index, operator in enumerate(OPERATORS):
    CASES['live-right-' + str(index)] = f'''<?php
function h($n,$m,$f,$l) {{ echo "H:",$n,":",$m,":",$l,";"; $GLOBALS['b']=3.9; return true; }}
set_error_handler('h'); $a=11.5; $b=5;
$v=$a {operator} $b;
echo "V:",$v,":",$v===((int)$v),":",$a,":",$b,";";
'''.encode()
    CASES['reference-rebind-' + str(index)] = f'''<?php
function h($n,$m,$f,$l) {{ echo "H;"; $GLOBALS['b']=&$GLOBALS['c']; return true; }}
set_error_handler('h'); $a=5.75; $old=1; $b=&$old; $c=3;
$v=$a {operator} $b;
echo $v,":",$b,":",$old,";";
'''.encode()
    CASES['right-failure-' + str(index)] = f'''<?php
function h($n,$m,$f,$l) {{ $GLOBALS['a']=true; return true; }}
set_error_handler('h'); $a=5.75; $b=[];
try {{ $v=$a {operator} $b; echo "wrong"; }} catch (TypeError $e) {{ echo $e->getMessage(),";"; }}
echo $a===true;
'''.encode()

CASES.update({
    'leading-frozen': b'''<?php
function h($n,$m,$f,$l) { echo "H:",$n,":",$m,";"; $GLOBALS['a']='99.75tail'; $GLOBALS['b']=5; return true; }
set_error_handler('h'); $a='12.5tail'; $b=7;
$v=$a % $b; echo "V:",$v,":",$a,":",$b;
''',
    'same-cv': b'''<?php
function h($n,$m,$f,$l) { echo "H;"; $GLOBALS['a']=3; return true; }
set_error_handler('h'); $a=5.75; $v=$a % $a; echo $v,":",$a;
''',
    'throw-first': b'''<?php
$failure=new Exception('stop');
function h($n,$m,$f,$l) { echo "H:",$n,";"; throw $GLOBALS['failure']; }
set_error_handler('h'); $a='12.5tail'; $b=7;
try { $v=$a % $b; echo "wrong"; } catch (Exception $e) { echo "C:",$e===$failure,";"; }
echo $a,":",$b;
''',
    'throw-second': b'''<?php
$failure=new Exception('stop'); $count=0;
function h($n,$m,$f,$l) { ++$GLOBALS['count']; echo "H:",$n,";"; if ($GLOBALS['count']===2) { throw $GLOBALS['failure']; } return true; }
set_error_handler('h'); $a='12.5tail'; $b=7;
try { $v=$a % $b; echo "wrong"; } catch (Exception $e) { echo "C:",$e===$failure,";"; }
echo $count;
''',
    'false-fallback': b'''<?php
function h($n,$m,$f,$l) { echo "H:",$n,";"; return false; }
set_error_handler('h'); $a='12.5tail'; $b=5;
echo "V:",$a % $b;
''',
    'suppressed-fallback': b'''<?php
function h($n,$m,$f,$l) { echo "H:",$n,";"; return false; }
set_error_handler('h'); $a='12.5tail'; $b=5;
$v=@($a % $b); echo "V:",$v;
''',
    'mod-zero': b'''<?php
function h($n,$m,$f,$l) { echo "H;"; $GLOBALS['b']=0; return true; }
set_error_handler('h'); $a=5.75; $b=2;
try { $v=$a % $b; echo "wrong"; } catch (DivisionByZeroError $e) { echo $e->getMessage(); }
''',
    'shift-negative': b'''<?php
function h($n,$m,$f,$l) { echo "H;"; $GLOBALS['b']=-1; return true; }
set_error_handler('h'); $a=5.75; $b=2;
try { $v=$a << $b; echo "wrong"; } catch (ArithmeticError $e) { echo $e->getMessage(); }
''',
    'right-leading': b'''<?php
function h($n,$m,$f,$l) { echo "H:",$n,":",$m,";"; $GLOBALS['a']=true; $GLOBALS['b']='99.75tail'; return true; }
set_error_handler('h'); $a=12; $b='5.5tail';
echo "V:",$a % $b,":",$a,":",$b;
''',
    'two-strings': b'''<?php
function h($n,$m,$f,$l) { echo "wrong"; return true; }
set_error_handler('h'); $a='12.5tail'; $b='5.5tail';
echo $a & $b,":",$a | $b,":",$a ^ $b;
''',
    'handler-replacement': b'''<?php
function h2($n,$m,$f,$l) { echo "B:",$n,";"; return true; }
function h1($n,$m,$f,$l) { echo "A:",$n,";"; set_error_handler('h2'); return true; }
set_error_handler('h1'); $a='12.5tail'; $b=5; echo $a % $b;
''',
    'fixed-bitwise-dispatch': b'''<?php
function h($n,$m,$f,$l) { echo "H:",$n,";"; $GLOBALS['a']='12.5'; $GLOBALS['b']='3'; return true; }
set_error_handler('h'); $a=5.75; $b=3; $v=$a & $b; echo $v,":",$v===1;
''',
    'borrowed-left-failure': b'''<?php
function h($n,$m,$f,$l) { $GLOBALS['a']=&$GLOBALS['c']; return true; }
set_error_handler('h'); $a=5.75; $keep=&$a; $c=true; $b=[];
try { $v=$a % $b; echo "wrong"; } catch (TypeError $e) { echo $e->getMessage(),";"; }
echo $a===true,":",$keep===5.75;
''',
    'multiline': b'''<?php
function h($n,$m,$f,$l) { echo $l,";"; return true; }
set_error_handler('h'); $a=5.75; $b=3;
$v=$a
  %
  $b;
echo $v;
''',
})

for name, value in (('nan', 'NAN'), ('infinity', 'INF'), ('negative-infinity', '-INF'),
                    ('overflow', '9223372036854775808.0'), ('overflow-string', "'9223372036854775808'")):
    CASES[name] = f'''<?php
function h($n,$m,$f,$l) {{ echo "H:",$n,":",$m,";"; $GLOBALS['a']=3; return true; }}
set_error_handler('h'); $a={value}; $b=2;
$v=$a % $b; echo "V:",$v,":",$v===((int)$v),":",$a===3;
'''.encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=tuple(CASES))
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    names = (args.case,) if args.case else tuple(CASES)
    out = args.output or Path(tempfile.mkdtemp(prefix='integer-operator-warnings-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py', Path(__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    environment = {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')}
    rows = []
    for name in names:
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(CASES[name])
        native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        row = {'id': name, 'source_sha256': digest(source), 'native': native}
        if args.native_only:
            row['passed'] = native['exit'] == 0 and not native['timeout']
            row['native_agreement_credit'] = 0
        else:
            model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
            try:
                outcome = json.loads((directory / 'model.stdout').read_bytes())
            except ValueError:
                outcome = {}
            row['model'] = model
            row['passed'] = (native['exit'] == model['exit'] == 0 and not native['timeout'] and not model['timeout']
                and not (directory / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                and outcome.get('checked') == 'program' and outcome.get('status') == 'normal'
                and outcome.get('exit_status') == 0 and outcome.get('reason') is None
                and base64.b64decode(outcome.get('stdout', '')) == (directory / 'native.stdout').read_bytes()
                and base64.b64decode(outcome.get('stderr', '')) == (directory / 'native.stderr').read_bytes())
        rows.append(row)
        print(name, row['passed'], flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'profile': profile,
        'rows': rows, 'environment': environment, 'scope': 'native-only preparation' if args.native_only else 'checked original-source agreement'}, indent=2) + '\n')
    return all(row['passed'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
