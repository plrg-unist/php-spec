#!/usr/bin/env python3
"""Malformed finite file facts leave the live adapter pause untouched."""
import base64
import copy
import hashlib
import importlib.machinery
import json
import os
import subprocess
from pathlib import Path
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CLI = importlib.machinery.SourceFileLoader('php_semantics_include', str(ROOT / 'bin/php-semantics')).load_module()
MAIN = b"<?php echo include 'one.php';"
CHILD = b'<?php return 7;'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree

def main():
    out = Path(tempfile.mkdtemp(prefix='include-adapter-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
              ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
              ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
              ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php',
              ROOT / 'frontend/target.php', ROOT / 'frontend/SourcePrinter.php',
              ROOT / 'frontend/encoding.php', ROOT / 'spec/schema.json',
              ROOT / 'spec/php.watsup', ROOT / 'adapter/main.ml', ROOT / '.tools/php/bin/php',
              ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
              ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py',
              ROOT / 'tests/validate.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_before = vendor_identity()
    path = out / 'main.php'
    child = out / 'one.php'
    path.write_bytes(MAIN)
    child.write_bytes(CHILD)
    main_path = os.fsencode(path.resolve())
    child_path = os.fsencode(child.resolve())
    entry = {'caller': b64(main_path), 'requested': b64(b'one.php'),
             'status': 'opened', 'resolved': b64(child_path),
             'opened': b64(child_path), 'source': b64(CHILD)}
    snapshot = {'version': 1, 'main': b64(main_path),
                'cwd': b64(os.fsencode(ROOT.resolve())),
                'include_path': b64(b'.:'), 'entries': [entry]}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = CLI.AdapterSession([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    checks = 0
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(MAIN)})
        assert parsed['accepted'], parsed
        initial = adapter.request({'op': 'execute', 'ast': parsed['ast'],
                                   'filename': b64(main_path), 'steps': 300,
                                   'file_snapshot': snapshot}, 30)
        assert initial['ok'] and initial['pending']['mode'] == 'file-resolve', initial
        assert initial['pending']['cwd'] == snapshot['cwd']
        assert initial['pending']['include_path'] == snapshot['include_path']
        checks += 1
        resolver = {'id': initial['pending']['id'], **entry}
        forged = copy.deepcopy(resolver)
        forged['opened'] = b64(b'/forged/one.php')
        rejected = adapter.request({'op': 'resume_file_resolve', 'response': forged}, 30)
        assert not rejected['ok'] and rejected['category'] == 'adapter_rejection', rejected
        checks += 1
        opened = adapter.request({'op': 'resume_file_resolve', 'response': resolver}, 30)
        assert opened['ok'] and opened['pending']['mode'] == 'file', opened
        assert opened['pending']['id'] == initial['pending']['id']
        checks += 2
        wrong_phase = adapter.request({'op': 'resume_file_resolve', 'response': resolver}, 30)
        assert not wrong_phase['ok'] and wrong_phase['category'] == 'adapter_rejection', wrong_phase
        checks += 1
        parsed_file = frontend.request({'op': 'parse-file', **opened['pending']})
        assert parsed_file['ok'] and parsed_file['accepted'], parsed_file
        response = {key: value for key, value in parsed_file.items() if key not in {'ok', 'diagnostics'}}
        checks += 1
        forged_file = copy.deepcopy(response)
        forged_file['source'] = b64(b'<?php return 8;')
        bad_parse = adapter.request({'op': 'resume_file_parse', 'response': forged_file}, 30)
        assert not bad_parse['ok'] and bad_parse['category'] == 'adapter_rejection', bad_parse
        checks += 1
        completed = adapter.request({'op': 'resume_file_parse', 'response': response}, 30)
        assert completed['ok'] and 'pending' not in completed, completed
        assert completed['state']['COMPLETION']['tag'] == 'NORMAL'
        checks += 2
        replay = adapter.request({'op': 'resume_file_parse', 'response': response}, 30)
        assert not replay['ok'] and replay['category'] == 'adapter_rejection', replay
        checks += 1

        fallback_path = out / 'fallback.php'
        wrapper = b'php://filter/read=/resource=' + child_path
        fallback_source = b'<?php $p="' + wrapper + b'"; echo include_once $p; echo include_once $p;'
        fallback_path.write_bytes(fallback_source)
        fallback_main = os.fsencode(fallback_path.resolve())
        fallback_entry = {'caller': b64(fallback_main), 'requested': b64(wrapper),
                          'status': 'opened', 'resolved': None,
                          'opened': b64(child_path), 'source': b64(CHILD)}
        fallback_snapshot = {**snapshot, 'main': b64(fallback_main), 'entries': [fallback_entry]}
        fallback_program = frontend.request({'op': 'parse', 'source': b64(fallback_source)})
        assert fallback_program['accepted'], fallback_program
        fallback_initial = adapter.request({'op': 'execute', 'ast': fallback_program['ast'],
                                            'filename': b64(fallback_main), 'steps': 300,
                                            'file_snapshot': fallback_snapshot}, 30)
        assert fallback_initial['ok'] and fallback_initial['pending']['mode'] == 'file-resolve'
        checks += 1
        fallback_fact = {'id': fallback_initial['pending']['id'], **fallback_entry}
        forged_fact = {**fallback_fact, 'resolved': b64(child_path)}
        assert not adapter.request({'op': 'resume_file_resolve', 'response': forged_fact}, 30)['ok']
        checks += 1
        fallback_parse = adapter.request({'op': 'resume_file_resolve', 'response': fallback_fact}, 30)
        assert fallback_parse['ok'] and fallback_parse['pending']['resolved'] is None
        checks += 1
        fallback_worker = frontend.request({'op': 'parse-file', **fallback_parse['pending']})
        assert fallback_worker['accepted'] and fallback_worker['resolved'] is None
        fallback_response = {key: value for key, value in fallback_worker.items() if key not in {'ok', 'diagnostics'}}
        checks += 1
        forged_parse = {**fallback_response, 'resolved': b64(child_path)}
        assert not adapter.request({'op': 'resume_file_parse', 'response': forged_parse}, 30)['ok']
        checks += 1
        fallback_second = adapter.request({'op': 'resume_file_parse', 'response': fallback_response}, 30)
        assert fallback_second['ok'] and fallback_second['pending']['mode'] == 'file-resolve'
        checks += 1
        second_fact = {'id': fallback_second['pending']['id'], **fallback_entry}
        fallback_done = adapter.request({'op': 'resume_file_resolve', 'response': second_fact}, 30)
        assert fallback_done['ok'] and 'pending' not in fallback_done
        assert fallback_done['state']['COMPLETION']['tag'] == 'NORMAL'
        assert len(fallback_done['state']['FILES']) == 2
        checks += 3
        assert not adapter.request({'op': 'resume_file_resolve', 'response': second_fact}, 30)['ok']
        checks += 1

        context_entry = {**entry, 'cwd': snapshot['cwd'],
                         'include_path': snapshot['include_path']}
        other_context = {**context_entry, 'cwd': b64(b'/other'),
                         'include_path': b64(b'other'),
                         'resolved': b64(out.as_posix().encode() + b'/other.php'),
                         'opened': b64(out.as_posix().encode() + b'/other.php'),
                         'source': b64(b'<?php return 8;')}
        context_snapshot = {**snapshot, 'version': 2,
                            'entries': [context_entry, other_context]}
        context_initial = adapter.request({'op': 'execute', 'ast': parsed['ast'],
                                           'filename': b64(main_path), 'steps': 300,
                                           'file_snapshot': context_snapshot}, 30)
        assert context_initial['ok'] and context_initial['pending']['mode'] == 'file-resolve'
        assert context_initial['pending']['cwd'] == context_entry['cwd']
        assert context_initial['pending']['include_path'] == context_entry['include_path']
        checks += 1
        context_fact = {'id': context_initial['pending']['id'], **context_entry}
        forged_context = {**context_fact, 'include_path': other_context['include_path']}
        assert not adapter.request({'op': 'resume_file_resolve', 'response': forged_context}, 30)['ok']
        checks += 1
        context_parse = adapter.request({'op': 'resume_file_resolve', 'response': context_fact}, 30)
        assert context_parse['ok'] and context_parse['pending']['mode'] == 'file'
        checks += 1
        context_worker = frontend.request({'op': 'parse-file', **context_parse['pending']})
        context_response = {key: value for key, value in context_worker.items()
                            if key not in {'ok', 'diagnostics'}}
        context_done = adapter.request({'op': 'resume_file_parse', 'response': context_response}, 30)
        assert context_done['ok'] and context_done['state']['COMPLETION']['tag'] == 'NORMAL'
        checks += 1

        context_path = out / 'context-snapshot.json'
        context_path.write_text(json.dumps(context_snapshot, sort_keys=True) + '\n')
        cli_result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path),
                                     '--file-snapshot', str(context_path), '--steps', '300'],
                                    cwd=ROOT, capture_output=True, timeout=60)
        cli_outcome = json.loads(cli_result.stdout)
        assert cli_result.returncode == 0 and cli_outcome['status'] == 'normal'
        assert base64.b64decode(cli_outcome['stdout']) == b'7'
        checks += 1
    finally:
        frontend.close()
        adapter.close()
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    assert vendor_before == vendor_identity()
    report = {'result': 'pass', 'assertions': checks, 'inputs': before, 'vendor_parser_tree': vendor_before,
              'main_sha256': digest(path), 'child_sha256': digest(child),
              'fallback_main_sha256': digest(fallback_path),
              'fallback_snapshot_sha256': hashlib.sha256(json.dumps(fallback_snapshot, sort_keys=True).encode()).hexdigest(),
              'snapshot_sha256': hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest(),
              'scope': 'Live v1/v2 resolve/parse pauses, forged context and source responses, phase separation and one-shot replay.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('include-adapter-protocol', checks, flush=True)
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
