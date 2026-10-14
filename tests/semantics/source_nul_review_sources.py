#!/usr/bin/env python3
"""A throwing NUL-filename warning preserves its message and source trace."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import error_handler_run as recorder

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
SOURCE = br'''<?php
function nul_throw($level,$message){
    echo "H:",$level,";";
    ini_set("include_path","next");
    throw new Exception($message);
}
set_error_handler("nul_throw");
$x=99;
try{$x=include "proto://u:p@host\0tail";}
catch(Exception $e){
    echo "C:",$x,":",get_include_path(),":",$e->getMessage(),"|";
    foreach($e->getTrace() as $frame){
        echo $frame["function"],":",isset($frame["file"])?"F":"I",":",isset($frame["line"])?$frame["line"]:0,";";
    }
}
echo "Z";
'''
EXPECTED = b"H:2;C:99:next:include(): Failed opening 'proto://...@host' for inclusion (include_path='.:')|nul_throw:F:9;include:F:9;Z"
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
b64 = lambda value: base64.b64encode(value).decode()


def fingerprint():
    paths = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    paths += [ROOT / p for p in ('spec/semantics/modules.json', 'spec/schema.json', 'bin/php-semantics',
        '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
        'frontend/worker.php', 'frontend/target.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php',
        'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/profile.json')]
    return {str(p.relative_to(ROOT)): sha(p) for p in [*paths, Path(__file__).resolve()]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='source-nul-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    source = out / 'main.php'; source.write_bytes(SOURCE)
    snapshot = out / 'snapshot.json'
    snapshot.write_text(json.dumps({'version': 1, 'main': b64(bytes(source.resolve())),
        'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'entries': []}) + '\n')
    profile = dict(json.loads((ROOT / 'tests/semantics/profile.json').read_bytes()), include_path='.:')
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'before': fingerprint(), 'source_sha256': sha(source), 'profile': profile,
        'source_agreements': 0, 'passed': False}
    print(out, flush=True)
    try:
        native = recorder.recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], out / 'native', 10)
        report['native'] = native
        assert native['exit'] == 0 and not native['timeout'] and not native['group_after']
        assert (out / 'native.stdout').read_bytes() == EXPECTED and (out / 'native.stderr').read_bytes() == b''
        model = recorder.recorded([str(ROOT / 'bin/php-semantics'), str(source), '--file-snapshot',
            str(snapshot), '--steps', '10000', '--timeout', '60'], out / 'model', 90)
        report['model'] = model
        outcome = json.loads((out / 'model.stdout').read_bytes()); report['outcome'] = outcome
        assert model['exit'] == 0 and not model['timeout'] and not model['group_after']
        assert (out / 'model.stderr').read_bytes() == b''
        assert outcome['status'] == 'normal' and outcome['reason'] is None and outcome['exit_status'] == 0
        assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
        assert base64.b64decode(outcome['stdout'], validate=True) == EXPECTED
        assert base64.b64decode(outcome['stderr'], validate=True) == b''
        report.update(passed=True, source_agreements=1)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['inputs_stable'] = report['before'] == report['after']
        report['head_stable'] = report['revision'] == subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        if not report['passed']:
            report['source_agreements'] = 0
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
