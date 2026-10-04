#!/usr/bin/env python3
"""Nullable display entries, captured destinations and checked service responses."""
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
SOURCES = Path(__file__).with_name('display_errors')
b64 = lambda value: base64.b64encode(value).decode()


def text(value):
    return '$base64(' + json.dumps(b64(value)) + ')'


def render(fixture, source, cwd):
    C = Path(cwd)
    checks = [
        'program_main = $display_protocol_program()',
        'S_legacy = $initial_state(NORMAL)', '$display_state_valid(S_legacy)',
        'S_legacy.DISPLAYINIT = ($ptascii("stderr"))', '$display_state_mode(S_legacy) = 2',
        '$display_mode(eps) = 1', '$display_mode(($ptascii(""))) = 0',
        '$display_ini_bytes(eps) = $display_ini_bytes(($ptascii("")))',
        '$display_mode(($ptascii("StDeRr"))) = 2', '$display_mode(($ptascii("TrUe"))) = 1',
        '$display_mode(($ptascii("258tail"))) = 2', '$display_mode(($ptascii("256"))) = 0',
        '$display_mode(($ptascii("3"))) = 1', '$display_mode(($ptascii("2e3"))) = 2',
        '$display_mode(($ptascii("-254"))) = 2',
        '$display_mode(($ptascii("stderr") ++ [0] ++ $ptascii("tail"))) = 0',
        '$display_mode(($ptascii("9223372036854775808"))) = 1',
        '$display_mode(($ptascii("-9223372036854775809"))) = 0',
        'S_null = $display_initial(eps, eps)', 'S_empty = $display_initial(eps, ($ptascii("")))',
        '$display_state_valid(S_null)', '$display_state_valid(S_empty)',
        '~$display_state_valid(S_null[.DISPLAYINIT = ([256])])',
        '~$display_state_valid(S_null[.DISPLAYINI = ([256])])',
        '~$display_state_valid(S_null[.DISPLAYINI = ($ptascii(""))])',
        '~$display_state_valid(S_null[.DISPLAYMODIFIED = true])',
        'S_changed = S_null[.DISPLAYINI = ($ptascii(""))][.DISPLAYMODIFIED = true]',
        '$display_state_valid(S_changed)', '$display_state_mode(S_changed) = 0',
        '$display_restore(S_changed) = S_null', '$display_restore(S_null) = S_null',
        'preqbytes_file = ' + text(bytes(source)), 'preqbytes_cwd = ' + text(bytes(C)),
        'Q = {ENV eps, ARGV ([preqbytes_file]), FILE preqbytes_file, SECONDS 0, MICROSECONDS 0, VARIABLES $ptascii("EGPCS"), JIT true, CWD (preqbytes_cwd)}',
        'S_plain = $php_display_run(program_main, 0, ' + json.dumps(b64(bytes(source))) + ', eps, ($ptascii("StDeRr")))',
        'S_request = $php_request_display_run(program_main, 0, ' + json.dumps(b64(bytes(source))) + ', Q, eps, ($ptascii("StDeRr")))',
        'S_file = $php_file_display_run(program_main, 0, preqbytes_file, preqbytes_cwd, eps, ($ptascii("StDeRr")))',
        'S_both = $php_request_file_display_run(program_main, 0, preqbytes_file, Q, preqbytes_cwd, eps, ($ptascii("StDeRr")))',
        '$call_descriptors_valid(S_plain)', '$call_descriptors_valid(S_request)',
        '$call_descriptors_valid(S_file)', '$call_descriptors_valid(S_both)',
        'S_plain.DISPLAYINIT = ($ptascii("StDeRr"))', 'S_both.DISPLAYINI = S_plain.DISPLAYINI',
        'S_plain.FILEINCLUDEPATH = eps', 'S_request.FILEINCLUDEPATH = eps',
        'S_file.FILEINCLUDEPATH = ($ptascii(".:"))', 'S_both.FILEINCLUDEPATH = S_file.FILEINCLUDEPATH',
        'S_plain.FILECWD = eps', 'S_file.FILECWD = (preqbytes_cwd)',
        'S_request.REQUEST = (Q)', 'S_both.REQUEST = (Q)', 'S_file.INCLUDEDOPENED = [preqbytes_file]',
        'pstartup = {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii("/registered")}',
        'S_registered = $php_file_display_run(program_main, 0, preqbytes_file, preqbytes_cwd, (pstartup), eps)',
        '$call_descriptors_valid(S_registered)', 'S_registered.STARTUP = (pstartup)',
        'S_registered.FILEINCLUDEPATH = (pstartup.INCLUDEPATH)', '$display_state_mode(S_registered) = 1',
        '~$call_descriptors_valid(S_file[.DISPLAYINI = ([256])])',
        '~$call_descriptors_valid(S_file[.DISPLAYINI = eps])',
        'S_done = $drive(S_plain[.COMPLETION = NORMAL], 10000)',
        'S_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_done)', '~S_done.DISPLAYMODIFIED',
        'S_done.DISPLAYINI = S_done.DISPLAYINIT', '$display_protocol_modes(S_done.EVENTS) = [2,1,2]',
        'S_null_done = $php_display_run(program_main, 10000, ' + json.dumps(b64(bytes(source))) + ', eps, eps)',
        'S_null_done.COMPLETION = NORMAL', '$call_descriptors_valid(S_null_done)',
        'S_null_done.DISPLAYINI = eps', '~S_null_done.DISPLAYMODIFIED', '$display_protocol_modes(S_null_done.EVENTS) = [1,1,1]',
        'S_empty_done = $php_display_run(program_main, 10000, ' + json.dumps(b64(bytes(source))) + ', eps, ($ptascii("")))',
        'S_empty_done.COMPLETION = NORMAL', '$display_protocol_modes(S_empty_done.EVENTS) = [1]',
    ]
    helpers = r'''
    dec $display_protocol_modes(pevent*) : int*
    def $display_protocol_modes(eps) = eps
    def $display_protocol_modes((DISPLAY_STDOUT pevent) :: pevent_tail*) = 1 :: $display_protocol_modes(pevent_tail*)
    def $display_protocol_modes((DIAGNOSTIC text preqbytes z) :: pevent_tail*) = 2 :: $display_protocol_modes(pevent_tail*)
    def $display_protocol_modes((OUTPUT preqbytes) :: pevent_tail*) = $display_protocol_modes(pevent_tail*)
    '''
    rendered = 'dec $display_protocol_program() : program\ndef $display_protocol_program() = ' + fixture + '\n' + helpers
    rendered += '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks) + 'def $main() = false -- otherwise\n'
    assert len(checks) == 76
    return rendered, len(checks)


def prepare(out):
    source = SOURCES / 'main.php'
    eval_source = out / 'eval.php'
    eval_source.write_text("<?php ini_set('display_errors', 'stdout'); echo eval('return 4;');\n")
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(source.read_bytes())})
        parsed_eval = frontend.request({'op': 'parse', 'source': b64(eval_source.read_bytes())})
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], out / 'syntax-adapter')
    try:
        fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
    finally:
        adapter.close()
    rendered, count = render(fixture, source, R)
    (out / 'protocol.watsup').write_text(rendered)
    (out / 'prepared.json').write_text(json.dumps({'source': str(source), 'eval_source': str(eval_source),
                                                 'parsed': parsed, 'parsed_eval': parsed_eval, 'count': count}) + '\n')
    return out / 'protocol.watsup', count



def transport(prepared_path):
    C = R
    D = prepared_path.parent
    prepared = json.loads(prepared_path.read_text())
    b64 = lambda value: base64.b64encode(value).decode()
    startup = {'display_errors': b64(b'StDeRr')}
    request = {'op': 'execute', 'ast': prepared['parsed']['ast'], 'steps': 0,
               'filename': b64(bytes(Path(prepared['source']))), 'startup_ini': startup}
    snapshot = {'version': 1, 'main': request['filename'], 'cwd': b64(bytes(C)),
                'include_path': b64(b'.:'), 'entries': []}
    facts = {'env': [], 'argv': [request['filename']], 'file': request['filename'],
             'seconds': '0', 'microseconds': 0, 'variables': b64(b'EGPCS'), 'jit': True, 'cwd': snapshot['cwd']}
    cases = []
    for name, extra in [('ordinary', {}), ('request', {'request': facts}),
                        ('file', {'file_snapshot': snapshot}), ('request-file', {'request': facts, 'file_snapshot': snapshot})]:
        cases.append((name, dict(request, **extra), None))
    cases.append(('nullable', dict(request, startup_ini={'display_errors': None}), None))
    cases.append(('present-empty', dict(request, startup_ini={'display_errors': ''}), None))
    all_three = copy.deepcopy(dict(request, request=facts, file_snapshot=snapshot))
    all_three['startup_ini'].update(error_reporting=b64(b'30719'), include_path=b64(b'/registered'))
    all_three['file_snapshot']['include_path'] = b64(b'/registered')
    cases.append(('three-directive-request-file', all_three, None))
    bad = [
        ('empty-startup', {}, 'unexpected/missing fields'),
        ('partial-reporting-display', {'display_errors': startup['display_errors'], 'error_reporting': b64(b'1')}, 'unexpected/missing fields'),
        ('display-number', {'display_errors': 1}, 'expected string'),
        ('noncanonical-display', {'display_errors': 'Zh=='}, 'noncanonical base64 padding'),
        ('unknown-key', dict(startup, precision=b64(b'14')), 'unexpected/missing fields'),
    ]
    for name, ini, reason in bad:
        cases.append((name, dict(request, startup_ini=ini), reason))
    mismatch = copy.deepcopy(dict(request, file_snapshot=snapshot))
    mismatch['file_snapshot']['include_path'] = b64(b'/different')
    cases.append(('display-only-snapshot-mismatch', mismatch, 'file snapshot include_path differs from startup INI'))
    mismatch = copy.deepcopy(dict(request, request=facts, file_snapshot=snapshot))
    mismatch['request']['cwd'] = b64(b'/different')
    cases.append(('display-request-file-cwd-mismatch', mismatch, 'file snapshot request cwd mismatch'))
    rows = []
    worker = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], D / 'transport-worker')
    try:
        for name, payload, reason in cases:
            sequence = worker.sequence
            try:
                result = worker.request(payload)
            except AssertionError:
                result = types.wire.loads((worker.output / (str(sequence) + '.response')).read_text())
            if reason is None:
                state = result['state']
                raw = payload['startup_ini']['display_errors']
                expected = None if raw is None else list(map(str, base64.b64decode(raw)))
                expected_mode = '1' if raw is None else '0' if raw == '' else '2'
                path = payload['startup_ini'].get('include_path', b64(b'.:'))
                expected_path = list(map(str, base64.b64decode(path))) if 'file_snapshot' in payload or 'include_path' in payload['startup_ini'] else None
                passed = (result['ok'] and result['display_mode'] == expected_mode
                          and state['DISPLAYINIT'] == expected and state['DISPLAYINI'] == expected
                          and state['DISPLAYMODIFIED'] is False and state['FILEINCLUDEPATH'] == expected_path
                          and (state['REQUEST'] is not None) == ('request' in payload)
                          and (state['FILECWD'] is not None) == ('file_snapshot' in payload))
            else:
                passed = result.get('ok') is False and result.get('category') == 'runner_failure' and reason in result.get('message', '')
            rows.append({'id': name, 'packet': sequence, 'pass': passed, 'reason': result.get('message')})
            assert passed, (name, result)
    finally:
        worker.close()

    # Duplicate JSON keys are retained by wire.loads and must be rejected precisely.
    packet = types.wire.dumps(request)
    for name, raw_packet, reason in [
        ('duplicate-display-key', packet.replace(types.wire.dumps(startup), '{"display_errors":"U3REZVJy","display_errors":null}'), 'unexpected/missing fields'),
        ('duplicate-startup-header', packet[:-1] + ',"startup_ini":' + types.wire.dumps(startup) + '}', 'duplicate startup INI field'),
    ]:
        packet_path = D / (name + '.stdin')
        packet_path.write_text(raw_packet + '\n')
        command = ['bash', '-c', 'exec "$1" "$2" < "$3"', '--',
                   str(R / '_build/default/adapter/main.exe'), str(R), str(packet_path)]
        result = recorded(command, D / name, 30)
        response = types.wire.loads((D / (name + '.stdout')).read_text())
        passed = (result['exit'] == 0 and not result['timeout'] and not (D / (name + '.stderr')).read_bytes()
                  and response.get('ok') is False and response.get('category') == 'runner_failure'
                  and reason in response.get('message', ''))
        rows.append({'id': name, 'pass': passed, 'process': result, 'reason': response.get('message')})
        assert passed, (name, response)

    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(R / '.tools/php-file.so'),
                       str(R / 'frontend/worker.php')], D / 'eval-frontend')
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], D / 'eval-adapter')
    try:
        first = adapter.request({'op': 'execute', 'ast': prepared['parsed_eval']['ast'], 'steps': 1000,
                                 'filename': b64(bytes(Path(prepared['eval_source']))), 'startup_ini': {'display_errors': ''}})
        assert first['display_mode'] == '1' and first['pending']['mode'] == 'eval'
        parsed = frontend.request({'op': 'parse-eval', **first['pending']})
        response = {key: value for key, value in parsed.items() if key not in ('ok', 'diagnostics')}
        resumed = adapter.request({'op': 'resume_eval', 'response': response})
        passed = (resumed['display_mode'] == '1' and resumed['state']['DISPLAYINI'] == list(map(str, b'stdout'))
                  and resumed['state']['COMPLETION']['tag'] == 'NORMAL' and 'pending' not in resumed)
        rows.append({'id': 'genuine-execute-eval-resume-mode', 'pass': passed})
        assert passed, resumed
    finally:
        adapter.close()
        frontend.close()
    report = {'scope': 'new display entry and transport controls, including a genuine parser-service resume',
              'prepared': str(prepared_path), 'rows': rows, 'pass': all(row['pass'] for row in rows)}
    (D / 'transport-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'raw': str(D), 'checks': len(rows), 'pass': report['pass']}), flush=True)

    assert len(rows) == 17
    return report


def main():
    out = Path(tempfile.mkdtemp(prefix='display-errors-protocol-', dir=R / '.tools'))
    print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, Path(__file__), *sorted(SOURCES.rglob('*.php')), R / 'bin/php-semantics',
              R / 'adapter/main.ml', R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php',
              R / '.tools/php-file.so', R / 'tests/semantics/profile.json', R / 'tests/semantics/recorded_worker.py',
              R / 'tests/semantics/error_handler_run.py', R / 'tests/semantics/_build/default/numeric_runner.exe']
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in inputs}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    fixture, count = prepare(out)
    numeric = recorded([str(R / 'tests/semantics/_build/default/numeric_runner.exe'),
                        *map(str, modules), str(fixture)], out / 'numeric', 90)
    numeric_pass = (numeric['exit'] == 0 and not numeric['timeout']
                    and (out / 'numeric.stdout').read_bytes() == b'true\n' and not (out / 'numeric.stderr').read_bytes())
    process = recorded([sys.executable, str(Path(__file__).resolve()), '--transport', str(out / 'prepared.json')],
                       out / 'transport', 90)
    transport_pass = process['exit'] == 0 and not process['timeout'] and not (out / 'transport.stderr').read_bytes()
    assert before == {str(path.relative_to(R)): digest(path) for path in inputs}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    report = {'revision': revision, 'inputs': before, 'conditions': count, 'numeric': numeric,
              'transport': process, 'pass': numeric_pass and transport_pass,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['pass'], report


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--transport':
        transport(Path(sys.argv[2]))
    else:
        main()
