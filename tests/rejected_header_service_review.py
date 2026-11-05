#!/usr/bin/env python3
"""Independent rejected-header facts, typed service boundary and CLI custody."""
import argparse
import base64
import copy
import hashlib
import importlib.machinery
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from encoding_declare_protocol import ParserWorker
from recorded_worker import Worker
import static_types as types

CLI = importlib.machinery.SourceFileLoader('rejected_header_cli', str(ROOT / 'bin/php-semantics')).load_module()
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
POSITIONS = ('beginLine', 'beginTokenPos', 'closeLine', 'closeTokenPos')
CASES = {
    'later-parse': (b'declare(encoding=1);\necho ;', [(1, 0, 1, 5)], [1]),
    'missing-body': (b'declare(encoding=1)', [(1, 0, 1, 5)], [1]),
    'literal-then-compile': (b'declare(encoding=1, encoding=true); echo "BAD|";', [(1, 0, 1, 10)], [1]),
    'nested-header': (b'declare(Foo=function(){declare(encoding=2);}, encoding=1); echo ;',
        [(1, 8, 1, 13), (1, 0, 1, 21)], [1, 1]),
    'nested-unclosed': (b'declare(encoding=1, Foo=function(){declare(encoding=2);},', [(1, 13, 1, 18)], [1]),
    'first-nonliteral': (b'declare(encoding=true);\ndeclare(encoding=1);', [(1, 0, 1, 5), (2, 8, 2, 13)], []),
}


def service(adapter, pending, response, accepted=True):
    operation = 'check_source_service' if pending['mode'] == 'eval' else 'check_file_source_service'
    try:
        result = adapter.request({'op': operation, 'pending': pending, 'response': response})
    except AssertionError as error:
        result = error.args[0]
    assert isinstance(result, dict) and result['ok'] is accepted, result
    if not accepted:
        assert result['category'] == 'adapter_rejection', result
    return result


def run(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    records, packets = [], {}
    try:
        for mode, name in [('eval', name) for name in CASES] + [('file', 'later-parse')]:
            code, positions, lines = CASES[name]
            if mode == 'file':
                code = b'<?php ' + code
                positions = [(a, b + 1, c, d + 1) for a, b, c, d in positions]
            pending = {'id': '1', 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(code)}
            if mode == 'file':
                pending.update(requested=b64(b'unit.php'), resolved=b64(b'/review/unit.php'), opened=b64(b'/review/unit.php'))
            result = frontend.request({'op': 'parse-' + mode, **pending})
            raw = (frontend.output / 'stderr').read_bytes()[len(frontend.recorded_stderr):]
            frontend.recorded_stderr.extend(raw)
            assert not result['accepted'] and result['diagnostics'] == []
            assert [tuple(row[key] for key in POSITIONS) for row in result['headers']] == positions
            assert raw.count(b'Warning: declare(encoding=...)') == len(lines)
            assert [int(line.rsplit(b' ', 1)[1]) for line in raw.splitlines()] == lines
            assert CLI.dynamic_parser_stderr(result, mode, raw)
            assert not CLI.dynamic_parser_stderr(result, mode, raw + b'Unexpected\n')
            if raw:
                assert not CLI.dynamic_parser_stderr(result, mode, b'')
                assert not CLI.dynamic_parser_stderr(result, mode, raw.replace(b'line 1', b'line 9'))
                assert not CLI.dynamic_parser_stderr(result, mode, raw.replace(b' in ', b' from '))
            response = {key: value for key, value in result.items() if key not in ('ok', 'diagnostics')}
            checked = service(adapter, pending, response)
            assert checked['headers'] == response['headers']
            packets[mode, name] = (pending, response)
            records.append({'id': mode + '-' + name, 'source_sha256': hashlib.sha256(code).hexdigest(),
                'header_positions': positions, 'warning_lines': lines, 'category': result['category']})

        pending, response = packets['eval', 'later-parse']
        legacy = copy.deepcopy(response); del legacy['headers']
        assert 'headers' not in service(adapter, pending, legacy)
        assert not CLI.dynamic_parser_stderr(legacy, 'eval', b'Warning: unexplained\n')
        empty = dict(response, headers=[])
        assert service(adapter, pending, empty)['headers'] == []
        malformed = []
        for value in (None, {}, 'headers'):
            malformed.append(('headers-type', dict(response, headers=value)))
        for key in POSITIONS:
            for value in (True, '1', 1.5, []):
                changed = copy.deepcopy(response); changed['headers'][0][key] = value
                malformed.append((key + '-type', changed))
        for change in ('missing', 'extra', 'items-type', 'item-node', 'item-integer'):
            changed = copy.deepcopy(response); header = changed['headers'][0]
            if change == 'missing': del header['closeLine']
            elif change == 'extra': header['severity'] = 'Warning'
            elif change == 'items-type': header['items'] = {}
            elif change == 'item-node': header['items'][0] = {'node': 'Stmt_Nop', 'fields': [], 'meta': {}}
            else: header['items'][0]['fields'][1]['fields'][0] = {'int': '01'}
            malformed.append((change, changed))
        for key, value in [('id', '2'), ('mode', 'file'), ('profile', 'other'), ('source', b64(b'other'))]:
            malformed.append((key + '-identity', dict(response, **{key: value})))
        for name, changed in malformed:
            service(adapter, pending, changed, False); records.append({'id': name, 'expected': 'adapter_rejection'})
        file_pending, file_response = packets['file', 'later-parse']
        for key in ('requested', 'resolved', 'opened'):
            service(adapter, file_pending, dict(file_response, **{key: b64(b'/forged.php')}), False)
            records.append({'id': key + '-identity', 'expected': 'adapter_rejection'})
        # Well-typed range/order facts pass this transport boundary. Semantic
        # response-shape guards, exercised separately, decide their admissibility.
        changed = copy.deepcopy(response); changed['headers'][0]['closeLine'] = 0
        assert service(adapter, pending, changed)['headers'][0]['closeLine'] == 0
        code = b'declare(encoding=1);\n/* incomplete'
        lexical = frontend.request({'op': 'parse-eval', **dict(pending, source=b64(code))})
        raw = (frontend.output / 'stderr').read_bytes()[len(frontend.recorded_stderr):]
        frontend.recorded_stderr.extend(raw)
        assert not lexical['accepted'] and lexical['headers'] and raw
        assert CLI.dynamic_parser_stderr(lexical, 'eval', raw)
        records += [{'id': 'typed-range-deferred', 'expected': 'checked_fact'},
                    {'id': 'lexer-prefix', 'expected': 'checked header prefix'}]
    finally:
        try: adapter.close()
        finally: frontend.close()
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), *(ROOT / name for name in ('adapter/main.ml', 'bin/php-semantics',
        'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php',
        'frontend/encoding-literal.php', 'spec/php.watsup', 'spec/schema.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/profile.json', 'tests/semantics/recorded_worker.py',
        'tests/semantics/static_types.py', 'tests/semantics/encoding_declare_protocol.py'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    assert before['.tools/php/bin/php'] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'profile': types.PROFILE,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'source_agreement_credit': 0, 'passed': False}
    try:
        report['records'] = run(out)
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['inputs_stable'] and report['head_stable']
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', len(report['records']))


if __name__ == '__main__': main()
