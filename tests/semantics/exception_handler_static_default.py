#!/usr/bin/env python3
"""An entered exception callback triggers a foreign-file static default warning."""
import base64
import json
from pathlib import Path
import subprocess
import tempfile

from error_handler_run import ENV, ROOT, recorded

MAIN = '''<?php
require __DIR__."/decl.php";
function w($n,$m,$f,$l){echo ($f===__FILE__?"F":"bad"),":",$l,":",get_exception_handler()===null?"N":"bad",";";return true;}
set_error_handler("w");
function h($e){echo func_num_args(),";",C::$x;}
set_exception_handler("h");
throw new Exception;
'''
DECL = '<?php\nclass C { public static $x = E_STRICT; }\n'


def run():
    out = Path(tempfile.mkdtemp(prefix='exception-static-default-', dir=ROOT / '.tools'))
    source = out / 'main.php'
    child = out / 'decl.php'
    source.write_text(MAIN)
    child.write_text(DECL)
    b64 = lambda data: base64.b64encode(data).decode()
    snapshot = {'version': 1, 'main': b64(bytes(source)), 'cwd': b64(bytes(ROOT)),
                'include_path': b64(b'.:'), 'entries': [{
                    'caller': b64(bytes(source)), 'requested': b64(bytes(child)),
                    'status': 'opened', 'resolved': b64(bytes(child)),
                    'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
    snap = out / 'snapshot.json'
    snap.write_text(json.dumps(snapshot) + '\n')
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    print(out, flush=True)
    native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], out / 'native', 30)
    model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--file-snapshot', str(snap),
                      '--steps', '100000', '--timeout', '60'], out / 'model', 90)
    actual = json.loads((out / 'model.stdout').read_bytes())
    expected = b'1;F:5:N;2048'
    passed = (native['exit'] == 0 and not native['timeout']
              and (out / 'native.stdout').read_bytes() == expected and not (out / 'native.stderr').read_bytes()
              and model['exit'] == 0 and not model['timeout'] and not (out / 'model.stderr').read_bytes()
              and actual.get('frontend') == 'accepted' and actual.get('checked') == 'program'
              and actual.get('status') == 'normal' and actual.get('exit_status') == 0
              and base64.b64decode(actual['stdout']) == expected and base64.b64decode(actual['stderr']) == b'')
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'native': native, 'model': model,
        'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ']}, 'profile': profile,
        'observation': actual, 'passed': passed}, indent=2) + '\n')
    print('foreign-file-static-default', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
