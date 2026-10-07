#!/usr/bin/env python3
"""Reporting Fiber callback composed with ordinary GC and an autoglobal eval child."""
import base64
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

from exception_handler_review import recorded
from source_stringable_retirement_sources import REQUEST_EXEC

ROOT = Path(__file__).resolve().parents[2]
SOURCE = b"""<?php
class CoreReportingGcAutoEval313 {
    public function __toString() { echo 'S|'; return 'echo $_GET;'; }
    public function __destruct() { echo 'D|'; error_reporting(19); }
}
set_error_handler(static function () {
    $_GET = 'E|';
    $cycle = [];
    $cycle['self'] =& $cycle;
    unset($cycle);
    echo gc_collect_cycles(), '|';
    eval(new CoreReportingGcAutoEval313);
    return true;
});
$f = new Fiber('error_reporting');
$f->start(2.5);
echo $f->getReturn(), ':', error_reporting(), ':', ini_get('error_reporting');
restore_error_handler();
"""
SOURCE_SHA256 = '8f006b5c36360b9ec1eedfaac122e8de819cf6ab56f4027624184feeca7e9fbc'
EXPECTED = b'1|S|D|E|19:30719:2'


def main():
    out = Path(tempfile.mkdtemp(prefix='fiber-core-latest-source-', dir=ROOT / '.tools'))
    print(out, flush=True)
    source = out / 'source.php'
    source.write_bytes(SOURCE)
    assert hashlib.sha256(SOURCE).hexdigest() == SOURCE_SHA256
    b64 = lambda value: base64.b64encode(value).decode()
    request = {'env': [[b64(b'LC_ALL'), b64(b'C')], [b64(b'TZ'), b64(b'UTC')]],
               'argv': [b64(bytes(source))], 'file': b64(bytes(source)), 'cwd': b64(bytes(out)),
               'seconds': '1700000000', 'microseconds': 125000, 'variables': b64(b'EGPCS'), 'jit': True}
    context = out / 'request.json'
    context.write_text(json.dumps(request) + '\n')
    entries = [base64.b64decode(k) + b'=' + base64.b64decode(v) for k, v in request['env']]
    payload = out / 'input.bin'
    payload.write_bytes(b'PHPRQ001' + struct.pack('<qII', int(request['seconds']), request['microseconds'], len(entries))
                        + b''.join(struct.pack('<I', len(entry)) + entry for entry in entries))
    profile = dict(json.loads((ROOT / 'tests/semantics/profile.json').read_bytes()),
                   include_path='.:', variables_order='EGPCS', auto_globals_jit='1')
    startup = out / 'startup.json'
    startup.write_text(json.dumps({key: b64(profile[key].encode()) for key in ('error_reporting', 'include_path')}) + '\n')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, text=True).strip()
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    watched = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    watched += [ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', ROOT / 'bin/php-semantics',
                ROOT / 'frontend/worker.php', ROOT / 'frontend/target.php', ROOT / '_build/default/adapter/main.exe',
                ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / '.tools/php/bin/php',
                ROOT / '.tools/php-file.so', ROOT / '.tools/request-clock.so', ROOT / 'tests/semantics/profile.json',
                ROOT / 'tests/semantics/exception_handler_review.py',
                ROOT / 'tests/semantics/source_stringable_retirement_sources.py', Path(__file__),
                source, context, payload, startup]
    snapshot = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    identity_process = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-r',
                                 'echo json_encode([\"version\"=>PHP_VERSION,\"sapi\"=>PHP_SAPI,\"int_size\"=>PHP_INT_SIZE,\"zts\"=>PHP_ZTS]);'],
                                out, 'identity', env, 75)
    assert identity_process['exit'] == 0 and not identity_process['timeout'] and not (out / 'identity.stderr').read_bytes()
    identity = json.loads((out / 'identity.stdout').read_bytes())
    assert (identity['version'], identity['sapi'], identity['int_size'], identity['zts']) == ('8.5.10', 'cli', 8, False)
    before = snapshot()
    identity['binary_sha256'] = before[str(ROOT / '.tools/php/bin/php')]
    report = {'revision': revision, 'working_tree_status': status, 'source_sha256': SOURCE_SHA256,
              'inputs': before, 'profile': profile, 'request': request, 'passed': False, 'normal_agreements': 0,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1},
              'budgets': {'steps': 100000, 'model_seconds': 60, 'process_seconds': 75},
              'runtime': identity, 'runtime_process': identity_process}
    try:
        native = recorded([sys.executable, '-c', REQUEST_EXEC, str(ROOT / '.tools/php/bin/php'), '-n', *flags,
                           str(source), str(ROOT / '.tools/request-clock.so'), str(payload)], out, 'native', env, 75)
        report['native'] = native
        nout, nerr = (out / 'native.stdout').read_bytes(), (out / 'native.stderr').read_bytes()
        native_pass = native['exit'] == 0 and not native['timeout'] and nout == EXPECTED and nerr == b''
        report['native_passed'] = native_pass
        if native_pass:
            print('native', True, flush=True)
            model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--startup-ini', str(startup),
                              '--request-context', str(context), '--steps', '100000', '--timeout', '60'], out, 'model', env, 75)
            report['model'] = model
            try:
                outcome = json.loads((out / 'model.stdout').read_bytes())
            except ValueError:
                outcome = {}
            report['outcome'] = outcome
            report['passed'] = (model['exit'] == 0 and not model['timeout'] and (out / 'model.stderr').read_bytes() == b''
                                and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
                                and outcome.get('status') == 'normal' and outcome.get('exit_status') == 0
                                and outcome.get('reason') is None and outcome.get('stdout') == b64(nout)
                                and outcome.get('stderr') == b64(nerr))
            report['normal_agreements'] = int(report['passed'])
    finally:
        report['inputs_stable'] = before == snapshot()
        report['head_stable'] = revision == git('rev-parse', 'HEAD')
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('source', report['passed'], flush=True)
    return all(report[key] for key in ('passed', 'inputs_stable', 'head_stable'))


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
