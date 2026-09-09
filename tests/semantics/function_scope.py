#!/usr/bin/env python3
"""Actual function-source superglobal scope with exact primitive request facts."""
from pathlib import Path
import argparse, base64, hashlib, json, os, signal, subprocess, tempfile
import request_environment as q
from recorded_worker import Worker
ROOT = Path(__file__).resolve().parents[2]
CASES = {'dim-read-order': b'<?php $_GET=[1]; function keyf(){$_GET=[2];return 0;} function f(){echo $_GET[keyf()];} '
                   b'f();',
 'dim-write-order': b'<?php $_GET=[1];$old=&$_GET;function rhs(){unset($_GET);$_GET=[2];return 3;}function'
                    b' f(){$_GET[0]=rhs();}f();echo $old[0],$_GET[0];',
 'read-before-call': b'<?php $_GET=1;function rhs(){$_GET=2;return 3;}function f(){echo $_GET+rhs();}f();',
 'self-dim': b'<?php $_GET=[1];function f(){$_GET[0]=$_GET;echo $_GET[0][0];}f();',
 'read-undefined': b'<?php unset($_ENV);function f(){echo $_ENV;}f();',
 'quiet-direct': b'<?php $_ENV=[1];function f(){echo isset($_ENV),empty($_ENV),$_ENV[0]??9;unset($_ENV);ech'
                 b'o isset($_ENV),empty($_ENV),$_ENV??9;}f();',
 'quiet-computed': b'<?php $_ENV=[1];function f(){echo isset(${"_E"."NV"}),empty(${"_E"."NV"}),${"_E"."NV"}[0'
                   b']??9;unset(${"_E"."NV"});echo isset(${"_E"."NV"}),empty(${"_E"."NV"}),${"_E"."NV"}??9;}f'
                   b'();',
 'coalesce-write': b'<?php unset($_ENV);function f(){$_ENV??=[1];$_ENV[0]??=2;$_ENV[1]??=3;echo $_ENV[0],$_EN'
                   b'V[1];}f();echo $_ENV[0];',
 'coalesce-computed': b'<?php unset($_ENV);function f(){${"_E"."NV"}??=[1];${"_E"."NV"}[0]??=2;echo ${"_E"."'
                      b'NV"}[0];}f();echo $_ENV[0];',
 'update': b'<?php $_GET=1;function f(){echo ++$_GET,$_GET++,$_GET;$_GET+=4;echo $_GET;}f();echo $_GET;',
 'update-computed': b'<?php $_GET=1;function f(){echo ++${"_G"."ET"},${"_G"."ET"}++;${"_G"."ET"}+=4;echo $'
                    b'{"_G"."ET"};}f();echo $_GET;',
 'alias-local': b'<?php $_GET=1;function f(){$x=&$_GET;$x=2;echo $_GET;unset($_GET);$x=3;echo $x;}f();echo'
                b' isset($_GET);',
 'alias-super-target': b'<?php $_GET=1;function f(){$x=2;$_GET=&$x;$x=3;echo $_GET;}f();echo $_GET;',
 'alias-computed-target': b'<?php $_GET=1;function f(){$x=2;${"_G"."ET"}=&$x;$x=3;echo $_GET;}f();echo $_GET'
                          b';',
 'alias-super-source-dim': b'<?php $_GET=1;function f(){$a=[];$a[0]=&$_GET;$a[0]=3;echo $_GET;}f();echo $_GET'
                           b';',
 'alias-super-source-dynamic': b'<?php $_GET=1;function f(){$n="x";$$n=&$_GET;$x=3;echo $_GET;}f();echo $_GET'
                               b';',
 'list-value': b'<?php $_GET=[1,2];function f(){[$a,$b]=$_GET;echo $a,$b;[$_GET,$x]=[3,4];echo $_GET,$x;}f();'
               b'echo $_GET;',
 'list-ref': b'<?php $_GET=[1,2];function f(){[&$x]=$_GET;$x=3;echo $_GET[0];}f();echo $_GET[0];',
 'list-ref-target': b'<?php $_GET=1;function f(){$a=[2];[&$_GET]=$a;$_GET=3;echo $a[0];}f();echo $_GET;',
 'foreach-value': b'<?php $_GET=[1,2];function f(){foreach($_GET as $x){echo $x;}echo isset($x);}f();',
 'foreach-ref': b'<?php $_GET=[1,2];function f(){foreach($_GET as &$x){$x+=2;}}f();echo $_GET[0],$_GET[1];',
 'foreach-ref-computed': b'<?php $_GET=[1,2];function f(){foreach(${"_G"."ET"} as &$x){$x+=2;}}f();echo $_G'
                         b'ET[0],$_GET[1];',
 'foreach-target': b'<?php $_GET=1;function f(){foreach([2,3] as $_GET){echo $_GET;}}f();echo $_GET;',
 'global-env': b'<?php function f(){global $_ENV;$n="_ENV";echo isset($$n)?"P":"A";}f();',
 'global-computed-env': b'<?php function f(){global ${"_E"."NV"};$n="_ENV";echo isset($$n)?"P":"A";}f();',
 'global-dynamic-env': b'<?php function f(){$n="_ENV";global $$n;echo isset($$n)?"P":"A";}f();',
 'param-autoglobal': b'<?php function f($_ENV){}',
 'activated-global-dynamic': b'<?php $_ENV;function f(){$n="_ENV";global $$n;echo isset($$n)?"P":"A";$$n=[3'
                             b'];}f();echo $_ENV[0];',
 'activated-global-literal': b'<?php $_ENV;function f(){global $_ENV;$n="_ENV";echo isset($$n)?"P":"A";}f();',
 'activated-global-computed': b'<?php $_ENV;function f(){global ${"_E"."NV"};$n="_ENV";echo isset($$n)?"P":"'
                              b'A";}f();',
 'globals-binding': b'<?php function f(){global $GLOBALS;$n="GLOBALS";echo isset($$n)?"P":"A";echo isset($'
                    b'GLOBALS["GLOBALS"])?"P":"A";}f();',
 'globals-computed-binding': b'<?php function f(){global ${"GLOB"."ALS"};$n="GLOBALS";echo isset($$n)?"P":"'
                             b'A";echo isset($GLOBALS["GLOBALS"])?"P":"A";}f();',
 'global-this-dynamic': b'<?php function f(){$n="this";global $$n;}f();',
 'global-this-computed': b'<?php function f(){global ${"th"."is"};}f();',
 'global-computed-name-cv': b'<?php $a=1;function f(){$n="a";global $$n;$$n=3;}f();echo $a;',
 'global-target-array-source': b'<?php $_GET=1;function f(){$a=[2];$_GET=&$a[0];$_GET=3;echo $a[0];}f();echo '
                               b'$_GET;',
 'super-direct': b'<?php function f(){echo $_ENV["FIRST"];}f();',
 'super-dynamic': b'<?php function f(){$n="_ENV";echo $$n["FIRST"]??7;}f();',
 'super-computed-constant': b'<?php function f(){echo ${"_E"."NV"}["FIRST"];}f();',
 'super-dynamic-write': b'<?php function f(){$n="_ENV";$$n=["FIRST"=>"local"];echo $$n["FIRST"],$_ENV["FIR'
                        b'ST"];}f();echo $_ENV["FIRST"];',
 'super-direct-write': b'<?php function f(){$_ENV=["FIRST"=>"changed"];}f();echo $_ENV["FIRST"];'}


def native(path, payload, output):
    command = [str(q.t.PHP), '-n', *q.t.FLAGS, '-d', 'variables_order=EGPCS', str(path)]
    (output / 'native.command.json').write_text(json.dumps(command) + '\n')
    with payload.open('rb') as stream:
        os.dup2(stream.fileno(), 198)
        try:
            result = subprocess.run(command, env={'LD_PRELOAD': str(ROOT / '.tools/request-clock.so')},
                                    pass_fds=(198,), cwd=path.parent, capture_output=True, timeout=10)
        except subprocess.TimeoutExpired as error:
            (output / 'native.stdout').write_bytes(error.stdout or b'')
            (output / 'native.stderr').write_bytes(error.stderr or b'')
            (output / 'native.status.json').write_text(json.dumps({'status': 'timeout', 'seconds': 10}))
            raise
        finally:
            os.close(198)
    (output / 'native.stdout').write_bytes(result.stdout)
    (output / 'native.stderr').write_bytes(result.stderr)
    (output / 'native.status.json').write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
    return {'stdout': q.b64(result.stdout), 'stderr': q.b64(result.stderr),
            'exit_status': result.returncode, 'command': command}


def main(catalogue=CASES, campaign="function-scope", producer=Path(__file__)):
    parser = argparse.ArgumentParser(); parser.add_argument('--match', default=''); args = parser.parse_args()
    cases = {k: v for k, v in catalogue.items() if args.match in k}
    assert cases, 'no source controls selected'
    before = q.t.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix=campaign+'-', dir=ROOT / '.tools'))
    inputs = [ROOT / rel for rel in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs += [Path(__file__), producer, ROOT / 'vendor/php-src/Zend/zend_compile.c',
               ROOT / 'vendor/php-src/Zend/zend_vm_def.h', q.t.PHP, ROOT / '.tools/php-file.so',
               ROOT / '.tools/request-clock.so', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'tests/semantics/recorded_worker.py']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    for path in inputs:
        target = out / 'original-inputs' / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(path.read_bytes())
    (out / 'inputs.json').write_text(json.dumps({'closure': before, 'direct': hashes}, indent=2))
    records = []
    for name, source in cases.items():
        directory = out / name; directory.mkdir(); path = directory / 'source.php'; path.write_bytes(source)
        entries = [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one']
        payload = directory / 'request.input'; payload.write_bytes(q.packet(1700000000, 125000, entries))
        request = {'env': [[q.b64(k), q.b64(v)] for k, v in (e.split(b'=', 1) for e in entries)],
                   'argv': [q.b64(os.fsencode(path))], 'file': q.b64(os.fsencode(path)),
                   'seconds': '1700000000', 'microseconds': 125000, 'variables': q.b64(b'EGPCS'),
                   'jit': True, 'cwd': q.b64(os.fsencode(directory))}
        (directory / 'request.json').write_text(json.dumps(request))
        record = {'id': name, 'source_base64': q.b64(source), 'context': str(path), 'request': request,
                  'native': native(path, payload, directory)}
        records.append(record); (out / 'originals.json').write_text(json.dumps(records, indent=2))
    def expired(signum, frame):
        raise TimeoutError('function scope worker exceeded 60 seconds')
    previous = signal.signal(signal.SIGALRM, expired)
    frontend = Worker([str(q.t.PHP), '-n', *q.t.FLAGS, '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend-wire')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter-wire')
    try:
        for row in records:
            directory = out / row['id']; signal.alarm(60)
            parsed = frontend.request({'op': 'parse', 'source': row['source_base64']})
            (directory / 'parsed.json').write_text(json.dumps(parsed)); assert parsed.get('accepted'), parsed
            request = {'op': 'execute', 'ast': parsed['ast'], 'steps': 10000,
                       'filename': q.b64(os.fsencode(row['context'])), 'request': row['request']}
            (directory / 'execute.json').write_text(json.dumps(request))
            try:
                result = adapter.request(request)
            except Exception as error:
                (directory / 'tool-failure.json').write_text(json.dumps({'type': type(error).__name__, 'message': str(error)}))
                raise
            finally:
                signal.alarm(0)
            (directory / 'state.json').write_text(json.dumps(result))
            actual = q.cli.observe(result['state'], row['context'])
            row['actual'] = actual
            row['pass'] = actual['status'] in ('normal', 'php_error', 'static_rejection') and all(
                actual[k] == row['native'][k] for k in ('stdout', 'stderr', 'exit_status'))
            (out / 'results.json').write_text(json.dumps(records, indent=2))
            print(row['id'], row['pass'], actual['status'], flush=True)
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, previous)
        try:
            frontend.close()
        finally:
            adapter.close()
    assert before == q.t.syntax_validation.implementation_fingerprint(), 'source inputs changed'
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    report = {'result': 'pass' if all(r['pass'] for r in records) else 'fail', 'selection': args.match,
              'catalogue_cases': len(catalogue), 'selected_cases': len(cases), 'fingerprint': before,
              'direct_inputs': hashes, 'raw': str(out), 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    if report['result'] == 'pass' and not args.match:
        (ROOT / 'coverage/semantics' / (campaign+'.json')).write_text(json.dumps(report, indent=2))
    print(out, report['result']); return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
