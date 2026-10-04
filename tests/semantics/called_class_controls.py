#!/usr/bin/env python3
"""A reached Closure dependency stays distinct from real PHP missing-class errors."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'from-callable-core-dependency': (
        '<?php class A{static function run($f){echo $f(),\';\',$f->__invoke(),\';\';}}'
        'class B extends A{}$f=Closure::fromCallable(\'GET_CALLED_CLASS\');B::run($f);'
        'try{$f();}catch(Error $e){echo \'E;\';}try{echo $f->__invoke();}'
        'catch(Error $e){echo \'E;\';}', 'unsupported'),
    'unknown-class-still-php-error': ('<?php Missing::fromCallable("get_called_class");', 'php_error'),
    'namespaced-user-method-still-runs': (
        '<?php namespace N;class Closure{static function fromCallable($f){return $f;}}'
        'echo Closure::fromCallable("USER");', 'normal'),
}


def main():
    out = Path(tempfile.mkdtemp(prefix='called-class-controls-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    records = []
    for name, (source, expected) in CASES.items():
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_text(source)
        commands = {'native': [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)],
                    'model': [str(ROOT / 'bin/php-semantics'), str(path), '--steps', '100000', '--timeout', '45']}
        (directory / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        results = {}
        for label, command in commands.items():
            result = subprocess.run(command, cwd=directory, env=environment, capture_output=True, timeout=55)
            (directory / (label + '.stdout')).write_bytes(result.stdout)
            (directory / (label + '.stderr')).write_bytes(result.stderr)
            (directory / (label + '.exit.json')).write_text(json.dumps({'exit_status': result.returncode}) + '\n')
            results[label] = result
        native, model = results['native'], results['model']
        actual = json.loads(model.stdout)
        passed = (not model.stderr and actual.get('frontend') == 'accepted'
                  and actual.get('checked') == 'program' and actual.get('status') == expected)
        if expected == 'unsupported':
            passed = passed and model.returncode == 1 and actual.get('reason') == 'Closure::fromCallable protocol'
        else:
            passed = passed and model.returncode == 0 and actual.get('exit_status') == native.returncode
            passed = passed and base64.b64decode(actual['stdout']) == native.stdout
            passed = passed and base64.b64decode(actual['stderr']) == native.stderr
        records.append({'id': name, 'pass': passed, 'control': expected == 'unsupported',
                        'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'native_exit': native.returncode, 'model_exit': model.returncode, 'model_status': actual.get('status')})
        print(name, passed, flush=True)
    passed = all(row['pass'] for row in records)
    (out / 'report.json').write_text(json.dumps({'pass': passed, 'records': records, 'profile': profile,
        'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'LC_ALL': 'C', 'TZ': 'UTC'}, indent=2) + '\n')
    print(out, passed)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
