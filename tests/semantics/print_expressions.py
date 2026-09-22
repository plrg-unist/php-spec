#!/usr/bin/env python3
"""Focused original-source print comparisons with the pinned oracle and SL CLI."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'scalars': '<?php print null; print false; print true; print -42; print 1.25; print "\\0Z";',
    'references': '<?php $x="A";$r=&$x;echo print $r;$r="B";echo print $x;',
    'array-reference': '<?php $x=2;$a=[&$x];$b=$a;print $a; $x=3;echo $b[0];',
    'operand-order': '<?php function f(){echo "F";return "X";}echo print f();',
    'delayed-read': '<?php $x=4;echo $x + (print ($x=7));',
    'binary-effects': '<?php echo (print "A") + (print "B");',
    'short-circuit': '<?php (print "A") || print "X"; (print "B") && print "C"; false && print "Y";',
    'ternary': '<?php echo (print "A") ? (print "B") : (print "X");',
    'loops': '<?php for($i=0;$i<2;$i++){if(print $i){echo "Y";}}',
    'return': '<?php function f():int{return print "A";}echo f()===1?"Y":"N";',
    'arrow': '<?php $f=fn()=>print "A";echo $f();',
    'nested-array': '<?php echo [print "A",print "B"][1];',
    'coalesce': '<?php echo (print "A") ?? (print "X");',
    'cast': '<?php echo (string)(print "A");',
    'quiet-missing': '<?php echo @print $missing;',
    'operand-abrupt': '<?php print (1/0);echo "unreachable";',
    'array-temporary': '<?php function f(){return [1,2];}echo print f();',
    'object-temporary': '<?php function f(){return new stdClass;}print f();echo "unreachable";',
    'parameter-default-static': '<?php function f($a=print "X"){}echo "unreachable";',
    'isset-static': '<?php isset(print "X");',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, Path(__file__), types.PHP, ROOT / 'bin/php-semantics',
               ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/profile.json',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): digest(p) for p in watched}
    out = Path(tempfile.mkdtemp(prefix='print-source-', dir=ROOT / '.tools'))
    rows = []
    for name, source in CASES.items():
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source.encode())
        processes = {}
        commands = {
            'native': [str(types.PHP), '-n', *types.FLAGS, str(path)],
            'runner': [str(ROOT / 'bin/php-semantics'), str(path), '--steps', '100000', '--timeout', '45'],
        }
        for kind, command in commands.items():
            process = subprocess.run(command, cwd=directory, env=types.ENV,
                                     capture_output=True, timeout=55)
            processes[kind] = process
            (directory / (kind + '.stdout')).write_bytes(process.stdout)
            (directory / (kind + '.stderr')).write_bytes(process.stderr)
            (directory / (kind + '.json')).write_text(json.dumps({
                'command': command, 'exit_status': process.returncode}) + '\n')
        native, runner = processes['native'], processes['runner']
        try:
            actual = json.loads(runner.stdout)
        except json.JSONDecodeError:
            actual = {'status': 'runner_failure'}
        passed = (runner.returncode == 0 and not runner.stderr
                  and actual.get('status') in ('normal', 'php_error', 'static_rejection')
                  and actual.get('exit_status') == native.returncode
                  and actual.get('stdout') == base64.b64encode(native.stdout).decode()
                  and actual.get('stderr') == base64.b64encode(native.stderr).decode())
        rows.append({'name': name, 'pass': passed, 'status': actual.get('status'),
                     'source_sha256': digest(path), 'actual': actual})
        print(name, passed, actual.get('status'), flush=True)
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in watched}
    report = {'result': 'pass' if all(row['pass'] for row in rows) else 'fail',
              'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'fingerprint': before, 'rows': rows, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
