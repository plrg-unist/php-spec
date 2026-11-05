#!/usr/bin/env python3
"""Independent rejected-main transport, filename binding and startup forwarding."""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from encoding_declare_protocol import CLI, MESSAGE, ParserWorker
from recorded_worker import Worker
import static_types as types

b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
ORACLE = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
SOURCE = b'<?php\ndeclare(encoding=1,Foo=function(){\n declare(encoding=2);\n},encoding=3);\necho ;'


def file_packet(frontend, source, filename):
    identity = b64(os.fsencode(filename))
    value = frontend.parse({'op': 'parse-file', 'id': '0', 'mode': 'file', 'profile': 'cli-raw-85',
        'requested': identity, 'resolved': identity, 'opened': identity, 'source': b64(source)})
    assert not value['accepted'] and value['diagnostics'] == [], value
    return {key: value for key, value in value.items() if key not in ('ok', 'diagnostics')}


def request(adapter, packet, rejected=False):
    try:
        result = adapter.request(packet)
    except AssertionError as error:
        result = error.args[0]
    assert isinstance(result, dict) and result['ok'] is not rejected, result
    if rejected:
        assert result['category'] == 'adapter_rejection', result
    return result


def run(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    records = []
    try:
        filename = out / 'main \u03bb source.php'; filename.write_bytes(SOURCE)
        response = file_packet(frontend, SOURCE, filename)
        assert response['line'] == 5 and [row['closeLine'] for row in response['headers']] == [3, 4]
        packet = {'op': 'execute_rejected_main', 'source': b64(SOURCE), 'filename': b64(os.fsencode(filename)),
                  'steps': 0, 'response': response}
        messages = [b'Warning: ' + MESSAGE.encode() + b' in ' + os.fsencode(filename) + b' on line '
                    + str(line).encode() + b'\n' for line in (3, 4, 4)]
        messages.append(b'Parse error: syntax error, unexpected token ";" in '
                        + os.fsencode(filename) + b' on line 5\n')
        for name, startup, stdout, stderr in (
            ('default', None, b'', b''.join(messages)),
            ('stdout', {'display_errors': b64(b'1')}, b''.join(b'\n' + row for row in messages), b''),
            ('masked', {'error_reporting': b64(b'0'), 'include_path': b64(b'.:')}, b'', b'')):
            changed = copy.deepcopy(packet)
            if startup is not None: changed['startup_ini'] = startup
            result = request(adapter, changed)
            assert 'pending' not in result
            state = result['state']
            assert state['COMPLETION']['tag'] == 'REQUESTFATAL'
            assert all(state[key] == [] for key in ('SOURCES', 'CODE', 'DECLARATIONS', 'OBJECTS', 'TODO', 'FAILEDSOURCES'))
            observed = CLI['observe'](state, filename, result['display_mode'])
            assert observed['status'] == 'php_error' and observed['exit_status'] == 255
            assert observed['stdout'] == b64(stdout) and observed['stderr'] == b64(stderr), observed
            assert observed['diagnostic'] == {'class': 'ParseError', 'message': b64(b'syntax error, unexpected token ";"'), 'line': 5}
            records.append({'id': name, 'expected': 'terminal rejected source'})

        malformed = []
        for key, value in [('id', '1'), ('mode', 'eval'), ('profile', 'other'),
                           ('source', b64(b'<?php echo ;')), ('requested', b64(b'other.php')),
                           ('resolved', None), ('opened', b64(b'other.php')), ('category', 'other'),
                           ('message', ''), ('line', 0), ('line', True)]:
            changed = copy.deepcopy(packet); changed['response'][key] = value
            malformed.append((key + '-response', changed))
        for key, value in [('source', b64(b'<?php echo ;')), ('filename', b64(b'/other.php')),
                           ('steps', -1), ('steps', True), ('ast', {'version': 1, 'program': []}),
                           ('startup_ini', {'precision': b64(b'-2')})]:
            malformed.append((key + '-request', dict(packet, **{key: value})))
        for kind in ('missing-response', 'missing-source', 'header-type', 'header-integer', 'item-type', 'accepted'):
            changed = copy.deepcopy(packet)
            if kind.startswith('missing-'): del changed[kind.removeprefix('missing-')]
            elif kind == 'header-type': changed['response']['headers'] = {}
            elif kind == 'header-integer': changed['response']['headers'][0]['closeTokenPos'] = True
            elif kind == 'item-type': changed['response']['headers'][0]['items'] = ['not-a-node']
            else:
                identity = {key: changed['response'][key] for key in ('id', 'mode', 'profile', 'requested', 'resolved', 'opened', 'source')}
                changed['response'] = dict(identity, accepted=True, ast={'version': 1, 'program': []})
            malformed.append((kind, changed))
        for name, changed in malformed:
            request(adapter, changed, True); records.append({'id': name, 'expected': 'adapter_rejection'})
        # A typed position is a foreign fact. Its range is checked by P4.
        changed = copy.deepcopy(packet); changed['response']['headers'][0]['closeLine'] = 0
        result = request(adapter, changed)
        assert result['state']['COMPLETION'] == {'tag': 'UNSUPPORTED', 'args': ['invalid rejected main source or startup facts']}
        records.append({'id': 'typed-range', 'expected': 'unsupported'})
        # Receipt omission retains the legacy no-prefix service contract.
        changed = copy.deepcopy(packet); del changed['response']['headers']
        result = request(adapter, changed)
        observed = CLI['observe'](result['state'], filename, result['display_mode'])
        assert observed['stderr'] == b64(messages[-1]) and observed['exit_status'] == 255
        records.append({'id': 'legacy-no-headers', 'expected': 'terminal without prefix'})
    finally:
        try: adapter.close()
        finally: frontend.close()
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *modules, *(ROOT / name for name in ('adapter/main.ml', 'bin/php-semantics',
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php', '.tools/php/bin/php',
        '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/profile.json',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/semantics/encoding_declare_protocol.py'))]
    before = {str(path): sha(path) for path in paths}
    assert before[str(ROOT / '.tools/php/bin/php')] == ORACLE
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'profile': types.PROFILE, 'module_count': len(modules),
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'source_agreement_credit': 0, 'passed': False}
    try:
        report['records'] = run(out)
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path): sha(path) for path in paths}
        report['passed'] = report['head_stable'] and report['inputs_stable']
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', len(report['records']))


if __name__ == '__main__': main()
