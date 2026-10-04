#!/usr/bin/env python3
"""Source-derived startup entry/state authentication and exact transport rejection controls."""
from pathlib import Path
import base64
import copy
import hashlib
import json
import subprocess
import sys
import tempfile

from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

R = Path(__file__).resolve().parents[2]
C = R
SOURCES = Path(__file__).with_name('startup_ini')
b64 = lambda value: base64.b64encode(value).decode()


def text(value):
    return '$base64(' + json.dumps(b64(value)) + ')'


def prepare(out):
    sources = {'first': SOURCES / 'reporting.php', 'fatal': SOURCES / 'fatal-restore.php',
               'included': SOURCES / 'include/main.php', 'directory': SOURCES / 'directory.php'}
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], out / 'frontend')
    parsed = {}
    try:
        for name, source in sources.items():
            parsed[name] = frontend.request({'op': 'parse', 'source': b64(source.read_bytes())})
            assert parsed[name]['accepted'], parsed[name]
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], out / 'syntax-adapter')
    fixtures = {}
    try:
        for name, result in parsed.items():
            fixtures[name] = adapter.request({'op': 'check', 'ast': result['ast'], 'fixture': True})['fixture']
    finally:
        adapter.close()
    fixture, count = render(fixtures, sources, bytes(SOURCES / 'include/library'))
    (out / 'protocol.watsup').write_text(fixture)
    (out / 'prepared.json').write_text(json.dumps({'sources': {name: str(path) for name, path in sources.items()},
                                                'parsed': parsed, 'count': count}) + '\n')
    return out / 'protocol.watsup', count


def render(fixtures, sources, include_path):
    first, fatal, included, directory = (sources[name] for name in ('first', 'fatal', 'included', 'directory'))
    paths = {name: text(bytes(path)) for name, path in sources.items()}
    include_path = text(include_path)
    checks = [
        'pstartup_base = {REPORTING ($ptascii("  +512junk")), INCLUDEPATH $ptascii("/startup:.")}',
        'pstartup_null = pstartup_base[.REPORTING = eps]',
        'pstartup_empty = pstartup_base[.REPORTING = ($ptascii(""))]',
        '$startup_valid(pstartup_base)', '$startup_valid(pstartup_null)', '$startup_valid(pstartup_empty)',
        '~$startup_valid(pstartup_base[.INCLUDEPATH = eps])',
        '~$startup_valid(pstartup_base[.INCLUDEPATH = [0,47]])',
        '~$startup_valid(pstartup_base[.INCLUDEPATH = [256]])',
        '~$startup_valid(pstartup_base[.REPORTING = ([256])])',
        '$startup_bytes([0,255])', '~$startup_bytes([256])',
        '$startup_reporting_mask((pstartup_base)) = 512',
        '$startup_reporting_mask((pstartup_null)) = 30719',
        '$startup_reporting_mask((pstartup_empty)) = 0',
        '$startup_reporting_ini((pstartup_null)) = $startup_reporting_ini((pstartup_empty))',
        '$startup_reporting_mask(eps) = 30719',
        '$startup_reporting_ini(eps) = $ptascii("30719")',
        '$startup_include_path(eps) = $ptascii(".:")',
        'S_seed = $startup_state(NORMAL, pstartup_base)',
        '$startup_state_valid(S_seed)', '$file_state_valid(S_seed)',
        'S_seed.FILECWD = eps', 'S_seed.INCLUDEDOPENED = eps',
        '~$file_state_valid(S_seed[.STARTUP = eps])',
        '~$startup_state_valid(S_seed[.FILEINCLUDEPATH = eps])',
        '~$startup_state_valid(S_seed[.FILEINCLUDEPATH = ($ptascii(""))])',
        '~$startup_state_valid(S_seed[.FILEINCLUDEPATH = ([0,47])])',
        '~$startup_state_valid(S_seed[.FILEINCLUDEPATH = ([256])])',
        '$startup_state_valid(S_seed[.FILEINCLUDEPATH = ($ptascii("changed") ++ [0,255])])',
        'preqbytes_file = ' + paths['first'], 'preqbytes_cwd = ' + text(bytes(C)),
        'Q = {ENV eps, ARGV ([preqbytes_file]), FILE preqbytes_file, SECONDS 0, MICROSECONDS 0, VARIABLES $ptascii("EGPCS"), JIT true, CWD (preqbytes_cwd)}',
        '$request_valid(Q)',
        'S_plain = $php_startup_run(program_first, 0, ' + json.dumps(b64(bytes(first))) + ', pstartup_base)',
        'S_request = $php_request_startup_run(program_first, 0, ' + json.dumps(b64(bytes(first))) + ', Q, pstartup_base)',
        'S_file = $php_file_startup_run(program_first, 0, preqbytes_file, preqbytes_cwd, pstartup_base)',
        'S_both = $php_request_file_startup_run(program_first, 0, preqbytes_file, Q, preqbytes_cwd, pstartup_base)',
        'S_plain.STARTUP = (pstartup_base)', 'S_request.STARTUP = (pstartup_base)',
        'S_file.STARTUP = (pstartup_base)', 'S_both.STARTUP = (pstartup_base)',
        'S_plain.REQUEST = eps', 'S_file.REQUEST = eps',
        'S_request.REQUEST = (Q)', 'S_both.REQUEST = (Q)',
        'S_plain.FILECWD = eps', 'S_request.FILECWD = eps',
        'S_file.FILECWD = (preqbytes_cwd)', 'S_both.FILECWD = (preqbytes_cwd)',
        'S_plain.FILEINCLUDEPATH = (pstartup_base.INCLUDEPATH)',
        'S_request.FILEINCLUDEPATH = S_plain.FILEINCLUDEPATH',
        'S_file.FILEINCLUDEPATH = S_plain.FILEINCLUDEPATH', 'S_both.FILEINCLUDEPATH = S_plain.FILEINCLUDEPATH',
        'S_file.INCLUDEDOPENED = [preqbytes_file]', 'S_both.INCLUDEDOPENED = [preqbytes_file]',
        '$call_descriptors_valid(S_plain)', '$call_descriptors_valid(S_request)',
        '$call_descriptors_valid(S_file)', '$call_descriptors_valid(S_both)',
        'pstartup_fatal = {REPORTING ($ptascii("1")), INCLUDEPATH $ptascii("/startup/fatal")}',
        'S_fatal = $php_startup_run(program_fatal, 10000, ' + json.dumps(b64(bytes(fatal))) + ', pstartup_fatal)',
        'S_fatal.COMPLETION = NORMAL', '$call_descriptors_valid(S_fatal)',
        'S_fatal.REPORTING = 8', 'S_fatal.REPORTINGINI = $ptascii("1")', '~S_fatal.REPORTINGMODIFIED',
        '$config_reporting_restore(S_fatal) = S_fatal',
        'pstartup_file = pstartup_base[.INCLUDEPATH = ' + include_path + ']',
        'S_resolve = $php_file_startup_run(program_included, 10000, ' + paths['included'] + ', preqbytes_cwd, pstartup_file)',
        'S_resolve.COMPLETION = SOURCE_PENDING', '$call_descriptors_valid(S_resolve)',
        '$file_state_valid(S_resolve)', '$file_pending_state_valid(S_resolve)',
        'S_resolve.FILEINCLUDEPATH = (pstartup_file.INCLUDEPATH)',
        'S_resolve.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
        'pfilecontext.INCLUDEPATH = pstartup_file.INCLUDEPATH',
        '~$file_state_valid(S_resolve[.FILECWD = eps])',
        '~$file_pending_state_valid(S_resolve[.FILECWD = eps])',
        'S_directory0 = $php_startup_run(program_directory, 0, ' + json.dumps(b64(bytes(directory))) + ', pstartup_base)',
        'S_directory = $startup_seek_chdir(S_directory0, 1000)',
        '$startup_chdir_ready(S_directory)', '$call_descriptors_valid(S_directory)',
        'S_directory.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '~$config_string_launch(S_directory, pconfigcall)',
        'S_directory_file0 = $php_file_startup_run(program_directory, 0, ' + paths['directory'] + ', preqbytes_cwd, pstartup_base)',
        'S_directory_file = $startup_seek_chdir(S_directory_file0, 1000)',
        '$startup_chdir_ready(S_directory_file)', '$call_descriptors_valid(S_directory_file)',
        'S_directory_file.TODO = (CONFIG_INVOKE pconfigcall_file) :: ptask_file_tail*',
        '$config_string_launch(S_directory_file, pconfigcall_file)',
        'S_dir_pending = $drive(S_directory_file, 1000)',
        'S_dir_pending.COMPLETION = SOURCE_PENDING', '$dir_state_valid(S_dir_pending)',
        '~$dir_state_valid(S_dir_pending[.FILECWD = eps])',
    ]
    setup = '\n'.join('dec $startup_program_' + name + '() : program\ndef $startup_program_' + name + '() = ' + fixture for name, fixture in fixtures.items())
    helpers = r'''
dec $startup_chdir_ready(pstate) : bool
def $startup_chdir_ready(S) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CHDIR
def $startup_chdir_ready(S) = false -- otherwise
dec $startup_seek_chdir(pstate, nat) : pstate
def $startup_seek_chdir(S, n) = S[.COMPLETION = NORMAL] -- if $startup_chdir_ready(S)
def $startup_seek_chdir(S, n) = S
  -- if ~$startup_chdir_ready(S)
  -- if n = 0 \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $startup_seek_chdir(S, n) = $startup_seek_chdir($drive_steps(S[.COMPLETION = NORMAL], 1), n_rest)
  -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$startup_chdir_ready(S)
  -- if n_rest = $(n - 1)
'''
    bindings = ['program_' + name + ' = $startup_program_' + name + '()' for name in fixtures]
    checks = bindings + checks
    fixture = setup + '\n' + helpers + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in checks) + 'def $main() = false -- otherwise\n'
    assert len(checks) == 99
    return fixture, len(checks)


def transport(prepared_path):
    prepared = json.loads(prepared_path.read_text())
    D = prepared_path.parent
    source = Path(prepared['sources']['first'])
    startup = {'error_reporting': b64(b'  +512junk'), 'include_path': b64(b'/startup:.')}
    request = {'op': 'execute', 'ast': prepared['parsed']['first']['ast'],
               'filename': b64(bytes(source)), 'steps': 0, 'startup_ini': startup}
    snapshot = {'version': 2, 'main': request['filename'], 'cwd': b64(bytes(C)),
                'include_path': startup['include_path'], 'entries': [], 'chdir_entries': []}
    facts = {'env': [], 'argv': [request['filename']], 'file': request['filename'],
             'seconds': '0', 'microseconds': 0, 'variables': b64(b'EGPCS'), 'jit': True,
             'cwd': snapshot['cwd']}
    cases = []
    for name, extra in [('ordinary', {}), ('request', {'request': facts}),
                        ('file', {'file_snapshot': snapshot}),
                        ('request-file', {'request': facts, 'file_snapshot': snapshot})]:
        cases.append((name, dict(request, **extra), True))
    prefixed = copy.deepcopy(dict(request, file_snapshot=snapshot))
    prefixed['startup_ini']['include_path'] = b64(b'/startup:.\0suffix')
    cases.append(('raw-path-effective-snapshot', prefixed, True))
    for name, field, value in [('missing-path', 'include_path', None),
                               ('empty-path', 'include_path', ''),
                               ('leading-nul-path', 'include_path', b64(b'\0tail')),
                               ('reporting-number', 'error_reporting', 512),
                               ('noncanonical-reporting', 'error_reporting', 'Zh==')]:
        malformed = copy.deepcopy(request)
        if value is None:
            malformed['startup_ini'].pop(field)
        else:
            malformed['startup_ini'][field] = value
        cases.append((name, malformed, False))
    extra = copy.deepcopy(request)
    extra['startup_ini']['precision'] = b64(b'14')
    cases.append(('extra-startup-key', extra, False))
    mismatch = copy.deepcopy(dict(request, file_snapshot=snapshot))
    mismatch['file_snapshot']['include_path'] = b64(b'.:')
    cases.append(('snapshot-startup-mismatch', mismatch, False))
    baseline_mismatch = copy.deepcopy(dict(request, file_snapshot=snapshot))
    baseline_mismatch.pop('startup_ini')
    cases.append(('default-snapshot-mismatch', baseline_mismatch, False))
    cwd_mismatch = copy.deepcopy(dict(request, file_snapshot=snapshot, request=facts))
    cwd_mismatch['request']['cwd'] = b64(b'/other')
    cases.append(('request-file-cwd-mismatch', cwd_mismatch, False))
    reasons = {
        'missing-path': 'unexpected/missing fields',
        'empty-path': 'invalid startup INI facts',
        'leading-nul-path': 'invalid startup INI facts',
        'reporting-number': 'expected string',
        'noncanonical-reporting': 'noncanonical base64 padding',
        'extra-startup-key': 'unexpected/missing fields',
        'snapshot-startup-mismatch': 'file snapshot include_path differs from startup INI',
        'default-snapshot-mismatch': 'file snapshot include_path differs from startup INI',
        'request-file-cwd-mismatch': 'file snapshot request cwd mismatch',
    }
    rows = []
    worker = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], D / 'transport-worker')
    try:
        for name, payload, accepted in cases:
            index = worker.sequence
            try:
                result = worker.request(payload)
            except AssertionError:
                result = types.wire.loads((worker.output / (str(index) + '.response')).read_text())
            if accepted:
                state = result['state']
                expected_path = list(map(str, base64.b64decode(payload['startup_ini']['include_path'])))
                passed = (result['ok'] and state['STARTUP']['REPORTING'] == list(map(str, b'  +512junk'))
                          and state['REPORTING'] == '512' and state['REPORTINGMODIFIED'] is False
                          and state['FILEINCLUDEPATH'] == expected_path
                          and (state['REQUEST'] is not None) == ('request' in payload)
                          and (state['FILECWD'] is not None) == ('file_snapshot' in payload))
            else:
                passed = (result.get('ok') is False and result.get('category') == 'runner_failure'
                          and reasons[name] in result.get('message', ''))
            rows.append({'id': name, 'accepted': accepted, 'pass': passed, 'packet': index,
                         'error': result.get('message')})
            assert passed, (name, result)
    finally:
        worker.close()
    packet = types.wire.dumps(request)
    packet = packet[:-1] + ',"startup_ini":' + types.wire.dumps(startup) + '}\n'
    (D / 'duplicate-startup.stdin').write_text(packet)
    command = [str(R / '_build/default/adapter/main.exe'), str(R)]
    child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=R, env=types.ENV)
    stdout, stderr = child.communicate(packet.encode(), timeout=30)
    (D / 'duplicate-startup.stdout').write_bytes(stdout)
    (D / 'duplicate-startup.stderr').write_bytes(stderr)
    result = types.wire.loads(stdout.decode())
    passed = child.returncode == 0 and not stderr and result.get('ok') is False and result.get('category') == 'runner_failure' and 'duplicate startup INI field' in result.get('message', '')
    rows.append({'id': 'duplicate-startup-header', 'pass': passed, 'argv': command,
                 'pid': child.pid, 'exit': child.returncode, 'reaped': True, 'error': result.get('message')})
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip(),
              'scope': 'five genuine typed entry/prefix controls and ten malformed startup/transport controls',
              'prepared_source_reference': str(prepared_path),
              'environment': {'LC_ALL': types.ENV['LC_ALL'], 'TZ': types.ENV['TZ'], 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
              'rows': rows, 'pass': all(row['pass'] for row in rows)}
    (D / 'transport-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'raw': str(D), 'checks': len(rows), 'pass': report['pass']}), flush=True)
    assert report['pass']
    return report


def main():
    out = Path(tempfile.mkdtemp(prefix='startup-ini-protocol-', dir=R / '.tools'))
    print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, Path(__file__), *sorted(SOURCES.rglob('*.php')),
              R / 'frontend/worker.php', R / 'tests/semantics/profile.json',
              R / 'tests/semantics/recorded_worker.py', R / 'tests/semantics/error_handler_run.py',
              R / '.tools/php/bin/php', R / '.tools/php-file.so', R / '_build/default/adapter/main.exe',
              R / 'tests/semantics/_build/default/numeric_runner.exe']
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in inputs}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    fixture, count = prepare(out)
    numeric = recorded([str(R / 'tests/semantics/_build/default/numeric_runner.exe'),
                        *map(str, modules), str(fixture)], out / 'numeric', 90)
    numeric_pass = (numeric['exit'] == 0 and not numeric['timeout']
                    and (out / 'numeric.stdout').read_bytes() == b'true\n'
                    and not (out / 'numeric.stderr').read_bytes())
    transport_process = recorded([sys.executable, str(Path(__file__).resolve()),
                                  '--transport', str(out / 'prepared.json')], out / 'transport', 90)
    transport_pass = (transport_process['exit'] == 0 and not transport_process['timeout']
                      and not (out / 'transport.stderr').read_bytes()
                      and json.loads((out / 'transport.stdout').read_text())['pass'])
    assert before == {str(path.relative_to(R)): digest(path) for path in inputs}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    report = {'revision': revision, 'inputs': before, 'state_conditions': count, 'transport_conditions': 15,
              'numeric': numeric, 'transport': transport_process, 'pass': numeric_pass and transport_pass,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['pass']


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--transport':
        transport(Path(sys.argv[2]))
    else:
        raise SystemExit(0 if main() else 1)
